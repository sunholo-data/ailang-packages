#!/bin/bash
# Mutation test of the key checks. Each mutant is applied to a scratch copy of
# the package (never to the working tree) and must be KILLED by at least one
# of the checks listed for it. Exit 1 if any mutant survives.
#   checks: check (ailang check --package), verify (Z3 on core.ail),
#   bverify (Z3 on brand.ail), core / brand / widget (ailang test), flow (tests/flow_check.sh),
#   sim (tests/widget_sim.sh: the widget's after-upload flow under node, mocked App),
#   fetch (tests/fetch_check.sh, network),
#   e2e (tests/e2e_uploads.sh: real serve-api on a random local port)
# MUTATION_SKIP_NET=1 skips the fetch-only mutants (reported as SKIPPED).
set -uo pipefail
PKG="$(cd "$(dirname "$0")/.." && pwd)"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
survived=0; killed=0; skipped=0

run_check() {  # $1 = check name, cwd = mutant copy; returns 0 if the check PASSES
  case "$1" in
    check)  out=$(ailang check --package . 2>&1); grep -q "all passed" <<<"$out" ;;
    verify) out=$(ailang verify core.ail 2>&1); ! grep -qE "VIOLATION|ERROR" <<<"$out" ;;
    core)   out=$(ailang test core_test.ail 2>&1); grep -q " 0 failed" <<<"$out" ;;
    brand)  out=$(ailang test brand_test.ail 2>&1); grep -q " 0 failed" <<<"$out" ;;
    bverify) out=$(ailang verify brand.ail 2>&1); ! grep -qE "VIOLATION|ERROR" <<<"$out" ;;
    widget) ./tools/gen_bundle.sh >/dev/null 2>&1; out=$(ailang test widget_test.ail 2>&1); grep -q " 0 failed" <<<"$out" ;;
    sim)    ./tests/widget_sim.sh >/dev/null 2>&1 ;;
    flow)   ./tests/flow_check.sh >/dev/null 2>&1 ;;
    fetch)  ./tests/fetch_check.sh >/dev/null 2>&1 ;;
    e2e)    E2E_PORT=$((18900 + RANDOM % 90)) ./tests/e2e_uploads.sh >/dev/null 2>&1 ;;
  esac
}

mutant() {  # name file old new checks...
  local name="$1" file="$2" old="$3" new="$4"; shift 4
  if [ "${MUTATION_SKIP_NET:-0}" = 1 ] && [ "$*" = fetch ]; then echo "SKIPPED  $name (network)"; skipped=$((skipped+1)); return; fi
  rm -rf "$WORK/m"; cp -R "$PKG" "$WORK/m"
  if ! python3 -I "$PKG/tests/mutate.py" "$WORK/m/$file" "$old" "$new"; then echo "ERROR    $name: anchor"; survived=$((survived+1)); return; fi
  local by=()
  for c in "$@"; do (cd "$WORK/m" && run_check "$c") || by+=("$c"); done
  if [ ${#by[@]} -gt 0 ]; then echo "KILLED   $name  (by: ${by[*]})"; killed=$((killed+1))
  else echo "SURVIVED $name"; survived=$((survived+1)); fi
}

mutant "verdict ignores single use"      core.ail "if firstUse == false then Replayed else" "if false then Replayed else" verify core flow
mutant "expiry off by one"               core.ail "  nowSec >= expiresAt
}" "  nowSec > expiresAt
}" verify core flow
mutant "size cap off by one"             core.ail "else if size > maxBytes then TooLarge" "else if size > maxBytes + 1 then TooLarge" verify core flow
mutant "cross-account check dropped"     core.ail "if ownerMatches(owner, caller) == false then NotFound" "if false then NotFound" verify core flow
mutant "ceiling clamp dropped"           core.ail "if requested <= 0 || requested > ceiling then ceiling" "if requested <= 0 then ceiling" verify core flow
mutant "fileRef id not checked"          core.ail "if isFileId(id) then Some(id)" "if true then Some(id)" core
mutant "leading dots kept"               core.ail "let noDots = stripLeadingDots(cleaned)" "let noDots = cleaned" core
mutant "http download_url allowed"       core.ail '  startsWith(url, "https://") && length(url) > 8 && strContains(url, "@") == false
}' '  length(url) > 8 && strContains(url, "@") == false
}' verify core fetch
mutant "claim result ignored"            flow.ail 'let firstUse = claimMeta(h, "used:${d}", "{}", exp);' 'let firstUse = claimMeta(h, "used:${d}", "{}", exp) || true;' flow
mutant "token expiry extended"           flow.ail 'let exp = intOr(rec, "expires_at");' 'let exp = intOr(rec, "expires_at") + 600;' flow
mutant "fileRef not deleted after use"   flow.ail '                let _ = forget(h, id);
                if sha' '                let _ = true;
                if sha' flow
