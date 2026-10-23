# L0 prototype evidence — 2026-10-23

This is software evidence, **not full L0 acceptance**. The user ran the real
browser synthetic harness and reported Loop Lab working through the approved
private HTTPS preview. The [supplied Firefox report](browser-firefox158-user-run.json)
is preserved as user-run evidence; the agent did not independently rerun it.
Physical microphone/speaker loopback, the full lifecycle matrix, 100 actual host
handoffs and a 30-minute soak remain open. No physical audio timing has been measured.

## User-run browser check

The supplied report identifies Firefox 158 and a 44.1 kHz AudioContext, started at
2026-10-23T10:50:46.926Z. Do not infer actual hardware or macOS version from the user
agent string. One real browser handoff passed:

| Observation | Reported result |
|---|---:|
| Private input peak | 1.0 |
| Program peak before commit | 0.0 |
| Captured frames | 14336 (about 325 ms at 44.1 kHz) |
| Harness preparation | 4 ms |
| Staged at frame | 23808 |
| Planned / applied frame | 382530 / 382530 |
| Activation error | 0 frames |
| Program peak after commit | 0.203407883644104 |
| Harness verdict | passed |

This observes a nonzero private input while the measured program path stays
silent, followed by a nonzero committed program signal at the exact planned frame.
The harness deliberately mutes speaker output. Its preparation measurement times
`prepareTake` inline; it does not include the application's preparation worker,
SHA-256 or buffer-transfer costs. This is one sample, not a latency percentile or
long-session guarantee. The reported 28.798 ms output latency is a browser estimate;
reported base latency 0 does not establish zero physical latency.

## Toolchain and checks

AILANG `v0.54.17-dirty`, commit `8f58117f265471584176e2aeb45996c2c9822577`,
built 2026-10-22. macOS 26.6.2 arm64, Python 3.13.7, Node 26.12.1.
The optional current WASM binary was built from a **clean archive of that same
commit**, not the concurrently modified core checkout, using Go 1.26.10 and its
matching `wasm_exec.js`. Its version API reports `v0.54.17-8f58117` and its
SHA-256 is `92742e0b0c8f10d5e3eeac12f752ec27f7e6f45bc9497bf59b8433a44ff7d354`.
An older unversioned dev WASM binary failed module loading; it was not used for
the current measurements or runtime decision.

| Quality section | Recorded result |
|---|---|
| Compile | 4 files pass |
| Contracts | 3/6 verified, 0 refuted, 3 skipped, 0 errors, 1 uncontracted export |
| Interface | v2 `a777d55738158509c56b5a2df5f191fa7206179e48473ef35989f7962d6c56cd`, 11 signatures |
| Effects | Explicit max `[FS, IO]`, rank FS; planner pure; generator FS limit 4 and IO limit 1; smoke IO limit 1 |
| Release | Feature, nonempty 0.1.0 changelog section; this example is not being published |
| Documentation | AGENT.md, AI summary, both exported modules documented; public registry overlap lookup completed |
| Style | 7 exported functions, 6 pure (86%) |
| Native package tests | 10/10 pass, 0 failed/skipped, 1 file; strict run: 9 named bodies on VM, 0 fallback, 1 property on evaluator with 100 cases |
| Smoke | Present and passed |
| Badges / gates | PUB016: 3 skipped contracts; PUB011: generator has no contract; no gates |

`ceilDiv`, `boundaryFrame` and `nextBoundary` are the proved functions. Integer
inputs and intermediate products stay within stated bounds. Z3's mathematical
integer proof is not a machine-overflow or audio callback scheduling proof.
`initial`, `apply` and `handle` are skipped because of unsupported higher-order,
pattern or JSON encodings; their guards execute normally and are tested.
The effectful `generate() -> ()` has a fixed capability budget and checked WAV
construction, but no postcondition: a vacuous Unit assertion would add no evidence.
The smoke module passed the quality run; `handle(init)` also executed with strict
bytecode and runtime contract checking. No whole-state-machine proof is claimed.

`host-kernel-tests.txt`: 10/10 Node tests, 0 failed/skipped. Tests cover bounded
preparation, finite domains, four-part mixing, zero private output with nonzero
private input, cancellation, fixed capacity, exact in-block replacement, late/stale
rejection, malformed initialization and 100 handoffs. The clock and processor
base class are fakes: these exercise the actual kernel code but do not measure
Web Audio, speaker sound, GC deadlines or device behavior.

`integration-tests.txt`: 6/6 Python tests pass. They invoke the real AILANG JSON
handler and strict VM, exercise Prepare→Schedule→Activate→Reset, reject malformed
commands and stale epochs, and test the live loopback HTTP origin/Host, traversal,
request size, flat metadata-only and fixed non-mutating probe boundaries.

`fixtures.json`: four actual generated WAV byte hashes and independent Python
`wave` metadata checks (128000 frames, 16000 Hz, mono PCM16, 256044 bytes each).
These establish fixture identity/shape, not audible quality or cross-platform pins.
`generator-bytecode-limit.txt` records the VM's explicit refusal to push bounded
effect frames. The evaluator generator succeeded; its budget was not removed.

## Performance observations

| Probe | n | Median | p95 |
|---|---:|---:|---:|
| Evaluator CLI control sequence | 25 | 29.58 ms | 30.65 ms |
| Strict-bytecode CLI control sequence | 25 | 31.47 ms | 35.01 ms |
| Resident WASM in Node/V8 control sequence | 25 | 4.56 ms | 14.00 ms |

The sequence is one configure command plus 24 parameter commands through the same
JSON handler, updating state each time. All three final states match. CLI times
include process startup, package resolution, parsing, compilation and invocation.
WASM times exclude startup/module load; the reported 3.78 seconds from runtime
startup through **all** probes is a cold total, not a pure initialization duration.
The separate warm WASM init probe has 20 samples; use its raw distribution rather
than calling it a control-sequence or DSP measurement. p95 uses the nearest-rank
sample at ceil(0.95*n), with small-n limitations. No percentile is a guarantee.

For this workload the resident runtime saves process/compile overhead, and the
local evaluator and VM are comparable. The earlier audio render probe's ~29× VM
speedup does not transfer to this small control workload. Native Go code generation
was not benchmarked. WASM's exported `ailangCall` engine is not established here as
the CLI bytecode engine, and Node/V8 is not browser-worker or audio-device evidence.

Decision: keep the fixed strict-bytecode local bridge as the supported L0 baseline,
and use the optional worker probe to measure the browser before choosing the L1
resident transport. The 200 ms staging margin is a prototype policy supported by
these local observations, not a p95 end-to-end preparation/routing/physical latency
claim. Keep all language execution, allocation-heavy preparation, hashes and network
activity outside the audio render callback.

## Reproduction and next evidence

See the [example README](../../README.md) for commands. Raw reports are preserved
next to this file. Repeat `/host-check.html` across the reference browsers/rates;
it never opens the microphone. The user-run Firefox check above is the first real
browser result. Next run real capture/playback and physical loopback checks, the
device/lifecycle matrix, at least 100 actual handoffs, and a 30-minute soak before
accepting L0.
