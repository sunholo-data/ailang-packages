# Audio clips and editing 0.2.0

Status: second roadmap milestone implemented and validated, 2026-10-23. Publication is held until the feature group is validated and reviewed. This extends PR #155; the unpublished 0.1.1 hardening work will be included in 0.2.0.

Scope: validated planar mono/stereo clips backed by existing Array[float], explicit channel conversion/interleaving, checked editing/mixing, and channel-preserving PCM16/WAV adapters. Core updates remain with the other agent. Existing recipe records and mono render samples stay unchanged.

Policies: internal samples allow finite headroom; mono duplicates at unity; stereo downmix uses 0.5L+0.5R; mono panning uses equal-power gains with exact hard-pan endpoints; edits preserve rate/layout; PCM16 output has explicit Reject/Saturate policies and preserves legacy quantization for in-range samples. Rate/layout mismatch returns an error. There is no implicit resampling.

Clip records are public and can be forged, so every public operation validates its input. Limits bound input and output frames and total samples before allocation. Empty clips are valid. Temporary lists used by current array constructors/validation are bounded by the same dimensions; these are not exact host-memory or realtime guarantees.

Acceptance: independent stereo byte fixtures retain both channels; interleave/deinterleave and bounded PCM round trips have native properties; edits have known expected samples; malformed clips, non-finite values, format mismatch and allocation overflow are rejected; all new exports have meaningful contracts; package quality, source tests, smoke, strict VM and runtime-contract probes are recorded separately. Publication remains deferred.
