# Loop Lab repository split

Completed 2026-10-23: the application is now
[sunholo-data/ailang-loop-lab](https://github.com/sunholo-data/ailang-loop-lab)
(currently private; organization access required). `sunholo/audio` stays here as
a generic source-independent library. The old application directory is a migration
pointer. Application-owned plans now live in the application's `docs/design/`;
the old document URLs point there rather than maintaining duplicate plans.

## History, dependency and validation

- Source application: `examples/live-loop` at producer commit
  `93314fc581a7ee2fefdc82392a92228f8b01a2dd`.
- `git subtree split` retained ten application commits at new root commit
  `3a34de3d237f8fcfdde2330804e74ae74353f930`.
- Standalone setup `c574fe4` adds application-owned docs, Apache-2.0 text,
  brand/font provenance, agent guidance, generated-file ignores, Makefile and CI.
- App commit `1b43ba5` records fresh GitHub clone and preview checks.
- The prerelease app uses an exact Git dependency on audio at producer revision
  `93314fc…`, not a sibling directory. Registry 0.3 publication is not claimed.
  Released application builds must switch to an exact published registry version.
- A fresh clone from GitHub passed 5-file compile, 10 strict native tests,
  45 Node host/parity tests, 6 Python HTTP/planner tests and package quality.
  Hosted CI has not executed; its separate runner-availability failure is recorded
  in the private application's check. Local passes are not called hosted CI passes.

Standalone quality: 3/6 contracts verified; 3 unsupported skips; 0 refuted/errors;
1 uncontracted generator; 11 signatures, v2
`9bab335ab4070639a5303dcef2a337045b6d91b389c4b9b70fe9710efa82ddce`;
declared FS/IO ceiling; feature release/0.2.0 notes and docs pass; 6/7 exports pure;
10 native tests and smoke pass. PUB016/PUB011 remain, with no gates. Mathematical
Real/Int proofs do not establish host/device or IEEE behavior. Raw reports belong
to the application, under `evidence/repository-split/`.

## Preview and source cleanup

The existing authorized private preview on HTTPS port 8449 now points to the
standalone application on loopback 8978. Server-side HTML/module checks pass and
the module bytes match the new repo; all other Serve routes are unchanged. This
is a source-root move, not a fresh microphone/listening/physical-latency pass.

Historical public package evidence links are pinned to the producer source
revision, so removal of the old source tree does not erase its original evidence.
Generated demo WAVs and optional runtimes were copied only for the local preview;
they are ignored and not committed as application source.

Generic package development continues under
[audio 0.3 scope](../../planned/audio-0.3-generic-scope.md): checked block processors,
analysis/reports and headless generation/model-output workflows. UI, capture,
session save/load and DAW integration are application development.
