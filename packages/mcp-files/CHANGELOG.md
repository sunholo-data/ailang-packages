# Changelog — sunholo/mcp_files

## 0.1.3 — 2026-10-07

**The widget finishes the job: after the upload it calls a configured server tool itself; result
cards say what happened; one upload token per file, said everywhere.** One breaking change, for
literal `WidgetConfig` constructions only (pre-1.0).

- **Why.** Live in claude.ai (prod, 2026-10-07) the upload landed (13 211 B accepted) and the widget
  reported the fileRef with `ui/update-model-context`. That only updates the model's context; it
  starts no model turn. The widget sat on "parsing…" until the user typed, and Claude said it "never
  got confirmation that the upload finished".
- **`WidgetConfig.onUploaded: OnUploaded {tool, argsJson}`.** After a successful upload (direct POST
  or the via-host fallback) the widget calls `tool` through the host: an app-initiated `tools/call`
  (ext-apps `App.callServerTool`, 5-minute timeout), gated on the host's `serverTools` capability.
  `argsJson` is a JSON object template holding the string value `"{{fileRef}}"` exactly once, e.g.
  `{"fileRef":"{{fileRef}}","outputFormat":"blocks"}`. The widget parses it and replaces only that
  whole string value; nothing is concatenated into text or code.
  - Progress: "Uploaded <name> (<size>) — <afterUpload>", then "✓ Parsed AGM.docx · 68 blocks · 13
    headings · 4 tracked changes" when the result has a `summary` object (top level or up to two
    levels down, e.g. docparse's `document.summary`), else "✓ Done".
  - The model gets one `ui/update-model-context`: the receipt, the fileRef and the tool result. A
    result that would push the text past 100 000 characters is left out: the model gets the summary
    and the fileRef and is told to call the tool itself.
  - On error the widget shows it and tells the model (context update), so it can retry.
  - A host without `serverTools`: the 0.1.2 behaviour, plus "Uploaded <name> (<size>) — tell the
    assistant to continue."
  - Never `ui/message`.
- **Checked in the package.** `toolNameOk` (`[A-Za-z0-9_-]{1,64}`), `argsTemplateProblem` (valid
  JSON, an object, the placeholder exactly once in the raw text and once as a whole string value, never
  in a key or inside a longer string, no JSON-escaped spelling) and `onUploadedProblem`. A failing
  config is not rendered (`checkedOnUploaded`): the widget reports the fileRef only and logs the
  problem to the browser console. The widget re-checks the template before calling.
- **Result cards (`WidgetConfig.resultSummary: bool`, default `true`).** A card with no upload (a
  call given a fileRef or a document) showed a bare "Done." on every card; in a 14-file batch in
  claude.ai that said nothing. It now shows one compact line (≤ 120 characters, single line) read
  from the call's own result:
  - parse: "✓ Parsed <file> · <N> blocks · <H> headings · <T> tables · <I> images · <C> tracked
    changes · <M> comments", the file name's last path segment only, zero counts omitted, comments
    counted from the block tree (bounded walk);
  - error: "✗ <error.code>: <message>" (also the package's own `{error, error_description}` and a
    bare `isError` text);
  - anything else: "✓ <tool title> done · <file or target>", the title from the host context's
    `toolInfo`, plus a Download button for an https `download_url` (opened with `app.openLink`).
  `false` keeps "Done." / "No upload needed.".
- **One upload token per file.** In the same batch the model tried to upload 13 more files with one
  token. Tokens stay single use; now it is said:
  - every descriptor carries `note` (`core.singleUseNote()`): "One file per upload token … call
    createUpload again for each file (one createUpload/token per file)";
  - a reused token answers 409 "this upload token was already used — call createUpload again for
    each file";
  - new `flow.createUploads(h, account, count, maxBytes, nowSec)`: `count` (1..20,
    `core.maxBatchUploads()`) descriptors in one call, `{uploads, count, note}`, each with its own
    token and fileRef; outside 1..20 is 400. For clients that run code (the curl path); the widget
    still takes one descriptor per card.
