# Audio 0.4: AI-output processing and DAW foundations

Status: delay and gain automation released in audio 0.4.0, 2026-10-26.
[Release record](../implemented/audio-release-0.4.0/README.md),
[implementation evidence](../implemented/audio-effects-0.4.0/README.md).
The [Audio Tools demo design](https://github.com/sunholo-data/ailang-demos/pull/3)
consumes this version; existing consumers choose their own dependency upgrades.

The package operates on samples independently of who produced them. The DAW
application owns tracks, arrangement, devices, transport, permissions and projects.
AI/provider adapters own generation requests, formats, credentials and cancellation.

## Implemented feature group

| Feature | AI/media use | DAW/application use |
|---|---|---|
| Bounded mono/stereo feedback delay | Echo generated speech, textures and model PCM; render explicit tails in asset pipelines | Echo/send processing, with host-owned time/tempo conversion |
| Frame-defined linked gain ramps | Fade generated chunks, transition levels without restarting every block | Volume automation and worker-prepared fades; sample positions supplied by host |
| Delivered-WAV fixture evidence | Check provider-format import, output levels and immutable byte identity | Test rendering/export separately from playback/device timing |

The effect example uses synthetic fixture PCM, not a paid model call. The installed
v0.54.18 `std/ai.callSpeech` returns raw PCM and exposes `speechSampleRate()`; the
existing checked PCM importer provides the sample boundary. Real provider calls
remain an optional effectful consumer, with explicit request/output budgets.
The pure package never receives credentials or requires an inference account.

## Next generic package work

1. **Shared processing report.** Define a versioned typed report and JSON encoding
   for format/layout, frames, input/output byte identities, ordered processor
   settings, gain/limit decisions and measurements of delivered audio. Keep
   mathematical proofs, executed guards and observed measurements distinct.
   Provider/model/seed identity is optional caller metadata; private prompts and
   recordings are not retained automatically.
2. **Provider integration example.** A separate application/example owns one
   bounded AI speech request, imports its declared format, processes it with this
   package and explicitly writes the result. Unit tests use the same PCM fixtures;
   a real-provider acceptance run requires configured credentials and is reported
   separately. Model text/meaning quality is outside DSP validation.
3. **More effects.** Biquad EQ, compressor/limiter, parameter-specific smoothing
   and reverb, with independent response/impulse fixtures and state/partition tests.
   Gain ramps do not automatically smooth delay time, feedback or filter cutoff.
4. **Format/conversion coordination.** Use shared std/audio codecs and coordinate
   resampling upstream; do not infer support for arbitrary rates or compressed
   input from PCM16/WAV support. Preserve the existing quantization conventions.

## Next Loop Lab / DAW work, in its own repository

1. Save/load project metadata and explicitly committed audio; validate versions,
   byte/frame budgets and missing assets before changing the current session.
2. Checked WAV import and export with an explicit rate/layout policy. Imported
   files and generated audio should enter the same prepare/stage/commit boundary.
3. Effect/send controls and automation scheduling. The host uses the reference
   package behavior, while worker/worklet adapters have their own parity tests,
   allocation/deadline evidence, cancellation and stale-revision handling.
4. Hum-to-note/instrument workflow and arrangement, then native Live/plugin
   adapters. The pure package does not become a VST host or DAW project format.

Timing probes favour bytecode for preparation. They include CLI startup and full
validation, and do not establish callback deadlines. A host-owned render thread or
worklet remains responsible for realtime execution and device behavior. No new
core runtime boundary is needed by this effect group; the reproduced record-Eq
property-evaluator bug has been sent upstream independently.
