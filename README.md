# AILANG Packages

Curated AILANG packages for production use. Extracted from real projects (docparse, ecommerce demos, streaming agents) to eliminate duplication and provide tested, reusable modules.

This is a **monorepo** — multiple packages live in one repository. Each package in `packages/` has its own `ailang.toml` manifest. You can depend on individual packages via path deps or git deps with `subdir`.

## Quick Start

### Option 1: Git dependency (recommended — version pinned)

```bash
ailang init package --name myorg/myapp
ailang add --git https://github.com/sunholo-data/ailang-packages --subdir packages/auth --tag main
ailang lock
```

### Option 2: Clone + path dependency (for local development)

```bash
git clone https://github.com/sunholo-data/ailang-packages.git
cd my-project
ailang add --path ../ailang-packages/packages/auth
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

| Package | Description | Effects | AGENT.md |
|---------|-------------|---------|----------|
| [sunholo/gcp-auth](packages/gcp-auth/) | GCP ADC OAuth2 token exchange, project detection | FS, Net | [Guide](packages/gcp-auth/AGENT.md) |
| [sunholo/auth](packages/auth/) | API key validation, HMAC hashing, bearer token extraction | Pure | [Guide](packages/auth/AGENT.md) |
| [sunholo/http-helpers](packages/http-helpers/) | HTTP request builders, auth headers, JSON response parsing | Net | [Guide](packages/http-helpers/AGENT.md) |
| [sunholo/logging](packages/logging/) | Structured JSON logging (Cloud Run friendly) | IO | [Guide](packages/logging/AGENT.md) |
| [sunholo/config](packages/config/) | Config loading from env vars with validation | Env | [Guide](packages/config/AGENT.md) |
| [sunholo/testing-utils](packages/testing-utils/) | Test assertion helpers (assertEqual, assertOk, etc.) | Pure | [Guide](packages/testing-utils/AGENT.md) |
| [sunholo/firestore](packages/firestore/) | Firestore REST API client — CRUD, queries, field encoding | Net, FS, Env | [Guide](packages/firestore/AGENT.md) |

### Billing Packages (DocParse)

| Package | Description | Effects | AGENT.md |
|---------|-------------|---------|----------|
| [sunholo/billing_entitlements](packages/billing-entitlements/) | Plan catalog, entitlement resolution, quota checks, usage deltas | Pure | [Guide](packages/billing-entitlements/AGENT.md) |
| [sunholo/billing_proposals](packages/billing-proposals/) | Payment proposal lifecycle for AI-assisted and human billing | Pure | [Guide](packages/billing-proposals/AGENT.md) |
| [sunholo/billing_store](packages/billing-store/) | Firestore CRUD for billing records (customers, subscriptions, usage) | Net, FS, Env | [Guide](packages/billing-store/AGENT.md) |
| [sunholo/billing_stripe](packages/billing-stripe/) | Stripe adapter: checkout, portal, webhooks, event mapping | Net, Env | [Guide](packages/billing-stripe/AGENT.md) |
| [sunholo/billing_service_api](packages/billing-service-api/) | HTTP handlers for billing Cloud Run service | Net, FS, Env, IO | [Guide](packages/billing-service-api/AGENT.md) |
| [sunholo/docparse_access_gate](packages/docparse-access-gate/) | Entitlement enforcement and usage recording for DocParse | Net, FS, Env | [Guide](packages/docparse-access-gate/AGENT.md) |

## AGENT.md — AI Discovery

Each package includes an `AGENT.md` file — a structured guide for AI agents explaining:
- **When to use** the package
- **Quick start** code example
- **Exported functions** table with signatures
- **Common patterns** and integration advice

AI agents: read the `AGENT.md` for any package you add as a dependency.

## Monorepo Structure

This repo contains multiple packages. Use `subdir` to select specific packages:

```
ailang-packages/
  packages/
    auth/           # sunholo/auth
    gcp-auth/       # sunholo/gcp-auth (depends on auth)
    http-helpers/   # sunholo/http-helpers
    logging/        # sunholo/logging
    config/         # sunholo/config
    testing-utils/  # sunholo/testing-utils
    firestore/      # sunholo/firestore
    billing-entitlements/  # sunholo/billing_entitlements
    billing-proposals/     # sunholo/billing_proposals
    billing-store/         # sunholo/billing_store
    billing-stripe/        # sunholo/billing_stripe
    billing-service-api/   # sunholo/billing_service_api
    docparse-access-gate/  # sunholo/docparse_access_gate
```

### Using git deps with subdir

```toml
[dependencies]
"sunholo/auth" = { git = "https://github.com/sunholo-data/ailang-packages", subdir = "packages/auth", tag = "main" }
"sunholo/logging" = { git = "https://github.com/sunholo-data/ailang-packages", subdir = "packages/logging", tag = "main" }
```

The AILANG package system supports multiple packages per repo via the `subdir` field. You don't need one repo per package.

## How It Works

Each package has an `ailang.toml` manifest declaring its name, exports, effects, and dependencies. The `ailang.lock` file pins content hashes for reproducible builds.

Two dependency modes:
- **Path deps** (`{ path = "../..." }`) — local, for development
- **Git deps** (`{ git = "url", subdir = "...", tag = "..." }`) — remote, version-pinned

## Contributing

To add a package:

1. Create `packages/your-package/ailang.toml` with vendor/name format
2. Add `.ail` source files with `module vendor/name/module` declarations
3. List exported modules in `[exports].modules`
4. Declare max effects in `[effects].max`
5. Add `ai_summary` in `[metadata]` for agent discovery
6. Write `AGENT.md` with usage guide for AI agents
7. Test with `ailang add --path` or `ailang add --git` from a test project
