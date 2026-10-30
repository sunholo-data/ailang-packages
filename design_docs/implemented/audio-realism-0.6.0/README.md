# sunholo/audio 0.6.0: closer-to-real synthesis (evidence)

Plan: stapledons-godot `design_docs/planned/r3/sunholo-audio-realism.md` (R3-SUNHOLO-AUDIO-REALISM, approved by Mark on 2026-10-30). Measured on a Mac Studio (Apple M4 Max) with AILANG v0.54.18.

| Check | Result |
|---|---|
| 0.5.0 interface (`ailang iface -compact`, 15 modules, 154 lines) | every line present in 0.6.0 (`comm -23` empty) |
| Frozen compat pins (`compat.ail`, committed at 5ae8003e before any code change) | 8/8 through `recipe.render` and `sound.renderSound` |
| `ailang test --package .` | 270 passed (evaluator 302 s; `--bytecode` about 10 s) |
| `ailang verify --package .` | 16 verified, 0 counterexamples, 59 skipped (float encodings) |
| `ailang pkg quality .` | no gates; tests and smoke attested passing ([quality.txt](quality.txt)) |
| Strict VM = interpreter | identical on renderProbe, wavProbe, levelProbe, filterProbe, colourProbe, oscProbe, eventsProbe, spaceProbe, soundProbe, compatProbe |
| First consumer | stapledons-godot on a path pin: all 41 shipped sounds regenerate byte for byte before any recipe change (`make sound-synth-check`) |

Measured check values (each from its test):
- band-pass gains match the closed form within 0.05 dB;
- PSD slopes: white −0.05, pink −3.05, brown −6.01 dB/octave;
- FM lines equal |J_k(1)| and |J_k(2)| within 0.002;
- the tuned pluck is within 1 cent of its target, and the blocked string equals a per-sample reference bit for bit;
- the reverb's T60 is within 5% of the target, and allpass energy is 1 within 1e-9.

Timings: [timings.json](timings.json). Two items are over their budgets: pink at 1.51× white (budget 1.5×), and the evaluator suite at 302 s (budget 180 s); the suite takes about 10 s on `--bytecode`.

Upstream: ailang#2029. A `foldl` that conses onto its accumulator is superlinear on the VM and the interpreter. The package avoids that pattern and does not otherwise work around it.

Not published yet: the release waits for the consumer's listening ruling (stapledons-godot AR9).