mutant "sha256 integrity check dropped"  flow.ail 'if sha != strOr(rec, "sha256") then' 'if false then' flow
mutant "mime allow-list at accept dropped" flow.ail 'if mimeAllowed(mime, h.allowedMimes) == false then Err' 'if false then Err' flow
mutant "token key stored raw"            flow.ail 'putMeta(h, "tok:${digestOf(token)}"' 'putMeta(h, "tok:${token}"' check
mutant "fetch size cap dropped"          flow.ail 'if sizeOk(size, maxBytes) == false then' 'if false then' fetch
mutant "temp-path guard dropped"         flow.ail 'else if isUploadTempPath(path, tempDir) == false then {' 'else if false then {' flow e2e
mutant "unwired temp dir accepted"       flow.ail 'if trim(tempDir) == "" then Err(' 'if false then Err(' flow
mutant "temp-path prefix check dropped"  core.ail 'if startsWith(base, "/") == false || startsWith(path, prefix) == false then false' 'if startsWith(base, "/") == false then false' core flow e2e
mutant "relative temp dir allowed"       core.ail 'if startsWith(base, "/") == false || startsWith(path, prefix)' 'if startsWith(path, prefix)' core
mutant "temp-path depth loosened"        core.ail '    [dir, name] =>' '    dir :: name :: _ =>' core
mutant "temp-path dot names allowed"     core.ail '&& name != "" && name != "." && name != ".."' '&& name != ""' core e2e
mutant "serve-api dir prefix dropped"    core.ail 'startsWith(dir, uploadTempDirPrefix()) && length(dir) > length(uploadTempDirPrefix())' 'true' core
mutant "widget picker shown when idle"   assets/widget.js '  ready.hidden = true;
  const line = CFG.resultSummary' '  ready.hidden = false;
  const line = CFG.resultSummary' widget
mutant "via-host arg named token again"  assets/widget.js 'arguments: { ticket: desc' 'arguments: { token: desc' widget
mutant "widget oversize guard dropped"   assets/widget.js 'if (desc.maxBytes && f.size > desc.maxBytes) {' 'if (false) {' widget

