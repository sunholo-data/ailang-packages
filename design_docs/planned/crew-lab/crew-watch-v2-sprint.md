# S-CREW-WATCH-V2 — five specialists and understandable command choices

**Status:** In progress: M1–M3 committed; M4 final checks, evaluation and landing underway.
Both independent reviewers PASS revision1, controller PASS;
implementation already requested by
Mark, resource semantics approved in attended reply2026-10-10. Main landing and local
CLI installation authorization persist. AILANG prompt version loaded: v0.16.6 (whole
prompt loaded earlier in this session; installed version rechecked2026-10-10).

## Goal, isolation and reuse

Execute [design](crew-watch-v2.md), then independently judge actual newcomer screens
and causal gameplay. Work only in the owned clone /private/tmp/crew-watch-v2-20261010,
branch sprint/crew-watch-v2, base923a47b. Do not change any active game/package/design
checkout or existing response files. Root coordinates review/docs/landing; a distinct
sprint-executor implements all source sequentially; generator and judge differ.
No automatic coordinator dispatch or mission-loop schedule change.

Successful registry searches social, terminal, content and decisions recorded in
the design. Reuse in-repo experimental social_dynamics, content_library and terminal_ui
via existing path dependencies, registered decisions0.4.0 pinned. New work is app
scenario/presentation, not a competing generic TUI package. No publication in this slice.

Prior attended UI sprint changed803 AILANG lines with125 app native controls perengine
and took one attended day. This slice adds resource/identity/cache semantics, so estimate
2,000 changed lines across3 development days with buffer (not a user delivery promise).

## M1 — context before the first policy choice (~250 lines)

Files: examples/crew-lab/play.ail, journey_presenter.ail, journey_flow.ail and their
native *_test.ail modules. Create a pure initial-screen helper so real minimum-size
frames are directly testable. Keep explanations in visible chrome; add h/help before
start, an example and clear return. Display captain, preparation context, first action
flow, exact meanings and scope of both command styles. No initial seed questionnaire.

- [x] Actual first frame at80x24 and40x16 conveys captain/context/actions/style semantics.
- [x] h/help/n/v do not create host state, journal, RNG change or AI use.
- [x] Existing plain/ANSI/input-bound behavior retained; key+Enter instructions concise.

M1 committed b694236 (2026-10-10); integrated installed evidence is captured again in M4.

## M2 — isolated five-specialist scenario (~650 lines)

Files: packages/social-dynamics/model.ail, indicators.ail, relationships.ail,
wire.ail and native controls for an explicit BoundedIndicatorDelta effect (existing
strict deltas preserved, version0.2.0 breaking, known consumers/locks updated);
new examples/crew-lab/watch_scenario.ail + watch_test.ail, session.ail,
play_flow.ail, scenario.ail only if safely exporting reusable helpers, ailang.toml
export list and installed watch harness.
Keep old scenario funcs/start/policy/recording byte-identical. Add explicit known variant;
recompute authoritative config and recipe ownership for exact variant. Main work/rest
menus route five actors through shared offer/response/start/scheduler/relief.

- [x] Six actors (captain plusfive), actual five work/rest recipes, three named stocks.
- [x] Strict profile/config identity tests and consent cannot be bypassed.
- [x] Completion returns compute, spends physical stock once; stops refund reservations.
- [x] Per-specialist condition rules have real sustained/recovery behavior, not just text.
- [x] Bounded modern effects complete repeated work/rest at limits, release reservations,
retain numeric overflow/invalid state/ownership guards; legacy strict deltas unchanged.
- [x] All legacy scenario/play/recording controls still pass without updating expected rules.

M2 committed 4cae2e3 (2026-10-10); M4 reruns the full integrated regression gate.

## M3 — descriptive state and context-aware response library (~800 lines)

