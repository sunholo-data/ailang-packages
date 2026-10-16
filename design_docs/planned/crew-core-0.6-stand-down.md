# crew_core 0.6: stand down at the check-in

**Status:** Approved 2026-10-16 by Mark, attended ("yep agree with planners
recommendations proceed"). In progress (sprint S-CREW-CORE-0.6).
**Packages:**
- `sunholo/crew_core` 0.6.0 (minor; builds on 0.5.1, PR #149, merged as 100d8fd and published);
- `sunholo/social_dynamics` 0.4.0, unchanged (no engine change);
- `sunholo/crew_lab` (local only, never published).

**Follows:** crew_core 0.5.1 (#149, `fix/crew-core-0.5.1-checkin`). This plan
branches from it, so it merges after #149.

**Ruling:** Mark, attended 2026-10-16, "a is fine". At each auto-run check-in
(the game's monthly decision, D-76 cadence 30 on a long crossing), a crew
member under strain may ask to stand down, whether or not they are working on
a task at that moment. He chose this over two alternatives:
- (b) make the game's jobs weeks long;
- (c) leave relief to the daily cadence only.

**Game context:** stapledons-godot R2-INTERLUDE (`design_docs/planned/r2/interlude-card.md`).
- D2: the crossing review's **Aboard** page says "one asked to step back", and
  its **Waiting** page lists open requests and reliefs.
- D1/I2: the digest counts `reliefs_asked/granted/denied` from the
  `advanceAuto` Act log.
- I3b: moments later come from crew_core E4's skip report.

The game's crew_core consumer is `sim/crew*.ail` and `sim/cruise_digest.ail`.

**Note on numbering.** The 0.5 plan named the Archive actor (archive-npc A1)
as "crew_core 0.6". It becomes 0.7. Nothing about it changes here.

## What is wrong today (measured 2026-10-16, crew_core 0.5.1, AILANG v0.54.11)

1. **A monthly auto-run never asks for relief.** A 10-year skip on
   last-messages-home (`--skip 3650 --cadence 30 --archive 30 --concerns
   ask_advice`, v3, seeds 1–2) asks 0 times under either captain. A daily
   cadence asks 34 times a year under consent and 10 under orders (#149).
2. **Nobody is working at a monthly check-in.** Every Stapledon job lasts 2–3
   days. The auto-captain offers and starts work on the decision day, and the
   work is finished long before the next decision 30 days later.
3. **Work that does span the check-in cannot be asked about.** A project
   agreement falls due 20 days after its offer. After that `session.ask`
   refuses with `subject transition/expiry`, and #149's guard (`agreementLive`)
   skips the check-in.
4. **Relief exists only for running work.** The engine's `RequestRelief`
   requires a Working task the requester takes part in
   (`social_dynamics/proposals.ail` `request`). An idle crew member has no
   way to say "I need to stop".

Reproduce the baseline (relief counts come from the lab tally, M4 below):

```sh
cd examples/crew-lab
ailang run --quiet --bytecode --package-dir . --caps IO,FS,Env --fs-max-bytes 64MB sim_cli.ail -- \
  --skip 3650 --cadence 30 --captain consent --archive 30 --concerns ask_advice --seeds 1..2 \
  --scenario scenarios/stapledon/last-messages-home.json --policy scenarios/stapledon/policy.json
```

On 0.5.1 this prints `errors: 0`, about 610 offers and 405 starts per seed,
in 25 s for two seeds on the Studio.

## Design

### 1. Stand down in host terms: a duty check-in

A stand-down is a check-in that has no task, so it has no task agreement. The
host gives it a short-lived subject of its own, made at the check-in and gone
by the next tick.

**Two new host verbs** (the `input` command wire, so recordings and replays
see them like every other command):

| Command | Fields | What the host does |
|---|---|---|
| `check_in` | `actor`, `id` | Stages a **duty subject** for `actor` and asks them about it in one call. (1) The captain offers the worker's own rest recipe `rest_<actor>` as task `sd-<id>`. (2) The host offers a duty agreement `duty-<id>` between the captain and the worker, due `tick + 1`, which the captain accepts. (3) Both are receipted to the worker. (4) A `Request` is pending, phase `duty`, legal `["carry_on", "stand_down", "defer"]`, expiring at `tick + 1`. Bound as an ordinary `TaskAgreement`, so `binding`, `complete`, `cancel` and archiving work unchanged. |
| `resolve_stand_down` | `id`, `release` | Answers a stand-down. `release: true` grants it. The worker accepts the duty agreement, since they asked. If they hold running work, it is halted (`halt`, reason `stood_down`) and its reservation released. Then the rest task `sd-<id>` starts (`AcceptTask`), and a captain report goes out with outcome `granted_stand_down`. `release: false` denies it: a report with outcome `denied_stand_down` goes out, and the rest offer lapses at `tick + 1`. |

**Answering the duty request** (`answer`, as today):
- `carry_on` and `defer` change no state. The duty subject lapses at the next
  tick and is folded away by archiving as a lapsed offer (`lapsed`), exactly
  like an unanswered offer today.
- `stand_down` is recorded as the worker's concern `standdown-<request>`. It
  is an engine `RaiseConcern`, authored by the worker with cause `duty-<id>`
  and addressed to the captain, and receipted to the captain, the same
  mapping as `decline`. It does **not** open a conversation issue
  (`registerIssue` ignores the label), so the v3 concern machinery and the
  auto-captain's `settle` never see it.

**Why not a standing duty agreement for the whole voyage** (the alternative
named in the brief)? It was considered and rejected:
- **It changes every session from tick 0.** One extra commitment per crew
  member at init changes the snapshot, so every saved recording in the lab
  and the game changes. The per-check-in subject appears only when a check-in
  happens.
- **It needs a never-due agreement.** `due` must be a bounded int. Archiving,
  `stale`, `lapsed` and `agreementLive` would all need a special case for an
  agreement that never lapses.
- **It is a fiction under consent.** Consent means agreeing to each piece of
  work. A voyage-long "yes" signed at departure would let `startTask` pass
  the consent check for anything bound to it.
- **It still needs a task to rest on.** A grant must start something, and an
  idle worker has nothing running.

**Why not lengthen the project agreement** (#149's suggested follow-up)?
- It helps only work that is still running at the check-in, and Stapledon's
  never is. That route is Mark's rejected option (b).

**The expiry guard (#149) and the duty subject.**
- `agreementLive` stays as it is for project agreements.
- A duty agreement is made at the check-in and falls due at `tick + 1`. That
  is the same tick at which a request expires (`ask` sets
  `expires = min(due, tick + 1)`). So a duty check-in can never meet an
  expired agreement, and #149's guard never fires for one.
- `stale` and `busy` treat an Offered task bound to a `duty-` agreement as
  *not* occupying the worker. After a denial or a `carry_on`, the orders can
  still assign work on the same decision turn.

**The appraisal and grants.**
- `host_policy.appraisal` already reacts to a captain report whose causes
  include a captain `task_offer`. The report for a stand-down cites `sd-<id>`
  (a real task offer) and `duty-<id>`.
- So the appraisal needs **no new branch**. Only `codec` gains the two
  outcome codes and their trust deltas (§4).
- The policy id `received-outcome-v1` is kept. Saved games pin it in their
  config, and every input that existed before 0.6 appraises byte for byte as
  before.
- The authority policy (`captain-cooperation-v1`) applies to the rest offer
  as to any offer: under the cooperation floor (trust below 20) the host
  refuses `check_in`. The auto-captain therefore does not check in a worker
  below the floor, so it logs no host error and the stuck guard (3 identical
  errors) stays quiet. A crew member who no longer trusts the captain does
  not ask to stand down. That is in character, and a test pins it.

### 2. The auto-captain: who is asked, and how often

`auto.ail` gains a step between the working check-ins and the idle offers:

```
1. offered work: persuade                         (unchanged)
2. working crew: relief check-in                  (unchanged; live project agreement)
2b. duty check-ins (new)
3. idle crew: offer work or rest                  (unchanged)
4. advance                                        (unchanged)
```

**A worker gets a duty check-in at a decision turn when all of these hold:**
1. `orders.standDown == "on"` and the cadence is at least 2 (**OQ1**). The
   daily cadence already asks about relief at work every other day.
2. They are not resting: no Working or live Offered task on `rest_<worker>`.
3. They had no relief check-in this turn. A worker on running work under a
   live project agreement is asked about relief as today; running work whose
   agreement has fallen due gets a duty check-in. That covers "whether or not
   they are working".
4. They have no open concern (v3), as for the relief check-in.
5. **They are strained:** stress ≥ `orders.stress`, fatigue ≥
   `orders.fatigue` (the captain's own "tired" line, 75 and 70 by default),
   or they are overextended (the scenario's `overextended_<worker>` rule).
6. **They are off cooldown** (below).

**Cooldown (no flood of identical requests):**
- After a **grant**, a worker is not checked in again for 30 days.
- After the **k-th denial in a row**, they wait 90 × 2^(k−1) days, capped at
  360: that is 90, 180, 360, 360, ... A grant resets k.
- The waits are whole months, so on the monthly schedule they land on
  decision turns.
- A worker who stays strained under orders that always deny asks at most 12
  times in 10 years: days 0, 90, 270, 630, then every 360 to 3510. Five crew
  make at most **60**, which is the orders ceiling in AC3.
- Under consent, a grant rests the worker, which usually takes them below the
  line. The 30-day floor caps one worker at 122 asks in 10 years. The AC
  ceiling of **120 for the whole ship** is an empirical target: on average at
  most one stand-down a month.

**Where the cooldown lives.** It lives in `AutoState.raised`, the
caller-carried memory of once-per-crossing escalations.
- Each worker has one key, `stand_down/<worker>:<tick>:<k>`, holding the tick
  of the last ask and the current run of denials. Each ask replaces the key.
- `AutoState`'s shape is unchanged, so the game's four `AutoState` literals
  compile as they are.
- The game already persists `AutoState` in its world (`AutoRun.st`), so
  replays carry the cooldown. There is no hidden state.

**The worker's answer.** `authoredAnswer` on the duty request, as for any
request, uses the response policy plus the caller's seed. `policy.ail` gains
phase `duty`:
- `ruleOK` accepts `"duty"` as a phase.
- A request whose legal labels include `stand_down` is phase `duty`.
- **Fallback, so existing policy files work unchanged** (including the game's
  synced `policy.json`): when a policy has no `duty` rules, `carry_on` takes
  the weight of the `continue` rules, and `stand_down` takes the weight of
  `request_relief`, both phase `working`. `defer` keeps its `any` rule.
- The strain shift (`strained`) applies as for `continue` and
  `request_relief`.
- So the stand-down tendency comes from the same authored traits and
  indicators: fatigue ×3, stress ×2, morale −1, neuroticism.

**The captain's answer** follows the existing `relief` standing order through
`grants`: `grant` grants, `deny` denies, and `strained` grants only when the
worker is overextended. A new orders field selects only whether duty
check-ins happen (§6).

**A grant at a monthly check-in in practice.** At cadence 30 everyone gets at
most one job a month. A granted stand-down replaces this month's job with
the rest recipe (last-messages-home: 2 days, fatigue −20, stress −15,
morale +5). The worker is busy resting at the assign step, so they are not
offered work this turn. Under consent with `rest: tired`, the captain would
have sent them to rest anyway. The difference is that now the worker asks,
and the voyage records it.

### 3. Interactions

| With | Behaviour |
|---|---|
| **Expiry (#149)** | Duty agreements are made fresh and fall due at `tick + 1`, so they never meet the guard. Project agreements are unchanged. Running work whose agreement fell due now gets a duty check-in instead of nothing. |
| **Consent vs orders** | Consent (`relief: grant`): every stand-down is granted, and `startTask`'s consent check passes because the worker accepted the duty agreement. Orders (`relief: deny`): denied. The orders then assign work on the same turn, so `StrainedStart` and `RefusedOrder` costs follow as today. `strained`: granted only at or over the overextension line. |
| **`grants`** | Reused unchanged for duty check-ins. |
| **Rest recipes** | A grant starts `rest_<worker>`, the worker's own rest recipe, which already exists for every crew member (`scenario.rest`). Under `rest: tired` it would have been offered anyway. The stand-down records that the worker asked. |
| **Fatigue and stress thresholds** | The check-in gate uses the orders' `fatigue`/`stress` and the scenario's overextension rule. These are the same lines the captain's rest rule and the strain shift already use, so no new number is introduced. |
| **Concerns (v3)** | A worker with an open concern is not checked in. A stand-down is not a conversation issue. |
| **Escalation** | No escalation rule fires on a stand-down by default. **OQ3** asks whether `hands_on` should hand them to the player. |
| **Shortfall halts** | A grant on running work uses the same engine `halt` as a capacity shortfall, with reason `stood_down`. No regard changes: nobody argued. |
| **Archiving** | Denied or declined duty subjects are lapsed offers, and granted ones are ordinary rest tasks, so both fold with `keep`. `standdown-*` concerns and `report-standdown-*` reports fold with their task (`marks`), and a test shows a 10-year run's evidence stays bounded. |
| **Cohorts** | Untouched. Cohorts never take work. |

### 4. What a denial costs

Two new `CrewOutcome` codes, with trust deltas in `codec.traitDelta`:
- `GrantedStandDown`: **+4** (as `GrantedRelief`).
- `DeniedStandDown`: **−(2 + round(N/25))**, the same as `DeniedRelief`, from
  −2 at N0 to −6 at N100. Neurotic crew take a refusal harder. With no OCEAN
  traits, `outcomeDelta` is −4.

**Trust only, no stress (OQ2).** Under orders a denial is followed the same
turn by an assignment, and that already costs trust (`StrainedStart`,
`RefusedOrder`) and adds the job's stress. An extra stress charge would count
the same moment twice and speed up the breakdown spiral the 0.2 strain design
balanced.

The `traitDelta` contract range stays −12..4.

### 5. The journal, the Act log and the skip report (the E4 link)

What a stand-down leaves behind, and who reads it:

| Record | Content | Reader |
|---|---|---|
| Act `stand_down_asked` | actor, detail `sd-<id>` | game digest (`crew.counts.stand_downs_asked`) |
| Act `stand_down_decision` | label `granted` or `denied` | game digest (`stand_downs_granted/denied`) |
| Act `reply` | label `stand_down`, `carry_on` or `defer`, with the `Request` | game moments (`templateLine("stand_down")`) |
| Host report (`s.reports`) | outcome code `granted_stand_down` or `denied_stand_down`, evidence `report-standdown-<request>` | E4's skip report: a count of reports by code, in the journal and replayable |
| Engine evidence | `duty-<id>` (commitment), `sd-<id>` (task offer), `standdown-<request>` (concern) | replay, provenance |

The Act kinds are new rather than reused (`relief_asked` with a marker), so
the game can tell "stepped back from a job" from "asked to stand down". The
Aboard sentence may add the two together ("one asked to step back"). That is
the game's choice.

### 6. Wire, version and migration

**Standing orders** (`crew_standing_orders/1`, an optional field, so the
schema is unchanged):
- `stand_down`: `"on"` (default) or `"off"`.
- `Orders` gains `standDown: string`.
- `consentOrders()` and `ordersOrders()` return `"on"`.
- `decodeOrders` accepts the field and rejects any other value.
- `"off"` reproduces 0.5.1 byte for byte (AC8).

**New host commands:** `check_in` and `resolve_stand_down`. **New outcome
codes:** `granted_stand_down` and `denied_stand_down`. **New Act kinds:**
`stand_down_asked` and `stand_down_decision`. **New reply labels:**
`carry_on` and `stand_down`.

**Release kind:** `feature`, version **0.6.0**. It is minor because existing
commands, records and codes are unchanged. Behaviour changes only for
auto-runs at a cadence of 2 or more where a strained crew member is free at
a check-in.

**Migration notes for the game** (the integration agent's sprint, not this
one):
1. Pin `sunholo/crew_core = "0.6.0"` in `sim/ailang.toml`, then run
   `ailang install` and `ailang lock`.
2. **`sim/cruise_digest.ail`:**
   - count `stand_down_asked` and `stand_down_decision` (new
     `standDownsAsked/Granted/Denied` in `crew.counts`, protocol minor);
   - `momentKind("stand_down") = "relief"`;
   - `emotionOf("stand_down", _) = "sad"`, as `request_relief`.
3. **`sim/protocol_crew.ail` `templateLine`:** add `stand_down` (e.g. "I need
   to stand down for a while.") and `carry_on` (e.g. "I can keep going."). No
   digits (D-21).
4. **`ui/crew_page.gd`:** add `stand_down` to `STRAINED_LABELS` if the
   fallback list still lives there.
5. **Re-record** every monthly-cadence crew fixture: `make crew-parity`, the
   `crew_hold_test` expectations at cadence 30, and the digest fixtures.
   Daily-cadence fixtures are unchanged under OQ1's recommendation.
6. **AI replies (D-7, `crew_reply`):** a duty request's body lists the new
   labels, and the reply screen must accept them.
7. **Waiting page:** a stand-down is decided in the same call under auto-run,
   so it never waits. Under hands-on with OQ3's rule, the hold card shows it
   like a relief hold.
8. `AutoState`, `Act`, `Escalated` and the escalation schema are unchanged.
   The `Orders` record gains a field, which the game's `{ base | ... }`
   updates absorb.

### 7. Determinism, replay and the strict VM

- **Pure.** The duty check-in is pure `auto.ail` and `session.ail` code, with
  no effects. Ids are derived from the turn, the call salt and the worker
  (`d<turn><salt>-<worker>`), as for offers today.
- **Randomness.** The answer comes from `authoredAnswer` with the carried
  seed. The cooldown is in the caller-carried `AutoState`. There is no clock
  and no hidden state.
- **Same inputs, same output.** The 10-year run is printed twice and compared
  with `cmp` (AC6).
- **Both engines.** The tests run on the interpreter and under `--bytecode
  --strict-bytecode`. The lab's parity and replay recordings stay byte
  identical, because the new verbs are not in any existing recording (AC7).
  A new recording `stand-down.ndjson` exercises `check_in`, `answer`,
  `resolve_stand_down` (both ways) and `advance`, under parity.
- **VM workarounds avoided.** No cons-pattern list walks over long lists
  (ailang#1827): the gate uses `filter`/`any`/`foldl` over the five workers.
  No list of 1,000 or more built by non-tail recursion (#1576).

### 8. Crew-lab impacts (crew_lab is never published)

- **`crew_sim.ail`** tallies the new Acts.
  - Per-crew output gains `stand_down_asked/granted/denied`.
  - The `crew_skip/1` line gains `relief_asked/granted/denied` and
    `stand_downs: {asked, granted, denied}`, so the #149 measurement becomes
    a command.
  - The claims metrics gain `stand_downs.asked` and similar.
- **`sim_cli`** gains `--stand-down on|off`, default on.
- **New claims** `scenarios/stapledon/auto/stand-down-decade.claims.json`:
  the AC3 band under both captains, all grants under consent, all denials
  under orders, and 0 errors.
- **Claims that will move:**
  - **The cadence-30 skips:** `auto/v3-skip.claims.json` at `--cadence 30`
    (verdicts `errors == 0` and `tick == 365` must still hold) and the #149
    measurement (0 → more than 0).
  - **Under OQ1's recommendation, nothing at a daily cadence moves.**
    `review/*.claims.txt`, `data/watch-claims.json` (10 of 10) and the
    counting-mode `auto/*-year` and `hands_on-*` claims run at cadence 1 and
    must reproduce byte for byte.
  - **If Mark chooses every cadence instead (OQ1 alternative)**, these are at
    risk and are re-recorded with a REVIEW.md note:
    - `news-decades-late` `medic-asks-for-relief` (`relief_asked >= 0.5`):
      the medic may stand down before taking work;
    - `processing-cascade` `engineer-gets-relief-with-consent`;
    - `watch-claims` `consent-grants-every-relief` and
      `orders-grants-no-relief`;
    - the medic trust claims in `last-messages-home`.
- **The random captain** does not run at a cadence of 2 or more, so it is
  unchanged.
- **REVIEW.md** gains a section "Update (crew_core 0.6.0): stand down at the
  check-in" with the measured numbers.

## Acceptance criteria

Each is a command, run from the repo root unless it says otherwise. `A` is
the pinned runtime, `~/dev/sunholo-data/stapledons-godot-attended/runtime/bin/ailang`
(v0.54.11). `LAB` is `make -f examples/crew-lab/Makefile AILANG=$A`.

| # | Criterion | Command |
|---|---|---|
| AC1 | `check_in` and `resolve_stand_down` (grant and deny), the duty phase fallback, the new outcome deltas, and the `stale`/`busy` exclusion each have tests. These pass on the interpreter and the strict VM. The new tests fail on 0.5.1. | `$LAB core-tests` (runs `ailang test --package . --allow-skips --bytecode --strict-bytecode` in `packages/crew-core`), plus `cd packages/crew-core && $A test --package . --allow-skips` |
| AC2 | Auto-captain tests: an idle strained worker at cadence 30 is checked in and asks. An unstrained one is not. A worker resting or under cooldown is not. The denial backoff gives check-in ticks [1, 91, 271, 631] under `deny`. Under the cooperation floor no duty check-in is made. | same as AC1 (`auto_test.ail`) |
| AC3 | **The measurement.** A 10-year monthly auto-run on last-messages-home asks to stand down **more than 0 times and at most 120 (consent) or 60 (orders)** per seed. Consent has 0 denials, orders 0 grants, and both 0 errors. | `cd examples/crew-lab && crew-sim --check scenarios/stapledon/auto/stand-down-decade.claims.json --skip 3650 --cadence 30 --archive 30 --concerns ask_advice --seeds 1..2 --scenario scenarios/stapledon/last-messages-home.json --policy scenarios/stapledon/policy.json` prints "all claims hold". Here `crew-sim` means `$A run --quiet --bytecode --package-dir . --caps IO,FS,Env --fs-max-bytes 64MB sim_cli.ail --` |
| AC4 | The gate claims still hold at both cadences: the v3 skip at cadence 1 and 30, both captains, seeds 1..5, 3 of 3 each. | `crew-sim --check scenarios/stapledon/auto/v3-skip.claims.json --skip 365 --cadence {1,30} --archive 30 --concerns ask_advice --seeds 1..5 --scenario scenarios/stapledon/last-messages-home.json` |
| AC5 | Daily-cadence lab results are byte-identical to 0.5.1 (under OQ1's recommendation). | `$LAB claims-test scenario-pack-test sim-test`, and regenerating `review/*.claims.txt` gives `git diff --exit-code examples/crew-lab/scenarios/stapledon/review/` |
| AC6 | Determinism: the AC3 run printed twice is byte-identical, on the interpreter and on the VM. | `crew-sim --skip 3650 --cadence 30 ... > a; crew-sim ... > b; cmp a b`. The same without `--bytecode` gives `cmp` equal to the VM output. |
| AC7 | Saved host recordings replay identically and VM == interpreter, including the new `stand-down.ndjson`. | `$LAB parity replay` |
| AC8 | `stand_down: "off"` reproduces 0.5.1 exactly on the AC3 run. | `crew-sim ... --stand-down off` diffed against the 0.5.1 output recorded in the sprint (`cmp`) |
| AC9 | The evidence stays bounded: a 10-year monthly run with archive keep 30 has no `capacity_exceeded` error, and its peak evidence count is printed in the skip line. | AC3 command (`errors == 0` claim) |
| AC10 | Cost: the 10-year two-seed run stays within 1.25× of 0.5.1's wall time on the same machine (25 s on the Studio, measured 2026-10-16). | `time crew-sim --skip 3650 --cadence 30 ...` |
| AC11 | Package hygiene: `pkg quality --strict` shows no gates, the CHANGELOG has a 0.6.0 entry, `ailang.toml` has version 0.6.0 and release kind `feature`, and AGENT.md has a "Stand down" section. | `$LAB quality` (crew-core `pkg quality --strict .`), plus `grep -n '^## 0.6.0' packages/crew-core/CHANGELOG.md` |
| AC12 | The whole lab validates. | `$LAB validate` |

## Implementation notes (executor, 2026-10-16)

- The duty request's id is the check-in id: `check_in` with id `X` makes
  task `sd-X`, agreement `duty-X`, request `X`, concern `standdown-X` and
  report `report-standdown-X`.
- AC9: the `crew_skip/1` line prints `evidence`, the live evidence count at
  the end of the run, not a peak; a peak would need `AutoResult` to carry
  it. The `errors == 0` claims cover `capacity_exceeded`.
- AC8: the skip line's new fields (`relief`, `stand_downs`, `evidence`)
  appear only with stand-downs on, so `--stand-down off` is 0.5.1's line
  byte for byte.
- §8: `crew_sim/1` rows (counting mode, always daily) gain no per-crew
  stand-down fields, since no stand-down happens at cadence 1; the tally
  counts the Acts so they are never mistaken for errors.
- AC2's backoff test runs `start: agreed` under `relief: deny`: with
  overridden refusals, two years of orders take the worker below the
  cooperation floor before day 631, and then (rightly) no check-in is made.

- Evaluation fix (round 1, D1): a stand-down handed to the player sets the
  same cooldowns. The stop leaves `stand_down_pending/<worker>:<tick>:<id>`
  in `AutoState.raised`; on resume it is settled from the host's
  `report-standdown-<id>` before any duty check-in (a lapsed, undecided one
  counts as a denial). The grant cooldown now counts 30 days from the end
  of the granted rest (grant tick plus the rest's duration), in both paths.
  AC3 consent moved 28 → 27 on seed 1.

## Risks

- **#149 is not merged.** If review changes 0.5.1, rebase this branch onto it.
  The duty check-in reuses `checkInDue` and `agreementLive` only for the
  relief path.
- **`session.ail` is 917 lines.** The two verbs add about 90 lines. If the
  repo's size gate objects, they move to a companion `duty.ail` that takes
  the `Session` and the domain helpers as arguments. A cold compile is
  re-measured (#1812).
- **The asks may sit outside the band.** The policy fallback gives
  `stand_down` the `request_relief` weight. At high stress it often wins, so
  the count may be well above the measured daily rate. If AC3 fails high
  under consent, the sprint records the number and asks Mark before tuning,
  rather than changing the claim to match.
- **Under consent, a stand-down is nearly what `rest: tired` already does.**
  Under consent the numbers mostly change who gets the credit, not the
  indicators.

## Open questions for Mark

**Answered 2026-10-16 (Mark, attended: "yep agree with planners
recommendations proceed"):**
1. OQ1: stand-down check-ins only at a cadence of 2 days or more.
2. OQ2: a denial costs trust only, no stress.
3. OQ3: `hands_on` gets an opt-in `stand_down` escalation rule, listed only
   in `hands_on.json`; `critical_only` keeps deciding by standing order.
4. OQ4: the cooldowns stay as written: 30 days after a grant; 90, 180 and
   360 after denials.

The questions as asked:

1. **OQ1: duty check-ins at a cadence of 2 or more only, or at every
   cadence?** *Recommendation: 2 or more only.* Daily play already asks about
   relief every other day at work (34 a year under consent). It keeps every
   daily-cadence lab result and the game's near-star fixtures byte-identical.
2. **OQ2: does a denial cost stress as well as trust?** *Recommendation:
   trust only*, the same as a denied relief (−2 to −6 by N). Under orders the
   assignment that follows already costs trust and adds stress.
3. **OQ3: should `hands_on` hand stand-downs to the player?**
   *Recommendation: yes, opt in.* Add an escalation rule kind `stand_down`
   (about 20 lines) and list it in `hands_on.json` only. `critical_only`
   keeps deciding by standing order, and the game shows it in the review.
4. **OQ4: the cooldown numbers** (30 days after a grant; 90, 180, then 360
   after denials in a row). *Recommendation: as written.* They bound orders
   to at most 60 asks a decade for five crew and keep a strained crew member
   audible about once a year once refusals pile up.
