# sunholo/billing_entitlements

## When to use this package
Use for billing authorization decisions: checking if a user can parse, what their limits are, and computing usage deltas. This is the **pure policy core** — no network calls, no Firestore, no Stripe. Import this when you need to make capability decisions based on entitlement state.

## Quick start
```ailang
import pkg/sunholo/billing_entitlements/plan (lookupPlan, defaultCatalog, freePlan)
import pkg/sunholo/billing_entitlements/entitlement (resolveEntitlements, freeEntitlements)
import pkg/sunholo/billing_entitlements/capability_check (canParse, AllowDecision, Allow, Deny)
import pkg/sunholo/billing_entitlements/quota_policy (remainingPages, isNearLimit)
import pkg/sunholo/billing_entitlements/usage_policy (parseDelta, applyDelta, emptyUsage)

-- Resolve entitlements from subscription state
let sub = { status: "active", planKey: "pro_monthly", cancelAtPeriodEnd: false }
let ent = resolveEntitlements(sub, defaultCatalog(), "uid_123")

-- Check if a parse is allowed
let req = { fileSizeMb: 5, isApiRequest: true }
match canParse(ent, req, 412, 31) {
  Allow => -- proceed with parse
  Deny(reason) => -- reject with reason
}

-- Check quota status
let pages_left = remainingPages(ent, 412)  -- 4588
let near_limit = isNearLimit(ent, 4500)    -- true (>80%)

-- Compute usage delta after parse
let delta = parseDelta(12, 1048576, 3)
let new_usage = applyDelta(emptyUsage(), delta)
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `freePlan` | plan | `() -> Plan` | Free tier plan defaults |
| `lookupPlan` | plan | `([{key, plan}], string) -> Result[Plan, string]` | Find plan by key |
| `defaultCatalog` | plan | `() -> [{key, plan}]` | Standard plan catalog |
| `resolveEntitlements` | entitlement | `(SubscriptionState, catalog, principalId) -> Entitlements` | Derive capabilities from subscription |
| `freeEntitlements` | entitlement | `(principalId) -> Entitlements` | Free tier entitlements |
| `canParse` | capability_check | `(Entitlements, ParseRequest, pagesUsed, docsUsed) -> AllowDecision` | Authorization check |
| `canUseApi` | capability_check | `(Entitlements) -> bool` | API access check |
| `isOverPageLimit` | quota_policy | `(Entitlements, used) -> bool` | Page limit exceeded? |
| `remainingPages` | quota_policy | `(Entitlements, used) -> int` | Pages remaining |
| `isNearLimit` | quota_policy | `(Entitlements, pagesUsed) -> bool` | >80% quota used? |
| `applyDelta` | usage_policy | `(Usage, UsageDelta) -> Usage` | Apply usage delta |
| `parseDelta` | usage_policy | `(pages, bytes, ocrPages) -> UsageDelta` | Create delta from parse |
| `emptyUsage` | usage_policy | `() -> Usage` | Zero usage record |

## Common patterns
- Resolve entitlements once at request start, pass to all checks
- Use `freeEntitlements` as fallback when no subscription exists
- `canParse` checks file size, API access, and quota in one call
- Effects: **none** (pure package)
