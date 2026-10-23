# Capture ownership and lifecycle follow-up

Scope: normal Loop Lab input handling after merged PR 158's successful reference
software soak. Runtime package `sunholo/audio@0.2.0`, the pure planner and the program
renderer are unchanged. This is an application follow-up, not a registry release.

## Problem and change

The old hold path checked a shared `held` flag after `getUserMedia`. Releasing an
opening request and beginning a later hold could make that flag true again while
the old promise was still pending. Its late stream could attach to the wrong hold;
a late rejection could also cancel newer work. Code inspection identified this
race; no claim is made that a real microphone leak was observed in the browser.

`CaptureLifecycle` now owns a request/source/stream by object identity and a take ID.
Cancel invalidates it. Every eventual stream from an obsolete/disposed request is
stopped; its errors and device-ended callbacks cannot mutate newer captures. The
page-level permission gate bounds outstanding requests to one. Browser prompts
may remain pending indefinitely; cancellation revokes app intent rather than
pretending the browser permission operation itself was aborted.

An explicit Enable microphone action resolves the initial permission prompt before
hold capture. Its temporary stream is stopped without creating a take. The normal
capture path releases input on release, cancel, device loss and dispose; matching
buffer identity is required before preparation. A two-second finish timeout cancels
a stalled take. A processor error releases input and requires a fresh capture
context. The worklet's stop/cancel messages can carry IDs; existing unscoped test
controls remain compatible. Old IDs cannot stop a newer capture. Its output stays
zero and its meter resets per capture.

Window/page/control focus loss and audio-device-change callbacks cancel active
microphone capture. Lifecycle diagnostics whitelist states, counters and aggregate
peaks; they omit raw samples, device labels and IDs. They do not automatically
certify physical routing or device behavior.

## Automated evidence

`node-tests.txt`: **34/34 passed, 0 failed/skipped**. This retains the 19 earlier
kernel/orchestration checks and adds 14 input/worklet cases plus one full application
flow. Cases include release before grant, late success/rejection during a newer
take, single-request bounds, preflight disposal, normal/automatic completion, stale
device callbacks, disconnect, dispose during permission, processor error, finish
timeout, bad metadata, denial/retry, and old stop/cancel IDs.

The application regression imports the actual `app.mjs` and uses the real strict
AILANG JSON handler. It executes preflight → private capture → worker preparation
→ Prepare/Schedule/Activate with a lagging main clock → tab hide during pending
permission → late cleanup → device change/control focus loss → Stop/reset. DOM,
media tracks, audio contexts, workers and worklet clocks are test doubles; it does
not attest actual browser permission, hardware or physical audio behavior.

| Quality section | Result |
|---|---|
| Compile | 4 AILANG files pass |
| Contracts | 3/6 proved, 0 refuted, 3 skipped, 0 errors; 1 uncontracted generator |
| Interface | 11 signatures, unchanged v2 `a777d55738158509c56b5a2df5f191fa7206179e48473ef35989f7962d6c56cd` |
| Effects | Declared `[FS, IO]`, rank FS; pure planner; bounded asset generation/smoke |
| Release | Feature, matching 0.1.0 changelog (local example only) |
| Docs | AGENT.md, AI summary and both exported modules documented |
| Style | 6/7 exported functions pure, 86% |
| Native package tests | 10/10 passed, 0 failed; one evaluator property/100 cases in the established suite |
| Smoke | Present and passed |
| Badges/gates | PUB016: 3 skipped contracts; PUB011: effectful generator uncontracted; no gates |

This quality report measures AILANG modules, not the browser controller. Only the
three arithmetic helpers are proved. Node tests and device/user checks are separate
from proofs. `toolchain.txt` identifies the installed compiler. Runtime contract
execution is not claimed from the quality report.

## Browser/device work still required

The guide `/microphone-check.html` requests no permissions itself. The user should
exercise preflight/denial, private capture/discard, explicit commit, focus/tab/app
loss, actual device disconnect and repeated Stop/reset, then copy local metadata
reports with the scenario/observation. Agent validation has not opened a microphone
or attested these new browser flows. The earlier Firefox 100-handoff/30-minute
synthetic report remains baseline evidence; it does not replace these new real-input
checks or physical loopback/listening. Native implementation tests do not supply
an operating-system microphone indicator guarantee for other apps sharing a device.