- **Breaking:** `defaultWidgetConfig` sets `onUploaded: noAutoCall()` (`tool: ""`, today's
  behaviour) and `resultSummary: true`, so `defaultWidgetConfig(…)` and `{ cfg | … }` updates keep
  working. A literal `WidgetConfig` record must add `onUploaded: noAutoCall()` (or
  `callAfterUpload(tool, argsJson)`) and `resultSummary: true`. The descriptor golden gains `note`.
- **Tests:**
  - 17 widget tests (template validation: bad JSON, zero or two placeholders, a placeholder in a key,
    concatenated, JSON-escaped, not an object; tool names; config rendering; a template cannot close
    the script; result cards on by default);
  - 3 flow cases: the 409 and the descriptor say one createUpload per file; `createUploads(3)`
    gives three distinct tokens and fileRefs, each accepted once, a reused one 409; count 0, 21 and
    no account refused, 20 accepted;
  - `tests/widget_sim.sh`: 33 scenarios of `assets/widget.js` under node with a mocked ext-apps App
    (upload → `tools/call` with the substituted args → context update with the summary; no summary;
    text-JSON result; a large result; tool error; rejected call; no `serverTools`; no tool; via-host
    then the tool; 9 bad templates refused in the widget; a hostile fileRef stays one value; 11
    result cards: parse line with comments, Windows path, error object, package error, `isError`
    text, titled convert with an https download opened via `openLink`, http download refused, the
    120-character cap, `resultSummary: false`, nothing to read);
  - 28 new mutants (75 in all).

## 0.1.2 — 2026-10-07

**Widget branding: AILANG by default, adjustable downstream.** One breaking change, for literal
constructions only (pre-1.0).

- **New module `brand`:**
  - `Brand {name, logoSvg, accent, footerLinks: [FooterLink {label, url}], poweredBy}`;
  - `defaultBrand()`: "AILANG", the AILANG hexagon-and-lambda mark as a ~0.6 KB inline SVG, accent
    `#d03614` and "Powered by AILANG";
  - `brandWith(name, logoSvg, accent, footerLinks)` for a downstream service.
- **`WidgetConfig` gains `brand: Brand`.** `defaultWidgetConfig` sets `defaultBrand()`, so
  `defaultWidgetConfig(…)` and `{ cfg | … }` updates keep working. **Breaking:** a literal
  `WidgetConfig` record (all fields spelled out) must add `brand: defaultBrand()`.
- **Checked values.** A value that fails a check is replaced, never rendered:
  - the logo must pass `svgLogoOk`: an allow-list of SVG elements, no `script`, no `on*` handler,
    no `javascript:` or `&#`, no external `href`/`xlink:href`/`url()`. Fragments and raster `data:`
    images only. Otherwise the AILANG logo is used, and `""` means no logo;
  - the accent must pass `accentOk` (`#rgb`/`#rrggbb`), else `#d03614`;
  - footer links must pass `linkUrlOk` (https), else they are dropped;
  - labels and the name are html-escaped.
  `svgFrameOk`, `accentOk`, `isHexDigit` and `linkUrlOk` are proved by Z3.
- **Host theming.** The widget applies the MCP Apps host context (`theme`, `styles.variables`,
  `styles.css.fonts`) with the bundled ext-apps helpers, and re-applies it on `hostcontextchanged`.
  ChatGPT's `window.openai.theme` is followed too. Without a host theme it falls back to
  `prefers-color-scheme`. Text, borders, fonts and radii use host variables with light/dark
  fallbacks. The background is transparent.
- **Accent placement.** The accent colours only the primary button and the focus ring, with
  WCAG-contrasting text.
- **Header and footer.** They show with the picker. The header is hidden in ChatGPT, which draws
  the app's logo itself. Footer links open via `app.openLink` / `openai.openExternal`. The rules
  followed, with quotes and URLs, are in AGENT.md "Branding".
