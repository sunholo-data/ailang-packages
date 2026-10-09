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
