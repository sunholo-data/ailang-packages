# AILANG Packages

Curated AILANG packages for production use. Extracted from real projects (docparse, e-commerce demos, streaming agents) to eliminate duplication and provide tested, reusable modules.

This is a **monorepo** — multiple packages live in one repository. Each package in `packages/` has its own `ailang.toml` manifest. You can depend on individual packages via registry versions, path deps, or git deps with `subdir`. For authoring, read [AGENTS.md](AGENTS.md) and run `ailang docs package-authoring` (see the [package skill](.agents/skills/ailang-packages/SKILL.md) for older binaries).

## Quick Start

### Registry dependencies (recommended for published packages)

Use `ailang install sunholo/auth@latest` to resolve a published release to an exact
version, then `ailang lock`. Not every package/version in this checkout has been
published; check `ailang search` and `ailang pkg info sunholo/auth` first.

### Git dependency (for versions available only in git)

```bash
ailang init package --name myorg/myapp
ailang add --git https://github.com/sunholo-data/ailang-packages --subdir packages/auth --tag main
ailang lock
```

### Clone + path dependency (for local development)

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
| [sunholo/deontic](packages/deontic/) | Verified contract reasoning: obligations, notice-and-cure, waiver, force majeure, termination — pure event fold with Z3-proved settlement math | Pure (IO in demo only) | [Guide](packages/deontic/AGENT.md) |

### Billing Packages (DocParse)

| Package | Description | Effects | AGENT.md |
|---------|-------------|---------|----------|
| [sunholo/billing_entitlements](packages/billing-entitlements/) | Plan catalog, entitlement resolution, quota checks, usage deltas | Pure | [Guide](packages/billing-entitlements/AGENT.md) |
| [sunholo/billing_proposals](packages/billing-proposals/) | Payment proposal lifecycle for AI-assisted and human billing | Pure | [Guide](packages/billing-proposals/AGENT.md) |
| [sunholo/billing_store](packages/billing-store/) | Firestore CRUD for billing records (customers, subscriptions, usage) | Net, FS, Env | [Guide](packages/billing-store/AGENT.md) |
| [sunholo/billing_stripe](packages/billing-stripe/) | Stripe adapter: checkout, portal, webhooks, event mapping | Net, Env | [Guide](packages/billing-stripe/AGENT.md) |
| [sunholo/billing_service_api](packages/billing-service-api/) | HTTP handlers for billing Cloud Run service | Net, FS, Env, IO | [Guide](packages/billing-service-api/AGENT.md) |
| [sunholo/external_backend](packages/external-backend/) | Run external subprocesses that emit JSON; typed Result errors with stderr capture | Process | [Guide](packages/external-backend/AGENT.md) |

## Discord and agent/UI protocols (local development)

| Package | Purpose |
|---|---|
| [sunholo/discord](packages/discord/AGENT.md) | Bot REST v10 client, messages, replies, pagination and structured errors |
| [sunholo/agui](packages/agui/AGENT.md) | Pure AG-UI event codecs and sequential run validation |
| [sunholo/a2ui](packages/a2ui/AGENT.md) | Existing component builders plus additive A2UI 0.9.1 envelopes/review surfaces |

These changes are developed against the local `ailang-demos/discord` CLI/MCP app.
New versions are not yet registry releases. Use path dependencies during development.
The demo contains the cross-package and upstream schema/SDK integration suite.

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

Dependency modes:
- **Registry deps** — published versions pinned in the manifest and lockfile
- **Path deps** (`{ path = "../..." }`) — local, for development
- **Git deps** (`{ git = "url", subdir = "...", tag = "..." }`) — remote, version-pinned

## Contributing

To add a package:

1. Create `packages/your-package/ailang.toml` with `sunholo/name` format
2. Add `.ail` source files with `module sunholo/name/module` declarations
3. **Use underscores** in module paths (not hyphens): `sunholo/billing_store`, not `sunholo/billing-store`
4. **Use `export type`** for any types other packages will use: `export type MyRecord = { ... }`
5. **Use `./`** for sibling modules in the same package and **`pkg/`** for external package imports
6. List exported modules in `[exports].modules`
7. Declare max effects in `[effects].max`
8. Add `ai_summary` in `[metadata]` for agent discovery
9. Write `AGENT.md` with usage guide for AI agents
10. **Validate**: `ailang lock`, `ailang check --package .`, `ailang test --package .`, and `ailang pkg quality --strict .` (requires a binary with the quality command). Run inline tests in their source files too; package test discovery targets `*_test.ail` files. Review actual test counts and skips.
11. Add meaningful `requires`/`ensures`, native tests/properties, and effect budgets where applicable. A quality inventory reports evidence gaps; it does not execute tests or prove contracts.
12. Test with `ailang add --path` or `ailang add --git` from a test project

### Critical Conventions

```ailang
-- Module names use underscores (directory can have hyphens)
module sunholo/billing_store/customers_repo

-- Import Ok/Err explicitly (not in prelude)
import std/result (Ok, Err)

-- Use ./ for siblings in SAME package (preferred)
import ./entitlements_repo (getEntitlements)

-- Use pkg/ for EXTERNAL package dependencies
import pkg/sunholo/firestore/client (getDoc, setDoc)

-- Export types that other packages will reference
export type Customer = { name: string, email: string }
```

Before publishing, run the relevant runtime/integration and contract verification checks. `ailang publish --dry-run` creates and validates packaging locally; it does not run the remote validator or replace those checks. Publish dependencies before dependents when releasing new versions.
