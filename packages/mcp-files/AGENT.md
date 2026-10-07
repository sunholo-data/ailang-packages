# sunholo/mcp_files

## When to use this package
Use it when an `ailang serve-api` MCP service needs a **user's file**. MCP tool arguments are
model output, so a file passed as base64 `content` hits the model's output limit, and the model
may quietly parse the file itself instead (the AGM.docx incident). This package moves the bytes
**with code, not with the model**. It pairs with `sunholo/mcp_oauth`: the tools that create an
upload are signed in.

Three ways in, one stored file:

| Client | Path | What moves the bytes |
|---|---|---|
| claude.ai web / Desktop | the upload widget (MCP Apps) | the user's picker; a `fetch` to your `/uploads`, or the host via a widget-only tool |
| Claude Code, Codex, a sandbox with network access | the descriptor's `curl` line | the client's shell |
| ChatGPT | `openai/fileParams` | ChatGPT hands you a `download_url`; `fetchFileParam` fetches it once |

What it does:
- **single-use, account-bound, size-capped upload tokens.** Minted under `Rand[mode=crypto]` and
  stored only as a sha256 digest. The admission rule is proved by Z3: accept exactly when this is
  the first use, the token hasn't expired, and the size is 1..maxBytes;
- a **SEP-2631-shaped descriptor** (`{file, upload:{transport,method,url,headers,multipart,expiresAt}}`
  plus `fileRef`, `maxBytes`, `curl`), so adopting `files/authorizeUpload` later is a rename;
- **fileRefs** `mcp-file://<server>/file_<32 hex>`, parsed strictly, resolved **once** and **only
  for their owner**, then deleted. Another account's ref answers exactly like an unknown one;
- the **upload widget**: `uploadWidgetHtml(cfg)`, one self-contained HTML document;
- **`fetchFileParam`** for ChatGPT: one GET under `Net[scope=public] @limit=1`, size-capped.

What it does **not** do: storage (you plug it in), virus scanning, parsing, resumable/chunked
uploads, serving routes (serve-api does), and the `@mcp_ui`/`@mcp_app_only` wiring (serve-api F1c).

## Quick start
```ailang
import pkg/sunholo/mcp_files/core (errorStatus, openAiFileSchema)
import pkg/sunholo/mcp_files/flow (Hooks, StoredFile, createUpload, acceptUploadFile, receiveViaHost, resolveFileRef, fetchFileParam)
import pkg/sunholo/mcp_files/widget (defaultWidgetConfig, uploadWidgetHtml, widgetCspMeta, widgetMimeType, claudeWidgetOrigin)
```
Copy `routes_template.ail` into your service and replace `fileHooks()` and `accountOf()`.

### API
| Function | Effects | Returns |
|---|---|---|
| `createUpload(h, account, filename, mime, maxBytes, nowSec)` | hooks + `Rand[mode=crypto]`, `Declassify` | `Ok(descriptor JSON)` / `Err(error JSON)`. `filename`/`mime` may be `""` (widget path); `maxBytes <= 0` = the ceiling |
| `acceptUpload(h, tokenRaw, filename, data: bytes, nowSec)` | hooks + `Declassify` | `Ok(receipt JSON)`: SEP-2631 `file` (uri, name, mimeType, size, sha-256 digest) + `fileRef`, `sizeBytes`, `sha256` |
| `acceptUploadFile(h, tokenRaw, filename, path, nowSec)` | same | as above, from serve-api's multipart temp file |
| `receiveViaHost(h, tokenRaw, filename, base64, nowSec)` | same | as above; bad base64 is refused **before** the token is spent |
| `resolveFileRef(h, account, fileRef, nowSec)` | hooks | `Ok(StoredFile)` once, for the owner; then bytes and record are deleted |
| `fetchFileParam(fileObj: Json, maxBytes)` | `Net[scope=public] @limit=1` | `Ok(StoredFile)` (`fileRef` = the OpenAI `file_id`); nothing stored |
| `uploadWidgetHtml(cfg)` | pure | the widget document |

