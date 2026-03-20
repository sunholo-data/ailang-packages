# sunholo/config

## When to use this package
Use for validated environment variable loading. Replaces scattered `getEnvOr` calls with clear required/optional/default patterns and batch validation at startup.

## Quick start
```ailang
import pkg/sunholo/config/loader (requireEnv, optionalEnv, requireAll)

-- Load required env var (fails with clear error if missing)
match requireEnv("GOOGLE_CLOUD_PROJECT") {
  Ok(project) => -- use project
  Err(e) => logError("Config", e)  -- "Required env var GOOGLE_CLOUD_PROJECT is not set"
}

-- Load optional with default
let port = optionalEnv("PORT", "8080")

-- Validate multiple required vars at startup
match requireAll(["GOOGLE_CLOUD_PROJECT", "API_KEY", "DATABASE"]) {
  Ok(values) => -- values is [projectId, apiKey, dbName]
  Err(e) => -- first missing var reported
}
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `requireEnv` | loader | `string -> Result[string, string] ! {Env}` | Load required env var |
| `optionalEnv` | loader | `(string, string) -> string ! {Env}` | Load with default |
| `requireAll` | loader | `[string] -> Result[[string], string] ! {Env}` | Validate multiple required vars |

## Common patterns
- Call `requireAll` at startup to fail fast on missing config
- Effects: `--caps Env`
