# sunholo/logging

## When to use this package
Use for structured logging in any AILANG package or application. Built on the **Debug effect** (ghost effect) — completely invisible to callers, zero-cost in release mode. Replaces `println("[Error] ...")` patterns without forcing any effect on callers.

**Why Debug instead of IO?** The `IO` effect cascades: if your library uses `println`, every function that calls it must also declare `! {IO}`, all the way up to `main`. The `Debug` effect is a **true ghost effect** — callers don't need to declare it at all, the host collects logs after execution, and `--release` erases all Debug calls to zero cost.

## Quick start
```ailang
module myapp/server

import pkg/sunholo/logging/logger (info, warn, err, trace)

-- Debug is ghost: no effect declaration needed for logging!
-- Only declare effects you actually need (Net for HTTP)
export func handleRequest(path: string) -> Response ! {Net} {
  info("Handling request: " ++ path);
  let result = httpGet("https://api.example.com" ++ path);
  info("Request complete");
  result
}
```

Run with Debug capability:
```bash
ailang run --caps IO,Net,Debug --entry main server.ail
```

Output (collected by host, routed to stderr/Cloud Logging):
```json
{"message":"Handling request: /users","severity":"INFO"}
{"message":"Request complete","severity":"INFO"}
```

## Exported functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `info` | `string -> ()` | Log at INFO level |
| `warn` | `string -> ()` | Log at WARNING level |
| `err` | `(string, string) -> ()` | Log at ERROR with detail |
| `trace` | `string -> ()` | Log at DEBUG/TRACE level |
| `withContext` | `(string, string, Json) -> ()` | Log with structured JSON context |
| `verify` | `(bool, string) -> ()` | Record assertion (continues on failure) |

Note: These functions use the Debug effect internally, but **callers never need to declare it** — Debug is a ghost effect.

## Common patterns

### Logging in library packages (zero signature impact)
```ailang
module mylib/parser

import pkg/sunholo/logging/logger (trace, err)

-- Pure function signature — logging is invisible to callers
export func parse(input: string) -> Result {
  trace("Parsing input of length " ++ show(length(input)));
  match tokenize(input) {
    Ok(tokens) -> Ok(buildAst(tokens)),
    Err(msg) -> {
      err("Parse failed", msg);
      Err(msg)
    }
  }
}
```

### Structured context logging
```ailang
import pkg/sunholo/logging/logger (withContext)
import std/json (jo, kv, js, jnum)

withContext("INFO", "Request handled", jo([
  kv("latency_ms", jnum(42)),
  kv("path", js("/api/users")),
  kv("status", jnum(200))
]))
```

### Assertions (recorded, not thrown)
```ailang
import pkg/sunholo/logging/logger (verify)

verify(length(items) > 0, "items must not be empty")
-- Execution continues even if assertion fails
-- Host collects failed assertions via DebugContext.FailedAssertions()
```

### Release mode (zero cost)
```bash
# Development: logs collected and visible
ailang run --caps IO,Net,Debug --entry main app.ail

# Production: Debug calls erased, zero overhead
ailang run --release --caps IO,Net --entry main app.ail
```

## Migration from IO-based logging
```ailang
-- BEFORE (IO cascade — every caller needs ! {IO})
import std/io (println)
func process(x: int) -> int ! {IO} =
  let _ = println("[INFO] processing " ++ show(x));
  x * 2

-- AFTER (Debug ghost effect — no cascade, no effect declaration)
import pkg/sunholo/logging/logger (info)
func process(x: int) -> int =
  let _ = info("processing " ++ show(x));
  x * 2
```

## Effect: Debug (ghost effect)
- **Max effect**: `Debug` (declared in `ailang.toml`)
- **Capability needed**: `--caps Debug` at runtime
- **Ghost property**: Completely invisible to callers — no `! {Debug}` needed in signatures
- **Release mode**: `--release` erases all Debug calls to `()` (zero cost)
- **Host collection**: `DebugContext.Collect()` returns all logs + assertions after execution
