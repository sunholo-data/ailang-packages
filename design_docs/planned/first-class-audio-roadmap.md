# First class audio support in AILANG

**Status:** Roadmap accepted in session, 2026-10-23. Hardening and mono/stereo clips/editing are implemented in the unpublished 0.2.0 feature group; see [hardening evidence](audio-hardening-0.1.1.md) and [clip milestone](audio-clips-0.2.0.md). Core updates are assigned to another agent. Later milestones remain planned.
**Scope:** `sunholo/audio`, `std/audio`, and the small runtime boundaries needed by their consumers. Stapledon's game port remains with that project.

AILANG already supports deterministic sound generation, audio file output, offline measurements, and AI speech output. The next step should make these facilities safe to compose: validated formats, explicit channels and rates, bounded rendering, and evidence attached to the resulting bytes. Most sound processing should live in `sunholo/audio`; common file and sample conversions belong in `std/audio`. Runtime changes should serve a measured performance need or provide access to a host device.

## Current capabilities

The package baseline is the merged `audio-0.1.0` commit `e95368f`, included in main at `59ad5b0` and published as `sunholo/audio@0.1.0`. The installed toolchain is `v0.54.17-dirty`, commit `8f58117`. Core source inspection used the local checkout at `731fa1b`; installed CLI documentation and runtime probes confirm the relevant public behavior.

| Area | Available today | Boundary |
|---|---|---|
| Synthesis | Sines, exponential glides, vibrato, amplitude beats, seeded white noise and a legacy ramp generator | Mono; recipes render complete lists of floats |
| Shaping | Delay/attack/decay/stop envelopes, edge fades, swell, one-pole filters, sweeping low-pass, soft saturation, peak normalization | Small synthesis vocabulary; no general effects chain or sample player |
| Loops | Whole-cycle rules, periodic noise indexing, filter warm-up, seam measurement | Warm-up over two periods is an approximation to periodic filter state; structural rules are not an audible-seam proof |
| Mixing | Tiling loops, placing one-shots, sample-wise sums | A later one-shot cuts the previous voice; no polyphonic overlap policy, panning, buses, or rate conversion |
| Package PCM/WAV | Mono s16le encode and WAV output; integer-PCM RIFF metadata; first-channel s16le decode | No full channel-preserving decode; unsupported bit depth returns an empty list; metadata can be supplied separately from bytes |
| Stdlib WAV | `wavHeader`, `wavFromPcm`, `durationMs` | Integer PCM output only; no reader or checked format result; malformed/overflowing metadata and odd-byte padding need work |
| Stdlib compression | Pure deterministic Ogg Opus encoding of s16le, mono/stereo, 8/12/16/24/48 kHz, bitrate 6000–510000, input ceiling 100 MiB | CELT encoder; no compressed decode, 44.1 kHz resampling, or incremental encoder |
| Measurement | Peak and gated RMS in centi-dBFS, high-pass retention, low-band energy, seam steps | No standardized perceptual loudness, reconstructed true peak, spectrum, or general multichannel meters |
| AI speech | `std/ai.callSpeech` returns s16le, 24 kHz mono under the AI effect; speech stubs and fixtures exist | Provider support is separate from DSP; no provider-independent transcription function in the inspected `std/ai` surface |
| Live AI protocol | Registry `sunholo/gemini_live@0.5.1` provides audio message and transcript helpers; `std/stream` transports data | Protocol and transport support do not supply microphone capture, device playback, or a sample clock |
| Numeric foundation | Packed `Array[float]`, bulk arithmetic, scatter updates, f32/f64 byte codecs | Already implemented; a new generic float-buffer language type is unnecessary. Per-element immutable `set` still copies the array |
| Host output | WAV/Opus files can be passed to game engines, browsers, or applications | No built-in AILANG playback/capture API in the inspected stdlib |

The live registry search for `audio` returned `sunholo/audio` and `sunholo/gemini_live`; `dsp` returned `sunholo/audio`. Reuse these before creating another general audio package.

## Audit findings to address first

