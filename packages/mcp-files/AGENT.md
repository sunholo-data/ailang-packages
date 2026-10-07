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
- the **upload widget**: `uploadWidgetHtml(cfg)`, one self-contained HTML document that can also run
  your file tool itself once the upload lands (`cfg.onUploaded`, 0.1.3);
- **`fetchFileParam`** for ChatGPT: one GET under `Net[scope=public] @limit=1`, size-capped.

What it does **not** do: storage (you plug it in), virus scanning, parsing, resumable/chunked
uploads, serving routes (serve-api does), and the `@mcp_ui`/`@mcp_app_only` wiring (serve-api F1c).

## Quick start
```ailang
import pkg/sunholo/mcp_files/core (errorStatus, openAiFileSchema)
import pkg/sunholo/mcp_files/flow (Hooks, StoredFile, createUpload, createUploads, acceptUploadFile, serveApiTempDir, receiveViaHost, resolveFileRef, fetchFileParam)
import pkg/sunholo/mcp_files/widget (defaultWidgetConfig, uploadWidgetHtml, widgetCspMeta, widgetMimeType, claudeWidgetOrigin, callAfterUpload)
import pkg/sunholo/mcp_files/brand (Brand, FooterLink, defaultBrand, brandWith)   -- optional: your own branding
```
Copy `routes_template.ail` into your service and replace `fileHooks()` and `accountOf()`.

### API
| Function | Effects | Returns |
|---|---|---|
| `createUpload(h, account, filename, mime, maxBytes, nowSec)` | hooks + `Rand[mode=crypto]`, `Declassify` | `Ok(descriptor JSON)` / `Err(error JSON)`. `filename`/`mime` may be `""` (widget path); `maxBytes <= 0` = the ceiling |
| `createUploads(h, account, count, maxBytes, nowSec)` | same | `Ok({uploads: [descriptor…], count, note})`: `count` (1..20) descriptors, each its own single-use token and fileRef. For clients that upload several files with code; outside 1..20 = 400 |
| `acceptUpload(h, tokenRaw, filename, data: bytes, nowSec)` | hooks + `Declassify` | `Ok(receipt JSON)`: SEP-2631 `file` (uri, name, mimeType, size, sha-256 digest) + `fileRef`, `sizeBytes`, `sha256` |
| `acceptUploadFile(h, tokenRaw, filename, path, tempDir, nowSec)` | same | as above, from serve-api's multipart temp file. `path` must be `<tempDir>/ailang-upload-<x>/<name>`, else 400 before the path is read or the token spent (see "The temp-file guard"). Pass `serveApiTempDir()`; `""` = 500 |
| `serveApiTempDir()` | `Env` | the dir serve-api writes multipart parts under: `$TMPDIR`, else `/tmp` (Go's `os.TempDir()`) |
| `receiveViaHost(h, ticket, filename, base64, nowSec)` | same | as above; `ticket` is the descriptor's upload token. Bad base64 is refused **before** the token is spent |
| `resolveFileRef(h, account, fileRef, nowSec)` | hooks | `Ok(StoredFile)` once, for the owner; then bytes and record are deleted |
| `fetchFileParam(fileObj: Json, maxBytes)` | `Net[scope=public] @limit=1` | `Ok(StoredFile)` (`fileRef` = the OpenAI `file_id`); nothing stored |
| `uploadWidgetHtml(cfg)` | pure | the widget document |
| `callAfterUpload(tool, argsJson)` / `noAutoCall()` | pure | `cfg.onUploaded`: the tool the widget calls after the upload (see "After the upload") |
| `onUploadedProblem(o)` | pure | `""` when `cfg.onUploaded` is usable, else what is wrong (assert it in your tests) |
| `brandWith(name, logoSvg, accent, footerLinks)` / `defaultBrand()` | pure | a `Brand` for `cfg.brand` (see "Branding") |

**One upload token per file.** A token uploads exactly one file; a second upload with it answers
409 "this upload token was already used — call createUpload again for each file". Every descriptor
says so in `note` (`core.singleUseNote()`), because in a 14-file batch in claude.ai (2026-10-07) the
model tried to upload the other 13 with the first token. For N files: N `createUpload` calls (one
widget card each), or one `createUploads(…, N, …)` for a client that runs code.

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
     streams it to a temp file, then call `acceptUploadFile(h, token, file, file, serveApiTempDir(), now)`
     and answer `{_body: receipt-or-error, _status: errorStatus(err)}`. Never read `file` yourself;
   - the **widget-only tool** (`uploadViaHost(ticket, filename, base64)` → `receiveViaHost`). The
     parameter must be named `ticket`: that is what the widget sends;
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
5. **Never log** the `token` / `ticket` arguments, request bodies, or `createUpload`'s result (they
   carry the token). Run serve-api with `AILANG_TRACE_VALUES=off`; traces render arguments verbatim.
