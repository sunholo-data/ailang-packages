# sunholo/billing_store

## When to use this package
Use when you need to read or write billing records to Firestore. This package provides typed CRUD operations for all billing collections in the `docparse` Firestore database. Built on `sunholo/firestore` for Firestore operations.

## Quick start
```ailang
import pkg/sunholo/billing_store/entitlements_repo (getEntitlements, putEntitlements)
import pkg/sunholo/billing_store/customers_repo (getCustomer, putCustomer)
import pkg/sunholo/billing_store/usage_repo (getUsage, putUsage)
import pkg/sunholo/billing_store/proposals_repo (getProposal, putProposal)
import pkg/sunholo/billing_store/events_repo (isEventProcessed, recordEvent)

-- Read entitlements
match getEntitlements("uid_123") {
  Ok(ent) => -- use ent.plan, ent.canParse, etc.
  Err(e) => -- not found or error
}

-- Check webhook idempotency
match isEventProcessed("evt_stripe_123") {
  Ok(true) => -- skip, already processed
  Ok(false) => -- process event
  Err(e) => -- Firestore error
}
```

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `getCustomer` | customers_repo | `string -> Result[Customer, string] ! {Net, FS, Env}` | Get by principal ID |
| `putCustomer` | customers_repo | `Customer -> Result[(), string] ! {Net, FS, Env}` | Create or update |
| `getSubscription` | subscriptions_repo | `string -> Result[Subscription, string] ! {Net, FS, Env}` | Get by principal ID |
| `putSubscription` | subscriptions_repo | `Subscription -> Result[(), string] ! {Net, FS, Env}` | Create or update |
| `getEntitlements` | entitlements_repo | `string -> Result[Entitlements, string] ! {Net, FS, Env}` | Get by principal ID |
| `putEntitlements` | entitlements_repo | `Entitlements -> Result[(), string] ! {Net, FS, Env}` | Create or update |
| `getUsage` | usage_repo | `(string, string) -> Result[Usage, string] ! {Net, FS, Env}` | Get by principal+period |
| `putUsage` | usage_repo | `(string, string, Usage) -> Result[(), string] ! {Net, FS, Env}` | Write usage |
| `getProposal` | proposals_repo | `string -> Result[Proposal, string] ! {Net, FS, Env}` | Get by proposal ID |
| `putProposal` | proposals_repo | `Proposal -> Result[(), string] ! {Net, FS, Env}` | Create or update |
| `isEventProcessed` | events_repo | `string -> Result[bool, string] ! {Net, FS, Env}` | Idempotency check |
| `recordEvent` | events_repo | `BillingEvent -> Result[(), string] ! {Net, FS, Env}` | Log processed event |

## Dependencies
- `sunholo/firestore` — Firestore REST API client (CRUD, field encoding)

## Environment variables
- `GOOGLE_CLOUD_PROJECT` — GCP project ID (required)
- `FIRESTORE_DATABASE` — Firestore database name (default: `(default)`)

## Common patterns
- Uses `sunholo/firestore` for all Firestore operations (no direct REST calls)
- `usage_repo` uses subcollections via `getSubDoc`/`setSubDoc`
- Returns `Ok(emptyUsage())` for missing usage documents (lazy init)
- Effects required: `--caps Net,FS,Env`
