# Sprint SOCIAL-DYNAMICS-0.1: reusable kernel and standalone experiments

**Status:** Implementation completed and validated 2026-10-09; independent final evaluation pending. Approved by Mark ("yep approved"); independent design round2 PASS.
**Design:** [social-dynamics-0.1.0.md](social-dynamics-0.1.0.md).
**Branch:** `sprint/social-dynamics-0.1` on approval, isolated packages clone.
**Deliverable:** `sunholo/social_dynamics` experimental 0.1.0 plus a reusable headless
experiment runner. No game build, live provider call or publication.
**Estimate:** 2,500 implementation/test/example LOC, 8 working days including review buffer.
**Risk:** medium/high: temporal boundary ordering and generated-input validation.

## Existing work and reuse

Base packages `2b3c9b2`; game integration inspected at `5bc4aff`. Current development
includes relativity 0.9/0.10, AG-UI, and game session audits. Their delivery history
shows incremental tested pure modules, but not a reliable measured LOC/day for this
new social subsystem. Capacity uses the prior ship plan's provisional 400 LOC/day,
with ~25% buffer; this is an estimate, not observed social-package velocity.

Registry audit 2026-10-09: `social`, `event`, `simulation`, `personality`. Inspected
AG-UI via `pkg info/docs`: agent lifecycle codec, not domain social simulation. Read
local decisions AGENT.md: effectful decision-model API, not required here. All four
milestones are `none`: fresh domain logic and stdlib, no new registry dependency.
Domain recipes/policies remain configuration in examples, not baked into the library.

AILANG binary: v0.52.0, bf2436a. **AILANG prompt version loaded: v0.16.6**.
`ailang docs package-authoring` and package-local skill read. Contract proofs, runtime
tests and static quality inventory must be reported separately.

## Milestones

| ID | Deliverable and files | LOC | Depends | Acceptance |
|---|---|---:|---|---|
| ✅ S1 | Manifest; `model.ail`, `indicators.ail`, `relationships.ail` and corresponding `_test.ail`; exported types, bounded IDs/values, directed evidence-gated reactions and host policy seams | 500 | — | AC1, AC2 |
| ✅ S2 | `tasks.ail`, `conditions.ail`, `engine.ail` and tests; reservations, completion/release, duration/recovery/cooldown, monotone clocks, ordered scheduling and bounded continuation | 700 | ✅ S1 | AC3–AC5 |
| ✅ S3 | `proposals.ail`, `wire.ail` and tests; structured social proposal/1, atomic current-state validation, actor permissions, canonical recording and idempotent replay | 650 | S1, S2 | AC3, AC6 |
| ✅ S4 | `examples/social-dynamics/` runner package, Makefile, configs/NDJSON inputs for ship and community, example tests; README/AGENT/CHANGELOG, `_smoke.ail`, parity/replay/quality evidence | 650 | S1–S3 | AC7–AC9 |

Examples have a local path dependency on `../../packages/social-dynamics`, never game
modules. Regenerate local locks from each package root. Source filenames are examples
of the planned implementation surface; module splitting can be simplified without
changing acceptance behaviour. Do not edit other package locks or registry pins.

## Day-by-day execution

1. S1 red/green: IDs, config bounds, separate consumer types and directed relationships.
2. Finish S1: evidence projection, actor policy limits and scalar contracts.
3. S2: task reservation/consumption/release and aggregate capacity controls.
4. Finish S2: one session clock, threshold lifecycle and partition/continuation controls.
5. S3: strict proposal codec, seven operation payloads and per-origin permissions.
6. Finish S3: staged transactions, duplicate precedence, bounded ledgers and failure controls.
7. S4: standalone runner, contrasting ship experiments and unrelated community example.
8. S4 quality/proofs/parity/timing evidence, independent evaluation and fixes.

S2 must reevaluate relevant condition rules after initialization and successful
apply/deliver transactions as well as scheduled boundaries; timer starts and cancellations
are derived from that committed state. This is the round-2 nonblocking implementation check.

No auto-progress on partial tests. Mark a feature passing only with its named acceptance
commands and evidence. No executor dispatch until approval is recorded. Review revision 1
narrows time semantics to one scheduler clock per session; external ordering is host input.

## Experiment runner syntax gate

| Module | Contracts | Effects | Inline tests |
|---|---|---|---|
| library pure exports | include: bounds preservation, refused-input state identity, conservation and declared invariants; report Z3 limitations | include: pure/empty rows, no wall clock or AI | include: valid/invalid/boundary native examples plus `_test` discovery |
| `examples/.../config.ail` | include: valid config IDs/ranges and supported policy names | include: pure | include: ship/community config validation |
| `examples/.../scenario.ail` | include: deterministic replay and final state/event invariants; complex proofs may be runtime-only | include: pure | include: differing choice paths and no-knowledge control |
| `examples/.../main.ail` | skip: effectful input/output wrapper, invariants tested in pure codecs/runner | include: `! {IO}`; fixture reads via stdin, finite recorded input; exact budgets only where bounded | skip: native tests target pure decoder/session functions; runner exercised as process |
| private package `_smoke.ail` | include: pure `smokeChecks` reports meaningful invariant checks | include: main `! {IO}` only to print boot verdict | include: checks plus explicit smoke execution |

## Validation and evidence

Proposed `make -f examples/social-dynamics/Makefile validate AILANG=$A` aggregates
library check, actual package/inline tests, strict-VM pure probes, example check/tests,
smoke, VM/interpreter trace parity, replay, quality and publication dry run. Report
real test totals/failures/skips and proved/unknown/skipped contracts; do not hide a
quality warning or confuse `--dry-run` with registry publication.

Targeted mutations must demonstrate killers for reverse-directed trust, unseen-evidence
reaction, repeated charge/completion, partial invalid proposal commit, ignored cooldown,
early threshold, reordered simultaneous boundary and stale-revision acceptance.
No arbitrary coverage percentage claim; acceptance invariants and controls are the gate.

Measure cold/warm standalone scenario timings and report them separately from native
tests; use the pinned AILANG interpreter and VM, without fetching sky assets or invoking Godot.

## Pause points and delivery

- P0: independent design reviewers resolve blocking objections, then Mark approves
  this concrete sprint scope. Game visibility and final authority mechanics stay open;
  example policies do not silently decide them.
- P1: S2 behaviour review using traces before widening generated-effect grammar.
- P2: independent package evaluation and quality evidence before merge/release proposal.
- P3: separate explicit permission to publish this new package; no standing relativity
  publication grant is transferred to it.

No live API spend or provider routing change. No game `ui/*`, demo, sim, navigation,
art, mission schedule or active package changes. Only new social package/example files
and their documentation are in scope after approval.

Execution evidence: [validation](evidence/validation.log), [strict native tests](evidence/strict-native-tests.json), [contracts](evidence/contracts.json), [mutation controls](evidence/mutations.json) and [evidence report](social-dynamics-validation.md). Milestones passed all named local acceptance gates. Package publication remains unauthorised.
