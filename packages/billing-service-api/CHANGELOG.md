# Changelog

## 0.5.10

Builds again on current AILANG. 0.5.9 depended on `sunholo/billing_store` 0.9.3, which pulled in the
broken `sunholo/firestore` 0.7.2 (`STRICT_FALLBACK_001`), so every handler failed to compile. This
release depends on billing_store 0.9.4. The handlers are unchanged.
