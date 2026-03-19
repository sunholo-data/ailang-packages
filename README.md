# AILANG Packages

Curated AILANG packages for production use. Extracted from real projects (docparse, ecommerce demos, streaming agents) to eliminate duplication and provide tested, reusable modules.

## Quick Start

```bash
# Clone the package repository
git clone https://github.com/sunholo-data/ailang-packages.git

# In your AILANG project:
ailang init package --name myorg/myapp
ailang add --path ../ailang-packages/packages/gcp-auth
ailang add --path ../ailang-packages/packages/logging
ailang lock
```

Then in your `.ail` files:

```ailang
import pkg/sunholo/gcp-auth/token (getAccessToken)
import pkg/sunholo/logging/logger (info, logError)

export func main() -> () ! {IO, FS, Net} =
  match getAccessToken() {
    Ok(token) => info("Authenticated successfully"),
    Err(e) => logError("Auth failed", e)
  }
```

## Available Packages

| Package | Description | Effects | Stability |
|---------|-------------|---------|-----------|
| [sunholo/gcp-auth](packages/gcp-auth/) | GCP ADC OAuth2 token exchange, project detection | FS, Net | experimental |
| [sunholo/auth](packages/auth/) | API key validation, HMAC hashing, bearer token extraction | Pure | experimental |
| [sunholo/http-helpers](packages/http-helpers/) | HTTP request builders, auth headers, JSON response parsing | Net | experimental |
| [sunholo/logging](packages/logging/) | Structured JSON logging (Cloud Run friendly) | IO | experimental |
| [sunholo/config](packages/config/) | Config loading from env vars with validation | Env | experimental |
| [sunholo/testing-utils](packages/testing-utils/) | Test assertion helpers (assertEqual, assertOk, etc.) | Pure | experimental |

## Package Details

### sunholo/gcp-auth
OAuth2 token exchange via Application Default Credentials. Reads `~/.config/gcloud/application_default_credentials.json`, exchanges refresh tokens for access tokens. Also detects default GCP project from gcloud config.

**Extracted from:** `demos/ecommerce/services/gcp_auth.ail` + `demos/streaming/gemini_live/services/gcp_auth.ail` (98% identical code)

### sunholo/auth
Pure functions for API key management. SHA-256 hashing with constant-time comparison (prevents timing attacks), bearer token extraction from Authorization headers, key format validation.

**Extracted from:** `docparse/services/api_keys.ail` (key validation logic)

### sunholo/http-helpers
Eliminates the repeated pattern of building Bearer auth headers and parsing JSON responses that appears in every project making API calls.

**Extracted from:** Common patterns across `claude_haiku_call.ail`, `bigquery.ail`, `api_server.ail`

### sunholo/logging
Structured JSON logging to stdout. Every project currently writes `println("[Error] " ++ msg)` differently. This standardizes to JSON format that Cloud Run, Cloud Logging, and log aggregators can parse.

### sunholo/config
Environment variable loading with required/optional/default patterns. Replaces scattered `getEnvOr` calls with validated config loading.

### sunholo/testing-utils
Pure assertion functions returning `Result[string, string]` for test output. Provides assertEqual, assertContains, assertOk, assertErr, assertTrue.

## How It Works

AILANG packages use **path dependencies** (no registry needed). Each package has an `ailang.toml` manifest declaring its name, exports, effects, and dependencies.

```
my-project/
  ailang.toml           # your project manifest
  ailang.lock           # resolved deps (commit this)
  main.ail
ailang-packages/        # cloned alongside
  packages/
    gcp-auth/
    auth/
    ...
```

The `ailang.lock` file pins content hashes so builds are reproducible.

## Contributing

To add a package:

1. Create `packages/your-package/ailang.toml` with vendor/name format
2. Add `.ail` source files with `module vendor/name/module` declarations
3. List exported modules in `[exports].modules`
4. Declare max effects in `[effects].max`
5. Add `ai_summary` in `[metadata]` for agent discovery
6. Test with `ailang add --path` from a test project
