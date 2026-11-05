# sunholo/mcp_oauth

## When to use this package
Use it to give an `ailang serve-api` MCP service the OAuth 2.1 authorization server that the
Anthropic, OpenAI and Google directories require for account-backed tools. It pairs with serve-api's
listed surface: `@mcp_auth("oauth2")`, `@mcp_token_verifier`, `--oauth-issuer`, `/mcp/connect/`.

What it supports:
- PKCE S256 only, for every client (confidential included);
- CIMD clients (Claude and ChatGPT), which authenticate with `none`;
- **0.2:** pre-registered confidential clients (`mco_` ids, `client_secret_basic` / `client_secret_post`),
  the Gemini Enterprise custom MCP data store shape;
- **0.2:** RFC 7591 dynamic client registration (DCR), **off by default**, with abuse limits;
- **0.2:** per-client refresh policy: `rotate` (the default; reuse revokes the family) or `stable`
  (confidential clients only; 30-day idle and 180-day absolute lifetime);
- **0.2:** RFC 7009 revocation (`/oauth/revoke`), which Google calls when a user unlinks;
- exact redirect matching, plus RFC 8252 loopback with any port;
- single-use, digest-stored codes, where a replay revokes what the code issued.

What it does **not** do: `private_key_jwt`, JWT access tokens, OpenID Connect, `client_credentials`,
RFC 7592 client management.

**Turning a client model on is a deployment decision, not a code one.** The vendor behaviour behind
each model (GE PKCE and `state`, Google's refresh expectations and DCR shape) is documented but, as of
0.2.0, not yet measured against the live clients. Record that measurement before you enable the model
(ailang `design_docs/planned/v0_57_2/m-mcp-oauth-client-models.md` §P0).

## Quick start
```ailang
import pkg/sunholo/mcp_oauth/core (ClientConfig, defaultClientConfig, asMetadataFor)
import pkg/sunholo/mcp_oauth/flow (Hooks, beginAuthorizeFor, completeLogin, describeRequest, tokenRequest, revokeRequest)
```
Copy `routes_template.ail` into your service and fill in a `Hooks` record (unchanged since 0.1.1):

| Hook | Contract |
|---|---|
| `authenticate(idToken)` | ID token from your login page → account id (Parse: `sunholo/auth` `verifyFirebaseJWTFull`) |
| `mint(account, clientId)` | A fresh access token **your `@mcp_token_verifier` accepts** (Parse: a scoped `dp_` key) |
| `put/get/del(key, json, expiresAtSec)` | Storage with expiry (Parse: `sunholo/firestore`). Values hold digests only, never secrets |
| `revoke(tokenDigest)` | Invalidate the access token whose `sha256Hex` is `tokenDigest` |
| `accessTtlSec` | Lifetime of a minted access token, in seconds. Sent as `expires_in`; must match what your verifier enforces |
| `issuer` | Your issuer identifier: the same value you pass to `core.asMetadata(For)`. Returned as `iss` with every authorization code (RFC 9207) |

New behaviour is configured with a `ClientConfig`, passed only to the 0.2 entry points. **Always build
it as a record update of `defaultClientConfig()`**, never as a full literal, so a later field does not
break your build:

```ailang
pure func config() -> ClientConfig = { defaultClientConfig() | confidential: true, revocation: true }
```

| Field | Default | Effect |
|---|---|---|
| `confidential` | `false` | Accept operator-created `mco_` clients; advertise `client_secret_basic`, `client_secret_post` |
| `dcr` | `false` | Serve `POST /oauth/register` and advertise `registration_endpoint` |
| `dcrRedirectHosts` | `[]` | DCR redirect hosts: `[]` = any https host; else exact hosts or `.suffix` entries |
| `dcrPerCallerPerHour` | `10` | DCR registrations per caller (rightmost `X-Forwarded-For`) per hour; the next one is 429 |
| `dcrGlobalPerDay` | `500` | DCR registrations per day, all callers |
| `revocation` | `false` | Serve `POST /oauth/revoke` and advertise `revocation_endpoint` |

## API
| Function | Since | Notes |
|---|---|---|
| `core.asMetadata(issuer)` | 0.1 | 0.1.2's document, byte for byte (= `asMetadataFor(issuer, defaultClientConfig())`) |
| `core.asMetadataFor(issuer, cfg)` | 0.2 | Adds only what `cfg` turns on. CIMD and `none` are always advertised, `none` first |
| `core.clientKind(id)` | 0.2 | `"cimd"` (https URL) / `"registered"` (`mco_` + 32 hex) / `"unknown"`; Z3-proved disjoint |
| `flow.beginAuthorize(h, loginUrl, clientId, registered, …)` | 0.1 | You fetch the CIMD document first. Refuses `mco_` ids |
| `flow.beginAuthorizeFor(h, cfg, loginUrl, clientId, …)` | 0.2 | Fetches CIMD itself (`Net[scope=public]`) or looks up an `mco_` client; never fetches an `mco_` id |
| `flow.describeRequest(h, handle)` | 0.1 | 0.2 adds `"registered": "operator"` or `"dcr"`. Mark a `dcr` client **unverified**: anyone can register one, and no `client_name` is kept |
| `flow.completeLogin(h, handle, idToken, now)` | 0.1 | Unchanged |
| `flow.exchangeCode` / `flow.refreshTokens` | 0.1 | Unchanged signatures; **CIMD client ids only** (anything else is `invalid_client`) |
| `flow.tokenRequest(h, cfg, authorizationHeader, formBody, now)` | 0.2 | Both grants, every client model; returns `(status, body, wwwAuthenticate)` |
| `flow.revokeRequest(h, cfg, authorizationHeader, formBody, now)` | 0.2 | RFC 7009; `(status, body, wwwAuthenticate)`; 200 for any token once the client authenticates |
| `flow.registerClientDcr(h, cfg, callerKey, body, now)` | 0.2 | RFC 7591; `Ok((status, json))` (201/400/404/429), `Err(json)` only on a store failure |
| `flow.createClient(h, cfg, redirectUris, method, refreshPolicy, now)` | 0.2 | Operator only: `Ok((clientId, secret))`; the secret is shown once |
| `flow.rotateClientSecret(h, clientId, now)` / `flow.deleteClient(h, clientId)` | 0.2 | The old secret stops working at once |
| `clients.trustedCallerIp(xff, realIp)` | 0.2 | The DCR caller key: the **rightmost** `X-Forwarded-For` entry (`trustedCallerIpHops` for your own proxies) |

## Recipes

### 1. Claude / ChatGPT only (no change)
Keep 0.1.2's routes and `asMetadata`. Nothing changes: the metadata is byte-identical, CIMD clients
authenticate with `none` and always rotate, and ChatGPT's live CIMD document (singular
`private_key_jwt`, plural `["none","private_key_jwt"]`) is accepted. One deliberate tightening: a CIMD
document whose plural `token_endpoint_auth_methods_supported` lacks `none` is now refused, with a
message that says so. `exchangeCode`/`refreshTokens` now refuse a `client_id` that is not an https URL.

