# Changelog

## 0.1.1

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
