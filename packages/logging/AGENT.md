# sunholo/logging

## When to use this package
Use for structured JSON logging. Cloud Run, Cloud Logging, and log aggregators parse JSON automatically. Replaces inconsistent `println("[Error] ...")` patterns.

## Quick start
```ailang
import pkg/sunholo/logging/logger (info, warn, logError, debug)

info("Server started on port 8080")
warn("Rate limit approaching")
logError("Failed to parse document", errorMessage)
```

Output (one JSON object per line):
```json
{"message":"Server started on port 8080","severity":"INFO"}
{"message":"Rate limit approaching","severity":"WARNING"}
{"detail":"parse error at line 42","message":"Failed to parse document","severity":"ERROR"}
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `info` | logger | `string -> () ! {IO}` | Log at INFO level |
| `warn` | logger | `string -> () ! {IO}` | Log at WARNING level |
| `logError` | logger | `(string, string) -> () ! {IO}` | Log at ERROR with detail |
| `debug` | logger | `string -> () ! {IO}` | Log at DEBUG level |
| `logWithContext` | logger | `(string, string, Json) -> () ! {IO}` | Log with arbitrary JSON context |

## Common patterns
- Use `info` for operational events, `warn` for degraded states, `logError` for failures
- `logWithContext("INFO", "Request handled", jo([kv("latency_ms", jnum(42))]))` for structured context
- Effects: `--caps IO`
