# Audio 0.3 feature group: private preparation, recovery and WAV handoff

Implemented 2026-10-23. The audio package remains an unpublished **0.3.0 candidate**;
this consumer is local `sunholo/live_loop_lab@0.2.0`, never a registry release.
It combines the capture-ownership fixes with the existing level-plan API and adds
three usable host features. No AILANG core change or external plugin dependency
was required. Audio package source/content is unchanged from the level-API milestone.

Later [boundary/extraction validation](../audio-application-boundary/README.md)
moves the consumer fixture into the application (five compiling files), confirms
isolated consumer tests and clarifies generic package versus application scope.
The four-file quality snapshot below predates that fixture relocation.

## What the user can do

1. Capture privately and select Off, Peak-safe or Matched. Read the gain reason,
   before/after sample peak and active-window RMS before explicitly committing.
   Re-preparation uses the same unlevelled, trimmed/padded and faded original;
   switching modes does not compound gain or apply another fade.
2. Undo or redo the last committed take on each part. Restore uses the normal
   prepare/stage/activate protocol and the next planned loop boundary. Track
   level/pan/mute parameters are independent and are not part of take undo.
3. Download an **active committed** part as mono PCM16 WAV, before track level,
   pan and mute. The filename records active revision, 120 BPM and four bars.
   Import manually into Live and check warp/tempo interpretation against the
   eight-second/four-bar length. No embedded tempo marker or Live automation is claimed.

The prepared candidate is still inaudible until commit. No private monitor, sample
upload endpoint, project/session persistence or plugin host is introduced. A private,
scheduled, discarded or obsolete worker result cannot become an exported asset.
Stop/reset clears retained history and the owned download object URL; files already
explicitly downloaded are external user-owned files.

## Boundaries and implementation decisions

- AILANG `levels` owns the package reference semantics. `static/levels.mjs` is a
  browser implementation tested against it, not AILANG running in the callback or
  proof-carrying JavaScript. The fixed CLI planner receives metadata only.
- Matched: target active-window RMS 0.125, peak ceiling 0.501187, max boost 4,
  minimum active frames 1024. Activity windows are 1024 frames, floor 0.001.
  This is a configurable package policy with a prototype host preset, not LUFS,
  true peak, denoising, compression or universal instrument calibration.
- The browser uses Float32 sample buffers. If storage rounding raises the peak
  above the double-precision ceiling, it re-renders the original with a small
  reserve and checks the actual output again. That adjustment is explicit in
  worker metadata; double-precision reference equivalence does not cover it.
- One current, previous and pending buffer per part: at most 12 eight-second mono
  buffers / 18,432,000 retained Float32 samples at the 192 kHz host ceiling
  (73,728,000 sample bytes). This excludes renderer/worker/download copies, temporary
  allocation and other browser memory; it is not a total-heap guarantee.
- History/export moves only after the exact-frame renderer receipt and successful
  planner activation. Undo/redo never rolls revisions backwards; each restore is
  a new revision. Pending rejection preserves the active/previous pair.
- Worker jobs and callbacks are session/identity scoped. Discard invalidates late
  preparation; Stop invalidates late activation. Fatal worker errors release active
  input, discard private state and require reset before another capture.
- WAV uses the package's *32767, half-away-from-zero encoding and strict finite
  full-scale samples. Browser downloads save deliberately committed audio only.

## Validation

