# Changelog

## 0.4.0

Feature candidate: bounded feedback delay and frame-defined gain automation. Not yet published.

- `delay`: checked mono/stereo integer-frame delay with independent channel
  histories, signed feedback (-0.99..0.99), dry/wet gains, explicit silence tails
  and reset. Batch ring writes avoid a full history copy on every sample.
- `automation`: linked 0..64 linear-gain ramps with exact target frames, immediate
  changes and mid-ramp retargeting from the last delivered gain. Absolute ramp
  positions preserve output across block partitions.
- Both APIs validate public states, finite samples, rate/layout, block and
  cumulative budgets; delay has a separate history allocation budget. Headroom
  is preserved; arithmetic overflow returns typed errors. No callback guarantee,
  delay-time interpolation, tempo policy or host scheduler is implied.
- Add a headless speech/model PCM fixture → fade → echo → peak preparation → WAV
  pipeline that reports delivered quantized audio measurements and byte identity.
  No inference credentials, device or browser is required.
- Preserve legacy synthesis/PCM pins. Requires the tested AILANG v0.54.18 toolchain.

## 0.3.0

Feature: checked offline level preparation and stateful block filters.

- `levels`: whole-clip RMS and active-window RMS with sample peaks, frame/sample
  counts and full-scale/over-range counts. Scaled energy supports finite headroom
  without directly squaring the largest/tiniest samples. Windows span blocks;
  cumulative frame/sample limits and public accumulator records are checked.
- Explicit Off, PeakSafe and MatchRms policies return a bounded gain decision and
  reason. Matching uses one linked gain across channels, an activity floor/minimum,
  boost cap and peak ceiling. Silence/below-floor takes are never boosted.
- Checked preparation recomputes its plan and checks output headroom. Original
  immutable clips remain available for caller-owned preview/undo/explicit commit.
  No microphone control, perceptual loudness, plugin hosting or UI is implied.
- Preserve every existing recipe, legacy gated-RMS and PCM quantization behavior.
- `block`: checked mono/stereo low-pass, high-pass and exact bypass, persistent
  per-channel histories, reset, per-block frame/sample limits and cumulative stream
  frame budgets. No device/clock/AI effects; generic for games, speech/model audio
  and offline processing. Legacy filter operation order remains untouched.
- Add headless fixture-backed pipelines for a model-proposed recipe and speech/model
  PCM: checked import/render → block filter → levels → measured PCM16 WAV identity.
  Fixtures require no provider account and are not neural inference demonstrations.

## 0.2.0

Feature: checked mono/stereo clips, channel-preserving PCM16/WAV adapters and editing.
This release groups the unpublished 0.1.1 hardening milestone with the offline
clip and editing features.

- `clip`: planar `Array[float]` clips, explicit Mono/Stereo layouts, input/output frame
  and sample budgets, finite headroom, channel selection and interleaving. Unity
  mono duplication and 0.5L+0.5R downmix use explicit conversion functions.
- `edit`: gain, trim, padding, reverse, append, endpoint-defined fades, complementary
  linear crossfades, bounded placement/mixing and equal-power mono panning. Every
  public operation revalidates clip records; rates/layouts must match for composition.
- `clip_pcm`: preserve both stereo channels on PCM16/WAV import and export; choose
  Reject or Saturate clipping explicitly. In-range mono quantization keeps the old
  *32767/round convention; decode uses /32768. Huge finite samples saturate before
  integer conversion. Partial frames, unsupported depth/channel counts, excessive
  allocations and malformed RIFF return typed errors.
- Keep all v1 recipe record shapes and existing mono render behavior. Internal
  headroom is finite but can exceed full scale; integer encoding is the explicit
  clipping boundary. No implicit resampling or normalization is added.
- Add InvalidClip to the AudioError type introduced by the hardening milestone. Keep DSP pure and
  reuse existing std/array and std/bytes; core changes are developed separately.


## 0.1.1

Unpublished hardening milestone, included in 0.2.0.

Fix: harden the mono audio boundary without changing existing valid sound samples.

