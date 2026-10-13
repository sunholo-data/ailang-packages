# Crew resources that behave like the bubble's

**Status:** Proposed (2026-10-13), awaiting Mark's approval.
**Packages:** `sunholo/crew_core` (generic, unpublished) and `sunholo/crew_lab`
(Stapledon pack, local only). `sunholo/social_dynamics` is not changed.
**Game design:** stapledons-design `features/next/bubble-resources.md` (#20),
canon D-69.

## Problem

The pack now names the eight bubble resources, but the social simulation can
only spend them. Crew work reserves a resource while it runs and may consume
some of it. Nothing else can move a resource:

- **A failure can't take capacity away.** A reclaimer breaks only in the text.
- **Recycling and repair can't give anything back.** Water never returns from
  the brine pool, and a repaired reclaimer never restores capacity.
- **The ship can't tell the crew about it.** A shortage is not an event they
  hear about or react to.
- **Claims can't see resources.** `crew_sim/1` reports stockouts, but not which
  resource ran out or for how long.

So `water`, `power` and `heat`, the resources the bubble actually lives on,
can't be modelled honestly. A closed loop needs flows both ways: into a pool
and back out of it.

## Design

### 1. Resource kinds (crew_core, generic)

Each scenario resource gets a `kind`: `"stock"` or `"capacity"`. If it is
absent, it defaults to `"stock"`, so existing scenarios still load.

- **A capacity is never consumed.** A cost with `consume > 0` on a capacity
  is a scenario error. Capacity is reserved while work runs and released when
  the work ends.
- **A stock may be consumed.**

### 2. Ship events (crew_core, generic)

A scenario may list `events`. Each one happens at a tick, is applied by the
host, and is seen by every crew member:

```json
{"at": 2, "id": "reclaimer_fails", "text": "Reclaimer 2 has failed; the loop is draining into brine.",
 "transfers": [{"resource": "water", "delta": -2}], "major": ""}
```

- **Transfers move resources in or out.** A negative delta moves available
  units out (`transferredOut`). It is limited to what is available; a reserved
  unit is never taken, and any shortfall is journalled. A positive delta moves
  units in (`transferredIn`).
- **The crew hear about it.** The text becomes evidence known to the whole
  crew, so appraisal and words react to it.
- **`major`** is optional. It may name one of the existing personality major
  events (`loss`, `deep_time`, `first_contact`, `betrayal`).
- **Limits:** at most 32 events, each with at most 8 transfers.

### 3. Yields (crew_core, generic)

Work may list `yields`: `[{"resource": "water", "amount": 2}]`. When the
work completes, these are transferred in. This is how recycling returns
water and a repair restores capacity. Work that is stopped yields nothing.

### 4. How transfers are applied

`social_dynamics` 0.3.0 already accounts for `transferredIn` and
`transferredOut`: its resource invariant is `available + reserved + consumed
== initial + transferredIn − transferredOut`. It just has no operation that
sets them.

- **crew_core applies transfers to the session state itself.** It keeps that
  invariant, and records each transfer in its own journal as a host record.
- **No published package changes.** A `Transfer` operation in
  `social_dynamics` 0.4.0 is a later, attended publish, if wanted.
- **Determinism:** events are data, applied at fixed ticks in list order.

### 5. Measures and claims (crew-lab)

`crew_sim/1` gains a `resources` measure for each resource: minimum
available, ticks spent at zero, stockouts, units transferred in and units
transferred out. Claims can then name
`resources.<id>.min|zero_ticks|stockouts|in|out`.

### 6. The eight in the lab (crew-lab, Stapledon-specific)

`bubble.ail` holds the table from `bubble-resources.md` §6: id, kind,
crew-scale unit and physical unit.

- **`allocate`** turns a physical ship state (kg, t, kW, m², shifts,
  slots, windows) into crew units, rounding down. That is the seam the game
  sim will use.
- **`lintPack`** checks that a scenario uses only the eight, with the right
  kinds. `scenario-pack-test` runs it.

### 7. The pack, made physical

Claims are written before running. Failures are findings, not tuning targets.

| Scenario | What becomes physical |
|---|---|
| `processing-cascade` | **Water and fabrication:** a reclaimer failure moves water into brine (`water −2`, then `−1` at ticks 4 and 6). The rebuild yields `water +3` and consumes `mass`. The botanist's crop shift reserves `garden` and `power`. |
| `ergosphere-question` | **Heat:** on the approach (tick 4) the forward sky heats the dome, so `heat −2`. Bracing the generator reserves `power` and `heat`. |
| `last-messages-home` | **Signal:** the farewell broadcast reserves `signal` and `power`. At departure, `signal` drops to 1 as Earth falls behind. |
| `light-from-the-dead` | **Signal, compute and power:** decoding reserves `compute` and `power`. A second burst arrives at tick 6 (`signal +1`). |
| `news-decades-late`, `archive-misremembers` | Only `kind` is added; their stories are not about the physical loop. |

Example claims:
- `processing-cascade`: water reaches zero in most seeds under orders, but not
  under consent.
- `ergosphere-question`: the bracing work stalls on `heat` more often after the
  approach event.

## Acceptance (every item is a command)

1. `make core-tests` (crew_core, both engines) covers:
   - kinds, events and yields decode;
   - invalid ones are rejected (a capacity that is consumed, an unknown
     resource, `at` out of range, over the limits);
   - the transfer invariant holds after every event;
   - a negative transfer never takes reserved units;
   - yields apply only on completion;
   - a scenario without the new fields plays byte-identically to before
     (journal compared with a recorded fixture).
2. `make tests` (crew-lab, both engines): `bubble.ail` `allocate` and
   `lintPack` tests; `crew_sim` resource measures; claims metric validation.
3. `make scenario-pack-test`: every pack scenario passes `lintPack`; all six
   play clean over seeds 1..3; every claims file loads.
4. `crew-sim --check` over 20 seeds for the four reworked scenarios. Results
   are recorded in `REVIEW.md`, including failures.
5. `make validate` passes keyless; `pkg quality --strict` shows no gates for
   crew_core and crew_lab.

## Out of scope

- The game sim's physical ledger (the game repo, later).
- Emergent failures from failure rates. Events stay authored for now.
- A `social_dynamics` publish.
- New personality major-event kinds (for example `scarcity`), unless the
  claims show they are needed.
