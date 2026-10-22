# AGENT.md: sunholo/audio

## When to use

Use this package when you need sound that is **made, not recorded**, and must come out the same
every time:
- Rendering tonal sounds and textures from a small JSON recipe: sines that glide, waver and beat,
  noise through filters, envelopes, a slow swell, a soft saturation, normalised to a peak
  (`recipe`).
- Seamless loops: `loopErrors` refuses a loop that would click before you render it.
- Writing 16-bit WAVs (`pcm.wav16`) and reading them back (`pcm.wavInfo`, `pcm.pcm16Floats`).
- Mixing renders into a bed or a preview: loops tiled, one-shots placed at start times (`mix`).
- Measuring loudness offline, headless, with no audio device: peak, gated RMS, how much a
  high-pass keeps (small speakers), how much sits under a low-pass cascade (rumble guards), and a
  loop's seam (`analysis`).

Everything is pure: no effects, no clocks, no randomness except the two seeded index generators,
and the same bits on the bytecode VM (`--strict-bytecode`) and the interpreter. It depends on no
other package; WAV headers and Ogg Opus encoding are `std/audio` (call `std/audio.encode` on
`pcm16(...)` for Opus).

Do NOT use it for:
- Realtime or streaming synthesis, or anything sample-accurate against a clock: it renders whole
  lists of floats.
