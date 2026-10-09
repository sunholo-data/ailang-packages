# Crew journey evidence

M3 candidate uses internal `journey.ail` bin wrappers and the public supported-mode
`play.launchJourney` adapter. No new unit-return inventory contracts were added.

- `full-validate.log`: original full scoped run. Old suites, 125 native crew controls
  in each engine, content-library, saved scenarios, replay/parity, CLI/store/player
  controls passed. It stopped honestly at PUB011 for the initial new bin boundary.
- `final-quality.log`: corrected export boundary, strict crew and terminal quality;
  crew 16/83 verified, 64 skipped (not proved), 0 refuted, 0 uncontracted exports;
  terminal 2/9 verified, 7 skipped, 0 errors, 0 uncontracted exports. No gates.
- `final-installed.log`: final internal bin adapter harness: seven exact navigation
  versus legacy journal payloads, evaluator/strict VM recovery replay, indicator
  deltas, AI-cache/stock provenance, pending error, eight-turn review, actual plain
  and ANSI frame bounds, onboarding limit and publication failure. Zero AI calls.
- `mutations.log`: eight compiled causal/accounting/consent mutants killed.
- Saved `*-journey.txt` and `ansi-80x28.txt`: actual emitted terminal transcripts,
  temporary storage paths replaced with `<TEMP>`. Fixed Unicode-width/native
  controls complement the ASCII stream width checks; byte length is not cell width.

Initial failed and interim logs are retained as evidence, not described as passed.
Effectful entry behavior is established by installed controls, not Z3 unit proofs.
Registry export-overlap lookup was unavailable (DNS); absent `_smoke` is reported
informationally. Live provider generation was not exercised. Independent acceptance
and exact-head CI remain the parent agent's final landing gates.
