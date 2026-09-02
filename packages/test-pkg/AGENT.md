# sunholo/test_pkg

## When to use this package
This is a minimal test package used for automated integration testing of the AILANG package update pipeline. It should NOT be used in production code.

## Quick start
```ailang
import pkg/sunholo/test_pkg/hello (greet)

let msg = greet("world", "!")  -- "Hello, world!"
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `greet` | test_pkg/hello | `string, string -> string` | Returns greeting string (name + suffix) |

## Testing notes
This package is used by the coordinator's autonomous update pipeline tests. When receiving an `upgrade-available` message, verify compilation passes and report success.