The [probe source](audio-audit-2026-10-23/audit_probe.ail) and [observed output](audio-audit-2026-10-23/probe-output.txt) preserve the following results. The interpreter and strict bytecode VM produced identical output.

| Finding | Observed behavior | Proposed action |
|---|---|---|
| WAV metadata validation | `wavInfo` accepts rate 0, an inconsistent block alignment, and RIFF size 0 on otherwise recognizable WAV bytes | Validate chunk boundaries and declared sizes, minimum format lengths, rates, alignment, frame completeness, and arithmetic limits before exposing data |
| Recipe validation | A depth of 2 is accepted; a string-valued rate silently defaults; a zero-frequency exponential glide is accepted | Distinguish missing fields from wrong types; validate parameter domains and relationships; add a checked programmatic constructor |
| Silent saturation | A valid silent sine layer with drive enabled returns five NaNs in a five-frame render | Handle zero peak before division; require finite output for checked rendering |
| Event ordering | `tile` with starts `[0,4]` yields `[1,2,3,4,1,2]`; `[4,0]` yields `[1,2,3,4,5,6]` | Specify ordering and voice policy; reject unsorted input or normalize it explicitly instead of selecting the last qualifying list element |
| Stdlib WAV padding | One byte of 8-bit mono PCM produces a 45-byte WAV, RIFF size 37, without the required pad byte | Correct stdlib RIFF padding and size accounting; preserve the data chunk's unpadded payload length |
| Stdlib field widths | `wavHeader(0,8000,65536,8)` encodes channel count 0 despite satisfying its positive-channel precondition | Validate field widths and multiplication before encoding; provide a checked Result-returning writer |
| Stdlib frame integrity | One byte of 16-bit mono PCM is wrapped as a WAV | Refuse partial frames in a checked writer |
| Resource bounds | Recipes bound seconds but not total frames, channel/sample products, layers, or total working memory | Add caller-supplied render limits checked before allocation; seconds alone do not bound work |

Further source-level concerns need targeted tests during hardening: short `fmt` chunks, truncated unknown chunks, duplicate chunks, invalid decoder offsets supplied by callers, non-finite programmatic parameters, low-cutoff noise-loop seams, and aliasing near Nyquist. These are investigation items, not additional reproduced failures.

## Trust as an audio feature

The public checked path should be: **untrusted recipe or bytes → validated description → bounded processing → validated encoded output → evidence report**. A pattern guard is an ordinary runtime decision; the trust comes from what it checks and whether all public paths enforce it.

| Mechanism | Audio guarantee to target | Evidence and limits |
|---|---|---|
| ADTs and checked constructors | Supported sample formats, channel layouts, valid rates, explicit units and error cases | Use existing records/ADTs and `Result`; an exported record alone does not prevent callers constructing invalid values |
| Guards at boundaries | Reject malformed chunks, invalid relationships, NaNs/infinities, unsupported formats, and excessive allocation before processing | These checks must execute in ordinary runs; do not depend on callers enabling optional contract checks |
| `requires` / `ensures` and Z3 | Integer field ranges, checked frame/byte calculations, clipping bounds, index bounds, and simple state transitions | Publish actual verified counts and proof assumptions. Recursive checks have an explicit unrolling bound; unsupported operations remain unproved |
| Runtime contracts | Detect programmer invariant failures while testing processing code | Explicitly enable `--verify-contracts`. Public bad-input handling should return typed errors rather than contract panics |
| Properties and native tests | Quantization error bounds, channel separation, duration accounting, repeatability, block partition invariance | Use constrained generators; skipped or discarded cases do not count as passing coverage |
| Independent references | Known WAV fixtures, analytical filter responses, reference resampler/loudness vectors | Round trips through two functions sharing a bug are insufficient; add external or closed-form oracles |
| Capabilities and budgets | Keep DSP pure; bound FS, Stream, Net and AI operations in adapters | `@limit` counts effects, not sample allocations, CPU, or audible duration. Enforce these separately |
| Output report and hashes | Identify the exact input, implementation, parameters, and delivered bytes; record measured output properties | A hash establishes identity, not correctness or authorship. A measurement is not a proof of its implementation |

