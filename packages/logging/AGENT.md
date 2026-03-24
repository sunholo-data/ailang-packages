# sunholo/logging

## When to use this package
Use for structured logging in any AILANG package or application. Built on the **Debug effect** (ghost effect) — no IO cascade, zero-cost in release mode. Replaces `println("[Error] ...")` patterns and avoids forcing `! {IO}` on every caller.

**Why Debug instead of IO?** The `IO` effect cascades: if your library uses `println`, every function that calls it must also declare `! {IO}`, all the way up to `main`. The `Debug` effect is a ghost effect — it doesn't cascade, the host collects logs after execution, and `--release` erases all Debug calls to zero cost.

## Quick start
```ailang
module myapp/server

import pkg/sunholo/logging/logger (info, warn, err, trace)

-- No IO cascade! Only Debug effect required
export func handleRequest(path: string) -> Response ! {Net, Debug} {
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

| Function | Signature | Effect | Description |
|----------|-----------|--------|-------------|
| `info` | `string -> () ! {Debug}` | Debug | Log at INFO level |
| `warn` | `string -> () ! {Debug}` | Debug | Log at WARNING level |
| `err` | `(string, string) -> () ! {Debug}` | Debug | Log at ERROR with detail |
| `trace` | `string -> () ! {Debug}` | Debug | Log at DEBUG/TRACE level |
| `withContext` | `(string, string, Json) -> () ! {Debug}` | Debug | Log with structured JSON context |
| `verify` | `(bool, string) -> () ! {Debug}` | Debug | Record assertion (continues on failure) |

## Common patterns

### Logging in library packages (no IO cascade)
```ailang
module mylib/parser

import pkg/sunholo/logging/logger (trace, err)

-- Callers only need to declare their OWN effects, not IO
export func parse(input: string) -> Result ! {Debug} {
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

-- AFTER (Debug ghost effect — no cascade)
import pkg/sunholo/logging/logger (info)
func process(x: int) -> int ! {Debug} =
  let _ = info("processing " ++ show(x));
  x * 2
```

## Effect: Debug (ghost effect)
- **Max effect**: `Debug` (declared in `ailang.toml`)
- **Capability needed**: `--caps Debug`
- **Ghost property**: Does not cascade to callers; erased in `--release`
- **Host collection**: `DebugContext.Collect()` returns all logs + assertions after execution