6. **No silent fallbacks.** If an upload fails, tell the user what to do (allow network access to your
   domain, use the widget, or send a link). Never let the model parse the file itself.
7. Use seconds for `nowSec` (`std/clock.now()` is milliseconds; so are `std/datetime` timestamps).

## The temp-file guard
serve-api hands a `file: string` param the path of the temp file it streamed the multipart part to,
`os.MkdirTemp("", "ailang-upload-*")` + the part's base name. But a client can also send `file` as a
plain form value (`curl -F file=/etc/hosts`, no `@`), and serve-api passes that string through
unchanged. Before 0.1.1 the package read whatever path it named, stored it, and handed it back on
resolve. Now `acceptUploadFile` requires `core.isUploadTempPath(path, tempDir)`: exactly
`<tempDir>/ailang-upload-<suffix>/<name>`, an absolute `tempDir`, a non-empty suffix and a name that
is not `.` or `..`. Anything else gets 400 `invalid_request` with the same answer whether or not the
path exists. The path is not read and the token is not spent.

`tempDir` must be the `TMPDIR` serve-api runs with. Call `serveApiTempDir()` inside the route (same
process). Paths are compared as given: no symlink resolution. What remains: a client holding a valid
token could name *another* in-flight upload's temp file if it guessed the 32-bit random directory
suffix and the filename during that request. serve-api deletes the directory when the request ends.

## Renamed in 0.1.1: `token` to `ticket` on the via-host tool
The widget calls the widget-only tool with `{ticket, filename, base64}`. A tool parameter named
`token` reads as a credential to `ailang mcp check`, and possibly to directory scanners, even on an
app-only tool. The multipart field on `POST /uploads` and the descriptor's
`upload.multipart.fields.token` keep their SEP-2631 names. An adopter on 0.1.0 must rename the tool's
parameter when it upgrades. The 0.1.1 widget sends `ticket`, so a tool that still declares `token`
never receives the token and the via-host upload fails.