Important numeric scope: the inspected SMT encoder maps AILANG floats to Z3 `Real`, and ints to `Int`. A mathematical proof is not an IEEE-754 rounding, NaN/infinity, machine-overflow, or cross-architecture byte-equality proof. Keep values in explicitly checked ranges and test the actual numeric behavior on supported engines and targets. Do not describe the full DSP pipeline as formally verified.

Propose a structured `AudioReport` with input/output hashes, package and toolchain versions, format/rate/layout, frame count, render limits, gain and clipping policy, non-finite count, clipped-sample count, per-channel peak/RMS, and any requested seam or loudness checks. Keep release proof/test evidence separately referenced by version; avoid a blanket `verified: true` field. Meter the final decoded/quantized output when making claims about delivered samples.

The initial trust milestone is a reliable checked API and more useful proofs at its boundaries. Perceptual quality and correctness of every floating-point operation require additional evidence; an increasing contract count alone is not the objective.

## Division of responsibility

| Location | Owns | Reason |
|---|---|---|
| `sunholo/audio` | Clips, recipes, synthesis, editing, mixing, panning, envelopes, filters, effects, block state, analysis, render limits and reports | Pure domain behavior can evolve and be tested as a package |
| `std/audio` | Common WAV metadata/read/write and PCM conversion; codec boundaries; a measured shared resampling primitive if justified | These should work identically for speech, imported recordings, procedural sounds, and non-package consumers |
| `std/array`, `std/bytes`, `std/math` | General numeric and binary operations | Reuse the packed array work already shipped; add only reusable missing kernels supported by benchmarks |
| Runtime and host integration | Efficient codec implementations; eventually device handles, queues, clocking, cancellation and platform cleanup | Hardware and lifecycle access cannot be supplied by pure package functions |
| Provider packages and `std/ai` | TTS, transcription/provider protocols, credentials, network sessions, AI budgets | Keep provider assumptions out of the DSP library; reuse existing speech and Live support |
| Application adapters | Godot export/import settings, browser playback, CLI commands, asset manifests | The game remains a consumer; its cues, engine settings and rollout stay in its repository |

No new language syntax or compiler change is required for hardening, stereo clips, basic effects, or pure block processing. Native PCM kernels and a resampler are possible runtime optimizations, not prerequisites for designing those package APIs.

## Proposed roadmap

Version numbers below are release candidates for planning. Each milestone should be split further if its compatibility or performance evidence warrants it.

| Order | Candidate | User outcome | Main ownership | Depends on |
|---|---|---|---|---|
| 1 | 0.1.1 hardening | Existing sounds remain stable; invalid inputs and silent renders behave predictably | Package, plus stdlib WAV fixes | Current release |
| 2 | 0.2 clip model | Import, edit, mix and export stereo without losing format information | Package; stdlib reader/PCM coordination | Hardening |
| 3 | 0.3 blocks and conversion | Process long clips with bounded working memory; convert speech/game rates correctly | Package, selected stdlib kernels | Clip model |
| 4 | 0.4 sound design | A useful synthesis and effects toolbox with explicit automation and voice behavior | Package | Clip model and block state |
| 5 | 0.5 analysis | Inspect spectra, dynamics, loops, and standardized loudness with reference evidence | Package, measured numerical kernels if needed | Clip model; block engine for large inputs |
| 6 | Offline 1.0 | Stable APIs and portable examples for games, speech files and media tools | Package and stdlib documentation | Earlier milestones and compatibility suite |
| 7 | Device exploration | Playback/capture and interactive processing through host adapters | Host/runtime design plus package adapters | Measured block engine; separate platform design |

### Hardening and trust boundaries

Add `validateRecipe` and a checked render entry point returning `Result`. Cover both JSON and direct API construction. Set limits on input bytes, frames, layers, channels and work size before allocating. Specify finite-value policy, invalid parameter domains, gain headroom and aliasing behavior.

