# Changelog — sunholo/mcp_files

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