Every `Err` is `{"error", "error_description", "status"}`; `core.errorStatus(err)` gives the HTTP
status: 400 bad input, 401 unknown/expired token or no account, 404 unknown or another account's
fileRef, 409 token already used, 410 the owner's file expired, 413 too large, 415 mime refused,
500 storage, 502 fetch failed.

## Hooks
One effect row for every hook: `! {IO, FS, Env, Net, Clock, SharedMem}`.

| Hook | Contract | Parse |
|---|---|---|
| `putBytes(objectKey, data, expiresAtSec)` | store the bytes | temp GCS bucket (1-day lifecycle) |
| `getBytes(objectKey)` / `delBytes(objectKey)` | read / delete (absent counts as deleted) | same |
| `putMeta(key, json, expiresAtSec)` | create or replace | Firestore doc |
| `claimMeta(key, json, expiresAtSec)` | **create only if absent**; `true` only for the call that created it. **Must be atomic** (Firestore `create()`, SharedMem `put_if_absent`): single use rests on it | Firestore `create()` |
| `getMeta(key)` / `delMeta(key)` | read / delete | Firestore |
| `server` | authority in `mcp-file://<server>/file_<id>` (`[a-z0-9.-]`) | `docparse` |
| `uploadUrl` | the URL the descriptor names (https) | `https://docparse.ailang.sunholo.com/uploads` |
| `tokenTtlSec` | token lifetime | `600` (`core.defaultTokenTtlSec()`) |
| `objectTtlSec` | how long an unread upload is kept | `86400` |
| `maxBytesCeiling` | the cap every token is bound under | plan's `maxFileSizeMb` |
| `allowedMimes` | allow-list, `[]` = any | your parser's formats |

Expiry is checked by the flow from each record, so a lazy store TTL (Firestore TTL, GCS lifecycle)
is only cleanup. Keys are `tok:<digest>`, `used:<digest>`, `ref:<id>`, object `obj:<id>`; values
never hold a token. The flow reaches the hooks only through wrappers whose key/value parameters are
`string{not secret}`, so the type checker refuses any path that would store a token.

## Adopter checklist
1. **Routes** (see `routes_template.ail`):
   - the tool that starts an upload (signed in, `@mcp_auth("oauth2")`), returning `createUpload`'s
     descriptor as structured content. Parse: `mcpParse`/`mcpConvert`/`editDocument` called without
     a document, or a `createUpload` tool;
   - `POST /uploads` (`@nomcp`), multipart `token` + `file`. Declare `file: string` so serve-api
     streams it to a temp file, then call `acceptUploadFile(h, token, file, file, now)` and answer
     `{_body: receipt-or-error, _status: errorStatus(err)}`;
   - the **widget-only tool** (`uploadViaHost(token, filename, base64)` → `receiveViaHost`);
   - the widget resource `ui://<svc>/upload`: body `uploadWidgetHtml(cfg)`, mime `widgetMimeType()`,
     `_meta` `widgetCspMeta([<your origin>])`;
   - `fileRef` parameters on your file tools, resolved with `resolveFileRef(h, account, ref, now)`;
   - for ChatGPT: an optional `file` parameter with `core.openAiFileSchema()`, listed in
     `_meta["openai/fileParams"]`, fetched with `fetchFileParam`.
2. **serve-api F1c wiring, once it ships:** `@mcp_ui_resource("ui://<svc>/upload", connect…)` on the
   widget function, `@mcp_ui("ui://<svc>/upload")` on the tool that starts an upload, and
   `@mcp_app_only` on the widget-only tool. Until then the widget-only tool is visible to the model
   (harmless: it needs a live token).
3. **CORS for the widget origin.** The widget's multipart POST is a CORS "simple" request: it reaches
   your handler without a preflight, but can only read the receipt if the response echoes its
   origin. serve-api's allowlist is exact: `--cors-origin $(claudeWidgetOrigin(<connector URL>))`.
   Unlisted origins get 403 before the handler runs. If the widget cannot reach you, it falls back
   to the host tool (files up to `maxViaHostBytes`, default 1 MB).
