# Sprint CREW-TUI: standalone captain game

Source: standalone-captain-game.md. User has directly requested implementation;
standing merge/install authorization applies to packages/main. Sequential execution
in /private/tmp/stapledon-crew-tui-20261009; preserve all active game/package worktrees.

AILANG prompt version loaded: v0.16.6, whole prompt read; runtime v0.52.0 bf2436a.
Recent crew content work delivered approximately 1000 implementation lines in one
session; this smaller interface slice estimates 350 implementation + 150 test lines.
Estimate one working session, with scoped local checks, independent review and CI.

| Milestone | Files/example | Acceptance | Reuse |
|---|---|---|---|
| M1 recovery | play.ail, play_flow.ail, test-play.sh recovery transcript | Published rejection continues; unchanged seed/domain; partial work retained; FS failure fatal | contribute existing sunholo/crew_lab; depend unchanged social_dynamics |
| M2 player interface | pure presenter module if useful, play/menu integration, README example flow | Intro, ASCII panels, real costs/progress, help, consequence text, quit recap | contribute existing sunholo/crew_lab; std/string/list; no new framework |

Registry gate: installed `ailang search terminal` and `ailang search crew` on
2026-10-09 returned no packages. Existing local crew_lab is the target; no separate
TUI library required. No content-library or kernel changes planned.

Showcase syntax checklist:
- contracts: include meaningful pure budget/progress/preservation invariants where
  applicable; skip proof claims for rendered text or effectful session loops.
- effects: include explicit existing play !{IO,FS,Env,AI}; presenter !{}; ceilings
  unchanged. Help is pure and not journalled; existing bounded command limits stay.
- inline tests: include pure helper controls when meaningful; source test invocation
  required for any inline tests. Named/integration recovery tests are the main proof
  of player behavior; avoid tests merely mirroring decorative layout.

Execution: red recovery test, implement M1 and targeted checks; implement M2 with
real transcript inspection; full scoped make validate and mutation tests; independent
sprint-evaluator review and fixes; PR to main and CI; merge/install durable checkout.
No Godot build is needed because no game/native/rendering code changes.

Required executor handoff uses an existing agent. Independent evaluator must be
a different agent. Track progress in .ailang/state/sprints and a committed evidence
copy. Report native totals, source skips, solver totals/skips/encoder failures and
quality gates honestly; compile or contract presence alone is not a passing review.

M1 recovery completed: published rejected starts return to bridge; seed and domain
are preserved, while blocked advances retain earlier boundaries. The installed
shortage/occupancy/refusal harness and recovery replay pass; journal failures stay
fatal. Native checkpoint:97/97 evaluator and strict VM, zero fallback/skips.

M2 interface completed. Pure presenter supplies the bridge briefing, authority and
seed guidance, compact panels, configured costs, actual tick progress, directed
trust, source labels, factual action deltas and exit recap. Help and latest action
messages remain after the dashboard beside the next menu. No provider calls,
kernel/recipes/content-library/banked schema/model changes were made.

Acceptance evidence:
- [x] Briefing and conditional first experiment: newcomer-transcript.txt.
- [x] Immediate science reservation shortage and later depletion remain playable;
  rejection does not charge resources or RNG: shortage-transcript.txt + test-play.sh.
- [x] Consent/occupancy rejection and blocked partial boundaries recover safely:
  installed fixtures and native recovery controls.
- [x] Publication failure stays fatal with prior journal/Session/seed intact.
- [x] Help/navigation preserve host journal payloads, sequence, seed and call budget;
  guide remains beside the current numbered choices.
- [x] Final CI validate passes:109/109 named controls on both engines, zero fallback
  or skips;8/8 compile-success mutants killed; original social regression passes.
- [x] Actual newcomer transcript inspected by executor and root.
- [x] Independent sprint-evaluator:100/100; final-source CI37958354490 green;
  PR112 merged to packages main (93f4884).

Quality evidence:11/70 contracts proved,58 skipped and1 encoder limitation,
0 counterexamples/uncontracted exports;22 files compile;96 interface signatures;
AI/Env/FS/IO ceiling unchanged;63/69 exports pure;9 native-test files,109 passing;
no isolated _smoke.ail (installed CLI controls boot the repository graph); no gates.
Source checks: scenario7 passed; session3 passed/9 skipped; reactions3/4;
play_flow5/6; presenter7/8 (seven missing structured generators and one unsatisfied
requires input). Content-library source11/2; native14/14 on both engines.
Skips and encoder limits are not proofs. Registry export-overlap was unavailable
because DNS lookup failed; no publication or live-provider claim is made.

Execution used AILANG prompt v0.16.6 whole, runtime v0.52.0 bf2436a. Two sequential
milestones completed in the isolated checkout. Formatter nested interpolations
needed extracted local expressions; known upstream defects were not treated as
passing checks. New code remains under the package file-size bounds. Final scoped
harness/format evidence includes the last help-placement adjustment.

Final correction: cached authored bundles are labelled saved stock narration,
while saved/new AI quotations remain exact. Fetch provenance and selection metadata
are unchanged. Native totals are now109 app controls on each engine;14 library
controls remain unchanged. Final CI runs the complete scoped gates on ecdebb1.

Actual change:236 implementation additions/46 removals;231 test/harness additions/6
removals;30 recording lines. Completed in one attended working session. Provider
calls:0. Independent report is tui-evidence/evaluation.json.