- Add `safety.AudioError`, caller-supplied `RenderLimits` and `defaultLimits`; add
  `validateRecipe`, `renderChecked`, `parseRecipesChecked` and `parseRecipesAsChecked`.
  Checked rendering rejects invalid/non-finite parameters and excessive frames, layers
  or layer work before allocating sample lists. JSON limits count UTF-8 bytes before decoding.
- Reject wrong JSON field types, fractional rate/seed, invalid parameter domains,
  zero-frame durations and zero-frequency exponential glides. Missing fields still default.
- Silent layers with drive remain silence instead of producing NaNs. Existing nonzero
  render arithmetic and PCM quantization order are preserved.
- One-shot placement selects the greatest active nonnegative start, independently of
  input ordering or duplicates. All loop restrictions are checked independently.
- Validate all WAV chunks inside the declared RIFF extent: padding, fmt size, rate,
  alignment/byte rate, complete frames, duplicate fmt/data and trailing truncation.
  Bound scans to 4096 chunks. Integer PCM8/16/24/32 metadata is supported;
  float/extensible/compressed WAV remains explicitly unsupported.
- Add `pcm16FloatsChecked` (bounded first-channel decode with metadata revalidation),
  `pcm16Checked` and `wav16Checked` (reject non-finite samples and clipping).
  Decoding uses direct byte access instead of copying every byte into a boxed list.
  The compatibility decoder returns [] on invalid metadata rather than indexing out of bounds.
- Add regression/property tests, runtime-contract smoke coverage and verified integer
  work/PCM-size helpers. Effects stay pure, with IO used only by the smoke verdict.

Compatibility: public record shapes and existing function signatures are unchanged.
Previously accepted malformed WAVs and invalid recipes now fail validation; supported
recipe rates are 1..384000 Hz and peak targets are -120..0 dBFS. Checked APIs are
opt-in; the original raw render/encode functions remain caller-validated primitives.
Core WAV writers, codecs and resampling are unchanged.

## 0.1.0

Feature (first release; stapledons-godot R2-SUNHOLO-AUDIO, ledger D-119): the sound synthesis and
loudness measurement of Stapledon's Voyage, extracted from the game's `tools/audio/synth.ail` and
`tools/sound_check.gd` into a package. Every export is pure and gives the same bits on the strict
bytecode VM and the interpreter. The game pins this version and all its synthesised WAVs
regenerate byte for byte; the analysis gives the same numbers as the game's GDScript to 0.01 dB
on every shipped cue.

- `recipe`: `Env`, `Layer`, `Recipe` (with a per-recipe `rate`, default 48000), `frames`,
  `envAt`, `phaseAt` (exponential glide), `layerSamples`, `render`, `loopErrors`,
  `parseRecipes` (schema `sunholo.audio.recipes/1`), `parseRecipesAs` (a host's own schema id),
  `recipeSchema`, `defaultRate`. Unknown layer kinds are refused.
- `noise`: `white` (lag-1 |r| < 0.03) and `rampNoise`, the legacy generator kept under an
  honest name (it is a ramp mod 2^31, not white) because approved sounds use it.
- `dsp`: `clamp16`, `dbToGain`, `gainToDb`, `centiDb`, `onePole`, `lowpass`, `highpass`,
  `sweepLowpass`, `softSat`, `peakAbs`, `normalisePeak`, `twoPi`, `absF`.
- `pcm`: `pcm16`, `wav16` (through `std/audio.wavFromPcm`), `WavInfo`, `wavInfo` (RIFF chunk
  walk; integer PCM only), `pcm16Floats` (s16 / 32768, first channel).
- `mix`: `tile` (loops, one-shots at start samples) and `sum`.
- `analysis`: `levelGain`, `peak`, `rmsGated`, `Level`/`level` (centi-dB), `highpassKeepDb`,
  `lowbandDb`, `Seam`/`seam`.
- `reference`: the reference loop and one-shot recipes, `sineWave`, and the loop's pinned PCM
  sha256 `28ee281f...7467`.
- Tests: 51 checks in six `*_test.ail` files against closed forms (10^(-3/20), the one-pole
  |H(w)|, the gated sine RMS sqrt(24/46) = -2.8255 dB, e^-1 after one tau) and two byte pins;
  `_smoke.ail` with `renderProbe`, `wavProbe`, `levelProbe` (strict VM = interpreter).