4. **`--max-upload-size` above `maxBytesCeiling`.** A body over serve-api's limit is refused with 413
   before your handler runs (measured: `tests/e2e_uploads.sh`), so keep the ceiling below it.
5. **Never log** the `token` argument, request bodies, or `createUpload`'s result (they carry the
   token). Run serve-api with `AILANG_TRACE_VALUES=off`; traces render arguments verbatim.
6. **No silent fallbacks.** If an upload fails, tell the user what to do (allow network access to your
   domain, use the widget, or send a link). Never let the model parse the file itself.
7. Use seconds for `nowSec` (`std/clock.now()` is milliseconds; so are `std/datetime` timestamps).

## The widget
`uploadWidgetHtml(cfg)` inlines the official `@modelcontextprotocol/ext-apps` 2.0.3 client
(`app-with-deps.js`, the build the F1 spike ran in claude.ai; sha256-pinned in
`tools/gen_bundle.sh`) as a module script, then the widget logic from `assets/widget.js`:
1. waits for the tool result (`ui/notifications/tool-result`; also reads `window.openai.toolOutput`)
   and takes the descriptor from `structuredContent` (or from text content holding the JSON);
2. on pick, refuses an empty or oversize file **before** spending the token, then POSTs multipart
   `{token, file}` to `upload.url`;
3. if the fetch cannot leave the iframe, calls `cfg.hostToolName` with `{token, filename, base64}`;
4. reports with `ui/update-model-context` (text + the receipt as structured content). It never uses
   `ui/message`, which drafts a user message under a "Use caution" banner.

**Why an inlined bundle.** AILANG string literals carry the 400 KB bundle without trouble (check,
test and serve are unaffected). `ailang fmt` rewrites multi-line literals onto one line, so the
readable sources live in `assets/` and are generated into `widget_assets.ail` and
`extapps_bundle.ail` (`tools/gen_bundle.sh`, `--bundle` to refetch ext-apps). Edit the assets, never
the generated modules; `tests/assets_check.sh` fails when they drift.

## How the guarantees are checked
| Check | What it shows |
|---|---|
| `ailang verify core.ail` (`tests/verify_check.sh`) | Z3: `uploadVerdict` (single use + expiry + size), `isExpired`, `tokenExpiresAt`, `sizeOk`, `effectiveMaxBytes`, `ownerMatches`, `refVerdict`, `mimeAllowed`, `refFrameOk`, `downloadUrlOk` |
| `tests/broken_single_use.ail`, `tests/broken_expiry.ail` | must be **refuted** (a forgotten claim; an off-by-one expiry; an empty-owner match) |
| `ailang test --package .` | core (SEP-2631 descriptor golden, OpenAI schema golden, codec, sanitiser, properties) and widget tests |
| `tests/flow_check.sh` | flow over SharedMem hooks: single use, expiry, size cap, cross-account, sha256 round trip, delete after use, tamper, mime, via host |
| `tests/e2e_uploads.sh` | real serve-api: curl multipart of a 1.5 MB binary, sha256 round trip, replay 409, cross-account 404, CORS for the widget origin, 413 above `--max-upload-size` |
| `tests/fetch_check.sh` | `fetchFileParam`: http/userinfo refused; metadata IP and a name resolving to loopback refused with permissive Net flags on; a pinned public file fetched byte-exact; size cap (network) |
| `tests/ifc_leaks.sh` | logging or storing a token in the real `flow.ail` fails to compile |
| `tests/widget_check.sh` | widget HTML parses, one picker, two inline module scripts, nothing external; `node --check` on both scripts |
| `tests/lint.sh`, `tests/assets_check.sh` | source rules the types cannot express; generated modules in sync |
| `tests/mutation.sh` | 16 mutants of the key checks, each killed |

## Design
`sunholo-data/ailang` `design_docs/planned/v0_53_0/m-mcp-file-handoff.md` (F2). SEP-2631:
https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2631