- **Tests:**
  - 48 brand tests: hostile SVGs refused (script, handlers incl. tab/slash/quote-adjacent,
    javascript:, encoded, external and svg-data hrefs, `url()`, xml:base, style, foreignObject,
    animate/set, HTML breakout, comments), the AILANG and Parse logos accepted, accents, links and
    fallbacks;
  - 11 widget tests;
  - `widget_check` now parses a footer link;
  - 22 new mutants (47 in all).

## 0.1.1 — 2026-10-07

**Security fix, with two breaking changes (pre-1.0).**

- **Path traversal on `POST /uploads` (security).** serve-api passes a `file: string` param a path, but a
  client could send `file` as a plain form value (`-F file=/etc/hosts`) and have that server file
  stored and resolved back. `acceptUploadFile` now accepts only serve-api's own temp file,
  `<tempDir>/ailang-upload-<x>/<name>` (new `core.isUploadTempPath`), and answers 400 otherwise,
  before reading the path or spending the token. Every adopter on 0.1.0 is exposed until it upgrades.
- **Breaking:** `acceptUploadFile(h, token, filename, path, tempDir, nowSec)` takes the temp dir; pass
  the new `flow.serveApiTempDir()` (`$TMPDIR`, else `/tmp`). `""` is a wiring error (500).
- **Breaking:** the via-host argument is `ticket`, not `token`: `receiveViaHost(h, ticket, filename,
  base64, nowSec)`, and the widget calls the widget-only tool with `{ticket, filename, base64}`, so
  rename that tool's parameter. `ailang mcp check` reads a parameter named `token` as a credential.
- **Widget:** blank until the tool result arrives; the picker shows only for an upload descriptor.
  Any other result gets one quiet line ("No upload needed.", or "Done." when the call was given a
  fileRef). After an upload: "Uploaded <name> (<size>) — <afterUpload>". `WidgetConfig` gains
  `afterUpload` (default `"processing…"`).
- Tests: 7 core tests for the path predicate, a flow case, e2e under serve-api (`/etc/hosts`,
  `../../x`, `../../ailang.toml` and a temp-dir escape refused, token unspent), 4 widget tests;
  9 new mutants (25 in all).

## 0.1.0 — 2026-10-07

**First release.** Moves a user's file to a remote AILANG MCP service with code, never through
model output. Design: ailang `design_docs/planned/v0_53_0/m-mcp-file-handoff.md` (milestone F2).

- `core` (pure; 10 contracts proved by Z3):
  - the upload admission rule `uploadVerdict`: accept exactly on first use, before expiry, with
    1..maxBytes bytes; token lifetime, expiry and the ceiling clamp;
  - account binding for stored files (`refVerdict`: another account's file looks unknown);
  - the `fileRef` codec `mcp-file://<server>/file_<32 hex>` (SEP-2631's file URI shape), strict;
  - a filename sanitiser (from docparse `mcpInputSafeName`), mime lookup and allow-list;
  - the SEP-2631-shaped upload descriptor and receipt, golden-tested field for field;
  - the OpenAI `openai/fileParams` file-object schema and parser.
- `flow`:
  - `createUpload`, `acceptUpload` / `acceptUploadFile`, `receiveViaHost`, `resolveFileRef`,
    `fetchFileParam` (`Net[scope=public] @limit=1`);
  - tokens are `string<secret>`, minted under `Rand[mode=crypto]`, stored as sha256 digests; single
    use rests on an atomic `claimMeta` hook; storage is reached only through `string{not secret}`
    wrappers, so storing or logging a token does not compile;
  - files are read once, for their owner, sha256-checked, then deleted.
- `widget`: `uploadWidgetHtml(cfg)`, a self-contained MCP Apps upload widget (the ext-apps 2.0.3
  client inlined; direct multipart POST with a via-host fallback; reports with
  `ui/update-model-context`), plus `widgetCspMeta`, `widgetMimeType`, `claudeWidgetOrigin`.
