# sunholo/http_helpers

## When to use this package
Use when making HTTP API calls. Eliminates repeated Bearer auth header construction and JSON response parsing that every AILANG API project reinvents.

## Quick start
```ailang
import pkg/sunholo/http_helpers/request (authGet, authPost, bearerHeaders)
import pkg/sunholo/http_helpers/response (requireOk, parseJsonBody, requireField)

-- GET with Bearer token
match authGet("https://api.example.com/data", token) {
  Ok(resp) => match requireOk(resp) {
    Ok(body) => match parseJsonBody(body) {
      Ok(json) => requireField(json, "name"),
      Err(e) => Err(e)
    },
    Err(e) => Err(e)
  },
  Err(e) => Err(e)
}

-- POST JSON with Bearer token
match authPost(url, token, encode(jo([kv("query", js("SELECT 1"))]))) {
  Ok(resp) => requireOk(resp),
  Err(e) => Err(e)
}
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `bearerHeaders` | request | `string -> [{name, value}]` | Build Authorization: Bearer + Content-Type headers |
| `jsonHeaders` | request | `() -> [{name, value}]` | Build Content-Type: application/json headers |
| `apiKeyHeaders` | request | `string -> [{name, value}]` | Build x-api-key headers |
| `authGet` | request | `(url, token) -> Result[HttpResponse, string] ! {Net}` | GET with Bearer auth |
| `authPost` | request | `(url, token, body) -> Result[HttpResponse, string] ! {Net}` | POST with Bearer auth |
| `authPostJson` | request | `(url, token, Json) -> Result[HttpResponse, string] ! {Net}` | POST JSON with Bearer auth |
| `requireOk` | response | `HttpResponse -> Result[string, string]` | Check 2xx status, return body |
| `parseJsonBody` | response | `string -> Result[Json, string]` | Parse JSON from response body |
| `requireField` | response | `(Json, string) -> Result[string, string]` | Extract required string field |

## Common patterns
- Chain: `authGet` → `requireOk` → `parseJsonBody` → `requireField`
- Combine with `sunholo/gcp-auth` for GCP API calls
- Effects: `--caps Net`
