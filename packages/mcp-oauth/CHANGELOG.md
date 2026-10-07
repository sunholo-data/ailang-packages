# Changelog — sunholo/mcp_oauth

## 0.1.1 — 2026-10-07

- **Authorization responses carry `iss`** (RFC 9207). The redirect is now
  `…?code=…&state=…&iss=<issuer>`, and the metadata advertises
  `authorization_response_iss_parameter_supported: true`. This defends clients that talk to more
  than one authorization server against mix-up attacks. It is also what makes ChatGPT use its stable
  redirect URI (`https://chatgpt.com/connector_platform_oauth_redirect`) rather than a per-connector one.
- **Breaking (pre-1.0):** `Hooks` gains `issuer: string`. Set it to the issuer identifier you pass to
  `core.asMetadata`. New pure helper `core.authResponseUrl`.
- Tests: 3 new core tests and the integration check "redirect carries iss". A mutant that drops `iss`
  compiles and fails 3 checks.

## 0.1.0 — 2026-10-02

**First release.** An OAuth 2.1 authorization server for MCP services listed in the Anthropic and
OpenAI directories. Design: ailang `design_docs/planned/v0_52_0/m-mcp-oauth-package.md`.

- `core` (pure; contracts proved by Z3):
  - PKCE S256 only, checked against the RFC 7636 App. B vector;
  - exact redirect matching and RFC 8252 loopback (any port);
  - the CIMD `client_id` URL predicate (https only; no IP literal, localhost, `.internal`,
    `metadata`, userinfo or fragment);
  - 60 s code lifetime;
  - RFC 8414 metadata (S256, CIMD, no registration endpoint).
- `flow`:
  - authorize, login completion, code exchange and refresh;
  - the service plugs in four hooks: authenticate, mint, store, revoke;
  - secrets are `string<secret>` and stored as digests;
  - single-use codes; a replay revokes what the code issued;
  - refresh tokens rotate, and reuse revokes the whole family.
- Adopter feedback from AILANG Parse (before first publish):
  - `Hooks.mint` may use `Declassify` (to hash the key it stores).
  - New `Hooks.accessTtlSec`; the token response carries `expires_in`.
  - New `describeRequest(h, handle)` for consent screens, so adopters don't read internal store keys.
  - The login URL gets `&handle=` when it already has a query.
- - `cimd`: fetches and validates a client's metadata document. It first checks the URL with
  `core.cimdUrlOk`, then fetches once under `Net[scope=public]` (ailang ≥ 0.52.0, #1522), so
  loopback, metadata and private addresses are refused at connect time, including a hostname that
  resolves to 127.0.0.1. The document size is bounded, its `client_id` must equal the URL it was
  fetched from, and every redirect URI must be https or loopback http.
