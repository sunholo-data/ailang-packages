# AGENT.md: sunholo/audio

## When to use

Use this package for deterministic mono sound synthesis and checked offline mono/stereo
clip processing. Clips are source-independent: procedural/game audio, imported
recordings, TTS PCM and model-generated samples use the same checked representation.
Provider inference and device/session handling belong to consumers or adapters.
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
- Checked offline take preparation: whole-signal and active-window RMS, cumulative
  block measurements, peak protection and bounded RMS-matching gain plans (`levels`).
- Stateful checked mono/stereo low-pass/high-pass processing of bounded blocks,
  with independent channel histories, exact bypass and reset (`block`).
- Checked feedback echo/delay and linked linear-gain automation for provider PCM,
  offline effects and host-owned DAW automation (`delay`, `automation`).

Everything is pure: no effects, no clocks, no randomness except the two seeded index generators,
and matching output on the tested bytecode VM (`--strict-bytecode`) and interpreter. Cross-architecture equality needs separate evidence. It depends on no
other package; WAV headers and Ogg Opus encoding are `std/audio` (call `std/audio.encode` on
`pcm16(...)` for Opus).

Do NOT use it for:
- Realtime device I/O or a general streaming synthesis engine. Block-based level
  measurement and stateful filters are available; synthesis/clip edits are offline. Host clocks and device
  callbacks are separate from these pure APIs.
- Multichannel layouts beyond Mono/Stereo, resampling, or compressed input formats.
  The recipe renderer remains mono; convert/pan its output through the clip API.
  `std/audio` can encode supported raw PCM rates to Ogg Opus.
- Perceptual loudness (LUFS / ITU-R BS.1770 K-weighting): the measures here are plain dBFS peak
  and RMS, with one-pole filters.
- Model inference, transcription or neural voice generation. Use `std/ai`/provider
  adapters for those effects; supported PCM/WAV speech can be imported, edited,
  levelled and mixed here like any other audio. Use `std/audio` for shared codecs.

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
`levels`: LevelConfig, LevelEnergy, LevelState, LevelReport, LevelTarget, LevelPolicy,
GainReason, LevelPlan, PreparedLevels, defaultConfig, start, accumulate, finish,
measure, plan, prepare.
`block`: FilterKind (FilterBypass/LowPass/HighPass), BlockLimits, FilterState,
FilterBlock, defaultBlockLimits, startFilter, processFilter, resetFilter.
`delay`: DelayConfig, DelayLimits, DelayState, DelayBlock, defaultDelayLimits,
startDelay, processDelay, resetDelay.
`automation`: GainState, GainBlock, startGain, setGain, processGain.

## Validation

`ailang test --package .` runs 192 checks against closed forms and two byte pins; `_smoke.ail`
prints `OK:` and its three probes give the same bytes on `--strict-bytecode` and the interpreter.
The first consumer, stapledons-godot, regenerates its 19 shipped WAVs byte for byte from this
package (`make sound-synth-check`) and compares `analysis` with its GDScript loudness checks on
every cue (`make sound-levels-parity`: 0 differences in centi-dB).

## Pitfalls

- Rendering is list-based: a 30 s sound is 1.44 M floats. Fine on the bytecode VM (seconds); the
  tree-walking interpreter is about 10x slower, so compare engines on short probes.
- `render` normalises to `peak_db`: a layer's `amp` sets balance, not absolute level.
- `wavInfo` accepts integer PCM8/16/24/32 only (format tag 1), with fmt before data and at most 4096 chunks. `pcm16Floats` returns [] for malformed/unsupported input; use the checked decoder for typed errors.
- AILANG v0.54.18 now includes checked WAV/PCM APIs and fixed-precision formatting.
  The legacy helpers remain for compatibility: the new stdlib PCM writer's quantization
  differs from this package's pinned convention. Resampling remains outside this package.


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
and forged-clip rejection. The previous verifier constructor error on `checkSize`
is fixed in v0.54.18, where that function verifies. Larger operations still have
unsupported-encoding skips; consult the retained version-specific quality evidence.

## Offline level plans in 0.3.0

`levels` is pure, offline preparation, not a microphone AGC, compressor, LUFS meter
or true-peak limiter. It never alters the legacy `analysis.level`/`rmsGated` meaning.
Amplitudes, RMS, targets and gains are **linear**; use your display layer for dBFS.

