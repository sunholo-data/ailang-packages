# AGENT.md: sunholo/audio

## When to use

Use this package for deterministic mono sound synthesis and checked offline mono/stereo
clip processing:
- Rendering tonal sounds and textures from a small JSON recipe: sines that glide, waver and beat,
  noise through filters, envelopes, a slow swell, a soft saturation, normalised to a peak
  (`recipe`).
- Loop authoring: `loopErrors` checks structural rules; measure the rendered join with `analysis.seam`.
- Channel-preserving PCM16/WAV import/export with `clip_pcm`, explicit clipping policy,
  and bounded planar mono/stereo clips (`clip`). The `pcm` module keeps the mono compatibility API.
- Editing clips with gain, trim, padding, reverse, fades, crossfades, append, placement/mixing
  and equal-power mono panning (`edit`).
- Mixing renders into a bed or a preview: loops tiled, one-shots placed at start times (`mix`).
- Measuring loudness offline, headless, with no audio device: peak, gated RMS, how much a
  high-pass keeps (small speakers), how much sits under a low-pass cascade (rumble guards), and a
  loop's seam (`analysis`).

Everything is pure: no effects, no clocks, no randomness except the two seeded index generators,
and matching output on the tested bytecode VM (`--strict-bytecode`) and interpreter. Cross-architecture equality needs separate evidence. It depends on no
other package; WAV headers and Ogg Opus encoding are `std/audio` (call `std/audio.encode` on
`pcm16(...)` for Opus).

Do NOT use it for:
- Realtime or streaming synthesis, or anything sample-accurate against a clock: it renders whole
  lists of floats.
- Multichannel layouts beyond Mono/Stereo, resampling, or compressed input formats.
  The recipe renderer remains mono; convert/pan its output through the clip API.
  `std/audio` can encode supported raw PCM rates to Ogg Opus.
- Perceptual loudness (LUFS / ITU-R BS.1770 K-weighting): the measures here are plain dBFS peak
  and RMS, with one-pole filters.
- Speech: route TTS output through `std/audio`; this package does not generate voices.

## Units and conventions

- Recipe output is normalized around full scale [-1,1]. Clips preserve any finite float
  headroom; integer output uses an explicit clipping policy. Time is seconds or integer
  frame positions as stated by each API; frequencies are Hz and levels are dBFS.
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
the loop rules is refused with the first error. Every missing optional field has a default. Provided fields of the wrong type are refused; unknown keys remain permitted for schema compatibility.

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
run over two periods, keeping the second, to reduce filter startup transients. Two periods are not an exact periodic-state proof; check `analysis.seam` for the rendered loop.

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
loopErrors, recipeSchema, parseRecipes, parseRecipesAs, validateRecipe, renderChecked, parseRecipesChecked, parseRecipesAsChecked.
`pcm`: pcm16, wav16, WavInfo, wavInfo, pcm16Floats, pcm16Checked, wav16Checked, pcm16FloatsChecked.
`mix`: tile, sum.
`analysis`: levelGain, peak, rmsGated, Level, level, highpassKeepDb, lowbandDb, Seam, seam.
`reference`: noEnv, sine, hiss, loopRecipe, shotRecipe, sineWave, loopPcmSha.
`safety`: AudioError, RenderLimits, defaultLimits, inRange, samplesInRange, fitsWork, pcm16ByteCount, limitsValid.
`clip`: ChannelLayout (Mono/Stereo), Clip, ClipLimits, channelCount, defaultClipLimits, checkSize, validate, create, fromMono, selectChannel, interleave, fromInterleaved, toStereo, toMono.
`edit`: gain, trim, pad, reverse, append, fade, crossfade, mixAt, panMono.
`clip_pcm`: ClippingPolicy (Reject/Saturate), fromPcm16, fromWav16, toPcm16, toWav16.

## Validation

