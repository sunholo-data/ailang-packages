# sunholo/billing_entitlements

## When to use this package
Use for billing authorization decisions: checking if a user can perform an action, what their limits are, and computing usage deltas. This is the **pure policy core** — no network calls, no Firestore, no Stripe. Import this when you need to make capability decisions based on entitlement state.

**Plan values are config-driven**: set `BILLING_PLAN_CATALOG` env var with a JSON array of plans. No business logic is hardcoded in this package.

## Quick start
```ailang
import pkg/sunholo/billing_entitlements/plan (lookupPlan, parseCatalog, fallbackPlan, freePlanFromCatalog)
import pkg/sunholo/billing_entitlements/entitlement (resolveEntitlements, freeEntitlements)
import pkg/sunholo/billing_entitlements/capability_check (canParse, AllowDecision, Allow, Deny)
import pkg/sunholo/billing_entitlements/quota_policy (remainingPages, isNearLimit)
import pkg/sunholo/billing_entitlements/usage_policy (parseDelta, applyDelta, emptyUsage)

-- Load plan catalog from config (env var)
let catalog = parseCatalog(getEnvOr("BILLING_PLAN_CATALOG", "[]"))

-- Resolve entitlements from subscription state
let sub = { status: "active", planKey: "pro_monthly", cancelAtPeriodEnd: false }
let ent = resolveEntitlements(sub, catalog, "uid_123")

-- Check if an operation is allowed
let req = { fileSizeMb: 5, isApiRequest: true }
match canParse(ent, req, 412, 31) {
  Allow => -- proceed
  Deny(reason) => -- reject with reason
}

-- Fall back to free tier when no subscription exists
let freeEnt = freeEntitlements("uid_456", catalog)
```

## Config format (BILLING_PLAN_CATALOG)
```json
[
  {"key": "free", "name": "free", "monthlyPageLimit": 500, "monthlyDocumentLimit": 50, "maxFileSizeMb": 10, "apiAccess": true, "maxConcurrentJobs": 1},
  {"key": "pro_monthly", "name": "pro", "monthlyPageLimit": 10000, "monthlyDocumentLimit": 1000, "maxFileSizeMb": 50, "apiAccess": true, "maxConcurrentJobs": 5}
]
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `parseCatalog` | plan | `(json: string) -> [{key, plan}]` | Parse JSON config into plan catalog |
| `fallbackPlan` | plan | `() -> Plan` | Minimal safe fallback (1 page, no API) |
| `freePlanFromCatalog` | plan | `(catalog) -> Plan` | Look up "free" plan, fall back to fallbackPlan |
| `lookupPlan` | plan | `(catalog, key) -> Result[Plan, string]` | Find plan by key |
| `resolveEntitlements` | entitlement | `(SubscriptionState, catalog, principalId) -> Entitlements` | Derive capabilities from subscription |
| `freeEntitlements` | entitlement | `(principalId, catalog) -> Entitlements` | Free tier entitlements from config |
| `canParse` | capability_check | `(Entitlements, ParseRequest, pagesUsed, docsUsed) -> AllowDecision` | Authorization check |
| `canUseApi` | capability_check | `(Entitlements) -> bool` | API access check |
| `isOverPageLimit` | quota_policy | `(Entitlements, used) -> bool` | Page limit exceeded? |
| `remainingPages` | quota_policy | `(Entitlements, used) -> int` | Pages remaining |
| `isNearLimit` | quota_policy | `(Entitlements, pagesUsed) -> bool` | >80% quota used? |
| `applyDelta` | usage_policy | `(Usage, UsageDelta) -> Usage` | Apply usage delta |
| `parseDelta` | usage_policy | `(pages, bytes, ocrPages) -> UsageDelta` | Create delta from parse |
| `emptyUsage` | usage_policy | `() -> Usage` | Zero usage record |

## Common patterns
- Load catalog once from `BILLING_PLAN_CATALOG` env var at request start
- Resolve entitlements once, pass to all checks
- Use `freeEntitlements(id, catalog)` as fallback when no subscription exists
- `canParse` checks file size, API access, and quota in one call
- Effects: **none** (pure package — config loading is the caller's responsibility)
