# Changelog — sunholo/mcp_files

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