# 0.1.2 branding: the logo sanitiser, the accent check, links, rendering, theming.
mutant "logo: script frame check dropped"  brand.ail '&& contains(t, "script") == false && contains(t, "&#") == false && contains(t, "<!") == false && contains(t, "<?") == false' '&& contains(t, "&#") == false && contains(t, "<!") == false && contains(t, "<?") == false' bverify brand
mutant "logo: handler check dropped"       brand.ail 'svgFrameOk(t) && svgTagsOk(t) && svgNoHandlers(t) &&' 'svgFrameOk(t) && svgTagsOk(t) &&' brand widget
mutant "logo: handler after whitespace"    brand.ail 'contains("abcdefghijklmnopqrstuvwxyz0123456789", c)' 'contains("abcdefghijklmnopqrstuvwxyz0123456789 ", c)' brand
mutant "logo: element allow-list dropped"  brand.ail 'svgFrameOk(t) && svgTagsOk(t) &&' 'svgFrameOk(t) &&' brand
mutant "logo: any href allowed"            brand.ail 'startsWith(rest, "=${q}${v}")' 'startsWith(rest, "=")' brand
mutant "logo: svg data url allowed"        brand.ail '["#", "data:image/png",' '["#", "data:image/svg", "data:image/png",' brand
mutant "logo: external url() allowed"      brand.ail '&& svgHrefsOk(t) && svgUrlsOk(t)' '&& svgHrefsOk(t)' brand
mutant "logo: not lowercased"              brand.ail 'let t = toLower(trim(s));' 'let t = trim(s);' brand
mutant "logo: trailing content allowed"    brand.ail '&& endsWith(t, "</svg>") && find(t, "</svg>") == length(t) - 6
    &&' '&& endsWith(t, "</svg>")
    &&' bverify brand
mutant "logo: bad logo used as given"      brand.ail 'else if svgLogoOk(b.logoSvg) then trim(b.logoSvg) else ailangLogoSvg()' 'else trim(b.logoSvg)' brand widget
mutant "accent: any length up to 7"        brand.ail '  (length(a) == 4 || length(a) == 7) && startsWith(a, "#") && hexAt' '  length(a) <= 7 && startsWith(a, "#") && hexAt' bverify brand
mutant "accent: wider digit set"           brand.ail '  length(c) == 1 && contains("0123456789abcdefABCDEF", c)
}' '  length(c) == 1 && contains("0123456789abcdefABCDEF;} ", c)
}' bverify brand
mutant "accent: last digit unchecked"      brand.ail '&& hexAt(a, 5) && hexAt(a, 6)' '&& hexAt(a, 5)' brand
mutant "accent: fallback dropped"          brand.ail 'if accentOk(b.accent) then b.accent else' 'if true then b.accent else' brand widget
mutant "link: http allowed"                brand.ail '  startsWith(u, "https://") && length(u) > 8' '  length(u) > 8' bverify brand
mutant "link: filter dropped"              brand.ail 'filter(\l. linkUrlOk(l.url) && trim(l.label) != "", b.footerLinks)' 'b.footerLinks' brand widget
mutant "footer label not escaped"          widget.ail '${htmlEscape(trim(l.label))}</a>' '${trim(l.label)}</a>' widget
mutant "brand name not escaped"            widget.ail "<span class='name'>\${htmlEscape(name)}</span>" "<span class='name'>\${name}</span>" widget
mutant "host theme not applied"            assets/widget.js "    if (ctx.theme === 'light' || ctx.theme === 'dark') x.applyDocumentTheme(ctx.theme);
" "" widget
mutant "host context change ignored"       assets/widget.js "  app.addEventListener('hostcontextchanged', () => applyHost(app.getHostContext()));
" "" widget
mutant "logo shown in chatgpt"             assets/widget.js "if (window.openai) el('brand').hidden = true;" "" widget
mutant "accent leaks onto body text"       assets/widget.css 'color:var(--color-text-primary,var(--mf-fg))}' 'color:var(--mf-accent)}' widget