```ailang
import pkg/sunholo/audio/clip (defaultClipLimits)
import pkg/sunholo/audio/levels (defaultConfig, MatchRms, plan, prepare)
-- `c` is a validated mono/stereo Clip. Targets below illustrate an explicit policy.
let policy = MatchRms({targetRms: 0.125, peakCeiling: 0.5, maxBoost: 4.0, minActiveFrames: 1024});
-- Inspect plan(c, defaultConfig(), policy, defaultClipLimits()) while c is private.
-- prepare(c, defaultConfig(), policy, defaultClipLimits()) returns {clip, plan} in Ok.
-- Retain c for undo; the host separately chooses preview, commit, save or export.
```

| API | Behavior |
|---|---|
| `defaultConfig()` | `{windowFrames: 1024, activityFloor: 0.001}`; configurable amplitude threshold, not a universal noise detector |
| `start(rate, layout, config, limits)` | Empty checked LevelState |
| `accumulate(state, block, limits)` | Requires identical rate/layout; checks input and cumulative frame/sample budgets; retains an incomplete window |
| `finish(state, limits)` | Includes the last partial window using its actual size; does not flush/change state, so appending after a report preserves windows |
| `measure(clip, config, limits)` | Whole-clip convenience for start/accumulate/finish |
| `plan(clip, config, policy, limits)` | Validates and measures this clip, returning its report, policy, bounded requested/applied gain and reason |
| `prepare(clip, config, policy, limits)` | Recomputes the plan, applies one linked positive/zero gain to all channels, validates finite output and scans the peak ceiling |

Windows start at frame zero of the accumulated stream and span all channels.
Window RMS is pooled energy over channel samples: opposite-polarity stereo does
not cancel; a silent channel contributes zero energy. A window is active when RMS
is positive and >= activityFloor. Active RMS includes **all samples in qualifying
windows**, rather than selecting individual samples. `frames`/`activeFrames` count
time frames; `samples` counts frames times channels. The default window is a frame
count, so its duration changes with sample rate. The last partial window can be
reclassified after appending; only the final report describes the finished clip.

Reports contain `peak`, `rms`, `activeRms`, `frames`, `samples`, `activeFrames`,
`fullScaleSamples` (|x| >= 1), `overRangeSamples` (|x| > 1), `rate`, `layout` and
window/floor settings. These sample counts flag level risk; they cannot establish
whether a microphone or earlier processor clipped. Scaled sums avoid directly
squaring huge/tiny amplitudes; IEEE rounding/subnormal underflow still applies.

`LevelPolicy` is `LevelsOff | PeakSafe(peakCeiling) | MatchRms(LevelTarget)`:

- Off uses unity, including finite headroom beyond full scale. It provides no peak ceiling.
- PeakSafe only reduces gain when the sample peak exceeds the ceiling.
- MatchRms targets active-window RMS. No active windows or fewer than
  `minActiveFrames` disables boosting/level matching but still permits peak protection.
  Matching preserves phrase dynamics, stereo balance/polarity and frame/rate/layout.
- Ceilings/target RMS are 1e-12..1; maxBoost is 1..64; minimum active frames is
  1..2147483647; windowFrames is 1..65536; activityFloor is 0..1. Invalid/nonfinite
  values return AudioError even for empty clips. No automatic target preset is chosen.

`requestedGain` already respects the boost/activity policy; `gain` can be reduced
further by the peak ceiling. Reasons are Bypassed, BelowActivityFloor,
InsufficientActivity, AlreadyAtLevel, TargetMatched, BoostLimited or PeakLimited.
Peak protection takes precedence if both constraints apply. A tiny downward
rounding reserve near the ceiling may prevent an exactly attained RMS target.
Under extreme floating-point ranges, a gain may underflow to zero; prepare returns
an error rather than releasing nonfinite or above-ceiling output.

Public LevelState/LevelEnergy records are checked for finite values, dimensions,
counts, window alignment and plausible energy ranges. This is structural validation,
not authentication that the state came from actual samples. `plan` always measures
its supplied clip; `prepare` never accepts an externally constructed plan as authority.
Keep configuration fixed through accumulation. A policy change may reuse the original
clip, but start a fresh accumulator when window/floor settings change.

Work is O(frames * channels); the accumulator uses fixed-size numeric state.
Clip validation and edits retain their existing bounded temporary allocations;
this is not a heap-byte, wall-time or audio-callback guarantee. ClipLimits apply
to each block **and the cumulative stream**, with the same 2147483647 maxima.
No effects are used, so effect @limit does not meter sample work.

