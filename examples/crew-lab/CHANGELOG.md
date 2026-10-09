# Changelog

## 0.1.0

Adds an independent captain-and-crew CLI experiment using saved synthetic typed
decisions, explicit confidence gates and sampling rolls, actor-local perception,
personal work agreements, captain assignment and relief, bounded request retention
and directed trust consequences on receipt. Five contrasting recordings demonstrate
completion, refused orders, care, denied relief and competing materials.

The library and host transitions remain pure; only stdin/output use IO. Includes
strict response/command controls, native tests, saved replay, pure strict-VM parity,
temporary `[bin]` installation tests and package quality commands. Requires the
pinned AILANG0.52.0 runtime for the documented checks. Strict VM replay uses the
pure recording entry because stdin `readLine` is evaluator-only on that runtime.
No live decisions, provider costs, game integration or registry publication.
Completion-only project effects and full reservation refunds on stop remain
explicit limitations; no partial-work economics or moral winner is introduced.

Received trust deltas are illustrative fixed fixture rules; traits and values enter
request context, with trait-dependent appraisal deferred. Proof evidence reports
5/28 verified,22skipped and one unsupported function-record encoding; runtime
contracts remain active. No isolated publish smoke is claimed for the unpublished
path dependency. A scoped CI job runs the crew and original social lab checks.

Adds `[bin] crew-view` and `make view` for readable per-step interior state, sharing
the same pure host and saved decisions with the full JSON CLI.
