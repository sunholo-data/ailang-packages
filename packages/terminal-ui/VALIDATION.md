# v0.2.0 validation — 2026-10-10

Validated against the terminal sprint's development binary and stdlib, reported
v0.53.1 (base version); these results do not claim the >=0.54.0 runtime floor has
been released. The proposed floor remains in the manifest. Publication waits for
a supporting core release and registry validator. No registry upload was performed.

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

| Source tests | Passed | Failed | Skipped |
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
Interface: v2, 77 signatures. Effects: declared IO/Env ceiling, rank_max Env.
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

Compiler/test tooling issues encountered and accounted for: inline test-table
values containing imported Some/None fail harness lookup, so those assertions use
native named tests with imports; the formatter cannot format test bodies with let
sequences, so the same controls are factored into pure helper functions. Contracts
were retained. Missing generators/skipped Z3 fragments are reported explicitly.
