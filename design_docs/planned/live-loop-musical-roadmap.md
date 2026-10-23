# Loop Lab: from reliable capture to a musical instrument

Status: next-stage implementation roadmap, 2026-10-23. Priorities reflect the
user's working-microphone feedback: auto-levels, humming played by other
instruments/sounds, and effects. Version numbers are candidates, not release promises.
Related: [instrument design](live-loop-instrument.md), [audio roadmap](first-class-audio-roadmap.md),
[capture ownership](live-loop-capture-lifecycle.md).

Implementation checkpoint: the audio 0.3 candidate now has checked level plans;
the local host 0.2 candidate adds private mode/gain reports, boundary-staged undo/redo
and active committed WAV downloads for a manual Live handoff. See
[workflow evidence](../implemented/audio-v3-workflow/README.md). These changes are
unreleased and need browser/user acceptance. Project save/load, detected MIDI,
instruments, effects and plugin adapters remain subsequent feature groups.

## Starting point and order

Audio 0.2.0 is published; upstream v0.54.18 WAV/PCM/verifier fixes are validated.
The reference Firefox host passed 100 exact-frame handoffs and a 30-minute
synthetic soak, including background intervals. The user reports the new microphone
workflow working. That is a usable experimental foundation. Physical loopback,
full device/configuration evidence and additional platforms remain live-release
checks; they need not prevent developing the next musical experiments.

| Priority | Deliverable | Observable user result | Main ownership |
|---|---|---|---|
| 1 | Auto-level preparation + recovery | Quiet/strong takes join at sensible levels; undo restores a working loop | audio 0.3 candidate; host L1 |
| 2 | Hum → Bass MVP | A monophonic hum becomes editable notes played by a bass patch | audio analysis/synthesis; minimal music_patterns; host Notes mode |
| 3 | Sound palette + first effects | Play the same notes as bass/pluck/bell/lead/pad; shape with filter and delay | audio stateful DSP; host parameter controls |
| 4 | Broader effects and musical workflow | Reverb/dynamics, smooth automation, tempo/grid changes and controllers | audio + music_patterns + host |

Work on filter/delay prototypes can overlap pitch analysis once the block/state
contract exists. Do not make a resampler or a large pattern algebra a prerequisite
for level matching or one hum-to-bass workflow. Publish coherent feature groups
with consumer examples and evidence; keep the local application separate from
registry package releases.

## 1. Auto-levels and recoverable takes

The original preparation only limited peaks downward to about -6 dBFS. The candidate
now adds bounded RMS matching; it is not perceptual loudness matching. The policy is an
explicit Off / Peak-safe / Matched policy, with a previewed gain decision and a
reversible original. Match presets to track/patch needs rather than treating kick,
sustained bass and texture as identical signals.

Package work:

- Add labelled full-signal RMS and active-window RMS, sample peak, silence/activity
  classification and clipping counts. Existing gated RMS retains its legacy meaning;
  none of these measurements is LUFS or reconstructed true peak.
- Return a bounded level plan: target, proposed/applied gain, boost ceiling,
  peak/headroom constraint and reason for no adjustment. Silence/below-floor input
  must not be amplified. Expose the policy rather than silently boosting noise.
- Preserve phrase dynamics with a constant preparation gain. Treat compression and
  limiting as separate processors. Calibrate thresholds/track targets on reference
  fixtures before declaring defaults; do not present prototype values as universal.
- Build block accumulation/state primitives here, preserving counts and numeric
  stability over long clips. Reuse the released stdlib WAV/packed PCM boundaries
  where compatible; retain the package's pinned legacy quantization explicitly.

Host work: show before/after meters and the proposed gain while the take is private;
apply only the chosen policy at commit. Include simple per-track undo and explicit
local save/load of committed state before deeper transformations. Notes projects
save notes/patches; Audio projects may save their deliberately committed recordings.
Uncommitted/private raw takes are excluded from save/export by default. Add bounded
history/assets and overwrite warnings instead of unlimited retained capture buffers.