Files: journey_presenter.ail, journey_flow.ail, play.ail, reactions.ail, store.ail,
new narrative.ail/helper if useful, native controls and saved AI fixtures. All actual
normal surfaces audited: Bridge/Crew/Work/Log/Guide/waiting/dialogue/rejections/recap.
Debug is explicit --debug startup option; views without it cannot expose raw metrics.
Modern authored response policy separate filename; v2 signature domain separates all
config/prompt/context/model/policy details; v1 unchanged. Generate from actor-local
state, legal labels and project description. Check disclosure patterns before cache
publication and again on cache reads. No AI authority/effects or new peer knowledge.

- [x] Normal five-person narrative views reveal no trait names or numeric psychology.
- [x] Debug displays real OCEAN/state/trust and selection evidence when requested.
- [x] Authored reactions demonstrably respond to stress/morale and all OCEAN axes.
- [x] New signature/policy cannot consume or alter old caches/files.
- [x] Known score/hidden-mechanics disclosure patterns rejected; physical quantities allowed.
- [x] Invalid output stays pending, budgets count actual calls, zero providers in offline tests.
- [x] Cache words are exact selected/journalled words; stock is context-aware narrator text.

M3 committed c3e90ca (2026-10-10); final M4 controls regenerate actual player evidence.

## M4 — real gameplay evidence, docs and independent acceptance (~300 lines)

Files: new test-watch.sh, README.md, AGENT.md, CHANGELOG.md, Makefile; extend existing
test-journey.sh with explicit legacy-profile path to preserve comparable controls while
new default coversmodernwatch; scoped CI pathworkflow asneeded.

- [ ] make -f examples/crew-lab/Makefile watch-test runs installed onboarding/gameplay,
all views/debug/refusal/shortage/completion/help, temporary homes and no provider calls.
- [ ] Journal extraction/recovery replay matches bothengines; legacy controls unchanged.
- [ ] Scoped validate plus110social kernel native controls both engines; strict quality
inventory recorded with solver skips/errors separately from native tests.
- [ ] README has start command and two complete input flows with expected consequences.
- [ ] Independent evaluator reads actual first frames/gameplay, no unresolved blockers.
- [ ] Main merge only after CI passes; durable local CLI shims updated from mergedsource,
existing user policy/cache unchanged and active checkouts preserved.

## Syntax/contract/effect/source-test checklist

| Module | Contracts | Effects | Inline/native source tests |
|---|---|---|---|
| generic bounded effect helper | include configured-bound result range with checked arithmetic/reference guards | include !{} | include boundary/invalid/overflow/ownership plus old strict delta controls |
| watch_scenario | include exact bounds/ownership/config identity on pure catalog helpers | include !{} | include native config/resource/ownership boundary cases |
| narrative helper/presenter | include dimensions/debug visibility and bounded descriptions | include !{} | include descriptions at low/mid/high and normal/debug frames |
| journey_flow | include nav preserving PlayState and option bounds | include !{} | include --debug parsing and immutable navigation |
| reactions | include legal/bounded weights, nonempty versionedsignature and textguard | include !{} | include OCEAN/stress/morale direction, v1/v2 identity and disallowed prose |
| store | include actual call counts0..1, reject/cache semantics | include FS,AI@limit1 | source tests include pureguard integration; effectful fixture harness supplements |
| play/journey wrapper | skip: unit-return adapter has no useful result assertion | include IO,Env,FS,AI | skip inline effect execution: installed hermetic fixture controls provide behavior |

## Execution and completion

Failing controls first for each milestone; implementation sequential as all milestones
share adapter files. Do not pause for repeated approval for routine authorized changes.
If compiler DX fails, shrink/recheck and report actual bug via project feedback skill.
Independent review gate and evaluator must be explicit about unavailable proof/calls.
Acceptance remains implementation quality, not proof of compelling player stories.

Registry decisions per milestone: M1 depend terminal_ui/crew_lab; M2 depend social_dynamics;
M3 depend content_library/decisions; M4 depend crew_lab existing controls. Preserve
registry version pins. No new package capability is needed; generic model already
supports variable actors, recipes, indicators and reserve/consume separation.
