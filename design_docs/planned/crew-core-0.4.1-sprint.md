# Sprint S-CREW-CORE-0.4.1: auto-captain fixes (concerns, stuck runs, stale offers, hysteresis)

**Why:** with the game's `watch-v3` profile, crew_core's auto-captain
deadlocks from day 1. It was found by the R2-CREW integration agent
(stapledons-godot-74, 2026-10-14) and reproduced in the lab.
- **The deadlock.** A crew member replies `concern`. The auto-captain never
  answers; it re-asks about and re-offers the task, and the host refuses each
  time ("answer the existing concern before …"). The errors pile up at about
  one a day per worker, and nothing escalates.
  - Measured: the game's synced scenario, seed 7, 30 days, consent with
    critical_only gives 130 errors, 0 escalations and 5 starts. The same run
    on `watch-v2` gives 0 errors and 46 starts.
  - Every lab auto claim so far ran on `watch-v2`, where the concern guard is
    off. That is how this was missed.
- **Lab findings from the same day** (ailang-packages #140):
  - stale offers are asked about at cadence 1 (285 errors a year with
    archiving; without it, the ship stops offering after about day 35);
  - the `hands_on` breakdown line re-arms about 130 times a year.

**Authorization:** pending (Mark).
**AILANG prompt version loaded:** v0.16.7 (runtime v0.54.8).
**Registry reuse:** none (fixes inside crew_core).

**Compatibility:**
- The host wire is unchanged: commands, journal records, outcome codes, and
  the six parity recordings.
- `crew_standing_orders/1` gains an optional field `concerns`.
- `crew_escalation/1` gains the rule name `stuck`, and in v3 `uncovered` is
  implied.
- Auto-run output changes where it was wrong, at cadence 1 and in v3. Lab
  claims affected by that are re-run and the changes recorded, not tuned.

## Milestones

| ID | What | Gate |
|---|---|---|
| F1 | **Concerns.** The auto-captain never asks about or offers a task with an open conversation issue; that worker counts as waiting on the captain. An open concern always escalates (`uncovered`, implied in v3 whatever the rules say), **once per issue**: the issue id goes into `raised` and is not raised again until it is answered or reopened, so a resumed hold doesn't come back every decision day. New standing order `concerns: escalate` (the default) or a host suggestion approach (`clear_scope`, `ask_advice`, `explain_priority`, …): the auto-captain replies with that suggestion through `captain_reply` and play goes on | tests on both engines: deadlock repro gives 0 errors; default escalates at the concern's tick; resuming without an answer does not re-escalate the same issue; auto-reply answers and work resumes |
| F2 | **Stuck guard.** `advanceAuto` escalates `stuck` (actor, detail = the error) when the same error act (the same actor and error text) repeats 3 times in one call, so two crew stuck on different tasks each raise it once, so a dropped log cannot hide a deadlock | test: an injected repeating failure escalates on its third occurrence |
| F3 | **Stale offers at every cadence.** `stale` applies at cadence 1 too: a lapsed offer no longer holds its worker or gets asked about | test: seed-10 repro (orders, keep 30, 365 days) has 0 errors; without archiving the ship keeps offering after day 35 |
| F4 | **Hysteresis.** A crossing rule (breakdown, trust_floor, cohort) re-arms only after the value is 10 back across the line | test: a value oscillating 69–71 raises once; dropping to 59 then rising raises again |
| F5 | **Lab: v3.** `crew-sim --profile v2\|v3` (v3 default for `--auto` and `--skip`). Re-run all auto claims on v3, plus a new gate claim from the integration agent: zero error acts over 365 days at cadence 1 and 30, both captains, keep 30, the game's scenario. **Measure concerns per 100 days** on v3 (both captains, cadence 1 and 30), for Mark's choice of the game default | `crew-sim --check`; the claim changes recorded in REVIEW.md |
| F6 | Close: changelog, parity, independent evaluation (≥70), PR, publish 0.4.1, merge sha to the integration agent | CI green; publish |

## Questions for Mark

1. **The default for concerns under auto-run.**
   - crew_core's default: *escalate*. A concern is the crew asking the captain
     something.
   - The game chooses per preset. The integration agent proposes:
     - `critical_only` auto-answers (`concerns: <approach>`, logged in the
       crew lines), because in its seed-7 run 2 of 5 crew raised a concern
       within 3 days, and escalating each one would make critical-only a
       concern prompt every few days near stars;
     - `hands_on` escalates.
   - F5 measures concerns per 100 days so this is decided with numbers.
   - The game also needs a small sprint of its own before an escalated
     concern is answerable: open issues in the crew view, a
     `crew_captain_reply` intent with the three approaches as buttons on the
     hold card, and words for `stuck`. Today the hold card only has Resume.
2. **The hysteresis margin of 10.** It is a design number, set before
   measuring. The claims will show how often `hands_on` stops with it.
