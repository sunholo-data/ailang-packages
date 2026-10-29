# sunholo/specstore: agent guide

Use it when a task involves tagging or analytics specifications (GA4, Tag Manager, a data layer):
writing one, changing one, checking one against a house standard, recording a QA round, or
producing a spreadsheet for people who work in Sheets or Excel.

- Commands: `specstore template|check|guide|view|audit`; see README.md for arguments.
- Change a spec by editing `spec.yaml`: add a history row, bump `version` (whole number only when
  it goes to the client), set the event's `changed`. Then run `check`.
- Record QA as a new `qa/round-NN.yaml`; never edit an existing round. `by: automated` rounds may
  record failures, never passes.
- Change the standard in its YAML, then regenerate the guide with `guide`. A proposed rule becomes
  decided by changing `status` and saying in `source` where it was decided.
- Library use: `import pkg/sunholo/specstore/check (findings)` returns (rule id, status, message)
  without printing; `pkg/sunholo/specstore/model (toStd, toSpec, toRound, loadSpec)` reads them.
- Proofs: `rules.ail` (versions, rounds, pass-by-person, retest). Tests: `check_test.ail`.
