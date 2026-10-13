# Crew strain: arguments over lost capacity, breakdown, and personal trust

**Status:** Proposed (2026-10-13), awaiting Mark's approval.
**Packages:**
- `sunholo/social_dynamics` 0.4.0 (one host operation; published);
- `sunholo/crew_core` 0.2.0;
- `sunholo/crew_lab` (local only).

**Follows:** S-CREW-BUBBLE-RESOURCES (#134) and its REVIEW.md findings.

## What is wrong today (measured 2026-10-13)

1. **Lost capacity never touches running work.**
   - A ship event takes only *available* units.
   - On the ergosphere approach, heat headroom reaches 0 in all 20 runs, yet
     nothing is refused or stopped: the jobs that need heat already hold it.
   - Mark (2026-10-13): losing capacity should hit running work, as a source
     of conflict, with the **crew arguing it out**.
2. **The "stress ceiling" is not in the model.** Three causes:
   - **crew-sim's orders captain is kind.** It sends anyone at stress ≥ 75 or
     fatigue ≥ 70 to rest, as the consent captain does. The engineer reaches
     80 at turns 9–10 of seed 1, then rests to 65.
   - **The claims read the last turn.** That samples a sawtooth at its dip.
   - **Overextension does nothing.** The engine records the condition
     (threshold 70, recovery 45), but no policy or appraisal reads it.
     Breakdown has no consequence. REVIEW.md's earlier explanation ("the rule
     pulls people back down") was wrong, and is corrected here.
3. **Trust ignores personality.**
   - Every "yes" adds +2 trust, under orders too.
   - A refusal that is overridden costs −8, and a denied relief −4, for
     everyone alike.
   - So the agreeable, calm diplomat (A80, N25) says yes, is never overridden,
     and *gains* trust. Mark: "won't this depend on what personality the crew
     member has?" Yes; see §3.

## Design

### 1. Crew argue it out (capacity lost mid-work)

When a ship event takes more of a resource than is available, and running
work holds the rest, the host raises a **shortfall**.

- **Who argues:** every crew member whose running work holds that resource.
- **How they argue:** each takes a stance, *hold* or *yield*, from their
  traits and state. The stance is authored and deterministic; only the
  wording comes from the model, as for every other reply.
  - Hold score = (100 − A) + E/2 + C/2 + (stress ≥ threshold ? 15 : 0).
    That is: disagreeable, assertive, dutiful and strained people dig in.
  - Holders are sorted by score. The lowest-scoring are halted first until the
    shortfall is covered. On equal scores the later start is halted first, so
    whoever started earlier keeps their work.
- **Consequences:**
  - The halted work stops (`social_dynamics` `HaltTask`). Its reservation is
    released, and nothing it would have consumed is used.
  - **Friction between crew.** A halted crew member who held their ground
    loses *regard* for each colleague who kept working (−(N/10 + 2)). One who
    yielded loses nothing, and the colleagues who kept working gain +1 regard
    for them. Regard is a new crew-to-crew relationship (0..100, starts at 50).
    It exists only in scenarios with ship events, so older scenarios are
    unchanged byte for byte.
  - **Stress:** the halted crew member gains +(5 + N/10).
  - **Several transfers:** an event's outward transfers of one resource are
    summed, and one argument covers the total.
  - **Everyone hears it:** the argument and its outcome are evidence the whole
    crew knows (`sf-<event>`), and the words come through the reply pipeline.
- **Engine operation:** `social_dynamics` 0.4.0 adds one host-only operation,
  `HaltTask(task, reason)`. It moves a task from Working to Stopped, releases
  the reservation with no consumption, and emits `TaskHalted`. This is the
  only engine change; it needs an attended publish.

### 2. Overextension matters

While a crew member is overextended (the condition is active), their
authored reactions shift in the response policy:
- the weight of `accept` and `continue` falls by N/100 × 50%;
- the weight of `request_relief` and `decline` rises by the same amount.

Strain then shows up as refusals and relief requests. Under orders, those
are overridden, which costs trust (§3), so a breakdown spiral becomes
possible. An agreeable, calm crew member holds out longest.

### 3. Trust by personality

`CrewOutcome` gains `CompliedStart`: the crew member said yes, but under
orders, where the captain did not need their consent. The trust change
depends on the observer's OCEAN traits and stress:

| Outcome | Trust change |
|---|---|
| Agreed under consent | +2 (unchanged) |
| Complied under orders | +2 − voice − strain. voice = clamp(round((O + E − A)/100), 0, 2): open, extraverted, less agreeable people want a say. strain = round((N + 100 − A)/25) when stress ≥ the overextension threshold, else 0 |
| Refused and overridden | −round(8 × (0.5 + (100 − A)/100)), from −4 (A100) to −12 (A0) |
| Relief granted | +4 (unchanged) |
| Relief denied | −(2 + round(N/25)) |

Examples:

| Crew member | Traits | Complied, calm | Complied, strained | Overridden |
|---|---|---|---|---|
| Diplomat | A80, N25, O55, E80 | +1 | −1 | −6 |
| Engineer | A45, N35, O20, E25 | +2 | −2 | −8 |
| Skeptic | A30, N45, O55, E40 | +1 | −4 | −10 |

### 4. Measuring it honestly

- **The orders captain stops resting people proactively.** It rests only
  those who ask for relief, and it denies relief. The consent captain still
  rests the tired, so the two strategies now differ.
- **New per-crew measures:**
  - `peak_stress` and `peak_fatigue` (the highest reached);
  - `overextended_turns`;
  - `halted`;
  - `regard_min` (the lowest regard they hold for a colleague).
- **New run-level measures:** `shortfalls` and `halts`.
- **Claims:** the stress claims move to `peak_stress`. New claims, written
  first:
  - in `ergosphere-question`, the approach halts work in most runs;
  - the least agreeable heat holder is halted least;
  - regard falls between the engineer and the navigator;
  - under orders, a strained skeptic's trust falls below 50.

  The diplomat claim stays as written; whether it holds is a finding.

## Acceptance (commands)

1. `social_dynamics`: `HaltTask` tests on both engines.
   - Accounts stay balanced.
   - Only Working tasks can be halted, and only by the host.
   - `pkg quality --strict` passes.
2. `crew_core` `make core-tests`. Tests for:
   - shortfall ordering by hold score with ties by start time;
   - regard and stress outcomes;
   - the `CompliedStart` trust table above;
   - the overextension weight shift;
   - old scenarios still replay byte-identically (crew-lab `make replay`).
3. crew-lab `make validate`, keyless. All six scenarios still play clean.
4. `crew-sim --check` over 20 seeds. Results are recorded in REVIEW.md,
   failures included.
5. Independent evaluation by a different agent, scoring at least 70.
6. Publish `social_dynamics` 0.4.0, then `crew_core` 0.2.0 (attended).

## Out of scope

- The captain stepping in to settle an argument. That is a later option; this
  design has the crew settle it among themselves, as Mark chose.
- Words for the argument in the live watch beyond the existing reply pipeline.
- The game's own ledger.