`ailang test --package .` runs 116 checks against closed forms and two byte pins; `_smoke.ail`
prints `OK:` and its three probes give the same bytes on `--strict-bytecode` and the interpreter.
The first consumer, stapledons-godot, regenerates its 19 shipped WAVs byte for byte from this
package (`make sound-synth-check`) and compares `analysis` with its GDScript loudness checks on
every cue (`make sound-levels-parity`: 0 differences in centi-dB).

## Pitfalls

- Rendering is list-based: a 30 s sound is 1.44 M floats. Fine on the bytecode VM (seconds); the
  tree-walking interpreter is about 10x slower, so compare engines on short probes.
- `render` normalises to `peak_db`: a layer's `amp` sets balance, not absolute level.
- `wavInfo` accepts integer PCM8/16/24/32 only (format tag 1), with fmt before data and at most 4096 chunks. `pcm16Floats` returns [] for malformed/unsupported input; use the checked decoder for typed errors.
- Known std gaps (reported upstream as sunholo-data/ailang#1930): `std/audio` has no WAV reader
  (hence `wavInfo` here) and `std/string` has no fixed-precision float formatter (hence centi-dB).


## Checked APIs and trust boundaries in 0.1.1

Use the checked path for untrusted JSON or direct record construction:

```ailang
import pkg/sunholo/audio/safety (defaultLimits)
import pkg/sunholo/audio/recipe (parseRecipesChecked, renderChecked)
import pkg/sunholo/audio/pcm (wav16Checked)
-- Parse with limits; match Ok/Err at each stage.
-- parseRecipesChecked(text, limits) -> Result[[Recipe], AudioError]
-- renderChecked(recipe, limits) -> Result[[float], AudioError]
-- wav16Checked(samples, recipe.rate, limits.maxFrames) -> Result[bytes, AudioError]
```

`AudioError` variants: `InvalidClip(string)`, `InvalidRecipe(string)`, `InvalidWav(string)`,
`UnsupportedFormat(string)`, `ResourceLimit(string)`, `InvalidSamples(string)`.
Failures are ordinary Result values in both engines; no contract flag is required.
`validateRecipe` checks programmatic records too. The raw `render`, `pcm16` and `wav16`
remain compatibility primitives whose callers own input validity and resource use.
Legacy `parseRecipes`/`parseRecipesAs` gain strict types/domains but do not impose
input-byte or render-work limits; use the Checked variants for those limits.

`defaultLimits()` returns:

| Field | Default | Meaning |
|---|---|---|
| maxInputBytes | 1048576 | UTF-8 bytes of recipe JSON before JSON decoding |
| maxFrames | 1440000 | Frames per recipe, 30 seconds at 48 kHz |
| maxLayers | 32 | Layers per recipe |
| maxLayerFrames | 11520000 | Frames times total layer passes; loop noise costs two passes |

Limits may be replaced using record update. Valid maxInputBytes is 1..16777216;
maxFrames/maxLayerFrames are 1..2147483647; maxLayers is 1..1024.
These bound sample-list sizes and layer processing; they are not an exact heap-byte,
wall-time or host-memory guarantee. A caller can still choose limits too large for its machine.
JSON UTF-8 encoding can allocate a bounded temporary copy after a character-count precheck.
All recipes returned by checked parsing meet the per-recipe budget, not a cumulative batch budget.
The 32-second historical cue needs an explicit larger maxFrames than the default.
DSP is pure; `@limit` does not count sample operations. Smoke has `IO @limit=1`.

Validation domains are finite: rate 1..384000; seconds >0 and <100000 with at least
one rounded frame; peakDb -120..0; fadeMs 0..1e8; drive 0..1e6; swellDepth/beatDepth
0..1; frequencies/filter cutoffs/modulation rates 0..1e6; amplitude -1e6..1e6;
vibrato cents 0..12000; seed 0..2147483647; envelope/glide times 0..100000 with
glide1 >= glide0. An active exponential glide needs positive endpoints; a filter sweep
needs a positive starting cutoff. Negative seeds and empty IDs/layers are refused.
Frequency limits ensure arithmetic domains, not anti-aliasing. V1 filter fields act on
noise layers; existing sine processing is preserved. Loop validation is structural;
noise filter warm-up is approximate.

`renderChecked` validates before allocating samples and scans its result for finite
full-scale output with a 1e-12 tolerance for normalization rounding. `pcm16Checked`
strictly rejects samples outside [-1,1], non-finite values and excessive frames;
it never silently clips, so a rounding overshoot must be handled explicitly by the caller.
The legacy encoder still saturates. `wav16Checked` additionally checks that sample
rate and byte counts fit classic mono PCM16 WAV fields. maxFrames can be zero for
empty PCM; it must be <=2147483629 for checked encoding.

`wavInfo` validates every chunk within the declared RIFF extent, rejecting short fmt,
truncated headers/payloads/padding, invalid rate/alignment/byte rate, partial frames,
and duplicate fmt/data. Bytes after RIFF are ignored. Float, extensible, compressed,
and RIFX/RF64 WAV are unsupported. Zero-frame integer PCM WAV is valid.
`pcm16FloatsChecked(bytes, info, maxFrames)` re-parses metadata, rejects forged
fields, enforces the output-frame limit, and explicitly refuses non-PCM16 input.
It returns the first channel only, using s16/32768. No resampling or downmix is implied.
Callers bound acquisition/input bytes separately; this API avoids copying the whole file
into an integer list. Very fragmented WAVs over the chunk ceiling return an error.

The existing sample arithmetic and quantization order are retained. One-shot starts can
be unsorted or repeated; the greatest active nonnegative start wins. Negative starts are
ignored. This fixes order dependence while preserving sorted-start behavior.

Static verification, runtime checks, tests and byte identity are distinct evidence.
Use `--verify-contracts` explicitly to execute requires/ensures while validating;
ordinary checked APIs enforce their guards without that flag. Z3 uses mathematical
Real/Int models and bounded recursion: its proofs are not IEEE-754, NaN, overflow,
or cross-architecture byte-equality guarantees. The report records unsupported/missing
postcondition skips separately from counterexamples and errors. Do not claim fully
verified audio from a passing package quality badge.


## Mono and stereo clips in 0.2.0

`Clip = {rate: int, layout: ChannelLayout, frames: int, planes: [Array[float]]}`.
A Mono clip has one plane; Stereo has left then right. Each plane has exactly
`frames` samples. Empty clips contain the required number of empty planes. Samples
must be finite, but can exceed [-1,1] internally; gain and mixing retain headroom.
Public records can be forged, so every operation validates its input and output.
NaNs, infinities, shape errors and numeric overflow return typed errors.

`ClipLimits = {maxFrames: int, maxSamples: int}` bounds both inputs and outputs.
`defaultClipLimits()` allows 1440000 frames and 2880000 total samples (30 seconds
of stereo at 48 kHz). Both fields may be 0..2147483647; choose limits suitable
for the host. A clip with f frames and c channels requires f*c <= maxSamples.
Dimensions are checked before constructing output sample arrays. Current validation
and array construction can use bounded temporary boxed lists; this is not an exact
heap-byte or realtime guarantee. Rates are 1..384000 Hz; conversion is explicit.

| Function | Signature and behavior |
|---|---|
| `channelCount` | `(layout) -> int`, 1 or 2 |
| `checkSize` | `(rate, layout, frames, limits) -> Result[int, AudioError]`, returns validated total sample count |
| `create` | `(rate, layout, planes, limits) -> Result[Clip, AudioError]`, validates equal plane lengths and finite samples |
| `fromMono` | `(rate, [float], limits) -> Result[Clip, AudioError]`, bridge from recipe render output |
| `validate` | `(clip, limits) -> Result[Clip, AudioError]`, revalidates direct record construction |
| `selectChannel` | `(clip, index, limits) -> Result[Array[float], AudioError]`, zero-based checked selection |
| `interleave` | `(clip, limits) -> Result[Array[float], AudioError]`, L0,R0,L1,R1 for stereo |
| `fromInterleaved` | `(rate, layout, Array[float], limits) -> Result[Clip, AudioError]`, rejects partial frames |
| `toStereo` | `(clip, limits) -> Result[Clip, AudioError]`, duplicates Mono at unity; Stereo is unchanged |
| `toMono` | `(clip, limits) -> Result[Clip, AudioError]`, averages 0.5L+0.5R; Mono is unchanged |

The unity duplication shares immutable arrays. `toMono` scales before adding so
large correlated finite channels do not overflow at an intermediate sum. Neither
conversion changes the sample rate. Pairwise composition rejects differing rates
or layouts; it never drops a channel or resamples implicitly.

All editing functions return `Result[Clip, AudioError]` and take ClipLimits last:

| Function | Policy |
|---|---|
| `gain(c, factor, limits)` | Finite linear factor, including negative polarity inversion; rejects non-finite output |
| `trim(c, start, end, limits)` | Integer [start,end) frame interval; empty intervals allowed |
| `pad(c, before, after, limits)` | Nonnegative silence frames before/after |
| `reverse(c, limits)` | Reverse frame order within every plane, preserving channel identity |
| `append(a, b, limits)` | Consecutive clips with matching rate/layout |
| `fade(c, fadeIn, fadeOut, limits)` | Frame counts include endpoints; 0 disables, 1 mutes the edge sample; N>=2 ramps 0..1; overlapping fades multiply |
| `crossfade(a, b, overlap, limits)` | Complementary linear weights across N frames; N=0 appends; N=1 uses 0.5/0.5; N>=2 includes exact endpoints |
| `mixAt(base, overlay, start, limits)` | Nonnegative frame start, sum overlaps, extend with silence; empty overlays leave the base unchanged; start still must fit limits |
| `panMono(c, position, limits)` | Mono only, position -1..1; equal-power gains, exact hard endpoints, identical sqrt(0.5) center gains; returns Stereo |

Integer output is the clipping boundary. `clip_pcm.fromPcm16(bytes, rate, layout,
limits)` imports raw s16le, retaining every channel; `fromWav16(bytes, limits)`
uses validated RIFF metadata and supports integer PCM16 mono/stereo. Unsupported
metadata depths/channel counts are `UnsupportedFormat`; failures of the legacy
RIFF parser, including unsupported format tags, are `InvalidWav` with the parser's
reason. Empty PCM is valid. Acquisition/input bytes are bounded by the caller;
the limits here bound decoded sample allocation.

`toPcm16(c, policy, limits)` and `toWav16(c, policy, limits)` require an explicit
`ClippingPolicy`: `Reject` refuses samples outside [-1,1]; `Saturate` clips integer
output to int16 without peak normalization. Both use legacy *32767/round quantization
for in-range samples (so -1 encodes as -32767), while decode uses /32768. Saturation
handles huge finite values before integer conversion and reaches -32768 for excess
negative input. WAV output also checks classic RIFF size limits before encoding.
A PCM decode/encode round trip is not generally byte-identical; its sample error is
bounded by 1/32767 + 1/32768. Full recipe PCM pins stay unchanged.

From this package root, the complete stereo pipeline can be exercised with:

```sh
ailang run --quiet --relax-modules --verify-contracts --entry clipProbe --args-json 0 _smoke.ail
ailang run --quiet --relax-modules --bytecode --strict-bytecode --verify-contracts --entry clipProbe --args-json 0 _smoke.ail
```

Both print `true true true`: independent expected PCM bytes, stereo WAV reimport,
and forged-clip rejection. Static verification currently has an upstream constructor
declaration error on `checkSize`; retain that error separately from skipped proofs
and passing native/runtime-contract checks. Publication is deferred for this grouped
release candidate. See the roadmap's 0.2.0 report for actual proof/test counts.
