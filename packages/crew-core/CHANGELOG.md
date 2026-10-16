# Changelog

## 0.5.0

Resource units as data (Mark's repo-use review, 2026-10-15). The game had a
port of the crew lab's bubble table, made because the lab is never
published. The logic now lives here, and the table stays with each game's
scenarios.

- **New module `units`:** `UnitDef`, `UnitTable`, `Amount`, `Used`,
  `decodeUnits` (crew_units/1), `unitOf`, `allocate`, `lintPack`,
  `lintAgainstShip`, `usedOf`. It reproduces the game's port exactly: the same
  rounding and the same lint messages, word for word, for Stapledon's table.
  `decodeUnits` refuses a fractional `per` (std/json's `getInt` truncates).
  Tested on both engines and under the strict VM.
- **Contract fix:** `cohorts.years` gains the precondition its callers
  already meet (at most ten non-negative decade counts). Without it, the
  contract's sum claim was false for longer or negative lists. A generated
  property test found it.
- **Archiving no longer waits for the bank to fill.** An answered request
  stays in the bank for idempotent retries until it expires (one turn), and
  then can never be applied again. 0.4.x still counted it as holding its
  task, so with `keep` nothing answered was archived until the bank reached
  its limit of 64. Every request carries its crew member's visible evidence,
  so each auto-run decision grew with the session.
  - Found by the R2-CREW integration agent as step timeouts on a 1,201-tick
    leg: monthly decisions reached 750 ms.
  - Lab probe (last-messages-home, orders, cadence 30, keep 30), at day 300:
    evidence went from 203 to 23, knowledge from 332 to 32, tasks from 50 to
    5, and the bank from 60 to 6.
  - The cost per decision is now flat (about 21 ms to 730 days, where it
    grew from 20 to 64 ms), and a 292-day skip drops from 3.1 s to 1.7 s,
    with the same decisions.
  - `held` ignores expired bank entries, and archiving drops the bank
    entries of the tasks it archives. A retry of such an answer reports
    "unknown request", as for a bank entry that was already compacted.
  - New test: `archive_test` "answered work is folded away once its request
    expires". It fails on 0.4.1.
- Nothing else changes: the host wire, the journal and the saved recordings
  replay identically.

## 0.4.1

Auto-captain fixes for Stapledon's game profile (`watch-v3`). Found by the
R2-CREW integration agent and in the crew lab, 2026-10-14. The host wire is
unchanged (commands, journal records, outcome codes), and the saved
recordings replay identically.

- **Concerns no longer deadlock auto-play.** In 0.4.0, when a crew member
  replied with a concern, the auto-captain re-asked and re-offered the task
  every turn. The host refused each time, and nothing escalated: on the game's
  scenario, 130 errors in 30 days and 5 starts.
  - The auto-captain now never asks about or offers a task with an open
    concern; the worker waits on the captain.
  - New standing-order field `concerns`:
    - `escalate` (the default) raises `uncovered` once per opening of the
      concern;
    - an approach (`clear_scope`, `ask_advice`, `stage_plan`,
      `explain_priority`, `assert_authority`) replies once per concern with
      the host's suggested words, then hears the reconsideration. A concern
      reopened after that reply waits for its offer to lapse (20 ticks),
      and then the worker is offered work afresh.
  - An `uncovered` rule escalates even when the orders would reply.
  - Check-ins skip tasks with an open concern.
- **Moot concerns** (`session.moot`). A concern about a lapsed offer or about
  running work can no longer be answered. It no longer blocks offering that
  assignment again, and it no longer keeps the task from being archived.
- **Stuck guard.** The same host error (actor and text) three times in one
  `advanceAuto` call escalates `stuck`. A start blocked by a shortage is not
  counted.
- **Lapsed offers are stale at every cadence.** At cadence 1, 0.4.0 kept
  asking about them. Without archiving the worker stayed busy for good; with
  archiving, the host erred every turn (285 errors a year).
- **Hysteresis.** Breakdown, trust-floor and cohort rules re-arm only once
  the value is 10 back across the line. On the hands_on preset, a breakdown
  line at 70 had re-armed about 130 times a year.
- **Archiving folds personality receipts older than the window**, keeping any
  that an active response answers to. social_dynamics keeps 128 per crew
  member, so 21 to 27 years of replies filled them, and every later reply
  failed. The stuck guard found this in a century skip.
- **Tests:** 9 new (concerns, moot concerns, resume without an answer, auto-
  reply under both captains, the uncovered override, stuck, hysteresis,
  personality retention). The `morale` indicator was added to two test
  ships, whose crew could never answer before (the stuck guard showed it).
- **Lab (crew-lab):** `crew-sim --profile v2|v3` (v3 is the default with
  `--auto` or `--skip`) and `--concerns`. The gate claims on the game's
  scenario, both captains, a year at cadence 1 and 30: 0 host errors.
  Concerns under escalate: a median of 73 a year under consent and 57 under
  orders.

## 0.4.0

Cohorts for Stapledon's population (R2-CREW-POP CP-0, ledger D-73; about
1,000 aboard growing to about 1,500, D-75). Additive: a scenario without a
`cohorts` section behaves exactly as in 0.3.0, the six 0.2.0/0.3.0 parity
recordings replay byte-identically, and the snapshot gains `population`
only when cohorts exist.

- **New module `cohorts`.** A cohort holds counts, never individuals:
  people per mood band (content, uneasy, strained, breaking), per band of
  trust in the captain, and per year of age. Integer arithmetic only, so
  the VM and the interpreter agree bit for bit.
  - Moves between bands draw once per band, never per person: expected
    mode (default) rounds n·p; seeded mode draws per person below 13 and
    uses a normal approximation above. Cost does not grow with headcount.
  - Readouts: mean band, `division` (how split, 0..100) and `pressure`
    (strained and breaking, raised by low trust, 0..100).
  - Ship events are heard once by every cohort (major kinds by
    neuroticism; first contact also lifts open cohorts). Moods drift each
    week toward a target set by recent shocks, the voice's stress and
    shortages; trust drifts toward the voice's trust in the captain.
  - A yearly step: ageing, deaths by age band (fractions carried),
    births from adults aged 20-44 under the captain's `birth_policy`
    (encourage, hold, restrict), children joining departments at 18, and
    a department splitting off its ship-born once they are a quarter of
    it (16 groups at most). Births stop while a birth need is short.
  - **Birth policy is a source of tension** (Mark, 2026-10-13):
    restricting births costs trust and mood where many people are of
    child-bearing age, scaled by agreeableness and extraversion, for as
    long as the policy lasts; encouraging births while a birth need is
    short costs trust with the conscientious.
  - Default rates per mille of fertile adults a year: encourage 70, hold
    48, restrict 20, calibrated on the Stapledon founders pack. The first
    draft (60/30/8) was below replacement and the ship died out.
- **Session:** `birth_policy` and `depart` commands; cohorts catch up on
  every advance (365 ticks a year). `depart` (death, breakdown or left)
  promotes someone from the role's cohort: the role id stays (D-70 OQ2),
  the person is new (`<cohort>-p<n>`, named by the host, D-74), their work
  stops, traits come from the cohort mix plus a seeded offset. The trace
  carries a `promoted` record.
- **Auto-captain:** escalation rule kind `cohort` (indicator `pressure`
  or `division`, threshold 0..100), once per crossing per cohort.
- **Scenario:** optional top-level `cohorts` section (1-15 groups plus
  children), validated with the field named.

Measured (v0.54.8 strict VM, Apple silicon, lab founders pack: 1,000 aboard
in 10 departments plus children, five featured crew; 10-year skip at
cadence 30 with keep 30, seed 1):

| Run | Time |
|---|---|
| founders, no cohorts section | 19.6 s |
| founders, 1,000 people | 20.1-20.2 s |
| founders ×100, 100,000 people | 20.4 s |

Cohorts cost about 0.6 s a decade, the same at 1,000 or 100,000 people.
Pack claims (crew-lab, claims written before the runs; 18 of 18 hold over
seeds 1..3, split over 1..20): a calm year, the century (1,643 at year 100 under hold, the
top of D-75's band), births stop when the beds go dark, restricting births
escalates a cohort within ten years, a split cohort escalates and a
uniformly uneasy one does not. Two findings on the way: the restrict claim
first failed because the yearly grievance drifted away within weeks (fixed:
the grievance holds while the policy does), and decade skips without
archiving hit the 256-task cap (long claims run with keep 30, as the game
does). Observation for scenario design: ten years of restrict brought
births to zero in every run, because the grievance also sours moods.

## 0.3.0

For Stapledon's crew integration (R2-CREW CI-0; ailang-packages#137).
Existing commands, journal records and outcome codes are unchanged.
- 0.2.0 recordings replay byte-identically.
- The lab's consent and orders captains give byte-identical crew-sim output,
  checked to 80 turns.
- New features are opt-in.

- **`policy` command:** switch consent and orders mid-session, journalled
  (`Session.command`). The engine configuration keeps its founding policy,
  and the snapshot shows `command` once it differs.
- **`ship_event` command:** raise a ship event now. It joins the session's
  event list at the current tick and fires through the same path as a
  scheduled event, an advance to the current tick (see ailang#1812).
- **Archiving** (opt-in: start line `"keep": 1..10000`).
  - Folded away when older than keep: finished work and lapsed offers, with
    their agreements, reports, reliefs, evidence (including evidence caused by
    them), closed conversations and knowledge; and ship events, with their
    evidence and arguments (their ids are kept, so they never refire).
  - `completedCount` stays exact.
  - Only open conversation issues hold work.
  - The operation log keeps its newest 512 entries. Older operation ids
    leave the duplicate check, which matters only for hand-written
    recordings.
  - Without archiving, a busy session hits the 256-commitment cap near
    turn 290.
- **New module `auto`, the auto-captain.** It is opt-in: `session` does not
  import it.
  - `crew_standing_orders/1`: start agreed|always, rest tired|never, relief
    grant|deny|strained, a tired threshold, cadence 1..365.
  - `crew_escalation/1` rules:
    - refusal_under_orders;
    - breakdown and trust_floor, each once per crossing and re-armed on
      recovery;
    - major, read from the event list;
    - argument;
    - uncovered: an open conversation issue only the captain can answer.
  - `advanceAuto(session, AutoState, responses, orders, rules, n)` runs turns
    with the same host commands as a player and stops at the first
    escalation. From the second call on, `AutoState.calls` salts request ids,
    so a resume never reuses one.
  - At a cadence above 1, offers whose agreement fell due no longer occupy
    the worker.
  - `decideTurn` and `finishTurn` count escalations instead of stopping
    (lab).
- **Faster host identity check:** a structural comparison replaces three
  config encodings per host call.

Performance, measured on the crew lab's default ship, consent, no escalation
rules, archive 30, one seed:
- 500 turns take 28.5 s, linear.
- A 10-year skip (3,650 ticks) takes 1.8 s at yearly cadence, 16.8 s monthly,
  55 s weekly, and about 30 min daily.
- Each decision costs roughly 25 ms, much of it VM list-tail copying
  (ailang#1814).
- With escalation rules, a skip stops at the first escalation, so its length
  is not a fixed time.
- A cold compile peaks around 10 GB for `session` and 14 GB for `auto`
  (ailang#1812).

## 0.2.0

Crew strain (design `design_docs/planned/crew-strain.md`). Requires
`social_dynamics` 0.4.0.

- **Crew argue over lost capacity.** A ship event can take more than is
  available while running work holds the rest. The holders then take stances
  from their traits: hold score = (100 − A) + E/2 + C/2, plus 15 when
  overextended.
  - The least assertive are halted first (`social_dynamics` `halt`).
  - A halted crew member gains stress 5 + N/10.
  - One who held their ground loses regard for the colleagues who kept
    working. One who yielded gains +1 regard from them.
  - The argument is crew evidence `sf-<event>-<n>`.
  - Scenarios with events give crew a `regard` relationship (0..100, from 50).
- **Trust by personality.** New outcomes `complied_start` (a yes under
  orders) and `strained_start` (a yes while overextended). `traitDelta`
  scales every outcome's trust change by OCEAN traits and stress. Examples:
  - a strained yes: diplomat −1, engineer −2, skeptic −4;
  - an overridden refusal: −4 at A100 down to −12 at A0.
- **Strain in the response policy.** An optional `strain` block
  (`{indicator, threshold, shift}`) moves weight from accept and continue to
  decline and request_relief while the crew member is overextended, scaled by
  neuroticism. Policies without it are unchanged.
- The `sf-` id prefix is reserved for flows.
- **Behaviour change for orders runs.** Crew with OCEAN traits now get
  personal trust deltas, so orders sessions recorded on 0.1.0 replay to
  different trust values:
  - a "yes" under orders is `complied_start`, worth 2 − voice;
  - an overridden refusal costs −4 to −12, not a flat −8;
  - a denied relief costs −(2 + N/25), not −4.

  Consent sessions are unchanged. `session_test` pins the new values.

## 0.1.0

First release, split out of the local crew-lab example (S-CREW-CORE-SPLIT). A pure
captain/crew host for social and narrative games on `social_dynamics`:

- `scenario`: decode and validate `crew_scenario/1` JSON (captain and crew, OCEAN
  traits, priorities, starting indicators, offered work with held and spent
  supplies and bounded effects, rest, overextension, trust in the captain,
  supplies); `config(scenario, policy)`; `scenarioHash` (canonical sha256).
- `session`: the host. `start(scenario, line)`, `offer`, `ask`, `complete`,
  `startTask`, `resolve`, `cancel`, `captainReply`, `input` (NDJSON commands) and
  `recording`. Consent or orders, agreements, relief, conversations, gradual
  personality, atomic failures. `untraced(s)` skips per-call trace encoding for
  batch runs (same states, about 3x faster).
- `policy`: the authored response policy (`crew_response_policy/1`), reaction
  weights, `chooseReaction` and `authoredAnswer` (reaction plus answer body).
- `host_policy`, `actor_policy`, `personality_host`, `conversations`, `codec`.
- `example`: the five-specialist first-contact ship (generated from crew-lab's
  `data/watch-scenario.json`).

Long sessions: the answer bank keeps 64 answers for idempotent retries; when full,
answers to expired requests (which can never be retried) are dropped first, so a
session can run for many turns (60-turn crew-sim runs are clean). Scenario limits:
256 tasks, commitments and reliefs, 2048 evidence, 8192 knowledge. `callLimit` in
`crew_response_policy/1` is 0..64; the watch policy default is 12.

The public API is pure and deterministic. Known limits: the captain's id must be
`captain`; finished tasks are never archived, so runs slow down as they grow (one
seed: 12 turns about 1 s, 60 about 8 s, 120 about 40 s); conversation prompts are
still keyed by role in code.

Also in this first release:

- **Resource flows (S-CREW-BUBBLE-RESOURCES).** Optional fields in
  `crew_scenario/1`, so existing scenarios decode and replay unchanged:
  - resource `kind` (stock or capacity; a capacity is never consumed);
  - work `yields`;
  - top-level ship `events`, which move units at a tick and are heard by the
    whole crew.
- `scenario`: `Transfer`, `ShipEvent`, `Yield`, `resourceKind` and `yieldsOf`.
- `session`: applies due yields, then due events, after each completed advance.
- New module `flows`: balanced transfers (`transfer`, `transferAll`,
  `appliedDelta`, `balanced`). An outward transfer never takes reserved units.
  `social_dynamics` is unchanged; transfers use its existing
  `transferredIn` and `transferredOut` books.