Fix the zero-peak drive case; resolve event ordering; make WAV decoding return explicit unsupported/invalid errors. Keep the existing recipe's operation order, 32767 encoding convention, 32768 decoding convention, and reference PCM hash. Invalid-input changes and bug fixes need release notes; valid existing sounds must keep their bytes unless a breaking release is deliberate.

Acceptance: reproduce each audit case as a regression, keep all current pins, run property generators on valid domains, exercise runtime contracts, and increase meaningful boundary contracts. Start with simple integer functions that the verifier can handle; record skipped proofs by reason.

### Clips and stereo

Introduce a validated clip abstraction backed by existing `Array[float]`, with sample rate, explicit channel layout, and frame count. Prefer planar channels for package DSP; interleave only at PCM/codec boundaries. Require equal channel lengths. Permit finite internal headroom above full scale; apply an explicit Reject or Saturate policy on integer output. Dither, if offered, must take a seed and remain opt-in.

Add split/interleave, channel selection, explicit downmix, gain, trim, padding, concat, fades, crossfades, reverse, and stereo pan. Agree mono-to-stereo and stereo-to-mono coefficients before implementation. Avoid silent first-channel extraction and implicit sample-rate conversion. Stage PCM16 first; add PCM24 and float32 WAV deliberately, with extensible-WAV metadata handled correctly or explicitly rejected.

Acceptance: preserve left/right identity, frame counts and metadata on independent fixtures; reject mismatched rates/layouts; document quantization error and clipping behavior. New APIs can coexist with the list-based compatibility surface.

### Blocks and sample rate conversion

Model processing as explicit pure state transitions: a state and input block produce an output block and next state. Carry oscillator phase, filter history, random generator position and automation positions across block boundaries. Do not restart filters or fades for each block. Integer frame positions are the timing authority.

Whole-clip peak normalization requires a preliminary measurement pass, a replayable source, or a predeclared gain. Exact existing normalization cannot become a one-pass stream silently. Similarly, periodic noise-filter initialization needs its own policy rather than a fixed warm-up assertion.

Support a reference resampler with explicit input/output rates, anti-alias filtering, delay, output-length rounding and flush behavior. First coordinate the existing core proposal for s16le 24↔16 kHz; 44.1↔48 kHz and float clips are subsequent cases. Linear interpolation alone is not the quality default for downsampling. Add incremental PCM encoding and streaming peak/RMS; distinguish bounded DSP memory from filesystem streaming, because `readFileRaw` still reads the entire file. A bounded binary file-reader API is conditional on the chosen large-file workflow.

Acceptance: compare block sizes 1, 127, 128, 1024 and a single full block, including a short final block. Establish exact equality where operation order is identical, and documented numerical tolerances otherwise. Test DC, impulse, sine, out-of-band rejection, duration and flush tails. Benchmark 1/10/60-second mono and stereo clips at 48 kHz; record elapsed time, allocation/peak memory, engine, architecture and toolchain. Do not claim realtime throughput from unmeasured examples.

### Synthesis and effects

Add band-limited saw/pulse/triangle oscillators, ADSR, sample playback, pitch/time control with explicit resampling quality, and frame-based parameter automation. Add biquad low/high/band-pass and shelving/peaking EQ, delay/echo, compressor/limiter, and a small algorithmic reverb. Defer convolution and a large graph API until their costs and demand are established.

Add explicit polyphonic versus cut-previous scheduling, bus gain, stereo balance and pan. Keep saturation, peak normalization and limiting separate operations with distinct semantics. Give stateful effects a reset/flush/tail policy; verify filter parameter bounds and test frequency response and stability across supported rates.

Acceptance: alias-rejection and response tests, deterministic seeded output, automation continuity across blocks, bounded tails and final quantization checks. Existing recipes retain their render identity; a versioned recipe schema carries incompatible semantics.

### Analysis and perceptual loudness

Add DC offset, unclipped/full-signal RMS, crest factor, clipping detection, silence segmentation, windowing, FFT/STFT, spectral bands and spectrogram data. Label existing gated RMS clearly; it is not a LUFS meter.

