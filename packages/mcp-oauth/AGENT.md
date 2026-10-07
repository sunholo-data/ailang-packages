# sunholo/mcp_oauth

## When to use this package
Use it to give an `ailang serve-api` MCP service the OAuth 2.1 authorization server that the
Anthropic and OpenAI directories require for account-backed tools. It pairs with serve-api's
listed surface: `@mcp_auth("oauth2")`, `@mcp_token_verifier`, `--oauth-issuer`, `/mcp/connect/`.

What it supports:
- PKCE S256 only;
- CIMD clients (both Claude and ChatGPT use these);
- exact redirect matching, plus RFC 8252 loopback with any port;
- single-use, digest-stored codes, where a replay revokes what the code issued;
- rotating refresh families, where reuse revokes the family.

What it does **not** do: DCR, JWT access tokens, OpenID Connect.

## Quick start
```ailang
import pkg/sunholo/mcp_oauth/core (asMetadata)
import pkg/sunholo/mcp_oauth/flow (Hooks, beginAuthorize, completeLogin, exchangeCode, refreshTokens)
```
Copy `routes_template.ail` into your service and fill in a `Hooks` record:

| Hook | Contract |
|---|---|
| `authenticate(idToken)` | ID token from your login page → account id (Parse: `sunholo/auth` `verifyFirebaseJWTFull`) |
| `mint(account, clientId)` | A fresh access token **your `@mcp_token_verifier` accepts** (Parse: a scoped `dp_` key) |
| `put/get/del(key, json, expiresAtSec)` | Storage with expiry (Parse: `sunholo/firestore`). Values hold digests only, never secrets |
| `revoke(tokenDigest)` | Invalidate the access token whose `sha256Hex` is `tokenDigest` |
| `accessTtlSec` | Lifetime of a minted access token, in seconds. Sent as `expires_in`; must match what your verifier enforces |
| `issuer` | Your issuer identifier: the same value you pass to `core.asMetadata`. Returned as `iss` with every authorization code (RFC 9207) |

## Adopter security checklist
1. Run serve-api with **`AILANG_TRACE_VALUES=off`**. Traces render arguments verbatim.
2. **Never log** request bodies, query strings, or the values the flow returns: they carry codes and tokens.
3. Let `mint` draw randomness under plain `Rand` or `Rand[mode=crypto]`. The flow calls it from a `Rand[mode=crypto]` function, so the mode stack makes those draws crypto. **Never** declare another explicit mode (such as `seeded`) on `mint`: an explicit mode overrides the stack.
4. Store keys and tokens **hashed** (`sha256Hex`), so `revoke(digest)` can find them.
5. Fetch CIMD documents with `cimd.fetchClient`, which runs `core.cimdUrlOk` and then `Net[scope=public]` (ailang ≥ 0.52.0, #1522). Never fetch a `client_id` URL under plain `Net`.
6. Use `nowSec()` (seconds). `std/clock.now()` is milliseconds.

## How the guarantees are checked
| Check | What it shows |
|---|---|
| `ailang verify core.ail` | Z3 proofs: `redirectAllowed`, `verifierLengthOk`, `challengeMethodOk`, `cimdHttpsGate`, `codeExpiresAt`, `isExpired` |
| `tests/broken_redirect.ail` | Must show a **VIOLATION**, which proves the redirect proof bites |
| `ailang test --package .` | Pure-core tests, including the RFC 7636 App. B vector |
| `tests/flow_check.sh` | Effectful flow: single use, replay revocation, binding, expiry, rotation, family revocation |
| `tests/ifc_leaks.sh` | Leaks injected into the real `flow.ail` must fail to compile |
| `tests/cimd_check.sh` | CIMD fetch: the string layer refuses http and metadata IPs; `Net[scope=public]` refuses a name that resolves to 127.0.0.1, with permissive Net flags on |
| `tests/lint.sh` | No declared record holds a secret (ailang #1523); crypto minting; no `==` on raw secrets |

## Design
`sunholo-data/ailang` `design_docs/planned/v0_52_0/m-mcp-oauth-package.md` (threat model T1–T10).
