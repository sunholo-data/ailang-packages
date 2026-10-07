# Changelog — sunholo/mcp_files

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