### 2. Gemini Enterprise custom MCP data store (confidential client)
1. `config()` with `confidential: true`; serve `asMetadataFor(issuer, config())`; route `/oauth/token`
   through `tokenRequest` (it reads the `Authorization` header: mount the route with `@raw`), and
   `/oauth/authorize` through `beginAuthorizeFor`.
2. Create the client **once, from an operator script** with your real store hooks (never a route), see
   `routes_template.ail` `createGeClient`:
   `createClient(h, config(), ["https://vertexaisearch.cloud.google.com/oauth-redirect"], "client_secret_basic", "rotate", nowSec())`.
   It prints the client id and secret once. Keep the secret only in the GE admin form.
3. GE admin form: Client ID and Client secret from step 2; Authorization URL `<issuer>/oauth/authorize`;
   Token URL `<issuer>/oauth/token`. Leave **"Use HTTP Basic Authentication"** selected (untick it only for a
   `client_secret_post` client). **Tick "Enable PKCE Support"**: PKCE is required for every client (D4).
4. GE org policy: allow the FQDNs of your MCP server URL, authorization URL and token URL (egress allowlist).
5. If GE turns out to need a non-rotating refresh token (measurement P0-3), recreate the client with
   `"stable"`: allowed, because it is confidential.

### 3. Google Connected Apps (DCR)
1. `config()` with `dcr: true`, `revocation: true`, and `dcrRedirectHosts` set, for example
   `[".googleusercontent.com", "claude.ai"]`. With an allowlist, an attacker cannot register a redirect
   on their own host.
