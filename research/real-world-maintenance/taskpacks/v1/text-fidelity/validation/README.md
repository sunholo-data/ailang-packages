# Actual F2 qualification evidence

Run on AILANG v0.54.18 commit cd33d050b2276633c82624453309ebf7fcea9e2f,
teaching prompt v0.16.7. Native source/runtime/fixture/oracle digests are in
qualification.json. Re-run with a new output path; current receipts are attested
results, not trusted model telemetry or a protected holdout result.

- Native AILANG: starter 3/3 tests, reference 6/6 tests; both packages' five files
  compile, examples execute, and smoke passes. The qualifier compiles each copied
  source independently and executes with --verify-contracts.
- Python: starter 2/2 unit tests, reference 2/2 unit tests. Host oracle 4/4 tests.
- Independent cross-language qualification: all 22 variant verdict sets match the
  frozen matrix. Baseline + S1/S2/S3 references pass 98 assertions. No-op/semantic
  mutants produce exactly 144 named deliberate assertion failures. All intended
  failures occur after successful compilation and zero process exit. Weakening
  the oracle into unconditional acceptance is independently rejected.
- `red-native.txt` preserves the six failing native tests before implementation;
  the deliberately empty/identity source is red-stub.ail.txt. Initial flag/module
  setup errors were corrected before recording this actual semantic red state.
- SMT: starter logicalIdentity verified 1/2, render skipped (structured JSON/Result
  encoding); reference asciiEdge verified 1/3, trimAscii/render skipped (recursive
  helper/structured JSON encoding). No counterexamples or verification errors.
  Main transport is uncontracted: 1 export in each standalone task package.
  The trim-length and output-verdict contracts are runtime assertions, not proofs.
- Regular pkg quality: compile, tests, smoke, effects, interface, release and docs
  pass, no gates. Strict quality fails PUB011 only (one uncontracted main per
  standalone package); it is not reported as strict pass. Registry export-overlap
  lookup is unavailable in this sandbox (PUB023 info), not silently passed.
  These task assets are not registry release candidates and do not change the
  maintenance_bench package's existing 75-uncontracted-export ceiling.

`qualification-initial.json` and `qualification-retained-cases.json` preserve
intermediate development passes before mechanical retention replay and final
contract/metadata updates. Their hashes/counts are their own, not the current
source's identity. Only qualification.json binds the final source. No numerical
language comparison, population inference or model campaign took place.
