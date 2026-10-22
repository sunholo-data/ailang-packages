# Changelog

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