2. Mount `POST /oauth/register` (`registerClientDcr`, caller key from `clients.trustedCallerIp`) and
   `POST /oauth/revoke` (`revokeRequest`), and serve `asMetadataFor`.
3. DCR clients rotate refresh tokens. A public DCR client cannot be `stable` until measurement P0-4
   shows how Google registers (D3).

## Adopter security checklist
1. Run serve-api with **`AILANG_TRACE_VALUES=off`**. Traces render arguments verbatim.
2. **Never log** request bodies, query strings, the `Authorization` header, or the values the flow
   returns: they carry codes, tokens and client secrets. The 0.2 entry points type their secret-bearing
   results `string<secret>`, so passing one to a `string{not secret}` sink fails to compile.
   (The 0.1.2 functions' results are not labelled at your call site: be as careful with those.)
3. Let `mint` draw randomness under plain `Rand` or `Rand[mode=crypto]`. The flow calls it from a `Rand[mode=crypto]` function, so the mode stack makes those draws crypto. **Never** declare another explicit mode (such as `seeded`) on `mint`: an explicit mode overrides the stack.
4. Store keys and tokens **hashed** (`sha256Hex`), so `revoke(digest)` can find them. Client secrets are
   hashed by the package; your store never sees one.
5. Fetch CIMD documents with `cimd.fetchClient` (or let `beginAuthorizeFor` do it), which runs
   `core.cimdUrlOk` and then `Net[scope=public]`. Never fetch a `client_id` URL under plain `Net`.
6. Use `nowSec()` (seconds). `std/clock.now()` is milliseconds.
7. Send `tokenRequest`'s third value as `WWW-Authenticate` when it is not `""`, and send
   `Cache-Control: no-store` on token responses.
8. DCR counters are soft: the store hook has no compare-and-set, so concurrent registrations can exceed
   a limit by up to the number of requests in flight.
9. A stable refresh token cannot detect reuse (it is reusable by design). It is bound to its client,
   whose secret is checked on every refresh, and it dies at its idle or absolute deadline or on
   `/oauth/revoke`.

## How the guarantees are checked
| Check | What it shows |
|---|---|
| `ailang verify core.ail` / `ailang verify clients.ail` | Z3 proofs: redirects, PKCE length and method, CIMD https gate, code lifetime, **`clientKind`** (disjoint namespaces), **`authMethodOk`**, `cimdAuthMethodsOk`, `advertisedAuthMethods`, `refreshPolicyOk`, the stable lifetimes, **`dcrRedirectOk`**, `clientAccepted`, `clientLive`, the DCR windows |
| `tests/broken_redirect.ail` | Must show a **VIOLATION**, which proves the redirect proof bites |
| `ailang test --package .` | Pure tests, incl. the RFC 7636 App. B vector, the 0.1.2 metadata golden and ChatGPT's live CIMD document |
| `tests/flow_check.sh` | 0.1.2 flow: single use, replay revocation, binding, expiry, rotation, family revocation |
| `tests/confidential_check.sh` | Confidential clients, the GE happy path, Basic/post, T16 downgrades, legacy guards (run without `Net`) |
| `tests/dcr_check.sh` | DCR: allowlist, per-caller and global limits, unused TTL, body cap, rightmost `X-Forwarded-For` |
| `tests/refresh_policy_check.sh`, `tests/revoke_check.sh` | Stable refresh lifetimes and client auth, family pruning, RFC 7009 |
| `tests/e2e_flow.sh`, `tests/e2e_client_models.sh` | Both flows under real serve-api, plus `ailang mcp check` |
| `tests/compat_012.sh` | The 0.1.2 suites and example service, byte for byte from the 0.1.2 release, against this tree |
| `tests/ifc_leaks.sh` | Leaks injected into the real `flow.ail` (tokens, codes, client secrets) must fail to compile |
| `tests/cimd_check.sh`, `tests/cimd_live_check.sh` | CIMD fetch layers; the live ChatGPT and Claude documents are accepted |
| `tests/lint.sh` | No declared record holds a secret; crypto minting; no `==` on secrets; `clients.ail` never sees one |
| `tests/mutation_check.sh` | Each control, removed in a scratch copy, makes a named test or proof fail |

## Design
`sunholo-data/ailang` `design_docs/planned/v0_52_0/m-mcp-oauth-package.md` (threat model T1–T10) and
`design_docs/planned/v0_57_2/m-mcp-oauth-client-models.md` (client models, T11–T17).