- Stereo or multichannel rendering (mono only; `pcm16Floats` reads the first channel of a
  multichannel file), resampling, or compressed formats other than what `std/audio` encodes
  (no QOA, MP3 or Vorbis; a game engine's importer usually does those).
- Perceptual loudness (LUFS / ITU-R BS.1770 K-weighting): the measures here are plain dBFS peak
  and RMS, with one-pole filters.
- Speech: route TTS output through `std/audio`; this package does not generate voices.

## Units and conventions

- Samples are floats in [-1, 1]; time in seconds; frequencies in Hz; levels in dBFS.
- `Recipe.rate` is the sample rate (default 48000); every time step is `i / rate`.
- `pcm16` writes `round(x * 32767)` clamped to int16, little-endian. `pcm16Floats` reads
  `s16 / 32768`. The asymmetry is deliberate: the encode is what existing sounds were made with
  (render stability), the decode is the convention of Godot and most readers. A round trip is
  within 1/32767 + 1/32768.
- `analysis.level` returns **centi-dB integers** (`peakCdb`, `rmsCdb`), rounded as Godot's
  `snappedf(x, 0.01)` (`floor(x / 0.01 + 0.5)`), so reports print exact numbers. `dsp.centiDb`
  is that rounding. `gainToDb` is `20 log(g) / log(10)` with a -120 dB floor at 1e-6, and
  `levelGain` is `exp(db * ln10 / 20)`, both written as the GDScript reference computes them, so
  the two agree to the bit.

## Quick start

```ailang
import pkg/sunholo/audio/recipe (parseRecipes, render)
import pkg/sunholo/audio/pcm (wav16)
import pkg/sunholo/audio/analysis (level)
import std/fs (readFileResult, writeFileBytesResult)

-- recipes.json: {"schema": "sunholo.audio.recipes/1", "recipes": [ ... ]}
match parseRecipes(text) {
  Ok(rs) => ... for each r: writeFileBytesResult("${r.id}.wav", wav16(render(r), r.rate))
  Err(e) => ...
}
-- loudness of a rendered sound played at -12 dB: level(render(r), -12.0, r.rate)
--   -> {peakCdb: -1500, rmsCdb: -2277, seconds: 7.0}
```

Keep file IO in your own shell module; every function here is pure.

## The recipe schema (`sunholo.audio.recipes/1`)

A file is `{"schema": "sunholo.audio.recipes/1", "recipes": [recipe, ...]}`; a host that already
has files under its own id parses them with `parseRecipesAs("<its id>", text)`. An empty list,
a recipe without an `id`, `seconds <= 0`, no layers, an unknown layer kind, or a loop that breaks
the loop rules is refused with the first error. Every default is a no-op.

| Recipe field | Default | Meaning |
|---|---|---|
| `id` | required | Name |
| `seconds` | required | Length (> 0, < 100000) |
| `rate` | 48000 | Sample rate, Hz |
| `loop` | false | A loop: no edge fades; loop rules apply |
| `peak_db` | -6 | The rendered peak, dBFS |
| `fade_ms` | 20 | One-shot fade-out (fade-in is always 2 ms) |
| `swell` | none | `{"rate": Hz, "depth": 0..1}`: gain `1 - d + d sin(2 pi r t)` |
| `drive` | 0 | Soft saturation `x (1 + k) / (1 + k |x|)` after the sum (normalised first) |
| `layers` | required | One or more layers |

| Layer field | Default | Meaning |
|---|---|---|
| `kind` | `"sine"` | `"sine"`, `"white"` or `"noise"` (the legacy `rampNoise`) |
| `freq` | 0 | Sine frequency, Hz |
| `glide_to`, `glide_from_s`, `glide_until_s` | `freq`, 0, 0 | Exponential glide to `glide_to` between the two times |
| `amp` | 0 | Linear amplitude before normalisation |
| `env` | hold | `{"delay", "attack", "tau", "stop"}` seconds: silent before delay, linear attack, `exp(-(u - attack)/tau)` decay (0 = hold), silent from stop (0 = never) |
| `vib_hz`, `vib_cents` | 0, 0 | Vibrato as a phase offset |
| `beat_hz`, `beat_depth` | 0, 0 | Amplitude beat `1 - d + d (0.5 + 0.5 sin(2 pi r t))` |
| `lowpass_hz`, `lowpass_to_hz` | 0, 0 | One-pole low-pass; with `lowpass_to_hz` it sweeps exponentially over the sound |
| `highpass_hz` | 0 | One-pole high-pass (input minus its low-pass) |
| `seed` | 1 | Noise seed |

Loop rules (`loopErrors`): in a loop every sine is fixed-pitch, envelope-free and completes a
whole number of cycles over `seconds`; vibrato, beat and swell complete whole cycles too; no
filter sweep. Noise in a loop is periodic: sample i reads the generator at i mod n and its filters
run over two periods, keeping the second, so the join is seamless.

## Render stability

For a given recipe and rate, `render` and `pcm16` give the same bytes in every 0.x release unless
that release's `[release] kind = "breaking"`. New recipe fields must default to a no-op. The
`reference` module pins the reference loop's PCM sha256 (`loopPcmSha`); consumers can pin it too.
Do not "tidy" operation order in `dsp` or `recipe`: floating-point results depend on it.

## Noise

- `white(i, seed)`: an affine start then rounds of squaring mod 2^31; lag-1 autocorrelation
  below 0.03. Use it for new sounds.
- `rampNoise(i, seed)`: three affine LCG rounds. Affine rounds over a sequential index stay affine
  in the index, so this is a fast ramp mod 2^31 with a buzzy, tonal edge: **not white**. It is
  kept because sounds approved by ear were made with it (recipe kind `"noise"`).

## Analysis

- `level(xs, gainDb, rate)`: samples times the gain; peak over all samples; RMS over the samples
  with |x| > 0.001 (silence does not dilute a short sound); seconds rounded to 1 ms.
  A full-scale 1 kHz sine at 48 kHz gives peak 0 and RMS -2.83 dB (the gate drops the two exact
  zero crossings per cycle: sqrt(24/46)).
- `highpassKeepDb(xs, cut, rate)`: RMS kept by a one-pole high-pass, in dB of the whole (a laptop
  speaker check: does the sound survive losing its lows?).
- `lowbandDb(xs, cut, poles, rate)`: RMS left under `poles` cascaded one-pole low-passes, in dB of
  the whole (a rumble guard: four 120 Hz poles leave a 60 Hz sine at -3.9 dB and a 2 kHz sine near
  -58 dB, bounded by the start-up transient).
- `seam(xs)`: the int16 step from the last sample to the first and the largest inner step; a clean
  loop has `seam <= maxStep + 1`.

## Exported surface

`dsp`: twoPi, absF, clamp16, dbToGain, gainToDb, centiDb, onePole, lowpass, highpass,
sweepLowpass, softSat, peakAbs, normalisePeak.
`noise`: rampNoise, white.
`recipe`: Env, Layer, Recipe, defaultRate, frames, envAt, phaseAt, layerSamples, render,
loopErrors, recipeSchema, parseRecipes, parseRecipesAs.
`pcm`: pcm16, wav16, WavInfo, wavInfo, pcm16Floats.
`mix`: tile, sum.
`analysis`: levelGain, peak, rmsGated, Level, level, highpassKeepDb, lowbandDb, Seam, seam.
`reference`: noEnv, sine, hiss, loopRecipe, shotRecipe, sineWave, loopPcmSha.

## Validation

`ailang test --package .` runs 51 checks against closed forms and two byte pins; `_smoke.ail`
prints `OK:` and its three probes give the same bytes on `--strict-bytecode` and the interpreter.
The first consumer, stapledons-godot, regenerates its 19 shipped WAVs byte for byte from this
package (`make sound-synth-check`) and compares `analysis` with its GDScript loudness checks on
every cue (`make sound-levels-parity`: 0 differences in centi-dB).

## Pitfalls

- Rendering is list-based: a 30 s sound is 1.44 M floats. Fine on the bytecode VM (seconds); the
  tree-walking interpreter is about 10x slower, so compare engines on short probes.
- `render` normalises to `peak_db`: a layer's `amp` sets balance, not absolute level.
- `wavInfo` accepts integer PCM only (format tag 1); `pcm16Floats` returns [] unless bits == 16.
- Known std gaps (reported upstream as sunholo-data/ailang#1930): `std/audio` has no WAV reader
  (hence `wavInfo` here) and `std/string` has no fixed-precision float formatter (hence centi-dB).
