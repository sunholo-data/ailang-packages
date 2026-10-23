# L0 prototype evidence — 2026-10-23

This is software evidence, **not full L0 acceptance**. The user ran the real
browser synthetic harness and reported Loop Lab working through the approved
private HTTPS preview. The [supplied Firefox report](browser-firefox158-user-run.json)
is preserved as user-run evidence; the agent did not independently rerun it.
A subsequent [runner v2 short profile](browser-firefox158-runner-v2-short.json)
passed all eight full-path handoffs in Firefox; the scope is recorded below.
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

The initial benchmarks/browser baseline used AILANG `v0.54.17-dirty`, commit `8f58117f265471584176e2aeb45996c2c9822577`,
built 2026-10-22. macOS 26.6.2 arm64, Python 3.13.7, Node 26.12.1.
The current `quality.json`, `verify.json`, native and integration tests were rerun
on clean `v0.54.18`, commit `cd33d050b2276633c82624453309ebf7fcea9e2f`,
built 2026-10-23 11:36:25. The numerical benchmark samples remain the historical
v0.54.17 measurements; they have not been relabelled as v0.54.18 performance.
The optional WASM binary was built from a **clean archive of the earlier 8f58117
benchmark commit**, not the concurrently modified core checkout, using Go 1.26.10 and its
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
bytecode and runtime contract checking on v0.54.18; its output is preserved in
`runtime-contract-init.json`. That init probe does not measure contracts for every
command path. No whole-state-machine proof is claimed.

`host-kernel-tests.txt`: 19/19 Node tests, 0 failed/skipped. Tests cover bounded
preparation, finite domains, four-part mixing, zero private output with nonzero
private input, cancellation, fixed capacity, exact in-block replacement, late/stale
rejection, malformed initialization and 100 handoffs, plus four orchestration
tests for bounded waiters, timeout/cancellation cleanup and timing-summary validity.
Five further checks cover activation-clock domains, the real strict planner
regression and bounded visibility accounting/delivery. The clock and processor
base class in the render-kernel checks are fakes: these exercise the actual kernel code but do not measure
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

## Brand update and new browser runner

The user supplied the current Sunholo guide and authorized the AILANG logo. Original
local tokens, SVG and licensed Montserrat files are preserved with SHA-256 provenance.
HTML asset references and SVG parsing were checked; the private HTTPS preview served
the page, SVG, both fonts, token CSS, runner module and helper module with HTTP 200
and appropriate MIME types. The computer-use service still had no accessible browser
window, so the updated layout has not been visually reviewed by the agent.

`/soak-check.html` adds real planner/worker/worklet orchestration for 8-handoff trials
or 100 handoffs plus 30 audio minutes. It includes worker hashing/transfer round trips,
rotates all four tracks, rejects taking over an active session, and cleans up its own
epoch. The agent has **not independently run this runner in a browser**. User-run
trials below exposed two host-adapter issues. The Node suite is regression evidence,
not a substitute for a complete browser short/soak run.

## Interrupted user trials and runner v2 fixes

Two further user-supplied Firefox reports are preserved without calling them passes:

- [Soak interrupted by visibility](user-trials/soak-visibility-interrupted.json):
  three confirmed planner/render handoffs, all at the exact frame, before the old
  runner deliberately cancelled on hide. Four preparation samples and 13 bridge
  samples include work on a fourth pending take and cleanup; they are not four
  completed handoffs or a completed soak.
- [Short run rejected at activation](user-trials/short-activation-rejected.json):
  preparation/staging proceeded, but the planner rejected activation and cleanup
  reset the owned test session. No confirmed handoff was recorded.

The runner checked renderer/planned equality before sending Activate, and Schedule
had returned success. That isolates the remaining activation guard to the supplied
`now` clock. The original report did not record that clock. A regression reproduces
the exact error against the real strict planner with main clock 128 frames behind
an otherwise correct acknowledgement, then passes with the acknowledged frame as
its lower bound. Incorrect applied frames remain rejected. This supports the clock
mismatch diagnosis; the next browser report will also record both clock values.
[Mozilla documents block updates and possible precision reduction in currentTime](https://developer.mozilla.org/en-US/docs/Web/API/BaseAudioContext/currentTime).
No particular Firefox privacy setting is inferred from the supplied report.

Both the instrument and runner now use `max(mainFrame, appliedFrame)` only after
validating the exact planned/applied frame. The planner's guard is unchanged.
Runner v2 includes per-handoff clock observations and a last activation diagnostic
if a later request fails. Background visibility is recorded (32 bounded events,
all intervals counted) without aborting synthetic audio. Page closure, manual Stop,
context suspension, deadline/activation failures and incomplete duration still fail
or interrupt the run. The actual microphone capture UI still cancels on hide/focus
loss. The subsequent user-run short profile below validates the activation fix;
background-browser coverage and a complete soak remain open.

## Successful user-run runner v2 short profile

The [supplied Firefox 158 report](browser-firefox158-runner-v2-short.json) started at
2026-10-23T13:34:20.546Z and passed/completed the 8-handoff profile at 44.1 kHz.
Each of the four tracks activated twice; all eight applied frames exactly equal
their planned frames. There were zero clamped frames over 56.0514 audio seconds.
Private input peak was 1 while program output before commit was 0, becoming nonzero
after commit. This is user-run evidence, not an independent agent browser run.

The first activation directly confirms the diagnosed clock mismatch: main frame
46081 trails the correct planned/applied frame 46148 by 67 frames (about 1.52 ms).
Runner v2 used the confirmed frame 46148 as its known clock floor and the planner
accepted it. All subsequent activations also passed without weakening frame equality.

Worker preparation/hash median was 5 ms and p95 6 ms (8 observations); worker round
trip median 6.5 ms and p95 32 ms (8 observations). Bridge median was 34.3515 ms,
p95 53.508 ms and maximum 76.915 ms (26 observations, including setup/cleanup).
These are small-sample observations, not latency guarantees or physical measurements.
The stored summary values were recomputed from the supplied raw arrays and agree.

Visibility remained foreground for this entire run (`hiddenMs=0`, no changes), so
this does not validate background-tab operation. The 100-handoff/30-minute soak,
background behavior, microphone/device lifecycle and physical loopback remain open.
