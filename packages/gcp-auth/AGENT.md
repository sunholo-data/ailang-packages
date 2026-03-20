# sunholo/gcp-auth

## When to use this package
Use when your AILANG service runs on GCP and needs to authenticate API calls. Reads Application Default Credentials (ADC) and exchanges refresh tokens for access tokens via OAuth2. Also detects the default GCP project.

## Quick start
```ailang
import pkg/sunholo/gcp-auth/token (getAccessToken)
import pkg/sunholo/gcp-auth/project (getDefaultProject)
import pkg/sunholo/http-helpers/request (authGet)

-- Get OAuth2 access token from ADC
match getAccessToken() {
  Ok(token) => {
    -- Use token for authenticated API calls
    match authGet("https://storage.googleapis.com/...", token) {
      Ok(resp) => resp.body,
      Err(e) => "API error: " ++ e
    }
  },
  Err(e) => "Auth failed: " ++ e
}

-- Detect GCP project (checks GOOGLE_CLOUD_PROJECT env, then gcloud config, then ADC)
match getDefaultProject() {
  Ok(project) => -- use project ID
  Err(e) => -- no project configured
}
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `getAccessToken` | gcp-auth/token | `() -> Result[string, string] ! {FS, Net}` | Exchange ADC refresh token for access token |
| `readCredentials` | gcp-auth/token | `() -> Result[ADCCredentials, string] ! {FS}` | Read and parse ADC file |
| `getCredentialsPath` | gcp-auth/token | `() -> string ! {FS}` | Path to ADC JSON file |
| `getDefaultProject` | gcp-auth/project | `() -> Result[string, string] ! {FS}` | Detect GCP project ID |

## Common patterns
- On Cloud Run: ADC is automatic (service account). Set `GOOGLE_CLOUD_PROJECT` env var.
- Locally: Run `gcloud auth application-default login` first
- Combine with `sunholo/http-helpers` for authenticated HTTP requests
- Effects required: `--caps FS,Net` (FS to read ADC file, Net for OAuth2 exchange)
