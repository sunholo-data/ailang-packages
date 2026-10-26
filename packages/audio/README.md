# sunholo/audio

Deterministic, pure sound synthesis and measurement for AILANG: JSON recipes of gliding sines
and filtered noise rendered to floats, checked mono/stereo clips, PCM16/WAV import/export,
editing, mixing, and offline measurements. The same bits on the strict bytecode VM and the interpreter, on the tested host. Cross-architecture claims require their own evidence.

The checked clip APIs do not depend on where samples came from: game assets,
recordings, TTS and AI-generated audio can share the same processing pipeline.
Procedural synthesis is included; model inference belongs to `std/ai` or provider
adapters. Loop Lab is an application/reference consumer, not the package's domain.

```sh
ailang install sunholo/audio
ailang pkg-docs sunholo/audio   # AGENT.md: the recipe schema, conventions, pitfalls
```

- `clip`: validated planar mono/stereo arrays, explicit channel selection/conversion and interleaving.
- `edit`: gain, trim, padding, reverse, append, fades, crossfades, mixAt and equal-power mono panning.
- `clip_pcm`: channel-preserving PCM16/WAV adapters with explicit Reject/Saturate clipping policy.
- `levels` (0.3.0): whole-signal/active-window RMS, block accumulation,
  and explicit Off/PeakSafe/MatchRms preparation with bounded boost and peak ceilings.
- `block` (0.3.0): checked stateful mono/stereo low-pass/high-pass/bypass,
  independent channel histories, reset and per-block/cumulative budgets.
- `delay` (0.4.0): checked integer-frame feedback echo, independent
  mono/stereo history, explicit tail rendering/reset and allocation budgets.
- `automation` (0.4.0): linked linear-gain ramps, exact target frames,
  immediate changes and mid-ramp retargeting, independent of block partitioning.
- `recipe`: layers (sine with glide, vibrato, beat; white or legacy noise), envelopes, filters
  and sweeps, swell, drive, edge fades, peak normalisation; loop rules that refuse clicks.
- `pcm`: `pcm16`, `wav16`, strict `wavInfo`, `pcm16Floats`; checked encoding and bounded decoding.
- `safety`: typed `AudioError`, `RenderLimits`, `defaultLimits`; recipe validation and bounded rendering live in `recipe`.
- `mix`: `tile` (loops and one-shots at start samples), `sum`.
- `analysis`: peak and gated RMS in centi-dB, high-pass keep, low-band level, loop seam.
- `dsp`, `noise`, `reference`: the primitives, the two seeded generators, pinned references.

Made for Stapledon's Voyage (stapledons-godot), whose synthesised sounds regenerate byte for byte
from it. Use the checked APIs for untrusted recipes and bytes. Render stability: an existing recipe's samples change only in a `breaking` release.


For untrusted input, use `parseRecipesChecked(text, defaultLimits())`, then
`renderChecked(recipe, limits)`, then `wav16Checked(samples, recipe.rate, limits.maxFrames)`.
For stereo editing, wrap rendered samples with `clip.fromMono`, apply `edit` operations,
and export with `clip_pcm.toWav16` using an explicit clipping policy. Every checked step returns `Result[..., AudioError]` and executes guards in ordinary runs.
`--verify-contracts` adds runtime assertions during validation; it is not needed for input rejection.
See [AGENT.md](AGENT.md) for domains, resource limits, error variants and compatibility behavior.

0.2.0 groups the clip/editing features with the 0.1.1 hardening work.
0.3.0 adds offline level preparation and generic stateful block filters.
It exposes gain decisions for a host-owned private preview/undo/commit flow;
it does not add that UI or microphone gain control itself. See the
[validation evidence](../../design_docs/implemented/audio-levels-0.3.0/README.md).
See [block processing evidence](../../design_docs/implemented/audio-blocks-0.3.0/README.md)
and `examples/block_pipeline.ail` for headless recipe and speech/model PCM fixtures.
Loop Lab has [its own application repository](https://github.com/sunholo-data/ailang-loop-lab)
and consumes this package; its UI/session features are independently versioned.

Version **0.5.0** adds per-layer `lowpass_poles` (dark sounds) and refuses unknown layer keys. Version **0.4.0** adds delay and gain automation. Both work on
source-independent clips: process provider-produced PCM, game assets or DAW tracks
with the same guards. `examples/effects_pipeline.ail` demonstrates a synthetic
speech/model PCM fixture → fade → echo → peak preparation → measured WAV. Its
reported delivered measurements are taken after decoding the quantized output.
This does not perform model inference or host devices/plugins. Delay and gain
processing allocate and validate state; no realtime callback guarantee is claimed.
See [effect evidence](../../design_docs/implemented/audio-effects-0.4.0/README.md)
and [AGENT.md](AGENT.md) for limits, ramp endpoints, history and tail semantics.
