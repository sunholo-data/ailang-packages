# Generic audio / reference application boundary check

2026-10-23. The user identifies Loop Lab as an application, a main consumer of
`sunholo/audio`, and a candidate for its own repository. The implementation keeps
the existing app in place while preparing a concrete split and removing a test's
producer-checkout assumption. No remote repo was created, source directory deleted,
package published or preview route changed in this increment.

Plans: [application extraction](../../planned/loop-lab-repository-split.md),
[generic audio 0.3 scope](../../planned/audio-0.3-generic-scope.md).

## Changes

- Package docs now describe source-independent processing of game/procedural audio,
  recordings, TTS PCM and model-generated samples. Correct the overly broad speech
  exclusion: the package does not perform model inference, but can process supported
  speech audio. Pure DSP stays separate from AI/Net/device/session effects.
- Move the reference probe into the application's `test/fixtures/`. Its Node test
  invokes AILANG with the application's own manifest/dependency and canonical module
  path, without climbing to this repository's `packages/audio` or design docs.
- Separate generic release recommendations (block processors, reports, headless
  procedural/AI-output examples) from application work (session save/load, UI,
  capture, instruments, Live/plugin integration).

## Isolated consumer check

[`staging.json`](staging.json) records an isolated local export: 83 application
files and 29 library files, plus the repository license. The application depends
on an explicit sibling `../audio` copy. Generated audio/runtime/cache files are
excluded. This is a developer dependency check, not a new GitHub repository,
registry installation or a completed documentation migration.

All six commands passed from the isolated application root:

| Command | Evidence |
|---|---|
| `ailang lock` | [isolated-1.txt](isolated-1.txt) |
| `ailang check --package .` | [isolated-2.txt](isolated-2.txt): 5 files pass |
| `ailang test --strict-bytecode --package .` | [isolated-3.txt](isolated-3.txt): 10/10, 0 fallback |
| `node --test test/*.test.mjs` | [isolated-4.txt](isolated-4.txt): 45/45, including consumer API/codec parity |
| Python HTTP/planner tests | [isolated-5.txt](isolated-5.txt): 6/6 |
| `ailang pkg quality --json .` | [isolated-app-quality.json](isolated-app-quality.json): no gates |

[`isolated-results.json`](isolated-results.json) records exit codes/elapsed times.
The run establishes path-independent compilation and tests against the supplied
library, not that unpublished 0.3 exists in the registry. Original README/evidence
links requiring the monorepo are audited in the extraction plan and still need
moving or pinned historical URLs during actual migration. Browser/device/Live
acceptance is not established by this filesystem/test isolation check.

## Quality, section by section

| Section | Audio candidate | Application, including consumer-owned test fixture |
|---|---|---|
| Compile | 24 files pass | 5 files pass |
| Contracts | 12/57 verified; 45 skipped (5 missing postcondition, 40 unsupported); 0 refuted/errors; 33 uncontracted exports | 3/6 verified; 3 unsupported skips; 0 refuted/errors; 1 uncontracted generator |
| Interface | 130 signatures; unchanged v2 `288857c0489e83ce9f235a0263ef69b7af4ed55fc9dce1224e85b146eb1aa031` | 11 signatures; unchanged v2 `a777d55738158509c56b5a2df5f191fa7206179e48473ef35989f7962d6c56cd` |
| Effects | Declared `[IO]`, smoke only; processor exports pure | Declared `[FS, IO]`; generator FS 4 / IO 1, planner pure |
| Release | Feature; 0.3.0 changelog section present | Feature; 0.2.0 changelog section present |
| Docs | AGENT.md and ai_summary present | AGENT.md and ai_summary present |
| Style | 89/89 exports pure | 6/7 exports pure |
| Tests/smoke | 145 package checks and smoke pass | 10 native checks and smoke pass |
| Badges/gates | PUB016 / PUB011; no gates | PUB016 / PUB011; no gates |

Audio report: [audio-quality.json](audio-quality.json). The original-tree app run
is retained in [boundary-quality.json](../../../examples/live-loop/evidence/audio-v3-workflow/boundary-quality.json);
the isolated app report agrees on compile/interface/effects/proof/test counts.
The pure package source/ABI is unchanged; new processing features are proposed,
not claimed implemented by these documentation changes. Earlier numeric reference,
inline DSP skip and byte-pin evidence remains linked from the
[level milestone](../audio-levels-0.3.0/README.md).

Proofs use mathematical Real/Int models and do not establish IEEE arithmetic,
model-output meaning/quality, JavaScript correctness or physical audio behavior.
The uncontracted/skipped results remain explicit. Quality/test attestation is
separate from a registry publication or remote migration result.

Text logs have ANSI style escapes stripped. Ephemeral paths in staging/results
identify the tested local export, not a permanent application checkout.
