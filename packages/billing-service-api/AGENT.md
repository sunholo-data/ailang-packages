# sunholo/billing_service_api

## When to use this package
This is the **Cloud Run billing service** — deploy it with `ailang serve-api`. It provides HTTP endpoints for checkout, portal, proposals, webhooks, and entitlements. AI agents call proposal endpoints; frontend calls checkout/portal endpoints; Stripe calls the webhook endpoint.

## Quick start
```bash
# Deploy locally
ailang serve-api --caps Net,FS,Env,IO --port 8080 \
  packages/billing_service_api/*.ail

# Or on Cloud Run (via Dockerfile)
ailang serve-api --caps Net,FS,Env,IO --port 8080 \
  /app/billing_service_api/*.ail
```

## Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| `POST` | `/billing/checkout-session` | checkout_handler | Create Stripe Checkout session |
| `POST` | `/billing/portal-session` | portal_handler | Create Stripe Customer Portal |
| `POST` | `/billing/proposals` | proposal_handler | Create payment proposal |
| `POST` | `/billing/proposals/:id/approval-link` | proposal_handler | Generate approval link |
| `GET` | `/billing/proposals/:id` | proposal_handler | Get proposal status |
| `POST` | `/billing/webhooks/stripe` | webhook_handler | Receive Stripe webhooks |
| `GET` | `/billing/me/entitlements` | entitlements_handler | Get current entitlements |

## Environment variables
- `GOOGLE_CLOUD_PROJECT` — GCP project ID
- `FIRESTORE_DATABASE` — Firestore database name (set per product, e.g. `docparse`)
- `STRIPE_SECRET_KEY` — Stripe API secret key
- `STRIPE_WEBHOOK_SECRET` — Stripe webhook signing secret

## Common patterns
- All user-facing endpoints require Firebase Auth bearer token
- Webhook endpoint uses Stripe signature verification (no Firebase Auth)
- Proposals follow: create → approval-link → human approves → webhook confirms
- Effects: `--caps Net,FS,Env,IO`