Raw logs: [`examples/live-loop/evidence/audio-v3-workflow`](https://github.com/sunholo-data/ailang-packages/blob/93314fc581a7ee2fefdc82392a92228f8b01a2dd/examples/live-loop/evidence/audio-v3-workflow/README.md).

| Check | Observed result |
|---|---|
| Node tests | 45/45 passed; 0 failed/skipped |
| HTTP/planner Python tests | 6/6 passed |
| Native app tests | 10/10 passed, strict bytecode, no evaluator fallback |
| Cross-language adapter | 18 signal/policy cases × 7 fields agree with strict AILANG with runtime contracts enabled; numeric tolerance max(1e-15, abs(expected)*1e-12) |
| WAV reference | Pinned browser WAV bytes exactly equal AILANG clip_pcm output; Python wave independently reads the header/format |
| Actual-app integration | Fake DOM/Media/Audio/Worker boundaries, actual preparation job, actual render worklet and real strict AILANG planner; capture → mode changes → commit → undo → redo → download |
| Ownership/races | Export stays on old current during private/scheduled take; late discarded worker reply and post-Stop activation ignored; input released after worker error; obsolete worker error ignored |
| Private HTTPS | Six server-side HTTPS requests/probe pass; nine loopback routes pass; other Tailscale Serve routes unchanged |

The actual-app test checks three exact activations, byte-equal restoration/redo of
downloaded content, default-frame counts and raw-sample exclusion from API/report.
Browser/device APIs and downloads are faked in that test; it is not a real Firefox
download, microphone lifecycle, audible listening or Ableton-import test.

### Local application's quality report, section by section

[`quality.json`](https://github.com/sunholo-data/ailang-packages/blob/93314fc581a7ee2fefdc82392a92228f8b01a2dd/examples/live-loop/evidence/audio-v3-workflow/quality.json):

| Section | Result |
|---|---|
| Compile | 4 files pass |
| Contracts | 3/6 verified; 3 unsupported-encoding skips; 0 refuted/errors; 1 uncontracted asset generator |
| Interface | 11 signatures; unchanged v2 `a777d55738158509c56b5a2df5f191fa7206179e48473ef35989f7962d6c56cd` |
| Effects | Declared `[FS, IO]`, rank_max FS; generator FS limit 4 / IO limit 1; planner pure |
| Release | `kind=feature`, nonempty 0.2.0 changelog section |
| Docs | AGENT.md and ai_summary present; reported exports covered = 2 |
| Style | 6/7 exported functions pure |
| Tests/smoke | 10 native tests and smoke passed, attested execution |
| Badges/gates | PUB016 (3 skipped), PUB011 (1 uncontracted); no gates |

The unchanged audio 0.3 package has 24 compiling files, 12/57 contracts verified,
45 skips (5 missing postcondition, 40 unsupported), 0 refuted/errors, 33 uncontracted
exports; 130 interface signatures, declared IO ceiling, 89/89 pure exports,
feature release/docs checks, 145/145 package tests and passing smoke/dry-run.
See the earlier [package evidence](../audio-levels-0.3.0/README.md). No package code
changed in this consumer increment, so that report was not rerun solely for the UI.
Float=Real / Int mathematical proofs do not verify IEEE arithmetic or these host
adapters; all skipped results remain unproved.

### Descriptive preparation costs

[`node-worker-timing.json`](https://github.com/sunholo-data/ailang-packages/blob/93314fc581a7ee2fefdc82392a92228f8b01a2dd/examples/live-loop/evidence/audio-v3-workflow/node-worker-timing.json)
records one warm-process preparation per mode/rate, including shaping, analysis,
gain, output checks and SHA-256. Eight-second mono fixtures took 27.4–44.8 ms at
44.1/48 kHz on this host. These are Node kernel measurements, excluding browser
worker startup/transfer and not callback deadlines or physical latency.

### Review boundary

The existing private preview origin serves these controls; reload the page to use
the new modules. The backend is a fresh in-memory session. Other preview routes
were preserved. The Node integration does not substitute for user/browser review.
Try capture/mode changes/commit/undo/redo, then download an active part and inspect
its four-bar length in Live. No private take should appear in a download before
activation. No new 30-minute pass is claimed: runner v3 identifies the changed
preparation worker; the user's v2 soak remains historical baseline evidence.

Next feature groups remain project save/load with explicit committed assets, then
hum-to-notes and the first instrument/effect processors. This increment does not
implement MIDI export, pitch detection or third-party plugin hosting.

## Reproduce

```sh
cd examples/live-loop
ailang lock --check
ailang check --package .
ailang test --strict-bytecode --package .
node --test test/*.test.mjs
python3 -m unittest discover -s test -p '*_test.py'
ailang pkg quality --json .
```

The consumer-owned [adapter_probe.ail](https://github.com/sunholo-data/ailang-packages/blob/93314fc581a7ee2fefdc82392a92228f8b01a2dd/examples/live-loop/test/fixtures/adapter_probe.ail)
uses the application's `--package-dir` and declared dependency. The Node parity
test supplies only bounded fixture IDs 0..17 and no longer reaches into this repo's
package source or design-document directories. A later boundary/migration report
records the five-file app quality report after relocating this fixture.
