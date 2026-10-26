# Audio 0.3: generic package scope

Status: audio 0.3.0 released, 2026-10-23. Checked levels, the stateful
filter block foundation and headless fixture examples are published.
See the [release record](../implemented/audio-release-0.3.0/README.md);
The [0.4 release](audio-0.4-ai-daw.md) adds delay and gain ramps;
broader parameter smoothing and the shared report schema remain recommendations.
See [block evidence](../implemented/audio-blocks-0.3.0/README.md).
Loop Lab is a reference application, with its own standalone repository
and release lifecycle: [application split](loop-lab-repository-split.md).

## The common boundary

`sunholo/audio` operates on audio, independently of its source:

    procedural recipe / recording / TTS PCM / model-generated samples
      → checked Clip → processing → measurements/report → explicit encoding

An AI can also propose a typed/JSON recipe, which passes through existing checked
parsing and bounded deterministic rendering. This is procedural generation driven
by model-produced data; it does not make the DSP library a neural generative model.
`std/ai.callSpeech` already supplies an effectful speech-generation boundary.
Other speech/music/model providers belong in adapters with explicit credentials,
effects, cancellation and budgets. Pure processing should need no AI capability.

Current generic support: mono/stereo finite clips with explicit rates and limits,
procedural synthesis, checked editing/mixing, PCM16/WAV adapters and level plans.
Multichannel, compressed-input decode, arbitrary sample-rate conversion, full streaming
DSP and model inference are not supplied by the current package. A supported PCM
output can be consumed now; unsupported provider formats need an explicit adapter.
Coordinate the existing resampling work rather than assuming v0.54.18 shipped it.

## Generic feature group and remaining additions

| Priority | Generic deliverable | Multiple consumers served |
|---|---|---|
| 1 | Checked stateful block-processing contract and first filter/delay processors, plus bounded parameter smoothing | Game effects, generated sounds, speech shaping, offline media processing and Loop Lab |
| 2 | Shared machine-readable processing/report metadata: format/rate/layout, frames, input/output identity, applied gain/processor settings, peak/RMS and limit decisions | Batch AI pipelines, reproducible asset builds, headless validation and application inspection |
| 3 | Small headless consumer examples: checked procedural/AI-proposed recipe and fixture-backed TTS/model PCM → clip → processing → measured WAV | Demonstrates generic generation/processing without a DAW or browser |

Current checkpoint: `block` has low/high-pass/bypass, reset and bounded per-channel
state; both headless example paths run on the interpreter and strict VM with
runtime contracts. Processing reports in those examples are metadata, not yet the
shared typed AudioReport API. The released [0.4 effect group](audio-0.4-ai-daw.md)
adds delay and gain ramps independently of Loop Lab's UI/persistence schedule.

For processors, define state + input block + parameters → output + next state,
with explicit layout/rate, reset/flush/tail behavior and caller resource budgets.
Reuse existing numerical primitives while preserving legacy DSP order/byte pins.
Keep presets and musical tempo policy in consumers; the delay API should accept
explicit frame/time parameters. Add stereo/state/partition tests, analytical
impulse/frequency fixtures and measured performance before a callback claim.

Reports distinguish mathematical proofs, executed guards, observed measurements
and provenance. Model name/seed/response identity may be optional caller metadata;
do not automatically retain private prompts or recordings. Hashes identify bytes,
not musical quality, model accuracy or correctness. Measure delivered/quantized
output where that is the claim. Never replace these fields with a blanket verified flag.

Examples should run with deterministic fixtures in normal CI; external inference
is an explicit optional integration. Provider/sample errors return typed failures.
Verify finite samples, channels/rates, frame budgets, headroom and byte counts;
these checks do not establish that generated speech/music has the intended meaning.

## Application work, independently scheduled

Loop Lab owns session save/load, UI controls, capture, browser/native playback,
track history, hum-to-note editing, instruments, musical timing and Live/plugin
integration. Reusable algorithms may graduate into audio or music packages after
their domain is clear. A useful application feature is not automatically a new
generic audio export or a package-release prerequisite.

The next standalone application milestones can remain save/load, WAV import and
hum-to-bass. The package's 0.3 milestone should be judged against generic processors
and headless generation/processing flows as well as Loop Lab's consumer tests.