The 0.3.0 evidence directory records tests, native engine runs, runtime-contract
probes, independent Decimal reference checks and descriptive CLI timings. Z3 uses
Real/Int models: its two proofs in levels cover defaultConfig and boundedGain,
while the six public processing APIs are skipped for unsupported encodings.
This is not proof of IEEE arithmetic, audible quality or third-party DSP.

## Generic stateful filters in 0.3.0

`block` owns no application/device/model state. A caller supplies a validated
mono/stereo Clip block and keeps the returned state for the next block:

```ailang
import pkg/sunholo/audio/block (LowPass, defaultBlockLimits, startFilter, processFilter)
-- startFilter(24000, Mono, LowPass, 1200.0, defaultBlockLimits())
-- processFilter(state, inputClip, defaultBlockLimits()) -> Ok({clip, state})
-- Retain result.state; do not restart the filter at every chunk boundary.
```

| API | Meaning |
|---|---|
| `defaultBlockLimits()` | `{maxFrames:4096, maxSamples:8192, maxTotalFrames:2147483647}` |
| `startFilter(rate, layout, kind, cutoffHz, limits)` | New logical stream with zero per-channel histories and processedFrames=0 |
| `processFilter(state, input, limits)` | Checked block → output Clip + next FilterState; rate/layout/frame count preserved |
| `resetFilter(state, limits)` | Validate then flush history/restart its frame counter, keeping configuration |

Kinds: FilterBypass is byte-preserving identity, including finite headroom/negative
zero; its low-pass history stays unchanged but its processed-frame counter advances.
LowPass uses `a=1-exp(-2*pi*cutoff/rate)` and `low=(1-a)*previous+a*x`.
HighPass returns `x-low` from that same recurrence. These are first-order filters,
not biquads or a claim of an exact digital -3 dB point at every cutoff. Scaling
before adding avoids the opposite-extreme subtraction overflow in a naive update.
Legacy `dsp.lowpass` and its render order remain unchanged.

Rates: 1..384000 Hz, with no implicit resampling. Low/high cutoffs: 1e-6..rate/2 Hz;
bypass accepts a finite 0..rate/2 cutoff but ignores it. State history has one
finite value per channel, and block rate/layout must match. Public records are
structurally checked, not authenticated observations of an earlier stream.
Create/reset a state explicitly for a new logical stream; parameter changes are
not automatically smoothed. No clock, device or background worker is implied.

Block limits are integers 0..2147483647. maxFrames/maxSamples bound each input and
output block; maxTotalFrames bounds processedFrames since start/reset. Budgets are
caller-selected work/dimension limits, not global CPU or heap limits. An empty block
preserves history/cursor. Input/output headroom may exceed full scale; nonfinite
input, state or arithmetic output returns a typed error. Integer export remains an
explicit Reject/Saturate boundary. High-pass output can overflow with extreme finite
headroom; that returns InvalidSamples rather than releasing infinity.

Filter tails are state, not extra output frames. Process explicit silence within
the budget to render a decay; reset discards the remaining tail. IIR decay can be
very long, so callers decide tail truncation. History is fixed-size, with O(block
samples) processing; validation, toList/mapAccumL/fromList use bounded temporary
allocations. mapAccumL builds output in one pass rather than growing an immutable
list or copying an array for each sample. No callback deadline is guaranteed.

Two headless fixture-backed consumer entries exercise synthesis/model-output paths:

```sh
ailang run --package-dir . --strict-bytecode --verify-contracts --entry pcmDemo --args-json 0 examples/block_pipeline.ail
ailang run --package-dir . --strict-bytecode --verify-contracts --entry recipeDemo --args-json 0 examples/block_pipeline.ail
```

`pcmDemo` imports s16le as a speech/model adapter could supply. `recipeDemo` checks
JSON data as a model could propose, then renders it under limits. Both filter,
prepare levels and return measured WAV identity metadata without IO/model calls.
These analytic fixtures are not generated human speech or an inference accuracy
test. `std/ai`/provider adapters remain separate effectful consumers.

## Delay and gain automation (0.4.0 candidate, not yet published)

These pure APIs compose with checked Clip, filters, levels and WAV encoding. They
own no audio callback, musical tempo, scheduler, model/provider or application state.

### Integer-frame feedback delay

`startDelay(rate, layout, config, limits)` allocates zero history after validating
all dimensions. Config is `{delayFrames, feedback, dry, wet}`. Delay is at least
one integer frame; feedback is finite -0.99..0.99; dry and wet are each finite 0..1.
At each sample, read the old history value `d`, output `dry*x + wet*d`, then store
`x + feedback*d`. Stereo channels never share history. Delay duration in seconds
is delayFrames/rate; tempo and seconds-to-frame rounding belong to callers.

