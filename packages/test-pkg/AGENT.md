# sunholo/test_pkg

## When to use this package
This is a minimal test package used for automated integration testing of the AILANG package update pipeline. It should NOT be used in production code.

## Quick start
```ailang
import pkg/sunholo/test_pkg/hello (greet, version)

let msg = greet("world")  -- "Hello, world!"
let ver = version()       -- "test-pkg"
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `greet` | test_pkg/hello | `string -> string` | Returns greeting string |
| `version` | test_pkg/hello | `() -> string` | Returns package identifier |

## Testing notes
This package is used by the coordinator's autonomous update pipeline tests. When receiving an `upgrade-available` message, verify compilation passes and report success.
