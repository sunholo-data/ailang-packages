#!/bin/bash
# Mutation test of the key checks. Each mutant is applied to a scratch copy of
# the package (never to the working tree) and must be KILLED by at least one
# of the checks listed for it. Exit 1 if any mutant survives.
#   checks: check (ailang check --package), verify (Z3 on core.ail),
#   core / widget (ailang test), flow (tests/flow_check.sh),
#   fetch (tests/fetch_check.sh, network)
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
    widget) ./tools/gen_bundle.sh >/dev/null 2>&1; out=$(ailang test widget_test.ail 2>&1); grep -q " 0 failed" <<<"$out" ;;
    flow)   ./tests/flow_check.sh >/dev/null 2>&1 ;;
    fetch)  ./tests/fetch_check.sh >/dev/null 2>&1 ;;
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
mutant "widget oversize guard dropped"   assets/widget.js 'if (desc.maxBytes && f.size > desc.maxBytes) {' 'if (false) {' widget

echo "mutants: $killed killed, $survived survived, $skipped skipped"
[ $survived -eq 0 ]
