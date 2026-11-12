# Changelog

## 0.5.11

The handlers' `requires` clauses use the string length the module imports: `checkout_handler`, `portal_handler` and `entitlements_handler` import `length`, and `proposal_handler` and `webhook_handler` call their existing `strLength` alias. Depends on billing_entitlements 0.4.3, billing_proposals 0.3.3, billing_store 0.9.5 and billing_stripe 0.1.7. The handlers are unchanged.

Earlier AILANG releases never type-checked `requires`/`ensures` clauses, so these mistakes compiled. sunholo-data/ailang#2283 type-checks them. Once it ships, every program that imports this package would fail to compile. The fix also compiles on the current release, v0.60.2.

## 0.5.10

Builds again on current AILANG. 0.5.9 depended on `sunholo/billing_store` 0.9.3, which pulled in the
broken `sunholo/firestore` 0.7.2 (`STRICT_FALLBACK_001`), so every handler failed to compile. This
release depends on billing_store 0.9.4. The handlers are unchanged.
