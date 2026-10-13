# Stapledon crew scenarios (draft pack for review)

Six watch-sized crew situations drawn from the Stapledon's Voyage design canon
(`stapledons-design`), written as `crew_scenario/1` files with `crew_claims/1`
expectations. They are candidates for import into the game once the crew host is
integrated; nothing here is canon until reviewed.

Each scenario is a small cast from the proposed featured crew (roles from
`features/next/crew-assignment-system.md`, archetypes from
`features/future/crew-psychology.md`; names are still open, so ids are roles). The
reactions are authored (OCEAN traits, values, fatigue, stress, morale, trust); the
model only writes words, through the same prompts and checks as the watch.

| File | Situation | Canon |
|---|---|---|
| `last-messages-home` | Departure: the last messages Earth will receive, the drive sealed, the Archive's last Earth snapshot | Only information crosses the bubble wall (`bubble-constraint.md`); the medic's sibling on Earth (`art/generation-cast-plan.md`) |
| `news-decades-late` | After a 0.99c leg, decades of messages arrive; the medic's sibling died | "Every journey costs relationships outside the ship" (`core-pillars.md`); dilation figures (`journey-system.md`) |
| `archive-misremembers` | The Archive's household records contradict what the crew remember; Loyalists and Skeptics | Archive memory health and factions (`archive-crew-trust.md`) |
| `processing-cascade` | A failed water reclaimer eats finite repair mass; gardens shift crops | Mass budget and repair sinks (`mass-budget.md`); no routine meters, pressure in crisis (`design-decisions.md`) |
| `ergosphere-question` | Before a black-hole approach: tidal margins, a vigil, a skeptic's right to refuse | Black-hole dread and refusal (`black-holes.md`, `design-decisions.md`) |
| `light-from-the-dead` | A repeating signal from a civilisation already extinct | "Ruins, signals or light from the dead" (`life-and-intelligence-parameters.md`) |

## Run them

```sh
P=examples/crew-lab/scenarios/stapledon
crew-sim --check $P/news-decades-late.claims.json --scenario $P/news-decades-late.json
crew-watch-offline --scenario $P/news-decades-late.json          # play it, no provider
crew-watch --scenario $P/news-decades-late.json --home ~/.ailang/crew-lab-stapledon
crew-sample --scenario $P/news-decades-late.json --home ~/.ailang/crew-lab-stapledon --report words.txt
```

The words sampled for this review were saved in `~/.ailang/crew-lab-stapledon` on the
machine that ran them (not in the repo). With that home, the live watch and `crew-sample`
reuse them; anywhere else, sampling makes new provider calls (or use `crew-sample-offline`).

## What the claims say today

Claims were written as design intent before running them; failures are findings,
not tuned away. See `REVIEW.md` for the results, sampled words and open questions.