Acceptance: independent DC/sine/impulse/silence/quiet-noise fixtures; finite extreme
headroom; no NaN or silence amplification; declared gain/peak limits; channel/rate/
frame preservation; block sizes 1/127/128/1024/full with documented numeric tolerance.
Listen to sparse/transient and sustained fixtures, including four-part mixes. Measure
final mix headroom; keep clipping counts after effects/master processing. Verify undo,
late revision rejection and explicit save/reload round trips.

**First implementation slice:** pure level measurement + gain-plan API, closed-form
fixtures/properties/contracts, then the private take preview and one-step undo.
Do not start with continuously riding microphone gain or a full mastering chain.

## 2. Hum → Bass MVP

The intended first transformation is **private hum → monophonic notes → selected
instrument**, with Notes / Audio capture visibly distinct. Low-confidence analysis
must never fall back to publishing the raw voice. Note correction is reversible;
keep the detected note representation as well as the corrected candidate.

- Start with local bounded fundamental-frequency/voicing analysis. Evaluate a
  YIN-style difference/autocorrelation reference against a simpler baseline on the
  same versioned corpus; choose with measured octave errors, voiced/unvoiced errors,
  pitch/onset accuracy and worker cost. [YIN paper](https://doi.org/10.1121/1.1458024)
  is an algorithm reference, not evidence of this implementation's accuracy/speed.
- Turn frame observations into note events with explicit confidence, onset/offset,
  minimum duration, gap/splitting and hysteresis rules. Make pitch range, octave
  assignment into the patch range, optional scale snapping and timing quantization
  visible/versioned settings. Preserve intentional bends/vibrato by policy.
- Introduce only the necessary validated NoteClip/time model in the proposed
  sunholo/music_patterns package: source timing, musical ticks (960/quarter), bounded
  notes/velocity/duration, stable IDs and deterministic correction/transposition.
  Full text syntax, pattern algebra and MIDI can follow independently.
- Offer a small note preview with confidence/correction, then one convincing bass
  patch and explicit commit through the existing revision protocol. Pre-rendering
  a bounded candidate loop can reuse the proven buffer handoff before a general
  live event renderer exists. Keep note state editable rather than saving only WAV.

Corpus: analytical tones/harmonics, glides/vibrato, known note transitions, silence,
breath/noise, and project-owned or explicitly licensed/consented human humming.
Never silently bank live private takes as training/test assets. Declare ranges,
tolerances and acceptable error rates before evaluation, and report difficult cases
instead of removing them from the corpus.

Measure incremental analysis, post-release finalization, rendering and staging
separately. The existing under-ten-second turnaround is a target to test against
real audible onset, not a guarantee inherited from synthetic frame acknowledgements.
Keep a host/worker reference if needed while the AILANG package implementation is
benchmarked; require independent equivalence checks before swapping implementations.

## 3. Instruments and effects people can hear

Use one NoteClip to audition distinct bass, pluck, bell, soft-lead and pad patches.
Version the synthesis parameters/sample assets. A patch declares pitch range,
polyphony, envelopes, gain calibration, voice stealing and release/tail behavior.
Start with project-owned synthesis or properly licensed samples. A monophonic hum
can trigger a pad; that does not imply polyphonic/chord transcription. Explicit
harmonization can be a later musical edit.

First effect group: tone filter/EQ, tempo-related delay and gentle saturation.
Then add a small algorithmic reverb, compressor/limiter and richer modulation.
Distinguish changing notes/patches from retaining audio and processing its timbre;
model-based voice/timbre conversion is a separate optional future capability.

Shared processor shape: bounded state + input block + frame-timed parameters →
output block + next state. Preserve oscillator/filter/delay/envelope history across
blocks. Define start/reset/flush/tail behavior and maximum delay/tail/voice memory.
Clamp/reject invalid feedback, rates, frequency/Q, wet/dry, drive and dynamics inputs
through ordinary guards; use useful arithmetic contracts where encodable.

Effect controls belong after committed instrument/audio rendering on the track path,
then the mix/master meter/protection. No effect graph may implicitly monitor private
input. Schedule parameter changes on the audio timeline with smoothing. Explicitly
choose whether a replacement retains the old published tail; Stop flushes it.

Acceptance: bypass/no-op identity, analytical impulse/frequency response, finite
output and bounded decay, transition/click tests, automation across partitions and
resource/CPU budgets with four tracks active. A host-native reference can be used,
but do not claim bit identity with package/offline rendering without evidence.

## 4. Make effects and connect the existing ecosystem

The user wants both effect-authoring tools and existing plugins. Build a shared
processor/parameter model with separate execution adapters; a plugin format is a
host boundary, not a requirement to rewrite every effect in AILANG. This is planned
work: the current Loop Lab does not host third-party plugins or export them.

| Path | First useful deliverable | Execution boundary |
|---|---|---|
| Make our own | An effect starter with typed parameters, bounded state, block processing, presets, automation and a render/measurement harness | sunholo/audio reference + measured host runtime |
| Use the user's Ableton Live | Export committed WAV loops, then detected-note MIDI, into a Live template with existing instruments/effects | Local Live instance; first desktop integration |
| Use browser plugins | Insert one pinned WAM effect after a committed track; restore its state and bypass it | Browser Web Audio/AudioWorklet adapter |
| Use installed plugins | Process a committed loop with one locally installed VST3 effect, then stage its rendered result | Native companion on the machine with the plugin installed |
| Share our effects | Wrap one of our measured processors as a WAM; evaluate VST3/CLAP export separately | Build/runtime wrappers, not automatic package compatibility |

**Authoring toolkit.** Supply reusable gain/mix, oscillators/LFOs, envelopes,
filters, delay lines, smoothers and meters; compose them into processors with
declared channel layout, sample rate, parameter units/ranges, latency and tails.
Start with an editable delay or filter example and generated controls/presets.
Include offline WAV fixtures, impulse/frequency plots and level-matched A/B renders.
Use AILANG contracts for encodable state/parameter rules and guards for actual
samples, backed by tests and measurements. A host DSP or compiled kernel adapter
must demonstrate equivalence within declared tolerances; package verification
alone does not verify generated code or a different runtime implementation.

**Browser integration first.** Evaluate [WAM 2's API](https://github.com/webaudiomodules/api)
for audio nodes, parameter events, MIDI, state recall and lifecycle cleanup. Begin
with one reviewed, licensed, locally bundled/version-pinned effect rather than
loading arbitrary plugin URLs. A WAM's JavaScript/UI is application code, not an
isolated security boundary. Keep private capture outside the plugin graph; connect
only committed audio or an explicitly authorized private preview. Measure bypass,
tail/reset, reported versus measured latency, state recall and automation timing.
Do not assume every WAM supports offline rendering or required extensions.

**Native compatibility.** [VST3](https://github.com/steinbergmedia/vst3sdk) and
[CLAP](https://github.com/free-audio/clap) are native plugin interfaces; existing
desktop binaries cannot simply be imported into the browser graph. Prototype a
local companion using a native host library with license review, initially for
offline rendering of deliberately committed loops. Match OS/architecture and let
the installed plugin handle its own authorization. Keep transport metadata on the
control path and buffers in the renderer; the current Python/CLI planner bridge
is not the live plugin audio path. A plugin installed only on the Studio is not a
local laptop effect; network audio would be a separate latency/privacy design.

Later live hosting needs plugin discovery/validation outside the audio callback,
process isolation with a defined failure/bypass policy, bounded queues, plugin
editors/state, transport/automation, latency compensation, and tail accounting.
Validate format/host compatibility and actual plugin behavior rather than
promising universal support. Add CLAP and macOS Audio Units according to the user's
installed collection after the first VST3 path. SDK licensing does not grant rights
to redistribute third-party plugins, presets or sample assets.

**Learn from existing effects.** Use published algorithms and appropriately
licensed open-source code as references. For an available reference effect,
characterize behavior with impulses, frequency sweeps, amplitude steps, noise and
two-tone tests at several settings/sample rates. Distortion, dynamics and modulation
need more than a single impulse response. Write a behavior specification, implement
our own processor, then compare numerical responses and level-matched listening
fixtures on held-out inputs. Record implementation/asset provenance and applicable
permissions; do not copy proprietary code/assets or bypass protections. Treat
black-box reconstruction as measured approximation unless stronger evidence exists.
Choose a specific reference when we reach this work; no binary analysis is needed
for the first musical features.

### Ableton Live: use the existing local audio host

The user has Ableton Live installed locally. The browser is a convenient prototype
surface, not an architectural requirement: the package's pure plans/analysis can
serve a browser, CLI, desktop companion or DAW integration. Use Live as the first
desktop audio host rather than making our own native plugin host a prerequisite.
Keep the standalone browser instrument useful alongside this path.

1. **File handoff first:** export deliberately committed WAV loops with tempo,
   bar length, start alignment and gain metadata; later export detected NoteClips
   as Standard MIDI Files. Import them into a Live template with the user's chosen
   instruments and effect racks. Live supports
   [audio and MIDI file import](https://www.ableton.com/en/manual/managing-files-and-sets/).
   Verify loop length, Live's warp/tempo interpretation, note timing, levels and
   explicit export selection. A browser download is a deliberate handoff, not an
   automatic write into a Live project or a continuous audio connection.
2. **Live performance connection:** evaluate local virtual MIDI for notes/control
   and an explicit local audio route where needed. Add a transport adapter only
   after defining clock ownership and measuring latency/jitter on the user's
   device. [Ableton Link](https://ableton.github.io/link/) can coordinate beat,
   tempo, phase and optional start/stop; it does not carry our notes or audio.
   The current Tailscale preview is not a Link/audio bridge. Browser MIDI support,
   permissions and local endpoints must be checked rather than assumed.
3. **Deeper Live integration:** if the user's edition/license includes
   [Max for Live](https://www.ableton.com/en/live-manual/11/max-for-live/), evaluate
   a small device for clip/parameter control and later custom effects. Max for
   Live provides device-building and Live Set integration, but needs a specific
   AILANG adapter; installing Live alone does not establish that adapter or license.

Live's built-in devices remain hosted inside Live in this design; do not promise
to extract them into Loop Lab as browser/VST modules. Distinguish those devices
from independently installed third-party VST/AU instruments and effects. Record
the user's Live version/edition, relevant plugins and preferred performance
machine before choosing deeper APIs or building format-specific wrappers. This
can follow file handoff planning without delaying level processing or note capture.

An optional DSP authoring adapter can also evaluate
[Faust's WebAssembly/WAM export](https://faustdoc.grame.fr/manual/deploying/).
That offers another way to author DSP while AILANG owns checked plans, parameters
and orchestration. It is not evidence that AILANG currently compiles to a plugin.

Order: establish our processor contract with the first filter/delay; use one effect
to prove the authoring harness and browser adapter. Prioritize committed WAV/MIDI
handoff to the user's existing Live installation over building a native plugin
host. Explore our own native offline hosting later if independent plugin hosting
is useful. Keep auto-levels and Hum → Bass moving without waiting for a full DAW.
Third-party plugin internals are outside our proofs: test their boundaries and
observe output/latency, and retain post-effect metering/protection.

## Ownership, runtime and release gates

| Layer | Responsibility |
|---|---|
| std/audio | Shared WAV/PCM boundaries; resampling only when the coordinated upstream work actually ships |
| sunholo/audio | Level plans/reports, signal analysis, synthesis, stateful effects and checked block/clip processing |
| sunholo/music_patterns (proposed) | Note/tick/event semantics, correction/transposition, deterministic edits and query/replay rules |
| Loop Lab host | Device/capture privacy, workers, audio clock, playback/FX graph, local UI/assets/history and explicit persistence |
| AILANG core | Only reproduced missing kernels or measured runtime bottlenecks, sent through ailang messages |

The measured CLI bridge is adequate for prototype control decisions; it is not an
audio callback DSP engine. Benchmark the actual pitch/render algorithms on strict
VM and resident WASM/host workers, including startup, transfer, allocations and
worst-case inputs. No code-generation/native-kernel requirement is assumed in
advance. Request reusable core acceleration only with a small repro/profile.

Each feature group must retain recipe/PCM pins, enforce resource/effect bounds,
run native invalid/boundary/property tests, report quality/proof skips accurately,
and attach independent render/listening/reference evidence. Proved Real/Int models,
runtime guards, pitch quality and physical audio timing remain different evidence.
AI accompaniment and large-model sound generation remain later optional adapters;
the basic instrument works offline without a model account.
