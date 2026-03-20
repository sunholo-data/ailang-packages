# sunholo/testing_utils

## When to use this package
Use for test assertions in AILANG test files. Pure functions returning `Result[string, string]` — "PASS: context" on success, "FAIL: context — expected X but got Y" on failure.

## Quick start
```ailang
import pkg/sunholo/testing_utils/assertions (assertEqual, assertContains, assertOk, assertTrue)

-- String equality
assertEqual("hello", actual, "greeting field")

-- Integer equality
assertEqualInt(42, computed, "answer")

-- Contains check
assertContains(responseBody, "success", "API response")

-- Result check
assertOk(parseResult, "JSON parsing")

-- Boolean check
assertTrue(isValid, "validation result")
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `assertEqual` | assertions | `(string, string, string) -> Result` | String equality |
| `assertEqualInt` | assertions | `(int, int, string) -> Result` | Int equality |
| `assertContains` | assertions | `(string, string, string) -> Result` | Substring check |
| `assertOk` | assertions | `(Result, string) -> Result` | Result is Ok |
| `assertErr` | assertions | `(Result, string) -> Result` | Result is Err |
| `assertTrue` | assertions | `(bool, string) -> Result` | Boolean is true |

## Common patterns
- All functions take a `context` string as last arg for clear error messages
- Pure functions — no effects required
- Use with AILANG's inline test system: `test "my test" = assertEqual("expected", actual, "field")`
