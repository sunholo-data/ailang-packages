# Changelog — sunholo/mcp_oauth

## 0.2.0 — 2026-11-05

**Client models for Gemini Enterprise and Google Connected Apps.** Design: ailang
`design_docs/planned/v0_57_2/m-mcp-oauth-client-models.md` (Design Freeze D1–D8, ratified 2026-11-05).
Everything new is **off by default**: with no change, an adopter's metadata is byte-identical to 0.1.2
and its CIMD clients behave exactly as before. Turn a model on only after measuring the real client
(design §P0).

- **New `core.ClientConfig`** (`defaultClientConfig()`), passed only to the new entry points. `Hooks` is
  unchanged. Build the config as a record update of the default.
- **Pre-registered confidential clients (M1a, D1).** `flow.createClient` / `rotateClientSecret` /
  `deleteClient` (operator scripts, not routes). Ids are `mco_` + 32 hex; secrets are 366 random bits,
  returned once, stored only as sha256 digests and compared in constant time. `client_secret_basic` and
  `client_secret_post`; the method comes from the client record, never the request (T16). Exact
  per-client redirect list. PKCE stays required for every client (D4).
- **`flow.beginAuthorizeFor`** dispatches on the new `core.clientKind` (Z3: the `mco_` and https
  namespaces are disjoint, so a registered id is never fetched). **`flow.tokenRequest`** serves both grants
  for every client model and authenticates the client first; `invalid_client` is a 401 with
  `WWW-Authenticate: Basic`.
- **DCR (M1b, D2), RFC 7591.** `flow.registerClientDcr`: per-caller (rightmost `X-Forwarded-For`, via
  `clients.trustedCallerIp`) and global limits, a `dcrRedirectHosts` allowlist, at most 5 redirect URIs of
  at most 512 characters, a 16 KB body cap, a 24-hour TTL for an unused registration that slides to 90 days
  idle after first use, and `token_endpoint_auth_method` defaulting to `none`. No display metadata is kept;
  `describeRequest` marks such a client `"registered": "dcr"` (T15).
- **Refresh policy and revocation (M1c, D3).** Per client: `rotate` (default) or `stable` (confidential
  clients only): no rotation, `refresh_token` omitted from the refresh response, 30-day sliding idle and
  180-day absolute lifetime, client authentication on every refresh. **`flow.revokeRequest`** (RFC 7009):
  a refresh token revokes its family, an access token goes to `hooks.revoke`, the answer is 200. Family
  records are pruned to unexpired access tokens (T8).
- **Auth-method intersection (M1d).** A CIMD document's plural `token_endpoint_auth_methods_supported`, when
  present, must contain `none`; the singular field is never read. ChatGPT's live document is accepted.
  `core.authMethodOk`, `advertisedAuthMethods` (`none` always first; never `private_key_jwt`).
- **`core.asMetadataFor(issuer, cfg)`** (M1e): `registration_endpoint`, `revocation_endpoint` and the secret
  methods appear only when enabled. `asMetadata(issuer)` is pinned byte for byte to 0.1.2 by a golden test.
- **Behaviour changes for 0.1.2 call sites** (both deliberate, design §M1a/§M1d): `exchangeCode` and
  `refreshTokens` refuse a `client_id` that is not an https URL (`invalid_client`), so a registered client
  cannot skip authentication through them; `beginAuthorize` refuses an `mco_` id; and a CIMD document whose
  plural method list lacks `none` is refused. Claude's and ChatGPT's documents are unaffected.
- **One host parser, tightened (`core.httpsHost`).** The host now ends at the first `/`, `?`, `#` or `\`
  and the port at `:` (digits only); it is lowercased; userinfo, IPv6 brackets, percent-encoding, a
  trailing dot (`localhost.`), empty labels and any non-hostname character give `""`. In 0.1.2,
  `https://localhost?.example.com` had host `localhost?.example.com` and passed `cimdUrlOk`'s string
  layer (only `Net[scope=public]` refused it at connect time). `cimdUrlOk` now also refuses a backslash,
  single-label hosts (`https://intranet/`) and numeric hosts (`127.1`, `2130706433`, `0x7f.0.0.1`), and its
  shape rules are a new Z3-proved gate, `core.cimdUrlGate`. DCR redirect URIs use the same parser, and
  `clients.dcrRedirectOk` also refuses a backslash. This changes `httpsHost`'s result for malformed URLs
  only; every well-formed https URL gets the same host as before, lowercased.
- New module `sunholo/mcp_oauth/clients` (the non-secret client logic). Requires ailang ≥ 0.57.0 (the
  version this release was built and tested on).
- Tests: four new suites (`confidential`, `dcr`, `refresh_policy`, `revoke`), `e2e_client_models.sh`,
  `compat_012.sh` (the 0.1.2 suites and example, byte for byte), a live CIMD check, 6 new IFC leak fixtures (9 in all),
  new lint rules, and `mutation_check.sh` (47 mutants, all killed).

## 0.1.2 — 2026-10-14

- **Compiles on ailang ≥ 0.53.1.** `revokeFamily` called the `revoke` hook inside a lambda passed to
  `mapE`, which the latent-effect checker introduced in 0.53.1 rejects with an internal invariant
  (ailang #1826), so the package failed to build for any adopter on a current toolchain. It now
  revokes with a small recursive helper, in the same order. No behaviour or API change.

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