`processDelay(state, inputClip, limits)` returns `{clip, state}` with the same
rate/layout/frame count. Retain state across chunks. Dry/wet are independent gains,
not a normalized crossfade; their sum and feedback can produce above-full-scale
output. Apply explicit levels/clipping policy before integer encoding. Even with
wet=0, feedback history runs and its overflow is checked; this is not exact bypass.
No automatic normalization, interpolation, modulation or cross-feedback is added.

`defaultDelayLimits()` gives `{block: defaultBlockLimits(), maxDelayFrames:96000,
maxDelaySamples:192000}`. At 48 kHz this permits two seconds per channel. Rate
remains 1..384000; delay is a frame budget, not a fixed duration across rates.
Both maxDelay bounds are integers 1..2147483647, and channel samples are checked
before allocation. Existing BlockLimits apply to every block and cumulative frames
since start/reset. Caller-selected caps are not total-heap or wall-time guarantees.

State contains rate/layout/config, processedFrames, ring cursor and one finite
Array history per channel. Every boundary checks dimensions, cursor position
(processedFrames modulo delayFrames), counts and finite samples/history. Public
states are structurally checked, not authenticated. To change delay configuration,
start a new state; changing delay time is not smoothed by this API.

Tail rendering is explicit: process bounded silence for the desired duration.
An empty block advances nothing; resetDelay validates then drops all histories and
restarts the logical frame budget with the same configuration. Reset may truncate
an audible tail. No silence detector or automatic tail-completion claim is supplied.

Implementation batches at most delayFrames writes between ring-buffer copies using
std/array.updateMany, preserving read-before-write semantics even at delayFrames=1.
For N nonempty input frames and D history frames, work is O(channels*(N+D)) per
call, including full state validation; histories are O(channels*D), with bounded
temporary arrays/lists and allocations. Repeated tiny blocks still rescan/copy
history. This is an offline/reference implementation, not an allocation-free or
hard-realtime delay host. Nonfinite input, arithmetic output or history returns
InvalidSamples; failed calls leave the caller's immutable state intact.

### Linked gain ramps

`startGain(rate, layout, gain, blockLimits)` initializes a constant gain, finite
0..64. `setGain(state, target, frames, limits)` retains the cumulative frame count
and starts a ramp from the last delivered gain. Frames is an integer
0..2147483647. Zero means the next input uses target immediately. For a positive
N-frame ramp, sample k (1..N) uses `(1-k/N)*start + (k/N)*target`; sample N and all
later samples use target exactly. The starting gain belongs to the preceding frame.
Re-target at a caller-chosen boundary to replace a ramp without jumping to its old
target. This is linear amplitude, not dB interpolation or a complete automation lane.

`processGain(state, input, limits)` returns `{clip,state}` and applies one gain per
frame to all channels. Gains derive from absolute ramp positions; chunking does not
change their arithmetic or accumulated phase. Empty clips consume no ramp/frame
budget. Rate/layout, finite gains/samples and public position records are checked.
There is no input reset API: startGain explicitly begins a new logical stream.
Processing is O(block samples), with an O(block frames) gain vector; normal Clip
validation/allocation applies. Output overflow returns InvalidSamples. This gain
ramp does not smooth filter cutoff, delay time or feedback automatically.

### Headless AI-output/DAW processing example

```sh
ailang run --package-dir . --strict-bytecode --verify-contracts --entry demo --args-json 0 examples/effects_pipeline.ail
```

The synthetic s16le fixture stands in for provider output. It is decoded at its
declared 24 kHz rate, extended by 720 silence frames for a deliberately truncated
tail, faded over 8 frames, echoed at 120-frame intervals, peak-prepared, encoded and
decoded again. Returned peak/RMS measurements refer explicitly to delivered
quantized audio; the WAV SHA-256 identifies bytes, not perceptual/model correctness.
No inference, credentials, input upload or device access occurs.

Evidence and independent Python WAV reference:
`design_docs/implemented/audio-effects-0.4.0` in the source repository. The core
record-Eq/property-evaluator bug is reported upstream; explicit field comparisons
keep these APIs/tests compatible with v0.54.18. Verification skips, mathematical
proofs, runtime guards, fixture tests and descriptive CLI timings are reported
separately. No new browser soak or physical device acceptance is implied.
