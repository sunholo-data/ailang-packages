# sunholo/billing_stripe

## When to use this package
Use when you need to interact with the Stripe API: creating checkout sessions, customer portal sessions, verifying webhooks, or mapping Stripe events to internal state. This is the Stripe-specific adapter — all Stripe coupling lives here.

## Quick start
```ailang
import pkg/sunholo/billing_stripe/stripe_customer (createStripeCustomer)
import pkg/sunholo/billing_stripe/stripe_checkout (createCheckoutSession)
import pkg/sunholo/billing_stripe/stripe_portal (createPortalSession)
import pkg/sunholo/billing_stripe/stripe_webhook (verifyWebhook, VerifiedEvent)
import pkg/sunholo/billing_stripe/stripe_event_mapper (mapEventToStateChange)

-- Create customer
match createStripeCustomer("user@example.com", "uid_123") {
  Ok(customerId) => -- "cus_..."
  Err(e) => -- Stripe error
}

-- Create checkout session
match createCheckoutSession("cus_123", "price_pro_monthly", successUrl, cancelUrl, "uid_123") {
  Ok(session) => -- session.url for redirect
  Err(e) => -- error
}

-- Verify webhook
match verifyWebhook(signatureHeader, rawBody) {
  Ok(event) => -- event.eventType, event.data
  Err(e) => -- invalid signature
}
```

## Environment variables
- `STRIPE_SECRET_KEY` — Stripe API secret key (required)
- `STRIPE_WEBHOOK_SECRET` — Stripe webhook signing secret (required for webhook verification)

## Exported functions

| Function | Module | Signature | Description |
|----------|--------|-----------|-------------|
| `createStripeCustomer` | stripe_customer | `(email, principalId) -> Result[string, string] ! {Net, Env}` | Create Stripe customer |
| `createCheckoutSession` | stripe_checkout | `(customerId, priceId, successUrl, cancelUrl, principalId) -> Result[CheckoutSession, string] ! {Net, Env}` | Create checkout session |
| `createPortalSession` | stripe_portal | `(customerId, returnUrl) -> Result[string, string] ! {Net, Env}` | Create portal session |
| `verifyWebhook` | stripe_webhook | `(signature, body) -> Result[VerifiedEvent, string] ! {Env}` | Verify webhook signature |
| `mapEventToStateChange` | stripe_event_mapper | `(eventType, data) -> Result[SubscriptionStateChange, string]` | Map event to state change |

## Common patterns
- All Stripe calls use form-encoded bodies (Stripe convention, not JSON)
- Webhook verification uses HMAC-SHA256 with constant-time comparison
- Effects: `--caps Net,Env` (Net for API calls, Env for secret key)
