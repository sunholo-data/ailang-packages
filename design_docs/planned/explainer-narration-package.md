# sunholo/explainer — film narration in AILANG

**Status:** planned → implementing 0.1.0 (2026-10-26). **Asked by:** Mark ("lets port it across",
on the explainer-film pipeline in `~/dev/sunholo-data/ailang-explainers`).

## Problem

Sunholo's explainer films are made with Arni Westh's Manim kit (`ailang-explainers/kit/`, kept
byte-identical to upstream). The kit voices each line with Kokoro, offline. For `world_intro` we
narrate in Gemini Sulafat instead, and the glue that does it is Python
(`films/narrate/gemini.py`), with only the speech call in AILANG. It holds the parts of the
pipeline that are ours, and the ones that can be checked:

- voice the whole script in **one** call (one call per line drifts: measured line-to-line pitch
  spread 52 Hz per-line vs 22–39 Hz one-take);
- align Whisper's word timings to the script and cut the take into lines, each cut in the
  longest pause between one line's last word and the next line's first;
- trim and level each line the way the kit levels its own clips, and file it in the kit's cache.

## What moves, what stays

| Part | Where | Why |
|---|---|---|
| Drawing, frame geometry lint, rendering, mixing, the film's checks | **kit (Python/Manim)** | AILANG has no graphics stack; the kit is Arni's and changes go upstream |
| Reading a film's lines, the kit's clip-cache key (sha1) | **kit**, via a thin adapter | the kit owns its cache format; `std/crypto` has no sha1 |
| Speech-to-text word timings | **faster-whisper**, via the adapter | a local model; AILANG calls it as an external tool |
| Script → take text, voice id, take name | **package** `take` | pure |
| Word normalisation | **package** `words` | pure, inline tests |
| Alignment (difflib's matching blocks, re-implemented) → each line's first/last word time | **package** `align` | pure; same blocks as Python's `SequenceMatcher(autojunk=False)` |
| Cut points (10 ms frame energy, longest quiet run in a ±150 ms window) | **package** `cut` | pure; integer core with Z3 contracts |
| Trim + level + PCM16 per line | **package** `level` | pure; integer window contracts |
| The Gemini call with retries | **package** `narrate` | `! {AI}` |
| Orchestration (adapter → speak → words → cut → write clips) | `ailang-explainers/films/narrate/narrate.ail` | the app; uses the package |

Speed: per-sample work runs on the bytecode VM (`--bytecode`); one pass over a 6-minute take
(7.4 M samples) takes 1.1 s there, 56 s in the tree-walking evaluator.

## Registry reuse

| Part | Decision | Reason |
|---|---|---|
| Subprocess + JSON (adapter calls) | **depend** `sunholo/external_backend` 0.2.0, in the orchestrator | same job; better process-error messages than a hand-rolled `exec` |
| Levelling, PCM16, WAV | **none** (`sunholo/audio` 0.5.0 checked) | its `levels` uses active-window RMS and peak-limited gain, not the kit's plain RMS + clip at 0.98; PCM16/WAV are the same `std/audio` builtins either way |
| Voicing | **none** (`sunholo/gemini_live` 0.5.1 `tts` checked) | raw REST over Net; this package uses `std/ai.callSpeech` (AI effect, budgets, trace) |
| Alignment, word normalisation, cut points | **none** | no registry package does these |

(Recorded after the first draft: the registry was searched on review, and the orchestrator's
hand-written `exec` adapter was replaced by `external_backend.runJson`.)

## Interfaces

```
take.uniqueLines([string]) -> [string]
take.takeText([string]) -> string                       -- lines joined by blank lines
take.voiceId(voice, language, model, style, [string]) -> string
take.takeFile(voiceId) -> string                        -- "take-<sha256[:16]>.pcm"
words.normalise(string) -> [string]
align.lineSpans([string], [Heard]) -> Option[[Span]]    -- None if any line has no matched word
cut.cutPoints(Array[float], [Span]) -> Option[[int]]    -- sample offsets, strictly increasing
level.levelClip(bytes pcm, int from, int frames) -> Option[bytes]   -- WAV, mono s16 24 kHz
narrate.speak(text, voice, style, options, tries) -> Result[bytes, AIError] ! {AI}
narrate.cutTake(bytes, [Heard], [string]) -> Result[[bytes], string]
```

## Acceptance

1. On the approved `world_intro` take (sixth cut), the AILANG cut gives the **same 44 cut points**
   as `gemini.py`, and every line's clip has the same length and is within 1 LSB per sample.
2. `ailang test --package .`, inline tests, `ailang verify` on the integer cores, and
   `ailang pkg quality .`: numbers reported as printed.
3. `films/narrate/explainer-gemini render films/world_intro.py` runs through the AILANG
   orchestrator and the kit's checks pass (lint 0/0, sync ≤ 80 ms, loudness −17 LUFS).
4. `gemini.py` is retired; the kit stays byte-identical to upstream.

## Not in 0.1.0

- Speaker turns (two voices): `std/ai.callSpeech` has no multi-speaker mode; an AILANG feature.
- Line-at-a-time voicing (`GEMINI_TAKE=line`): it drifts; dropped with the Python driver.
- Publishing to the registry: after Mark says so.
