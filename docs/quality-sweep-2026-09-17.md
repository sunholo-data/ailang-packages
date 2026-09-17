# Quality sweep — 2026-09-17

First run of the shipped `ailang pkg quality` (ailang dev after v0.39.5, PR sunholo-data/ailang#1255) across every package here, with `ailang lock` regenerated locally first (43 committed lock files carry absolute paths from another machine — ailang core backlog, 2026-09-15). Tests and `_smoke.ail` were executed (attested); Z3 per-function timeout 3s.

Reproduce: `cd packages/<dir> && ailang lock && ailang pkg quality .`

| package | compile | contracts verified/total | pure exports | tests | smoke | gates |
|---|---|---|---|---|---|---|
| a2ui | ✓ | 0/1 (1 Z3-skipped) | 31/31 | 0/0 | — | — |
| agui | ✓ | 0/12 (12 Z3-skipped) | 8/8 | 19/19 | ✓ | — |
| auth | ✓ | 2/4 (2 Z3-skipped) | 5/5 | 41/41 | — | — |
| billing-entitlements | ✓ | 8/18 (10 Z3-skipped) | 17/17 | 6/41 | — | PUB012 |
| billing-proposals | ✓ | 3/8 (2 Z3-skipped) | 11/11 | 21/21 | — | — |
| billing-service-api | ✗ checkout_handler.ail | 0/0 | 0/0 | 0/0 | — | PUB000 |
| billing-store | ✗ customers_repo.ail | 0/0 | 0/0 | 0/0 | — | PUB000 |
| billing-stripe | ✓ | 0/4 (4 Z3-skipped) | 1/5 | 6/6 | — | — |
| config | ✓ | 0/0 | 0/3 | 0/0 | — | — |
| deontic | ✓ | 7/7 | 21/21 | 21/21 | ✓ | — |
| discord | ✓ | 1/21 (19 Z3-skipped) | 16/26 | 29/29 | ✓ | — |
| duckdb | ✓ | 0/0 | 3/10 | 2/2 | — | — |
| external-backend | ✓ | 2/2 | 2/3 | 0/0 | ✓ | — |
| firebase-auth | ✓ | 0/3 (3 Z3-skipped) | 1/4 | 0/0 | — | — |
| firestore | ✗ client.ail | 0/0 | 0/0 | 0/0 | — | PUB000 |
| gcp-auth | ✓ | 0/0 | 0/4 | 0/0 | — | — |
| gcs-storage | ✓ | 0/0 | 6/8 | 0/0 | — | — |
| gemini-files | ✓ | 0/0 | 5/7 | 0/0 | — | — |
| gemini-live | ✓ | 0/0 | 30/30 | 0/0 | — | — |
| gmail | ✓ | 0/3 (3 Z3-skipped) | 17/21 | 0/0 | ✓ | — |
| http-helpers | ✗ request.ail | 0/0 | 0/0 | 0/0 | — | PUB000 |
| linkedin | ✗ _smoke.ail | 0/0 | 0/0 | 0/0 | ✓ | PUB000 |
| logging | ✓ | 0/0 | 9/10 | 0/0 | — | — |
| motoko-ext-a2a | ✗ a2a.ail | 0/0 | 0/0 | 0/0 | — | PUB000 |
| motoko-ext-abi | ✓ | 0/0 | 0/0 | 0/0 | — | PUB012 |
| motoko-ext-ai-compat | ✓ | 0/0 | 0/1 | 0/0 | — | — |
| motoko-ext-ailang-docs | ✓ | 0/0 | 5/8 | 0/0 | — | — |
| motoko-ext-compaction-ai | ✓ | 0/0 | 1/4 | 0/0 | ✓ | — |
| motoko-ext-compose | ✓ | 0/0 | 33/49 | 0/0 | — | — |
| motoko-ext-context-mode | ✓ | 0/2 (2 Z3-skipped) | 9/15 | 0/0 | ✓ | — |
| motoko-ext-decision-framework | ✓ | 0/0 | 1/1 | 0/0 | — | — |
| motoko-ext-exa-search | ✓ | 0/0 | 6/10 | 0/0 | — | — |
| motoko-ext-fmt | ✓ | 0/0 | 1/1 | 0/0 | — | — |
| motoko-ext-mcp | ✓ | 0/2 (2 Z3-skipped) | 9/14 | 0/0 | ✓ | — |
| motoko-ext-microrag | ✓ | 0/0 | 1/1 | 0/0 | — | — |
| motoko-ext-omnigraph | ✓ | 0/0 | 9/13 | 0/0 | ✓ | — |
| motoko-ext-test-dummy | ✓ | 0/0 | 0/1 | 0/0 | — | — |
| oauth | ✓ | 0/0 | 3/10 | 0/0 | ✓ | — |
| ollama-stream | ✓ | 0/0 | 3/4 | 0/0 | — | — |
| registry-validator | ✗ validate.ail | 0/0 | 0/0 | 0/0 | — | PUB000 |
| test-pkg-consumer | ✓ | 0/0 | 2/2 | 0/0 | — | — |
| test-pkg | ✓ | 0/0 | 3/3 | 0/0 | — | — |
| testing-utils | ✓ | 0/0 | 6/6 | 0/0 | — | — |

## What the sweep says

- **Compile:** 37/44 pass on the current binary. `firestore` fails STRICT_FALLBACK_001 (`client.ail:184`) and takes `billing-service-api` and `billing-store` with it; `linkedin` fails the same rule in `comments.ail:112` (reached via `_smoke.ail`); `http-helpers` and `registry-validator` carry March-2026 dialect type errors; `motoko-ext-a2a` fails effect checking. A republish of any of these is refused (`PUB000`) until fixed.
- **Contracts:** proved — deontic 7/7, billing-entitlements 8/18, billing-proposals 3/8, auth 2/4, external-backend 2/2, discord 1/21. **58 contracts across 11 packages are Z3-skipped** (records, strings, list builtins): runtime assertions, not proofs (`PUB016`).
- **Tests:** 8 packages have `*_test.ail`; `billing-entitlements` is 6/41 passing; the rest are green.
- **Release description:** 0/44 have a `CHANGELOG.md` section or `[release] kind` — the ailang v0.41.0 gate (`PUB001`/`PUB002`) will refuse every package until each next release adds them.
- **Inbox:** agui, discord and motoko-ext-{ai-compat,compose,context-mode,exa-search,mcp,omnigraph,a2a} lack `[metadata] repository`, so no `pkg:<name>` agent can be derived (`PUB021`).