## The widget
`uploadWidgetHtml(cfg)` inlines the official `@modelcontextprotocol/ext-apps` 2.0.3 client
(`app-with-deps.js`, the build the F1 spike ran in claude.ai; sha256-pinned in
`tools/gen_bundle.sh`) as a module script, then the widget logic from `assets/widget.js`:
1. renders nothing until the tool result arrives (`ui/notifications/tool-result`; also reads
   `window.openai.toolOutput`), then takes the descriptor from `structuredContent` (or from text
   content holding the JSON). Only a descriptor shows the picker. Any other result (an error, a
   parse result) gets one compact line read from that result (`cfg.resultSummary`, see "Result
   cards"). ext-apps 2.0.3 sends a widget only its own call's result, so the instance that took the
   upload cannot see the later call that uses the file;
2. on pick, refuses an empty or oversize file **before** spending the token, then POSTs multipart
   `{token, file}` to `upload.url`;
3. if the fetch cannot leave the iframe, calls `cfg.hostToolName` with `{ticket, filename, base64}`;
4. hides the picker and shows "Uploaded <name> (<size>) — `cfg.afterUpload`" (default
   `processing…`; Parse: `parsing…`);
5. with `cfg.onUploaded` set, calls that server tool itself and reports its result (see "After the
   upload"); otherwise reports the receipt with `ui/update-model-context` (text + the receipt as
   structured content). It never uses `ui/message`, which drafts a user message under a "Use
   caution" banner.

**Why an inlined bundle.** AILANG string literals carry the 400 KB bundle without trouble (check,
test and serve are unaffected). `ailang fmt` rewrites multi-line literals onto one line, so the
readable sources live in `assets/` and are generated into `widget_assets.ail` and
`extapps_bundle.ail` (`tools/gen_bundle.sh`, `--bundle` to refetch ext-apps). Edit the assets, never
the generated modules; `tests/assets_check.sh` fails when they drift.

## After the upload
**`ui/update-model-context` starts no model turn.** Measured in claude.ai (prod, 2026-10-07): the
upload landed and the widget reported the fileRef, then sat on "parsing…" until the user typed;
Claude said it "never got confirmation that the upload finished". So the widget does the next step
itself. Set `cfg.onUploaded` to the tool that consumes the file:
```ailang
import pkg/sunholo/mcp_files/widget (WidgetConfig, defaultWidgetConfig, callAfterUpload)

-- docparse: parse the uploaded file into blocks as soon as it lands.
pure func widgetCfg() -> WidgetConfig =
  { defaultWidgetConfig("https://docparse.ailang.sunholo.com/uploads", "uploadViaHost") |
    afterUpload: "parsing…",
    onUploaded: callAfterUpload("mcpParse", "{\"fileRef\":\"{{fileRef}}\",\"outputFormat\":\"blocks\"}") }
```
What the widget then does, after a successful upload (direct POST or the via-host fallback):
1. shows "Uploaded <name> (<size>) — parsing…";
2. parses `argsJson` as JSON, replaces the one string value that is exactly `"{{fileRef}}"` with the
   fileRef, and calls the tool through the host: an app-initiated `tools/call`, ext-apps 2.0.3
   `App.callServerTool(params, options)` (`this.request({method:"tools/call",params:$},…)` in the
   bundle), with a 5-minute timeout (the SDK default is 60 s). The host proxies it to your server
   with the user's session, so the tool runs signed in, as if the model had called it;
3. shows "✓ Parsed AGM.docx · 68 blocks · 13 headings · 4 tracked changes" when the result holds a
   `summary` object (top level, or up to two objects down, as in docparse's `document.summary`; the
   counts as in "Result cards"), else "✓ Done";
4. sends one `ui/update-model-context`: the receipt and fileRef, the summary, and the tool result
   (`structuredContent` as JSON, else the text content). When that text would pass 100 000
   characters, the result is left out and the model is told to call the tool itself;
5. on an error (the tool's `isError`, a rejected or timed-out call, a bad template) it shows
   "Uploaded <name>, but <tool> failed: …" and tells the model, with the fileRef, so it can retry.

**The host must allow it.** The widget calls only when the host's `serverTools` capability is set
(claude.ai advertised it in the F1 spike handshake). Without it, the widget falls back to the 0.1.2
behaviour (the fileRef and `cfg.nextStep` into the model's context) and asks the user: "Uploaded
<name> (<size>) — tell the assistant to continue." `noAutoCall()` (the default, `tool: ""`) is the
0.1.2 behaviour too, with `cfg.afterUpload` as the last line.

**The template, checked.** `onUploadedProblem(cfg.onUploaded)` is `""` or the reason:
- `tool` must match `[A-Za-z0-9_-]{1,64}` (`toolNameOk`);
- `argsJson` must parse as a JSON **object** whose raw text holds `{{fileRef}}` exactly once, as a
  **whole string value**: not in a key, not inside a longer string (`"/files/{{fileRef}}"`), not
  twice, not spelled with JSON escapes (`argsTemplateProblem`).
A config that fails is not rendered: the widget gets `tool: ""` (fileRef only) and logs the
problem to the browser console. Assert `onUploadedProblem(...) == ""` in your own tests so a typo
fails CI instead. The widget re-checks the template before every call.

**Things to know.**
- **A fileRef is single use.** The widget's call resolves it. If the model calls the tool again
  with the same fileRef (a retry, or a result too large for the context), your tool answers 404
  unless it keeps the parsed result; the model is told to ask the user for a new upload then.
- **Neither call starts a model turn either.** The tool call runs without the model, and the result
  sits in the model's context; the user's next message picks it up. The widget's "✓" line is what
  tells the user the file was taken.
- **Billing and limits apply as usual**: the call is a normal signed-in `tools/call` to your server.

## Result cards
Each tool call renders its own widget card. A card with no upload descriptor (a call given a fileRef
or a document) used to say "Done.", which in a 14-file batch said nothing. With `cfg.resultSummary`
(default `true`) it shows **one line, at most 120 characters**, from the call's own result
(`structuredContent`, else text content holding JSON):

| Result | Line |
|---|---|
| a `summary` object (docparse: `document.summary`) | `✓ Parsed <file> · 68 blocks · 13 headings · 2 tables · 4 tracked changes · 2 comments` |
| `error: {code, message}` | `✗ INVALID_FORMAT: not a docx` |
| `error: "<code>"` + `error_description` (this package's errors), or `isError` text | `✗ token_used: this upload token was already used …` |
| anything else | `✓ <tool title> done · <file or target>`, plus a **Download** button for an https `download_url` |

- `<file>` is the result's `filename`, last path segment only (`/` or `\`), control characters
  dropped. Counts come from `summary` (`totalBlocks`, `headings`, `tables`, `images`, `changes` =
  tracked changes, then any other numeric field); zeros are omitted; comments are counted from the
  block tree (`type: "comment"`, a bounded walk of `blocks`/`children`/`items`).
- The tool title is the host context's `toolInfo.tool` (`title`, `annotations.title`, else `name`).
  Without a title and with nothing to read, the card keeps "Done." / "No upload needed.".
- The Download button opens through the host (`app.openLink`; ChatGPT `openExternal`). Only `https://`
  URLs without quotes, spaces or angle brackets are offered.
- Everything is written with `textContent`; a long line is cut with "…" and never wraps.
- `{ cfg | resultSummary: false }` restores the bare "Done.".

## Branding
The widget carries a small brand: a header (an 18px logo and a name), an accent colour, and a footer
(up to 4 links and "Powered by AILANG"). `defaultWidgetConfig` uses `defaultBrand()`, AILANG's:

| Field | Default | Rule (checked in `brand.ail`; a failing value is replaced, never rendered) |
|---|---|---|
| `name` | `"AILANG"` | trimmed, at most 40 characters, html-escaped. `""` = no name |
| `logoSvg` | `ailangLogoSvg()`: the AILANG hexagon + lambda, inline, ~0.6 KB | `svgLogoOk`, else the AILANG logo. `""` = no logo |
| `accent` | `#d03614` (AILANG docs `--ifm-color-primary-dark`) | `accentOk`: exactly `#rgb` or `#rrggbb`, else `#d03614` |
| `footerLinks` | `[]` | `linkUrlOk`: https, no userinfo, quotes, spaces or angle brackets, else dropped. Labels html-escaped |
| `poweredBy` | `true` | plain text "Powered by AILANG" in the footer, no link |

**Where the brand shows.** The header and footer appear with the picker and stay after the upload.
An idle instance (a tool result that holds no descriptor) shows only its quiet line. The accent colours
**only** the primary button (the picker's `::file-selector-button`) and the focus ring. Its text colour
is white or near-black, whichever contrasts more (`onAccent`). AILANG's primary `#e73c17` would give
white text 4.15:1, below WCAG AA; `#d03614` gives 4.98:1. Text, borders, fonts and radii use the
host's MCP Apps style variables. The background stays transparent. In ChatGPT (`window.openai`) the
header is hidden, because ChatGPT draws the app's logo and name itself.

**Host theming.** After `connect`, the widget applies the host context with the ext-apps 2.0.3
helpers already in the bundle: `applyDocumentTheme(theme)` (`data-theme` + `color-scheme`),
`applyHostStyleVariables(styles.variables)` and `applyHostFonts(styles.css.fonts)`. It re-applies them
on `hostcontextchanged` (`app.addEventListener`; `getHostContext()` holds the merged context). In
ChatGPT it follows `window.openai.theme` and `openai:set_globals`. Without a host theme, the CSS
falls back to `prefers-color-scheme`. Every variable has a light/dark fallback, because a host may
send any subset of the variables, or none. Footer links open through the host (`app.openLink`, which
is `ui/open-link`; ChatGPT `openExternal`): a sandboxed iframe cannot navigate on its own.

**The logo sanitiser (`svgLogoOk`).** It runs on the lowercased, trimmed logo, so `<SCRIPT` and
`OnLoad` are caught too.
- **Frame** (`svgFrameOk`, Z3-proved): one `<svg …>` element that closes exactly at the end. No
  `script` anywhere, which covers script elements and javascript:/vbscript: URLs. No `&#` (an encoded
  `javascript:`), no `<!` (comments, CDATA), no `<?`, no `xml:base`, at most 16 KB.
- **Elements** (`svgTagsOk`): every `<` opens or closes an allowed element: svg, g, path, rect,
  circle, ellipse, line, polyline, polygon, text, tspan, defs, linearGradient, radialGradient, stop,
  title, desc, clipPath, mask, use, symbol, image. So no `<script>`, `<style>` (it would restyle the
  whole widget), `<foreignObject>`, `<a>`, `<animate>`/`<set>` (the animate-href trick), `<iframe>`,
  or HTML breakout elements.
- **Handlers** (`svgNoHandlers`): every `on` must follow a name character, as in `polygon` or
  `none`. After whitespace, `/`, a quote or `=` (anywhere an attribute name can start) it is refused.
- **References** (`svgHrefsOk`, `svgUrlsOk`): every `href`/`xlink:href` is `="#…"` or a raster
  `data:image/png|jpeg|gif|webp`. `data:image/svg+xml` (a `<use>` XSS vector), any scheme and a spaced
  `href =` are refused. Every CSS `url(` is a fragment, `url(#id)`.

It errs toward refusing: a logo whose text starts with "on", or that contains the word "script",
is refused. Export your logo as plain paths, drop animations, and give gradient ids a unique prefix
(the widget page holds one document). The logo is inserted as markup, server-side, after this check.
The widget script never writes config values with `innerHTML` (`tests/lint.sh`).

**Customising.** A downstream service passes its own brand:
```ailang
import pkg/sunholo/mcp_files/widget (WidgetConfig, defaultWidgetConfig)
import pkg/sunholo/mcp_files/brand (brandWith)

pure func widgetCfg() -> WidgetConfig =
  { defaultWidgetConfig("https://svc.example.com/uploads", "uploadViaHost") |
    brand: brandWith("Acme Files", "<svg viewBox='0 0 16 16'><rect width='16' height='16' rx='3' fill='#0b6e4f'/></svg>",
                     "#0b6e4f", [{label: "Help", url: "https://svc.example.com/help"}]) }
```
`brandWith` keeps `poweredBy: true`; `{ brandWith(…) | poweredBy: false }` drops the line. Pick an
accent with at least 3:1 against both a white and a dark (`#262624`) background, so the focus ring
stays visible in both themes.

**Vendor rules this default follows** (fetched 2026-10-07):
- **OpenAI**, ChatGPT apps UI guidelines (https://developers.openai.com/plugins/concepts/ui-guidelines,
  formerly `/apps-sdk/concepts/ui-guidelines`):
  - "Partners can add branding through accents, icons, or inline imagery, but should not redefine
    system colors."
  - "Use brand accent colors on primary buttons inside app display modes."
  - "Partner brand accents such as logos or icons should not override backgrounds or text colors."
  - "Avoid custom gradients or patterns that break ChatGPT's minimal look."
  - "Don't use custom fonts, even in full screen modes. Use system font variables wherever possible."
  - "Do not include your logo as part of the response. ChatGPT will always append your logo and app
    name before the widget is rendered." This is why the header hides under `window.openai`.
  - "Text and background must maintain a minimum contrast ratio (WCAG AA)."
  - Plugin guidelines (https://developers.openai.com/plugins/plugin-guidelines): "Plugins must not
    serve advertisements". So footer links are informational, never checkout or upgrade pages. Neither
    vendor mentions a "powered by" line; ours is plain secondary text with no call to action.
- **Anthropic**, MCP Apps design guidelines
  (https://claude.com/docs/connectors/building/mcp-apps/design-guidelines):
  - "Use host tokens for all structural elements: backgrounds, text, borders, and icons. You can use
    your own brand colors for accents and identity, but the core UI should use the provided palette."
  - "All views must support both light and dark themes. Use the host's style tokens, which adapt
    automatically, and never hardcode colors."
  - Transparent theming (https://claude.com/docs/connectors/building/mcp-apps/transparent-theming):
    "Any opaque background on `<html>` or `<body>` hides the chat surface behind it. Explicitly set
    both to `transparent`". The `styles.css.fonts` it describes (Anthropic Sans) is served from
    `https://assets.claude.ai`. To load that font rather than fall back to the system stack, add that
    origin to `resourceDomains` in your own `_meta` (`widgetCspMeta` leaves it empty).
  - External links (https://claude.com/docs/connectors/building/mcp-apps/external-links): `ui/open-link`
    shows an "Open external link" confirmation for custom connectors.
- **MCP Apps 2026-01-26**
  (https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx):
  - `HostContext.theme` is `"light" | "dark"`.
  - `styles.variables` holds the standard keys: `--color-{background,text,border,ring}-*`,
    `--font-sans`, `--font-mono`, `--font-weight-*`, `--font-text-*-size`, `--font-heading-*-size`,
    `--border-radius-*`, `--border-width-regular`, `--shadow-*`. There is no brand or accent key.
  - `styles.css.fonts` is font CSS.
  - `ui/notifications/host-context-changed` carries a partial update: "the View SHOULD merge received
    fields with its current context state".
  - "Hosts can provide any subset of standardized variables, or not pass `styles` at all", and
    "Views should set default fallback values".

## How the guarantees are checked
| Check | What it shows |
|---|---|
| `ailang verify core.ail` (`tests/verify_check.sh`) | Z3: `uploadVerdict` (single use + expiry + size), `isExpired`, `tokenExpiresAt`, `sizeOk`, `effectiveMaxBytes`, `ownerMatches`, `refVerdict`, `mimeAllowed`, `refFrameOk`, `downloadUrlOk` |
| `ailang verify brand.ail` (same script) | Z3: `svgFrameOk` (one svg element, no `script`/`&#`/`<!`/`xml:base`, size), `accentOk` (`#` + length 4 or 7), `isHexDigit`, `linkUrlOk` (https, no userinfo or quotes). Proving "no `;` in an accepted accent" as a contract times the solver out, so tests pin it |
| `tests/broken_single_use.ail`, `tests/broken_expiry.ail` | must be **refuted** (a forgotten claim; an off-by-one expiry; an empty-owner match) |
| `ailang test --package .` | core (SEP-2631 descriptor golden, OpenAI schema golden, codec, sanitiser, properties), brand (48: hostile logos refused, the AILANG and Parse logos accepted, accents, links, fallbacks) and widget tests (default and custom brand rendered, hostile brand escaped or replaced, accent only on the button and ring, host theming, the after-upload template and tool-name checks) |
| `tests/flow_check.sh` | flow over SharedMem hooks: single use (and its "one createUpload per file" message), expiry, size cap, cross-account, sha256 round trip, delete after use, tamper, mime, via host, paths outside the temp dir refused, `createUploads` (distinct tokens, 1..20) |
| `tests/e2e_uploads.sh` | real serve-api: curl multipart of a 1.5 MB binary, sha256 round trip, replay 409, cross-account 404, CORS for the widget origin, 413 above `--max-upload-size`, `-F file=/etc/hosts` / `../../x` / a temp-dir escape refused with the token unspent |
| `tests/fetch_check.sh` | `fetchFileParam`: http/userinfo refused; metadata IP and a name resolving to loopback refused with permissive Net flags on; a pinned public file fetched byte-exact; size cap (network) |
| `tests/ifc_leaks.sh` | logging or storing a token in the real `flow.ail` fails to compile |
| `tests/widget_check.sh` | widget HTML (default brand + a footer link) parses, one picker, two inline module scripts, nothing external (the only href is an https footer link with `rel=noopener`); `node --check` on both scripts |
| `tests/widget_sim.sh` | 33 scenarios of `assets/widget.js` under node with a mocked ext-apps App: upload → `tools/call` with the substituted args → one context update with the summary; no summary; a large result; tool error and rejected call; no `serverTools` (fallback); no tool (0.1.2); via-host then the tool; 9 bad templates refused in the widget; a hostile fileRef stays one value; 11 result cards (parse line, path, errors, convert + download, the cap, off). Never `ui/message` |
| `tests/lint.sh`, `tests/assets_check.sh` | source rules the types cannot express (no `innerHTML`/`eval`/`ui/message` in the widget); generated modules in sync |
| `tests/mutation.sh` | 75 mutants of the key checks (the temp-file guard, the widget states, 22 for branding: the logo sanitiser, the accent check, link filtering, escaping, host theming, 17 for the after-upload call: skipped, string concatenation, the capability fallback, template and tool-name checks, the context cap, error reporting, and 11 for result cards and batches), each killed (one fetch mutant needs the network) |

## Design
`sunholo-data/ailang` `design_docs/planned/v0_53_0/m-mcp-file-handoff.md` (F2). SEP-2631:
https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2631
