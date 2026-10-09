# Social dynamics 0.1.0 validation

Validated 2026-10-09 on AILANG0.52.0/bf2436a, macOS arm64. New package and
standalone example only; existing game, physics packages and active checkouts untouched.
Implementation branch `sprint/social-dynamics-0.1`, base packages2b3c9b2.

| Evidence | Result |
|---|---|
| Library package check |16 files compile;8 public modules, public exports pure|
| Native library tests |110 passed,0 failed,0 skipped|
| Same native library tests strict bytecode |110 passed,0 failed,0 skipped; no fallback|
| Separate consumer/example native tests |8 passed,0 failed,0 skipped|
| Model source inline/native contract properties |10 passed,0 failed,2 skipped (no State/Config generators)|
| Config source inline/contract properties |5 passed,0 failed,0 skipped|
| Private smoke inline test/contract property |2 passed,0 failed,0 skipped; smoke executable OK|
| Five named scenarios |All outcome/resource/repeated-delivery controls pass|
| Interpreter stdin versus strictVM pure recording |Five complete traces byte-identical|
| Replay |Five recordings repeated identically without AI/Net|
| Compile-success behavioural mutations |8 killed by existing assertions,0 survivors,0 inconclusive|
| Package quality strict |No blocking gates;38 exported functions,38 pure,0 uncontracted|
| SMT verification |5/40 verified,32 skipped,3 verifier errors,0 counterexamples|
| Packaging |Dry run creates31611-byte tarball; nothing uploaded|

Source contracts are meaningful runtime assertions. Skipped Z3 contracts involve
lists/Result/Option/HOF builtins. Three verifier errors are missing ADT constructor
constants in Result contracts (add,multiply,abortAdvance), not proofs or refutations.
Native cases and properties run independently. Source generator skips concern State
and Config records; named adversarial tests exercise those paths. Strict quality
inventory says verified5/40 and notes32 skipped; full verify JSON discloses3 errors.
The sandbox quality run could not fetch registry overlap index (PUB023 information);
a subsequent read-only network-enabled quality run is recorded separately.

`std/io.readLine` is evaluator-only on this pin. The strict VM runs the identical
pure `session.recording` function through structured entry arguments with zero
capabilities; it is compared against the actual interpreter stdin trace. No
fallback or false assertion that VM supports stdin. Main's IO operation count is
variable; shell limits recording count/line size. Helpers and public core are pure.

First timed fresh-process collaboration run:0.23s real; repeated process:0.24s;
strictVM pure recording plus shell framing:0.21s. Filesystem was already warm from
validation; these are process startup/run measurements, not cold disk or live AI
latency claims. All three traces compare identical.

Independent preflight found and drove fixes for swapped observation fields, unsafe
public mutation helpers, early recovery, missing outcome evidence, source spoofing,
pending retry inconsistency and a final pending-effects helper loophole and lost partial blocked progress. Full config snapshots
prevent same-ID recipe/cap changes. Outcomes create finite immutable evidence with
reserved IDs and no automatic knowledge; recipients must receive them explicitly.
Successful partition/continuation invariance is checked with full state/event
encodings; blocked runs retain the last committed idle/boundary tick by design.

Mutation harness is Python **test harness only**, never simulation logic or a
production pipeline. It copies the package, compiles each single mutant, runs native
assertions, and verifies original source hashes unchanged. See evidence/mutations.json
and evidence/mutation-harness.py; set AILANG to the pinned binary to rerun.

AILANG feedback reports (shared cloud human-triage inbox):
`inbox_1791544165207_b830a11e`, `inbox_1791544554787_30a168d3`.
Reported permissive JSON trailing data, record-updated callback arithmetic, valid
named-test formatter failure, private local helper import/export behaviour,
cross-module derived record equality, VM readLine, and Result/ADT SMT error.
Curried comparator/fold arity mistakes were source errors and corrected, not
reported as AILANG defects. Formatter failure remains documented; valid tests
are handformatted and retained.

This is experimental, unpublished local work. Full civilisation/life generation,
live model generation, long-term retention/save migration and game UI adapters
remain outside this sprint; example policies don't decide final game mechanics.

Final pending-effects correction was test-first: the new indicator regression failed before its guard (21/22), then passed. The current aggregate and strict-VM suites each pass110/110; updated mutation baseline71/71 and all8 killers pass. The registry-aware quality log predates this private guard change but verifies the same unchanged module export set/interface; latest local strict-quality attestation is110/110. Full `verify` exits1 for the three explicitly recorded verifier errors, while the complete `validate` target exits0.

Independent final evaluation PASS100/100 against18e8ba1;11 separate adversarial consumer probes pass, no remaining blockers. Report: [independent evaluation](evidence/independent-evaluation.json). Follow-up delivery changes are documentation/archival only.
