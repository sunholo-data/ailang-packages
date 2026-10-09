# CREW-CONTENT-LIBRARY sprint

User continuation authorises implementation of the reviewed design in this isolated
checkout. Main baseline3b86383; no changes to ongoing game work. Sequential milestones
with independent evaluation. Estimated1100LOC across2days; prior terminal slice
shipped180LOC + tests in one attended session, budget includes codecs/persistence.

AILANG prompt version loaded: v0.16.6 (runtimev0.52.0/bf2436a); contracts/effects/
package sections loaded in the captain-lab session. Every implementer must load
whole ailang prompt before .ail edits. Compiler/runtime unchanged.

## M1 — Pure library and personality reactions (~450LOC)

- [x] Generic content_library package, strict bounded JSON, explicit seeded sampling.
- [x] Editable app reaction policy uses all five OCEAN fields and received context.
- [x] Native behavioural controls evaluator and strictVM, no fallback.
- [x] Source inline tests executed; contracts verified with honest skips.

Registry reuse: none for content cache/selector (search response/cache); depend on
existing social_dynamics and decisions for actual host decisions. config0.1.2 is
Env-only and doesn't replace JSON policy codec. Stdlib JSON/list/crypto reused.
Showcase library/reactions: contracts include weight/roll bounds, exact key/labels
and normalisation; effects pure; inline tests include seed/sampling/schema edges.

## M2 — Storage and generation (~300LOC), depends M1

- [x] Copy editable config on first run, cache exact signatures atomically.
- [x] At most configured0..8 attempted std/ai calls; default2; actual token metadata.
- [x] Per-key lock, strict errors; journal ownership/append failure handling.
- [x] Fixture-generated miss then zero-call cache hit; malformed/cache/budget controls.

Registry reuse: none for content-specific persistence (search cache/config); std/fs
Result operations and std/ai.step are sufficient. No second provider API binding.
Store showcase contracts: skip for effectful FS/AI outcomes (native integration
controls instead); effects FS/AI @limit=1 per resolve; inline tests pure prompt/schema
helpers where meaningful, skip IO ownership (integration tests execute it).

## M3 — Human menus and installation (~350LOC), depends M1/M2

- [x] Numbered captain flows science/maintenance/rest/advance/check-in/relief/status.
- [x] Automatic crew reaction+dialogue and explicit captain start/leave choice.
- [x] Installed crew-play (selected GLM Flash) and crew-play-offline (no network).
- [x] Complete journal recording extracts/replays unchanged host input trace.
- [x] Existing crew/social validation and mutations remain green.
- [x] Bounded live smoke1 generation followed by same-context cache hit.
- [ ] README/AGENT/CHANGELOG, roadmap update, independent evaluation and PR CI.

Registry reuse: depend on existing crew host and new content_library (path locally).
Play showcase contracts: include pure menu routing and response binding; effects
IO/Env/FS/AI explicit; inline tests pure menu handlers, installed integration for IO.

Remote CI is a separate mandatory landing gate; a local PASS does not claim CI.
No registry publication. Peer disagreements/personality drift/Godot integration
remain subsequent milestones. Do not call live AI in CI or automated test harnesses.

Implementation status (2026-10-09): M1/M2 implemented and native/fixture controls
pass. M3 installed offline scenarios/replay pass. Google key was rejected as API_KEY_INVALID. Mark then selected the existing
OpenRouter key and GLM5.3Flash; bounded smoke passed (one generated bundle, identical
repeat from cache with zero calls). Independent implementation review passed94/100
before the provider switch; updated review and PR CI remain pending.
