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
