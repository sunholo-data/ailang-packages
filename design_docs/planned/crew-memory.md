# Crew memory: recall and variety from local embeddings

**Status:** Spike done (2026-10-13); design proposed, not planned.
**Package:** `sunholo/crew_lab` (local only; never published). The pure part
may later move to `sunholo/crew_core`.
**Game design:** stapledons-design `features/next/semantic-memory.md` (#19), stage S2 (crew recall), which owns the memory design; this is the lab prototype and its measurements. Also `inner-shapes-outer.md` §5 (#20).

## Problem

Over a long run, crew words repeat, and a crew member never refers to what
happened before. The prompt only knows the current moment. Mark's direction
(2026-10-13): embed locally with EmbeddingGemma 2 on Ollama. The same memory
later serves:
- the Archive's unreliable recall;
- contact history;
- the cross-run déjà-vu library.

## Spike (done)

- **`memory.ail`** (pure, exported, contracts, 7 tests on both engines):
  - `recall`: the k most similar earlier entries, by actor, above a floor;
  - `echoes`: same-actor lines inside a window that read as repeats;
  - `margin`: how far the best match leads the runner-up;
  - `pick`: a recaller that takes the runner-up under a small margin and a
    seeded roll (the Archive's near-miss);
  - ties go to the older entry, so ranking never depends on list order.
- **`recall_spike.ail`**: embeds the 120 sampled lines of the Stapledon pack
  (two wordings per moment) and reports calibration, echoes and recall.
  Report: `examples/crew-lab/spikes/recall-spike-2026-10-13.txt`.

Run it (needs Ollama with `embeddinggemma-2`; no provider spend):

```sh
cd examples/crew-lab
R=scenarios/stapledon/review
ailang run --caps IO,FS,Env --entry main recall_spike.ail embeddinggemma-2 \
  $R/last-messages-home.samples.ndjson $R/news-decades-late.samples.ndjson \
  $R/archive-misremembers.samples.ndjson $R/processing-cascade.samples.ndjson \
  $R/ergosphere-question.samples.ndjson $R/light-from-the-dead.samples.ndjson
```

### Findings

The run made 300+ embeddings in 16 s (768 dimensions).

| Pairs (document prefix) | Median cosine | Share at ≥ 0.85 |
|---|---|---|
| Same moment, two wordings | 0.85 | 26/60 |
| Same actor, other moment | 0.86 | 19/30 |
| Same scenario, other actor | 0.71 | 0/240 |
| Other scenario | 0.71 | 8/1500 |

1. **Embeddings capture the speaker more than the event.** Two wordings of
   the same moment score no higher than the same crew member on another
   occasion. Recall by meaning alone cannot tell "the same thing again" from
   "this person again".
2. **Repeats are detectable.** At ≥ 0.90 there are 9 to 11 same-actor pairs
   from different moments. All are the same request offered again (for
   example the zealot asked twice to lead the Archive rite, at 0.95). This is
   exactly the variety check's job.
3. **Recall is plausible but weakly separated.** Examples:
   - the skeptic's reclaimer inspection recalls their hand-kept ledger;
   - the medic preparing the bay recalls their own rest;
   - the dreamer translating alien music recalls writing the Cathedral
     remembrance.

   The best match leads the runner-up by only 0.00 to 0.08. A recall line
   needs a margin floor, or a second signal.
4. **The task prefix helps a little** ("title: none | text: "): it halves the
   other-actor false matches at 0.80.
5. **`_ollama_embed` aborts the whole run on failure** (model missing, Ollama
   stopped). Reported as ailang#1798. Until there is a Result form, embedding
   runs in a worker process.

## Design

- **Where:** the reply worker (`crew-reply-worker`) embeds and recalls. The
  watch stays AI-free and never blocks; an Ollama failure ends only that
  worker, and the reply still arrives without memory.
- **Memory store:** an append-only `memory.ndjson` per crew home. Each line is
  an id, actor, tick, text and the vector (base64 f32). The size is capped
  and the oldest lines go first.
- **Variety check:** before accepting new words, `echoes(..., window 200
  ticks, threshold 0.92)` against the same actor. A hit means the alternate
  wording is chosen, or the words are regenerated once.
- **Recall:** query with the situation (actor, request, reaction, the resource
  or value at stake). Accept the best hit only if its score is at least 0.75
  and its margin at least 0.05, and boost hits that share the same scenario
  resource or value (a structured second signal). Pass one recalled line into
  the prompt as "You once said: …".
- **The Archive:** `pick` with the Archive's memory health as `confusion` and
  `chance`. That is design data for archive-voice phase 2, not built here.
- **Determinism:** the domain journal never contains memory. Words, as
  before, are transport-only `wording` records.

## Compaction: memories that change as they are remembered

**Status:** proposed (Mark, 2026-10-14); the game design is stapledons-design semantic-memory §S2b.

A voyage lasts decades, and the memory store above is capped. Rather than
dropping the oldest lines, old memories are **compacted**: an AI pass
rewrites a span of a crew member's memories into fewer, shorter ones, the way
a long chat is summarised. Unlike a chat summary, compaction is meant to be
unfaithful in human ways.

### Game design (lives in the design repo)

What compaction means for the game is specified in stapledons-design
`features/next/semantic-memory.md` §S2b (#23): memories are coloured by the
present and the past, memories of memories degrade, first-hand significant
events last longer, the Archive misremembers by its Memory Health and crew by
personality and state, and players only hear memories in dialogue (Mark's
rulings, 2026-10-14). This doc is the lab's mechanism for that design.

### Mechanism: numbers decide, AI only words

The rule from R2-CREW holds: **AI text never decides anything.**

- **A memory record:**
  - `id`, `actor`, `sources` (event and memory ids), `span` (first..last
    tick);
  - `generation` (0 for a first-hand memory);
  - `fidelity` and `salience`, 0..100;
  - `tone` (−100..100, toward the captain or the people involved);
  - `state` (the crew member's bands at compaction);
  - `text`.
- **Deterministic and pure (lab first, later crew_core):** integers and the
  run's seed only.
  - When to compact: at a year turn, when someone departs, at the end of a
    skip, or when the store reaches its cap.
  - Which records: the lowest salience among the oldest.
  - The new numbers:
    - fidelity = the parents' fidelity × a retention rate, less a stress
      term. The rate is about 85/100 for ordinary memories and about 95/100
      for first-hand memories of significant events (loss, first contact,
      deep time, betrayal, a large trust or regard change), so those last for
      decades (Mark, 2026-10-14);
    - tone moves a bounded step toward current trust and regard
      (reconsolidation);
    - salience is the parents' maximum plus a recall bonus.
  - Tested on both engines, and the same seed gives the same numbers.
- **AI (the reply worker, never the watch or the game's core):** writes the
  compacted text from the parent texts, the new numbers and the state.
  - The numbers become instructions in the prompt. For example: "fidelity
    40: keep the gist and the feeling, lose names and numbers; you now
    distrust the captain".
  - The model is local where possible (Ollama, as for embeddings).
- **Checks on the words:**
  - length;
  - no identifiers;
  - no people or events outside the sources;
  - tone agrees in sign with `tone` (an embedding against valence anchors).

  Misattribution (who did what, when, in what order) is allowed only below a
  fidelity floor, by a seeded roll. Its chance comes from:
  - **the Archive:** its memory health;
  - **crew:** personality and state at compaction, with no separate trait.
    - Low conscientiousness loosens details.
    - High neuroticism pulls memories toward threat and blame.
    - High openness fills gaps with plausible invention.
    - High stress or fatigue raises the chance, and age raises it slowly.

  Two crew members can then remember one event differently because of who
  they are and what they were going through.
- **Cache and offline:**
  - Cached by a hash of the parent hashes, the numbers, the state, the prompt
    version and the model, like the sampled words. Replays and offline play
    reuse it.
  - With no model, a template writes the gist from the numbers ("Years ago,
    something about the reclaimer. Still bitter.").
- **Where memories are used:** only in what crew and the Archive say
  (dialogue prompts). Players hear memories; they never see a list of them
  (Mark, 2026-10-14).
  - Grievance, trust and regard stay as numbers in crew_core; behaviour never
    reads memory text.

### Acceptance (when planned)

- **Pure tests:**
  - fidelity never rises across generations;
  - tone moves toward current trust and never past it;
  - salience orders survival;
  - the same seed and inputs give byte-identical records on both engines.
- **Lab claims over a century skip** (founders, the v3 profile):
  - no memory store exceeds its cap;
  - memories over 30 years old have fidelity under 40;
  - after a betrayal, the betrayed crew member's memories of the captain have
    a lower median tone than a control run's.
- **Words:**
  - compacted text names no identifier;
  - compacted text names no person absent from its sources (above the
    misattribution floor);
  - offline play gives the template text, and the run completes.

Rulings and their rationale: design repo §S2b, not repeated here.

## Acceptance (for the sprint, when planned)

- `make memory-test`: pure tests on both engines. A fixture memory with a
  known repeat triggers the variety check; one without does not.
- `crew-sample --memory`: on the pack, the share of same-actor near repeats
  (≥ 0.92) across samples falls compared with the run without memory, and
  no recalled line names an identifier.
- Ollama stopped: the watch still plays; replies arrive without memory, and
  one notice is journalled.
