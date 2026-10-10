# Changelog

## 0.3.0

Add a pure personality sidecar with receipt-bound major-event responses. OCEAN
traits move only over simulation time, at most one point per trait per turn,
within individual baseline and world bounds. Ordinary perceived interactions
can influence an active response but cannot initiate one. Exact retries are
idempotent; altered receipts, rewinds and full retention return typed errors.

## 0.2.0

Breaking: Effect adds opt-in BoundedIndicatorDelta. Checked arithmetic and reference/observer ownership gates remain; only a valid configured indicator result saturates at its bounds. Existing IndicatorDelta and wire tags are unchanged.

## 0.1.0

Experimental pure social dynamics kernel: bounded domain indicators, directed
relationships and evidence-gated appraisal, explicit project offers/assignments,
conserved materials and work allocations, individual commitment consent, hysteresis
conditions, deterministic scheduling/continuations, immutable configuration,
atomic proposals and strict canonical recordings. Standalone ship and community
experiments live in `examples/social-dynamics`. No provider calls or game coupling.