# 0.1.3 after-upload tool call: the widget runs it, substitutes safely, falls back, reports.
mutant "after-upload: auto-call skipped"     assets/widget.js "    await runTool(rc, via);" "    await reportOnly(rc, via, CFG.afterUpload);" sim
mutant "after-upload: string concatenation"  assets/widget.js "const args = fillArgs(CFG.onUploaded.argsJson, rc.fileRef);" "const args = JSON.parse(CFG.onUploaded.argsJson.split(PLACEHOLDER).join(rc.fileRef));" sim
mutant "after-upload: capability fallback dropped" assets/widget.js "  } else if (!canCallTools()) {" "  } else if (false) {" sim
mutant "after-upload: capability not checked" assets/widget.js "(app.getHostCapabilities() || {}).serverTools" "(app.getHostCapabilities() || {})" sim widget
mutant "after-upload: substring placeholder filled" assets/widget.js "      if (v.indexOf(PLACEHOLDER) >= 0) throw" "      if (false) throw" sim
mutant "after-upload: placeholder key allowed"  assets/widget.js "        if (k.indexOf(PLACEHOLDER) >= 0) throw" "        if (false) throw" sim
mutant "after-upload: placeholder count unchecked" assets/widget.js "  if (n !== 1) throw" "  if (n < 1) throw" sim
mutant "after-upload: context size cap dropped" assets/widget.js "  const text = head.length + body.length + 40 <= MAX_CONTEXT_CHARS" "  const text = true" sim
mutant "after-upload: error not told to the model" assets/widget.js "    try {
      await tell(uploadedText(rc, via) + ' The widget then called '" "    try { return;
      await tell(uploadedText(rc, via) + ' The widget then called '" sim
mutant "after-upload: summary not shown"     assets/widget.js "  const done = parsed ? clip(" "  const done = false ? clip(" sim
mutant "template: key check dropped"         widget.ail "        else if placeholderKeys(j) != 0 then" "        else if false then" widget
mutant "template: whole-value check dropped" widget.ail "        else if wholePlaceholders(j) != 1 then" "        else if false then" widget
mutant "template: raw count dropped"         widget.ail "        if occurrences(t, fileRefPlaceholder()) != 1 then" "        if false then" widget
mutant "template: non-object allowed"        widget.ail '      _ => "argsJson must be a JSON object"' '      _ => ""' widget
mutant "tool name: any character"            widget.ail "  length(t) >= 1 && length(t) <= 64 && toolCharsFrom(t, 0)" "  length(t) >= 1 && length(t) <= 64" widget
mutant "tool name: no length cap"            widget.ail "  length(t) >= 1 && length(t) <= 64 && toolCharsFrom(t, 0)" "  length(t) >= 1 && toolCharsFrom(t, 0)" widget
mutant "invalid onUploaded rendered anyway"  widget.ail "  if o.tool != \"\" && onUploadedProblem(o) == \"\" then o else noAutoCall()" "  o" widget
# 0.1.3 result cards and batches: one line from the result; one token per file.
mutant "result card: resultSummary ignored"   assets/widget.js "const line = CFG.resultSummary && r ? resultLine(" "const line = r ? resultLine(" sim
mutant "result card: line never shown"        assets/widget.js "const line = CFG.resultSummary && r ? resultLine(r, toolTitle()) : null;" "const line = null;" sim widget
mutant "result card: full path shown"         assets/widget.js "return clip(f.split(/[\\\\/]/).pop()" "return clip(f" sim
mutant "result card: http download offered"   assets/widget.js "/^https:" "/^https?:" sim
mutant "result card: no 120-character cap"    assets/widget.js "const ONE_LINE = 120;" "const ONE_LINE = 1000;" sim
mutant "result card: comments not counted"    assets/widget.js "    if (x.type === 'comment') n++;" "" sim
mutant "result card: zero counts shown"       assets/widget.js "isFinite(n) && n !== 0) parts.push" "isFinite(n)) parts.push" sim
mutant "result card: error object ignored"    assets/widget.js "  if (err && typeof err === 'object') {" "  if (false) {" sim
mutant "batch: count cap dropped"             flow.ail "  if count < 1 || count > maxBatchUploads()" "  if count < 1" flow
mutant "batch: note dropped from descriptor"  core.ail ', kv("note", js(singleUseNote()))])' '])' core flow
mutant "409 no longer says one per file"      flow.ail "already used — call createUpload again for each file" "already used; ask for a new one" flow

echo "mutants: $killed killed, $survived survived, $skipped skipped"
[ $survived -eq 0 ]
