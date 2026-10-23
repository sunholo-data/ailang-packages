# sunholo/audio

Deterministic, pure sound synthesis and measurement for AILANG: JSON recipes of gliding sines
and filtered noise rendered to floats, 16-bit PCM and WAV in and out, mixing, and offline loudness
measures. The same bits on the strict bytecode VM and the interpreter, on any machine.

```sh
ailang install sunholo/audio
ailang pkg-docs sunholo/audio   # AGENT.md: the recipe schema, conventions, pitfalls
```

- `recipe`: layers (sine with glide, vibrato, beat; white or legacy noise), envelopes, filters
  and sweeps, swell, drive, edge fades, peak normalisation; loop rules that refuse clicks.
- `pcm`: `pcm16`, `wav16`, `wavInfo`, `pcm16Floats`.
- `mix`: `tile` (loops and one-shots at start samples), `sum`.
- `analysis`: peak and gated RMS in centi-dB, high-pass keep, low-band level, loop seam.
- `dsp`, `noise`, `reference`: the primitives, the two seeded generators, pinned references.

Made for Stapledon's Voyage (stapledons-godot), whose synthesised sounds regenerate byte for byte
from it. Render stability: an existing recipe's samples change only in a `breaking` release.
