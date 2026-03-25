# sunholo/logging

## When to use this package
Use for structured logging in any AILANG package or application. Built on the **Debug effect** (ghost effect) — completely invisible to callers, zero-cost in release mode. Replaces `println("[Error] ...")` patterns without forcing any effect on callers.

**Why Debug instead of IO?** The `IO` effect cascades: if your library uses `println`, every function that calls it must also declare `! {IO}`, all the way up to `main`. The `Debug` effect is a **true ghost effect** — callers don't need to declare it at all, packages don't need `[effects].max`, runtime doesn't need `--caps Debug`. The host collects logs after execution, and `--release` erases all Debug calls to zero cost.

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

Run (no `--caps Debug` needed):
```bash
ailang run --caps IO,Net --entry main server.ail
```

Output (collected by host, routed to stderr):
```json
{"severity":"INFO","message":"Handling request: /users"}
{"severity":"INFO","message":"Request complete"}
```

Filter by log level:
```bash
# Only show warnings and errors
ailang run --log-level warn --entry main server.ail

# Suppress all debug output
ailang run --log-level none --entry main server.ail

# Show everything including trace
ailang run --log-level debug --entry main server.ail
```

## Exported functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `info` | `string -> ()` | Log at INFO level |
| `warn` | `string -> ()` | Log at WARNING level |
| `err` | `(string, string) -> ()` | Log at ERROR with detail |
| `trace` | `string -> ()` | Log at DEBUG/TRACE level |
| `infoWith` | `(string, [{key: string, value: Json}]) -> ()` | INFO with structured kv fields |
| `warnWith` | `(string, [{key: string, value: Json}]) -> ()` | WARNING with structured kv fields |
| `errWith` | `(string, string, [{key: string, value: Json}]) -> ()` | ERROR with detail + structured kv fields |
| `traceWith` | `(string, [{key: string, value: Json}]) -> ()` | DEBUG with structured kv fields |
| `withContext` | `(string, string, Json) -> ()` | Log with arbitrary severity and JSON context |
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

### Structured fields logging
```ailang
import pkg/sunholo/logging/logger (infoWith, errWith)
import std/json (kv, js, jnum)

-- Structured fields appended to the JSON log entry
infoWith("Request handled", [
  kv("latency_ms", jnum(42)),
  kv("path", js("/api/users")),
  kv("status", jnum(200))
])
-- Output: {"severity":"INFO","message":"Request handled","latency_ms":42,"path":"/api/users","status":200}

errWith("DB timeout", "connection refused", [
  kv("host", js("db.prod.internal")),
  kv("retries", jnum(3))
])
-- Output: {"severity":"ERROR","message":"DB timeout","detail":"connection refused","host":"db.prod.internal","retries":3}
```

### Legacy context logging (still supported)
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

### Log level filtering
```bash
# Development: see all logs
ailang run --entry main app.ail

# Production: only warnings and errors
ailang run --log-level warn --entry main app.ail

# Release mode: Debug calls erased, zero overhead
ailang run --release --entry main app.ail

# serve-api with log level
ailang serve-api --log-level error ./api/
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
- **No `[effects].max` needed** — ghost effects bypass package ceiling checks
- **No `--caps Debug` needed** — auto-granted in every execution context
- **No `! {Debug}` needed** — invisible to callers, no signature cascade
- **Release mode**: `--release` erases all Debug calls to `()` (zero cost)
- **Log level filtering**: `--log-level debug|info|warn|error|none`
- **Host collection**: `DebugContext.Collect()` returns all logs + assertions after execution
