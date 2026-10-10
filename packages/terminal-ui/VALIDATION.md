# v0.2.0 validation — 2026-10-10

Validated with the official [AILANG v0.54.0 release](https://github.com/sunholo-data/ailang/releases/tag/v0.54.0),
commit `361caeda13830b0a3faa11919cc2b5d37a14dde1`. The downloaded
`darwin.arm64.ailang.tar.gz` matches its entry in release `SHA256SUMS`:
`b67b8931875e8a6dd96bc34a6b912657c25b08905f817d20a15cb484c1d4580e`.
Version output confirms the exact tag and full commit. Loader tracing confirms
stdlib source `embedded`, including std/terminal; no stdlib path, module-relaxation
or development-cache overrides were used.

Package checks, evaluator/strict VM tests, strict quality with registry overlap
checking and smoke were rerun with this official runtime. The crew lock now records
`ailang lock v0.54.0`; all four dependency source/interface identities are unchanged.
Inline source tests and live PTY controls below retain their supporting-development
compiler provenance. An earlier publication request was rejected by validator
v0.53.2 because std/terminal was absent. Registry acceptance and fresh published
consumer validation remain pending; no package version has been accepted yet.

- `ailang lock`, `lock --check`, `check --package .`: all 12 source/test files compile.
- `test --package .`: 39 passed, 0 failed, 0 skipped. This is 37 named controls and
  2 properties, each running 100 generated valid-domain inputs without discards.
- `test --package . --bytecode --strict-bytecode`: same 39/0/0; all 37 named bodies
  run on VM, 0 fallback. Properties run on the evaluator by CLI definition.
- Explicit implementation-module tests, using `--allow-skips` to report missing
  ADT generators and auto-property domain shortages, have 42 passed, 0 failed,
  41 skipped. The 26 `no_generator` skips are vacuous, not verification evidence.
  Named/property controls above cover these API shapes with explicit valid values.
- `_smoke.ail` executes without a terminal and checks codec/replay and the plain
  scope; quality attests it passed. It has no inline tests because its driver is
  effectful; the pure logic has named controls.
- Formatting passes for all new/modified AILANG files. Existing ui source/tests
  were preserved byte-for-byte.

| Development source tests | Passed | Failed | Skipped |
|---|---:|---:|---:|
| ui | 8 | 0 | 10 |
| events | 5 | 0 | 1 |
| widgets | 11 | 0 | 11 |
| transcript | 6 | 0 | 6 |
| adapter | 3 | 0 | 6 |
| demo | 9 | 0 | 7 |

Strict quality (with network registry overlap check): 0 gates. Compile: 12 files.
Contracts: 12/34 verified, 0 refuted, 21 skipped, 1 Z3 encoding error, 0 uncontracted
exports. The error is lineEvent's Option[string] encoding (Some represented as Int
then compared with String); this is a tool error and is not counted as a proof.
Interface: v2, 77 signatures,
`sha256:ifacev2:e6b520bcefb43b7d8275594cad099203a701bb154dd53980ad8bddb6d908aab2`. Effects: declared IO/Env ceiling, rank_max Env.
Release kind feature and nonempty 0.2.0 changelog. AGENT.md/summary/license/repository
present. Pure exports: 30/34 (88%). Tests: 39 passed/0 failed. Smoke: passed.
Only informational PUB016 remains; registry overlap completed without PUB023.

`publish --dry-run` passes with network overlap checking, producing a package
preview without uploading or proving remote-validator compatibility. The
installed `[bin]` integration was separately checked from an unrelated cwd:
Down+Enter selects item 2 immediately; 20×8 resize shows fitting compact text;
80×24 enlargement retains item 2; q restores termios, cursor and alternate screen.
Blank line then q renders twice in line/plain; redirected auto selects plain,
and plain/auto output contains no ESC bytes.

Backend boundary: @limit budget frames are explicitly rejected by the current
strict VM; effectful demo validation uses the evaluator. Core unbudgeted native
API parity is a separate integration check. No fallback conceals this limitation.

Complete consumer regression with the supporting development compiler and
`AILANG_NO_CACHE=1`:

- Crew `validate`: passed, approximately 20m56s. Includes 149/149 crew and 14/14
  content-library tests in evaluator and strict VM, identical replay/parity traces,
  installed CLI/store/play/journey/watch flows and terminal package validation.
  Watch used zero live provider calls and one deterministic AI stub attempt.
- Crew `mutations`: all eight altered programs compiled, then were caught by the
  behavioral assertions; 21m57.09s.
- Existing social lab `validate`: passed, including 117 package tests, installed
  CLI, five replay/parity recordings, strict quality and publication dry-run;
  2m42.59s. Its optional overlap probe reported sandbox DNS unavailable.

Combined no-cache time is approximately 45m36s. CI preserves every gate and allows
60 minutes rather than the former 25. The scoped official-runtime checks above
pass; complete released-runtime consumer CI remains required. Logs
are `/private/tmp/terminal-crew-row-repair.log`,
`/private/tmp/terminal-crew-mutations-row-repair.log` and
`/private/tmp/terminal-social-row-repair.log`. These local paths are session evidence;
the final CI run provides complete released-runtime consumer evidence. Official
archive/checksum/version, test, quality and embedded-stdlib trace logs are under
`/private/tmp/terminal-v54-official`; the release link above is the persistent
archive provenance.

Compiler/test tooling issues encountered and accounted for: inline test-table
values containing imported Some/None fail harness lookup, so those assertions use
native named tests with imports; the formatter cannot format test bodies with let
sequences, so the same controls are factored into pure helper functions. Contracts
were retained. Missing generators/skipped Z3 fragments are reported explicitly.
