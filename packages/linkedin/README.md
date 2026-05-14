# sunholo/linkedin

LinkedIn API client for AILANG: OAuth2 authentication, publish posts on a
company page, read comments, derive GDPR-safe pseudonymous personas for
public display.

## Modules

| Module | What it provides |
|--------|------------------|
| `sunholo/linkedin/auth` | `LinkedInCreds` record + `linkedinReadCreds`, `linkedinGetToken`, `linkedinGetOrgUrn`. Reads `~/.ailang/linkedin/credentials.json` and refreshes expired access tokens via the LinkedIn OAuth2 endpoint. |
| `sunholo/linkedin/posts` | `PostResult` record + `linkedinCreatePost`, `linkedinCreateImagePost`, `linkedinEscapeLittleText`, `linkedinHeaders`, `linkedinFindHeader`. Publishes to `POST /rest/posts` with a `Net @limit=1` budget. Body is auto-escaped for LinkedIn's Little Text Format. |
| `sunholo/linkedin/images` | `ImageUpload` record + `linkedinInitializeImageUpload`, `linkedinUploadImageBytes`, `linkedinUploadImage`. Three-step register / PUT / finalise flow for attaching images to posts. |
| `sunholo/linkedin/comments` | `LinkedInComment` + `PublicComment` records + `linkedinGetComments`, `linkedinGetCommentReplies`, `linkedinGetAllComments`, `linkedinSanitiseComment`, `linkedinCommentsToJson`, `linkedinDerivePersona`. Reads `GET /rest/socialActions/{urn}/comments` and serialises a GDPR-stripped, pseudonymous JSON for public publication. Uses IFC `Declassify` effect to enforce that PII can't leak without passing through the sanitiser. |

## Capability budgets

- `linkedinCreatePost`: `Net @limit=1` — exactly one outbound call per publish.
- `linkedinGetComments`: `Net @limit=1` per post.
- `linkedinGetAllComments`: `Net @limit=50` total — sweep up to 50 posts.
- `linkedinGetToken`: `Net @limit=1`, `FS @limit=5`, `Env` — read creds, maybe refresh.
- `linkedinUploadImage`: `Net @limit=2` total — initialise + upload.

## Contracts

Every contract here is `requires`/`ensures`-bounded; AILANG rejects code that violates them at the type-check stage.

| Function | Contract | Why |
|---|---|---|
| `linkedinCreatePost` / `linkedinCreateImagePost` | `requires { length(text) > 0 && length(text) <= 3000 }` | LinkedIn's documented hard limit. Caught at compile time, not in production. |
| `linkedinDerivePersona` | `ensures { length(result.initials) == 2, length(result.avatarSeed) == 6 }` | Renderers can rely on a 2-char monogram + 6-char hex CSS seed without runtime checks. |
| `linkedinHeaders` | `ensures { listLength(result) == 4 }` | Auth + Content-Type + protocol version + LinkedIn-Version, always. |
| `linkedinApiVersion` | `ensures { length(result) > 0 }` | Header value never blank. |
| `linkedinCredsPath` | `ensures { length(result) > 0 }` | Falls back to `/tmp` if HOME is unset; still always non-empty. |
| `linkedinHexVal` | `ensures { result >= 0, result < 16 }` | Hex-digit value usable as an array index without bounds-checking. |

## Credentials

The package looks for credentials in (in order):

1. `$LINKEDIN_ACCESS_TOKEN` — env override; useful in CI when you've baked a token in.
2. `$HOME/.ailang/linkedin/credentials.json` — the file `ailang-linkedin auth` writes.

The credentials file shape:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "client_id": "...",
  "client_secret": "...",
  "org_urn": "urn:li:organization:..."
}
```

Required OAuth2 scopes for the full publish + listen loop:

- `w_organization_social` — post on the company page
- `r_organization_social` — read posts
- `w_organization_social_feed` — write comments / reactions (forward-compat)
- `r_organization_social_feed` — read comments on company posts

The first two are covered by the standard "Share on LinkedIn" product; the
`_feed` scopes need the Community Management API approval.

## GDPR-safe personas

`linkedinDerivePersona(actor: string)` returns `{initials, avatarSeed}` where:

- `initials` — two letters `A`-`Z`, derived from `sha256(actor)` bytes 0 and 1
- `avatarSeed` — six hex chars from `sha256(actor)` bytes 2 through 4

Both are stable per-actor and one-way: the commenter sees the same monogram
on every visit, but the underlying URN can't be recovered from the output.

`linkedinCommentsToJson` uses this to produce a JSON suitable for serving
publicly — actor URN and commentUrn are stripped, only `{text, createdAt,
parentPostUrn, initials, avatarSeed}` ship.

## What's not in scope

- **State tracking**: which slugs have been published to which URNs. That's
  a consumer concern — keep your own `state.json` or DB. The `PostState`
  record shape is exported as a convention for those who want one.
- **Content loading**: parsing markdown posts off disk. The package takes
  `text: string` and `orgUrn: string` and trusts the caller.
- **OAuth dance**: the package consumes a credentials file rather than
  minting one. Use `ailang-linkedin auth` (in the `sunholo-data/ailang-demos`
  repo) or any compatible OAuth flow to produce the credentials.json.

## Versions

- **0.4.0** — Contracts sweep: persona shape, header count, hex range, post-text limit (already shipped on `create*Post`). `[metadata]`, `[cascade]`, `[stability]` sections added to `ailang.toml` so the docs page surfaces tags, AI summary, repository link, etc. No API breakage.
- **0.3.1** — Image uploads (`linkedinUploadImage`, three-step register + PUT + finalise).
- **0.2.x** — Comments, persona derivation, GDPR-stripped JSON output.
- **0.1.0** — First publish. OAuth refresh + text-post publish.

Breaking changes follow semver: 0.x to 0.(x+1) for breaking, 0.x.y to 0.x.(y+1) for additive / fix.
