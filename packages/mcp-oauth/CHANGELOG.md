# Changelog — sunholo/mcp_oauth

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
- Known gap: the CIMD fetch module waits for ailang `Net[scope=public]` (#1522). Until then,
  adopters must pre-register clients or fetch CIMD documents themselves under the checklist.
