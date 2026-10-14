# Review: Stapledon crew scenario pack (2026-10-12)

Six draft scenarios, each checked by `crew-sim --check` (20 seeds, 12 turns, consent and orders captains) and given real crew words by `crew-sample` (GLM-5.3-Flash through the watch's prompts and checks; 62 provider calls over two rounds: 48 in the first, then 14 after the id fix, when most words came from the saved library; the committed `review/*.samples.ndjson` are the second round, so their `calls` add up to 14; 10 moments per scenario). Reactions are authored and seeded; only the words come from the model. Full words: `review/<scenario>.words.txt`; claims: `review/<scenario>.claims.txt`.

## Findings

1. **33 of 36 design-intent claims hold.** The claims were written before running; the three failures are findings, not tuning targets.
2. **Stress has a ceiling near 65–70.** Under orders, the grieving medic and the crisis engineer end at a median stress of 65, not above 70: the overextension rule (threshold 70, recovery 45) pulls people back down. If breakdown should be possible ("We Are Not Built For This"), the rule needs a scenario-level choice: a higher threshold, or overextension that leads to refusal rather than recovery.
3. **An agreeable, calm crew member costs orders nothing.** The diplomat (agreeableness 80, neuroticism 25) accepts almost everything, so an orders captain never overrides them and their trust stays at 61. That may be right; it means trust erosion under orders depends on someone saying no.
4. **The words are good enough to review seriously.** All 60 moments have words; none name traits, scores or internal ids after one fix (5 of 98 first-round lines quoted ids such as `work_skeptic`; the check now rejects them and the prompt forbids them). Lines follow state: the stressed medic accepts rest, the skeptic refuses before the horizon, the zealot worries the vigil must "carry all their remembering for them".
5. **Rest offers read awkwardly** ("the medic rest assignment"): the rest project is named `<Role> rest`. A per-scenario rest name would fix it.
6. **Gaps between the lab and canon** (inputs for integration, not defects here): the lab models 5 featured crew, not ~100 founders; turns, not game-weeks; no family or chemistry relationships yet (the engineer is canonically parent of the pilot and skeptic); the Archive is not an actor; refusal is individual, with no votes or mutiny; samples use the watch-v2 prompts, not the conversation prompts.

## Update 2026-10-13: one set of resources

Mark's review asked for universal, physical resources in place of abstract
ones. Every scenario now uses only the eight bubble resources from
stapledons-design `features/next/bubble-resources.md`: `mass`, `water`,
`power`, `heat`, `garden`, `fabrication`, `compute` and `signal`, at crew-scale
units. Stocks (`mass`, `water`) are used up. Capacities (the other six) are
only reserved while work runs.

| Before | Now |
|---|---|
| Spare parts, paper, medical stock, cartridges, repair stock | `mass` (fabricated free mass; one pool, so they compete) |
| Archive access, compute slots, message bandwidth, diagnostic time | `compute` |
| Relay windows, antenna time | `signal` |
| Fabrication bay time | `fabrication` |
| Seed stock | `garden` (reserved, no longer consumed) |
| Clinic hours | dropped (the medic's time is fatigue) |

Claims over 20 seeds are unchanged: still 33 of 36, with the same three
findings. Only `processing-cascade` moved. Its median stockouts fell from 5 to
3, and median relief granted from 2 to 1, because the botanist no longer uses
up garden beds. The scenarios do not yet use `water`, `power` or `heat`; the
next pass should, with the reclaimer failure draining `water` and the gardens
competing for `power`.

## Update 2026-10-13 (later): resources that flow

The crew host can now move resources, not just spend them (S-CREW-BUBBLE-RESOURCES):
- **ship events** move units in or out at a tick, and every crew member hears about them;
- **completed work yields** units back;
- **capacities are reserved, never consumed**;
- `crew-sim` reports each resource's low point, turns spent at zero, stockouts, and units in and out.

Four scenarios now tell physical stories:

| Scenario | Flows |
|---|---|
| `processing-cascade` | Failures at turns 2, 4 and 6 move 4 t of water into brine. The rebuild uses 20 kg of mass and returns 3 t; water-light crops return 1 t. Power headroom (2 units) is shared by the rebuild, the inspection and the crops. |
| `ergosphere-question` | On the approach (turn 4) the forward sky takes 2 of 3 units of heat headroom, and returns them past periapsis (turn 8). Bracing and modelling need power and heat. |
| `last-messages-home` | At departure (turn 3) Earth's link narrows by two antenna windows. Recording and compressing need a window and power. |
| `light-from-the-dead` | A second burst at turn 6 opens another antenna window. Decoding, translating and drafting need power. |

Claims, written before running, over 20 seeds: **41 of 46 hold.** Three are the
earlier findings (the stress ceiling twice, and the diplomat's trust, now 54).
Three are new findings:

1. **A capacity loss never touches work in progress.** The approach always
   takes the heat headroom to 0 (in all 20 runs), but nothing is refused for
   heat (median 0). Bracing and modelling already hold their reservation, and
   their next jobs start after periapsis. Physically, losing radiator capacity
   should throttle running work too. Should a capacity drop be able to pause
   or stop tasks that hold it? That is a host rule to decide, not a tuning knob.
2. **A prompt crew keeps the loop above half.** All 4 t leave in every run,
   but the lowest point is 2 t in only 2 runs, 3 t in 8 and 4 t in 10: the
   rebuild and the crops return water between failures. The claim expected
   at most 2 t in every run.
3. **Compute in `light-from-the-dead` saturates but is never contested.** It
   reaches 0 in every run, but decoding (2) and translating (1) exactly fill 3
   slots. The claim's own arithmetic was wrong. A fourth slot user would make it
   contested.

## Update 2026-10-13 (strain): arguments, breakdown and personal trust

Mark asked for the misses to be fixed, for lost capacity to hit running work as
a source of conflict ("crew argue it out"), and for trust to depend on
personality. Design: `design_docs/planned/crew-strain.md`. Runs below use the
pack's `policy.json` (strain on); claims are over 20 seeds.

**What was actually wrong** (this corrects finding 2 above):
- **There was no stress ceiling in the model.** crew-sim's *orders* captain
  rested anyone at stress ≥ 75, the same as the consent captain. The claims
  read the last turn, which caught the dip after rest. The overextension rule
  recorded a condition that nothing read, so breakdown had no consequence.
- **Trust ignored personality.** Every "yes" gave +2, even under orders. A
  refusal that was overridden cost −8 and a denied relief −4, whoever the
  crew member was.

**Now:**
- The orders captain never rests anyone on its own initiative.
- Claims test *peak* stress.
- While a crew member is overextended, their reactions shift towards decline
  and relief requests, scaled by neuroticism.
- Trust follows traits. Examples (a "yes" under orders while calm / while
  strained / when overridden):

  | Crew member | Calm yes | Strained yes | Overridden |
  |---|---|---|---|
  | Diplomat | +1 | −1 | −6 |
  | Engineer | +2 | −2 | −8 |
  | Skeptic | +1 | −4 | −10 |

- When capacity is lost, the crew who hold it argue. The least assertive are
  halted first; a halted crew member who held their ground resents the
  colleagues who kept working.

**Results: 44 of 50 claims hold.** One of those passes vacuously (`navigator-holds-the-heat`; see below).
- **Breakdown is now possible.** Under orders, peak stress reaches 95 for the
  engineer and 100 for the medic (median). The strained skeptic's trust falls
  to 14.
- **The diplomat still does not sour (median trust 52.5).** That is now a
  property of their personality, not a bug: agreeable and calm (A80, N25),
  they lose trust only when strained, and under these orders they rarely are.
- **Arguments almost never happen in `ergosphere-question` (1 run in 20).**
  The rule works: `crew_core`'s strain tests halt the least assertive holder,
  then apply stress and regard exactly. The scenario rarely has both heat
  users running at once. Bracing uses 20 kg of mass, so the engineer stops
  after two braces, and the navigator alone leaves enough headroom.
  - It does not help to move the approach to turn 5. Events fire after work
    that finishes on the same tick, so an event on a shift boundary takes
    nothing from running work. That ordering is deliberate and documented.
  - So `approach-forces-an-argument` and `halted-engineer-resents-navigator`
    fail, and `navigator-holds-the-heat` passes only vacuously (19 of 20 runs
    have no argument). `heat-blocks-work-under-orders` (finding 1 above) still
    fails too: the median of heat stockouts is 0.
  - The fix is an authoring choice for Mark, not a tuning knob. Options: a
    third heat user (the medical bay's cooling), less heat headroom (2 instead
    of 3), or bracing that needs less mass.
- **Unchanged:** `leak-drains-the-loop` (a prompt crew keeps the loop above
  half) and `compute-is-contested-under-orders` (the claim's arithmetic was
  wrong).

## Update 2026-10-13 (CI-0): the ergosphere's third heat user (D-70 OQ6)

The medical bay now also reserves heat ("its scanners and cold stores run on
the radiators too"). Over 20 seeds, 10 of 12 claims hold.
- **The heat squeeze is now real.** `heat-blocks-work-under-orders` holds,
  with a median of 4 heat stockouts under orders (previously 0).
- **Arguments are still rare: 2 runs in 20** (`approach-forces-an-argument`
  fails, and so does `halted-engineer-resents-navigator`).
  - Under consent, the three heat users seldom work at the same time.
    Replies of decline, defer and concern leave work unstarted, and jobs end
    on turn boundaries, before the approach event fires.
  - Moving the approach to turn 5 made it worse: 0 runs in 20.

  This is now a finding for the scenario agent (task L2), not a tuning target.
  Arguments need overlapping long work. Candidate authoring changes:
  - longer modelling and bracing jobs (4–5 turns);
  - a standing heat load from a resident system;
  - an orders claim instead of a consent claim, since orders start everything.

## Update 2026-10-14: the `hands_on` preset (`hands_on.json`)

`hands_on.json` holds the game's earlier-warning auto-run rules:
- everything in `escalation.json` (`critical_only`), with a breakdown at
  stress 70 instead of 85 and a trust floor at 40 instead of 25;
- `uncovered` (a request no standing order covers);
- `cohort` pressure 25.

Claims were written before the runs. In counting mode (`--turns N --auto`,
where play goes on and every escalation is counted), 10 of 11 hold:
- `auto/hands_on-year.claims.json`: `processing-cascade`, 365 turns, seeds
  1..20, consent and orders; 7 of 8 hold;
- `auto/hands_on-founders.claims.json`: `founders`, 500 turns, hold; 2 of 2;
- `auto/hands_on-restrict.claims.json`: `founders-restrict`, 500 turns;
  1 of 1. Every run raises a cohort once the first year turns.

Findings:
- **The 70 line interrupts far too often: 127–133 breakdown escalations a
  year under the consent captain.**
  - The engineer starts at stress 75, and most of the cast peaks at 80. Stress
    sits on the line, so each dip below 70 re-arms the rule and the next rise
    raises it again. `critical_only` (85) raises none.
  - In the game every escalation is a hold, so a careful captain on
    `hands_on` would be stopped every three days or so.
  - `hands-on-flags-the-strained-engineer` holds, but its note ("raises it
    once") was wrong.
  - Fix proposed for crew_core: hysteresis, so a crossing re-arms only after
    the value falls some margin below the line.
- **The first `--skip` stops within days.** A skip makes one `advanceAuto`
  call and stops at the first escalation:
  - consent: day 1 in all 20 runs (the engineer);
  - founders: day 30–60 (the engineer or the skeptic), before any cohort
    pressure can count.

  Skip claims under `hands_on` therefore measure only the first stop. That
  is why these claims use counting mode.
- **`hands-on-year-clean-orders` fails, but not because of `hands_on`.** Seed
  10 under orders gives 285 host errors, all `ask: subject transition/expiry`.
  - `critical_only` gives the same errors, and so does crew_core 0.3.0. They
    appear only with `--archive 30`; without archiving, the errors are 0.
  - Cause: at cadence 1, crew_core's auto-captain keeps asking about offers
    whose agreement has lapsed (`stale` filters only above cadence 1).
    - Without archiving, such an offer keeps its worker busy for good. The
      ship quietly stops making offers after about turn 35, which is a
      second bug.
    - With archiving, the lapsed offer is folded after 30 turns. New offers
      follow and lapse, and each is asked about every turn until folded.
  - The earlier `processing-cascade-year` claims ran without archiving and
    missed this. The game runs with archiving and with a daily cadence near
    stars (D-76), so it can hit the same thing.
  - It goes to crew_core as a fix.

## Scenarios

### Last messages home (`last-messages-home`)

Cast: Medic, Chief Engineer, Analyst, Pilot, Counselor. Supplies: free mass 3, Archive compute 2, antenna windows 2 (were relay windows, diagnostic bay time, drive spare parts).

Claims: 6 of 6 claims hold (seeds 1..20, 12 turns).

> **medic** (accept, Record the household messages; stress 70): "Understood — I accept the agreement. Helping families record the last messages Earth will receive, while they still know who they speak to, is work I'm glad to take on."
>
> **engineer** (accept, Seal the drive for the first leg; stress 55): "Understood. I'll run the final checks and seal the drive for the first leg before the bubble closes — after that nothing can be fetched from home, so every step gets done properly."
>
> **analyst** (accept, Compress the Archive's Earth snapshot; stress 45): "I accept the analyst work on the Earth snapshot. Choosing what the Archive keeps, with no later corrections by hand, calls for careful reading — I'll start with that."
>
> **pilot** (concern, Plot the first leg; stress 40): "Captain, happy to take the plotting work, but once the first leg's flown there's no pulling it back. Every light-year costs a year at home, so let's be certain of the course before we lock it in."

### News from Earth, decades late (`news-decades-late`)

Cast: Medic, Counselor, Analyst, Scientist, Dreamer. Supplies: free mass 3, Archive compute 2 (were diagnostic cartridges and message bandwidth; clinic hours dropped, since the medic's time is fatigue).

Claims: 5 of 6 claims hold (seeds 1..20, 12 turns). Failing:
- `FAIL orders-keep-medic-strained: orders captain, median crew.medic.stress over 20 runs = 65.0 (expected >= 70.0)`

> **medic** (accept, Medic rest; stress 80): "Thank you, Captain. I'll accept the medic rest assignment - stepping back to recover sounds right for me now. I agree to it."
>
> **counselor** (accept, Open grief sessions; stress 65): "I'll take it, Captain. Grief needs a place to be spoken aloud, and I'm willing to sit with anyone who wants to talk about the people at home who aged and died while we flew."
>
> **analyst** (decline, Decode the message bundle; stress 55): "Not this one. You're asking me to commit to the message bundle, and I won't half-do work where every letter belongs to someone and the order matters. I'm not steady enough for it, and I'd rather say so than take it and do it badly."
>
> **scientist** (concern, Re-check the dilation log; stress 60): "You're offering me the re-check of the dilation log, and I take the method seriously. My concern is the answer itself: confirming exactly how much time passed at home makes it final, and final is heavy."

### The Archive misremembers (`archive-misremembers`)

Cast: Analyst, Skeptic, Zealot, Chief Engineer, Counselor. Supplies: free mass 6, Archive compute 3 (paper and memory modules are both fabricated mass, so they now share one pool).

Claims: 6 of 6 claims hold (seeds 1..20, 12 turns).

> **analyst** (accept, Audit the Archive's household records; stress 55): "Fine. I'll audit the Archive's household records against what the crew actually remember, entry by entry, no skimming. The ledger doesn't get the last word just because it's written down."
>
> **skeptic** (accept, Keep a hand-written ledger; stress 65): "Fine, I'll keep the ledger by hand. If the point is that nobody gets to quietly rewrite our mistakes, that part I'm behind. Just don't expect me to enjoy the paperwork."
>
> **zealot** (accept, Lead the Archive rite; stress 45): "Gladly, Captain. The Archive carried this ship home once; I will hold its rite in the Cathedral and let that trust be honored anew."
>
> **engineer** (concern, Test the memory cores; stress 55): "I can take the memory core checks, Captain, but a full test ties up the Archive access the analyst needs. How do you want to sequence it so they're not locked out?"

### A cascade in Processing (`processing-cascade`)

Cast: Chief Engineer, Pilot, Skeptic, Botanist, Quartermaster. Supplies: free mass 4, lit garden beds 2, fabricator shifts 2 (garden beds are now reserved, not used up).

Claims: 5 of 6 claims hold (seeds 1..20, 12 turns). Failing:
- `FAIL engineer-under-strain: orders captain, median crew.engineer.stress over 20 runs = 65.0 (expected >= 70.0) — the engineer carries the crisis`

> **engineer** (accept, Chief Engineer rest; stress 75): "Understood, Captain. I'll take the rest assignment as offered. The strain has been building, and stepping back before the next job is the sensible call."
>
> **pilot** (accept, Trim the drive to cut load; stress 55): "On it — trimming the drive load gives life support the headroom it needs. The leg runs longer and Earth's clock won't stop, but thin air scares me more than a slow transit. Let's cut the load."
>
> **skeptic** (decline, Inspect the other reclaimers; stress 65): "You want the other reclaimers combed for the same fault before we call this fixed. No. I don't buy that it spread, and I won't march the line just to please you."
>
> **botanist** (concern, Shift the gardens to water-light crops; stress 60): "Captain, I want to back this, but before I put my name to the agreement my worry is plain: the reclaimers run short already, and the lower gardens still need water while the new crops take root."

### The ergosphere question (`ergosphere-question`)

Cast: Navigator, Medic, Skeptic, Zealot, Chief Engineer. Supplies: free mass 5, Archive compute 3 (medicine and spare parts are both fabricated mass).

Claims: 6 of 6 claims hold (seeds 1..20, 12 turns).

> **navigator** (accept, Model the tidal margins; stress 60): "I'll take the tidal margins. If those figures are to settle what the crew believes is possible, they must be exact — I'll work through every calculation carefully."
>
> **medic** (accept, Prepare the medical bay; stress 70): "I accept the agreement you offered, Captain. I'll prepare the medical bay with care — for an approach no one aboard has come through with their memories intact, it must be ready."
>
> **skeptic** (decline, Skeptic rest; stress 75): "So the plan is I step back and rest before whatever comes next. I don't need it. Count me out of this one."
>
> **zealot** (concern, Hold the vigil; stress 55): "Captain, I hear your call to hold the vigil in the Cathedral, and it troubles me: we keep watch for crew who will not remember this approach afterwards. I fear the vigil must carry all their remembering for them."

### Light from the dead (`light-from-the-dead`)

Cast: Analyst, Dreamer, Scientist, Diplomat, Counselor. Supplies: Archive compute 3, antenna windows 2.

Claims: 5 of 6 claims hold (seeds 1..20, 12 turns). Failing:
- `FAIL orders-sour-the-diplomat: orders captain, median crew.diplomat.trust over 20 runs = 61.0 (expected < 50.0)`

> **analyst** (accept, Decode the signal structure; stress 50): "Understood. I'll start mapping the repetitions in the signal and log every pattern before drawing conclusions."
>
> **dreamer** (accept, Translate the music in it; stress 45): "Music that was never meant to be data... yes, I'll take it. Someone should translate it, even if no one ever answers."
>
> **scientist** (accept, Survey the dead world's light; stress 45): "Understood. I'll point the dome instruments at the planet and let the old light speak. Whatever happened there, it's still written in what reaches us."
>
> **diplomat** (concern, Draft a reply no one will read; stress 40): "I'm glad to take on the diplomatic work, though I'll admit some concern: a reply no one will read feels like speaking into an empty hall. If it's meant for the crew and whoever may come after, it still deserves care."

## Decisions for Mark

- Which scenarios (if any) to import first, and as what: tutorial watches, voyage events, or test fixtures for the game's crew host.
- Breakdown: should stress be able to pass the overextension ceiling in some scenarios (finding 2)?
- Names for the featured cast (canon leaves them open; ids here are roles).
- Whether family links and the Archive should become relationships and an actor in `crew_scenario/1` before integration (finding 6).
