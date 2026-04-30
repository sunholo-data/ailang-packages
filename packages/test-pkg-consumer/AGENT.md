# sunholo/test_pkg_consumer

## When to use this package

You almost certainly should not. This package exists as a **cascade-fixture** for the M-PKG-AUTONOMOUS-CASCADE-SAFE smoke tests. It depends on `sunholo/test_pkg` and does nothing useful — its sole purpose is to be a dependent that the autonomous cascade can bump when `test_pkg` ships a new version.

## Quick start

```ailang
import pkg/sunholo/test_pkg_consumer/wrap (greetExcited)

let msg = greetExcited("smoke")
-- "Hello, smoke! (via test-pkg_consumer)"
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `greetExcited` | `wrap` | `string -> string` | Calls `test_pkg.greet` + appends a marker so the cascade-driven bump is observable in tests |
| `consumerVersion` | `wrap` | `() -> string` | Returns a marker string mentioning the wrapped `test_pkg` version |

## Cascade behaviour (for the autonomous package agent)

When you receive a `release-sync` / `upgrade-available` message bumping `sunholo/test_pkg`:

1. The cascade trigger has `Source: cascade` (publisher-IAM-restricted ailang-cascade Pub/Sub topic). Verify this before acting per the `pkg-update.md` template guard.
2. Bump `dependencies."sunholo/test_pkg"` in this package's `ailang.toml` to the new version.
3. Bump this package's own version (patch unless test_pkg's interface hash changed, in which case minor).
4. Run `ailang test --package .` to ensure compilation against the new test_pkg.
5. **Do not auto-merge.** The smoke-test PR is labelled `[smoke-test, do-not-merge]` — humans review it. v1 of the cascade is always-PR.
6. Open a PR with title `[cascade] bump test_pkg → vX.Y.Z` and emit `PUBLISH_RESULT:` markers.

## Cascade budget

This fixture sets `[cascade] max_cost_usd = 0.50` (vs the $1.00 default) so the forced-fail variant of the smoke test trips the budget gate quickly without burning much money on agent Sonnet calls. Don't change this without coordinating with the smoke-test scripts.

## Testing notes

This package is exercised by:
- `scripts/integration/test_cascade_e2e.sh` (real publish → real PR observed)
- `scripts/integration/test_cascade_negative.sh` (public MCP cannot trigger publish)

Both scripts clean up their PRs at end. If you find a stale `[cascade] [smoke-test]` PR open against this package, it's safe to delete the branch.