Implement standardized loudness and true-peak measurement against a pinned revision of [ITU-R BS.1770](https://www.itu.int/rec/R-REC-BS.1770/en), with the required channel weighting, filters, gating and reference vectors. Add EBU-specific reporting only against its own selected specification and tests. A sample peak is not a reconstructed true peak. Expose data for plots without giving the DSP library filesystem or UI effects.

Acceptance: known spectra and analytical signals; agreement with independent reference vectors within declared tolerances; explicit handling of silence, short clips, layouts and unsupported channels. FFT/codec acceleration moves upstream only after a reproducible bottleneck is demonstrated.

### Stable offline support and host adapters

An offline 1.0 should cover three complete flows: recipe → bounded stereo render → measured WAV/Opus; imported WAV → edit/resample → output; fixture-backed TTS PCM → clip → gain/measurement → file. Ship short examples, a format support table, machine-readable error/report examples, documented limits and a compatibility suite. Game asset generation can demonstrate consumption without requiring changes to Stapledon's port.

Explore browser/Web Audio and native host adapters after that foundation. The [W3C Web Audio Recommendation](https://www.w3.org/TR/2021/REC-webaudio-20210617/) separates offline rendering, buffers and live contexts; use it as a host-integration reference rather than copying its whole graph into AILANG.

A device API needs negotiated formats, bounded queues, underrun/overrun reporting, cancellation, timestamps, device loss and scoped cleanup. Reuse capability enforcement, but settle IO versus a dedicated Audio effect in that design rather than assuming a nonexistent capability today. CLI, embedded and WASM hosts must return typed Unsupported errors where appropriate. The garbage-collected VM has no established hard realtime guarantee; use a host-owned audio thread and measure latency before offering interactive DSP promises.

Compressed input support is a separate decision: prioritize Ogg Opus decode if consumers need to round-trip the existing output, then evaluate FLAC/MP3/Vorbis by demand, conformance, licensing, portability and maintenance. Do not require shell codecs for the base library. MIDI/sequencing, spatial/HRTF audio, transcription, denoising, plugin hosting and music generation are later package/adapter opportunities, not dependencies of the first offline release.

## Compatibility and release evidence

Preserve the v1 recipe schema and the legacy noise generator. Adding a required field to an exported `Recipe` or `Layer` record can break source consumers even if JSON has a default; introduce a new type/constructor or make the breaking change explicit. Keep existing functions as compatibility adapters while checked clip APIs mature.

For every release, run package checks, native package tests, source-module inline tests/properties, smoke, raw verification and `ailang pkg quality`. Use meaningful contracts and document every unresolved warning. A strict-quality goal should address the current 33 uncontracted exports with real invariants or a deliberate public-surface review, not vacuous annotations. Test engine parity; maintain separate architecture/WASM evidence before expanding portability claims.

| Baseline check | Observed result on this toolchain |
|---|---|
| Compile | 14 files pass in the session's quality run |
| Contracts | 2/12 verified, 0 counterexamples, 10 skipped, 0 errors; 33 uncontracted exports |
| Raw skipped reasons | Five have no `ensures`; five encounter unsupported encoding of folds/map/log/round. The quality report groups these under PUB016 |
| Verified functions | `clamp16` and `absF`, within the verifier's numeric model |
| Interface | v2 `fb89f45aa833…`, 51 signatures, from the installed-toolchain quality run |
| Effects | Declared ceiling `[IO]`, rank IO; all 45 exported functions pure; IO is used by smoke |
| Release | `feature`; matching changelog section present |
| Docs | AGENT.md and AI summary present |
| Package tests and smoke | 51 passed, 0 failed across 6 test files; smoke passed |
| Source DSP tests | 6 inline examples passed; 5 generated properties passed at 100 cases each; 1 property skipped because its generated input violated `onePole`'s precondition |
| Audit probes | Interpreter and strict-bytecode outputs identical; observations above reproduced |
| Quality caveat | No gates; registry export-overlap check was unavailable because the sandbox could not reach the index |

The [raw verification report](audio-audit-2026-10-23/verify.json) preserves per-function outcomes. Compilation, attested test execution, mathematical proof and listening/reference checks remain separate evidence categories.

## Upstream coordination

The open [core request 1930](https://github.com/sunholo-data/ailang/issues/1930) already requests a WAV reader, PCM16 decode and fixed-precision formatting. Core's [implemented std/audio design](https://github.com/sunholo-data/ailang/blob/731fa1b958bc8268889ede0ae90e6165cf1897fc/design_docs/implemented/v0_44_0/m-std-audio.md) already leaves resampling as planned M3. Extend those efforts rather than filing the same feature again.

Three focused messages were sent through `ailang messages` to the canonical Firestore core `user` inbox in project `ailang-multivac`. Each send confirmed Pub/Sub notification; a subsequent listing confirmed all three messages are present and unread. Package features can proceed while those requests are triaged; no core implementation date is assumed.

| Request | Canonical message ID |
|---|---|
| Reproduced stdlib WAV padding, field-width and partial-frame behavior | `inbox_1792742860257_d0cd3f0f` |
| Coordinate WAV/PCM boundaries with issue 1930 and the existing resampling M3 | `inbox_1792742861419_98f58254` |
| Distinguish verification skips and expose the numeric model and proof scope | `inbox_1792742862200_201d0d83` |

## Reproducing the audit

The checked-in probe is audit evidence, not a test module exported by the package. From the repository root, copy the baseline into a temporary directory and place the probe inside that package so its relative imports resolve:

```sh
audio_audit_dir=$(mktemp -d)
git archive e95368f4acbaf04d70fee0eee2a8c971f6bd9e9c packages/audio | tar -x -C "$audio_audit_dir"
cp design_docs/planned/audio-audit-2026-10-23/audit_probe.ail "$audio_audit_dir/packages/audio/_audit_probe.ail"
ailang run --quiet --relax-modules --caps IO --entry main "$audio_audit_dir/packages/audio/_audit_probe.ail"
ailang run --quiet --relax-modules --bytecode --strict-bytecode --caps IO --entry main "$audio_audit_dir/packages/audio/_audit_probe.ail"
rm "$audio_audit_dir/packages/audio/_audit_probe.ail"
ailang verify --package "$audio_audit_dir/packages/audio" --json
ailang test "$audio_audit_dir/packages/audio/dsp.ail"
ailang pkg quality "$audio_audit_dir/packages/audio"
```

The probe prints observations of existing defects; it does not assert that those behaviors are correct. The [source test log](audio-audit-2026-10-23/dsp-inline.txt) includes the skipped property and replay seed. Future fixes should turn the observations into meaningful regression assertions with the intended behavior.

## Source references

- [Package source at the merged audio commit](https://github.com/sunholo-data/ailang-packages/tree/e95368f4acbaf04d70fee0eee2a8c971f6bd9e9c/packages/audio): recipe, PCM, DSP, mix, analysis and tests.
- Installed `ailang docs std/audio`, `std/array`, `std/bytes`, `std/math`, `std/fs`, `std/stream`, `std/ai`; live registry `pkg info`, `versions`, and `search` results.
- Local core `std/audio.ail`, `internal/builtins/audio*.go`, `std/ai.ail`, `internal/eval/value.go`, `internal/smt/types.go`, and contract/capability-budget documentation.
- [Microsoft RIFF layout](https://learn.microsoft.com/en-us/windows/win32/xaudio2/resource-interchange-file-format--riff-): chunk lengths, sizes and WORD padding; [WAVEFORMATEXTENSIBLE](https://learn.microsoft.com/en-us/windows/win32/api/mmreg/ns-mmreg-waveformatextensible): valid bits, subformats and channel masks.
- [RFC 7845](https://www.rfc-editor.org/rfc/rfc7845): Ogg Opus encapsulation, pre-skip and end trimming; consult its updates when extending codec support.

