# Growing dialogue library and guided captain sessions

| Game pillar | Score | Alignment |
|---|---:|---|
| Choices Are Final | +1 | Append-only run journal; new seed is a new experiment |
| The Game Doesn't Judge | +1 | Separate consequences, no overall moral score |
| Time Has Emotional Weight | +1 | Explicit ship ticks, never provider wall time |
| The Ship Is Home | +1 | Captain chooses projects; autonomous crew speak |
| Grounded Strangeness | 0 | Human lab; no alien OCEAN assumptions |
| We Are Not Built For This | +1 | Strain, refusal and personality influence choices |

**Status:** Planned; attended user authorisation2026-10-09.
**Target:** Experimental content_library0.1.0 + crew_lab0.1.0. **Priority:** P0.
**Estimate:** 2days/~1100LOC. **Depends on:** packages/main3b86383,
social_dynamics0.1.0 and decisions0.4.0.
**Implements:** shared-social-dynamics-and-events and crew-psychology in the
stapledons-design design/human-life-bridge-first-level branch.
**Quorum triggers:** 3 (cache/journal schema), 4 (live model availability).

## Problem and user direction

crew-view requires manual crew replies and request IDs. Mark approved numbered
captain choices, automatic responses shaped by OCEAN, and a content library that
AI expands on a miss then reuses probabilistically. Library grows across runs;
relationships, promises and discovered facts belong to one run. Mark chose the
existing laptop AI setup. After Google rejected its configured key, Mark selected
OpenRouter with GLM5.3Flash (z-ai/glm-5.3-flash).

## Design

M1 creates pure reusable sunholo/content_library: explicit weighted sampling,
seed-step, typed bounded dialogue bundles, strict JSON codecs and SHA256 keys.
Stable list order; exact required unique object keys; seed1..2147483646; signature<=32768chars,
bundle<=65536chars, variants<=16 and1..4 per legal label, IDs<=64chars, text1..512
chars without ASCII controls, label weights1..1000, token counts0..1000000000; duplicate variant IDs,
missing/extra labels, noninteger/nonpositive weights, nonfinite/out-of-range rolls,
oversized/control-bearing dialogue and unsupported versions are errors. Package
has no game authority or persistence. Caller defines the situation signature.

M2 adds app-owned editable response-policy JSON and numbered menus. Signed bounded
coefficients multiply attributes (all five OCEAN dimensions), values, fatigue and
directed captain trust. Recipe/phase choose applicable rules. At most32 rules/16 influences per rule;
coefficients -100..100, base0..1000, context values0..100. Missing required
perception fields are errors rather than guessed zero values. Resulting weights
clamp to1..1000 and normalise. These are authored experimental policy weights, not
calibrated Jev probabilities. Read ONLY the existing Request.context perception,
received evidence and legal labels; no undisclosed colleague/global state. Tests
must demonstrate each trait, fatigue, values and trust affects some weights.
An explicit seeded draw selects the response; another selects its text variant.

Existing host receives synthetic:library-v1 one-hot fixture of the selected legal
label. Fixture confidence1 denotes an authored policy decision, never model
calibration. Existing consent, captain authority, binding, revision, receipts and
work rules remain authoritative. No host, kernel or scenario changes.

Menu: science, maintenance, scientist/engineer rest; advance one tick; check in
with working crew; review an offered task; resolve pending relief; status; quit.
IDs generated internally. After reply the captain explicitly chooses start/leave
Offered. No automatic enforced orders following refusal. Check-ins can request
relief, separately granted/denied by captain. Concern has no invented negotiation
mechanic. Start policy chosen through numbered consent/orders options; integer
seed is explicit. GUI inputs bounded10000 lines/65536chars, EOF exits.

M3 adds FS storage and AI text generation, outside the pure reusable package.
Installed crew-play uses GLM5.3Flash through OpenRouter (z-ai/glm-5.3-flash),
with the existing OPENROUTER_API_KEY. crew-play-offline
binds stub but never calls it. No new secrets, provider routing or core edits.
Local home defaults ~/.ailang/crew-lab; --home overrides for tests/separate libraries.
First use copies default JSON config under a per-config directory lock, rechecking
existence after acquisition; existing config never silently overwritten.
Calls per session bounded0..8, default2. Every attempted AI call consumes a slot,
even on transport/malformed response; no automatic retries/provider fallback.

AI produces1..4 short variants for EVERY currently legal label using std/ai.step
Result and actual token usage. It cannot set response probabilities, state effects,
actor identity, cache key or provenance. Prompt restricts dialogue to present
feelings/requests supported by perception, forbids invented events/promises/other
people's thoughts. Strict structural validation does not prove narrative accuracy;
semantic content QA remains a documented limitation. Invalid output is not cached. A cached bundle retains the original generation
usage, but Fetch for a hit has calls0/current tokens0; these must be displayed
and recorded separately to avoid charging historical tokens again.

Version1 signature contains EXACT Request.context, legal labels, policy snapshot,
model and prompt version, omitting only external request ID/tick/revision. Context
already contains task/evidence identities, deliberately retained: similar later
occurrences may miss. No fuzzy matching/bands yet. Changed fatigue/personality,
known history, model or policy must miss. Key hashes full signature; each stored
bundle includes signature too and both must match. This conservative boundary
favours correctness over hit rate. Later broadening is a separate experiment.

Cache has one bounded JSON file per key, validated before temp-file atomic rename.
Per-key mkdirResult lock prevents concurrent generation; busy is a visible error,
no implicit wait/retry. Recheck for a valid cache entry AFTER acquiring the lock,
before any generation; a raced-in valid entry is a hit. Never overwrite valid bundle. Abandoned lock maintenance
is explicit. Offline misses use labelled authored starter variants without storing
as AI. Live cache/generation errors leave request pending and present retry or
explicit authored continuation; no silent replacement of unavailable AI.

Run journal records seed/config snapshot, host inputs/outputs, full weights,
response/text rolls, selected variant, complete bundle and source/usage. Run
ownership acquired by an exclusive directory; PID+seed names do not overwrite
previous run. Each action stages the pure host output and proposed seed, then
atomically publishes the complete input/output/selection record BEFORE accepting
or displaying the new Session/seed. Failure leaves prior Session/seed unchanged
and stops play. This includes blocked-advance outputs with retained prior boundaries.
The journal uses bounded whole-file replacement (8MiB maximum), writing a temporary
file in the owned run directory then renameFileResult; prior valid records survive
a failed/partial temporary write. No fsync/power-loss durability claim is made.
Failed generation attempts consume call budget and are journaled before retry.
No journal tail repair or resume is silently attempted. Failed host operations
remain visible and successfully committed earlier boundaries retained. Replay
extracts the recorded host NDJSON including selected reply, independent of cache/AI.

## Shared interfaces

Package library.ail exports WeightedLabel{label,weight}; Variant{id,label,text,weight};
Bundle{key,signature,origin,model,promptVersion,inputTokens,outputTokens,variants};
pickLabel(xs,roll), pickVariant(bundle,label,roll), nextRoll(seed)->{seed,roll},
cacheKey(signature), decodeBundle(body,signature,legal), encodeBundle(bundle),
decodeGenerated(raw,signature,legal,model,inputTokens,outputTokens), starterBundle.
Origin is ai or authored; metadata comes from adapter, never generated fields.

reactions.ail exports Policy, decodePolicy(body), defaultPolicyBody(),
weights(policy,request), signature(request,policyBody,model),
fixtureBody(request,label), prompt(signature,legal). Default model constant
specified by caller. Config callLimit separate from decision weighting.

store.ail exports loadPolicy(home), resolve(home,signature,legal,model,mode,remaining)
->Fetch{outcome,source,calls,inputTokens,outputTokens,usageKnown}, openRun,
appendRun. Caller tracks remaining attempts. Unknown failed-call usage is not
labelled zero spend. Effects FS for policy/journal; FS,AI for resolve, @limit=1
AI per resolution. play.ail owns IO/Env and invokes the same pure host.

## Verification log, reuse and conflict surface

Read Request/perception, immutable retry/stale guards, scenario OCEAN and fixed
recipes. std/ai.step docs/source show Result/token usage and per-call same-provider
models. std/fs docs show Result IO, mkdirResult and renameFileResult. std/crypto
sha256Hex is pure/documented. Installed manifest source supports [bin].run_flags.
Compile/native probes discharge these premises before landing.
OpenRouter model page https://openrouter.ai/z-ai/glm-5.3-flash confirms the selected
model ID. Attended smoke passed: one generated bundle (1058input/2692output tokens),
then identical context reused the full selection and seed from cache with zero calls.
OPENROUTER_API_KEY presence verified, value not printed. Google key was rejected
as API_KEY_INVALID; the user explicitly selected OpenRouter instead. No scientific
calibration claim.

Registry searches response/cache: no content selector/cache package; http_helpers
is HTTP plumbing. config0.1.2 docs: environment loading, not JSON content policies.
Reuse existing decisions decoder/gate and std/ai for free text. New pure module is
required. Existing host and five recordings unchanged, existing social lab unchanged.

Related-doc search returned high-ranked terminal controls/crew-decisions docs;
read them: manual saved replies, no persistent generated dialogue. Existing
v0.4.0 decisions use-case-map expressly excludes free text. This feature is distinct.

## Acceptance

| Criterion | Verification |
|---|---|
| Schema, weight edges, variant legal labels, context invalidation | native tests, evaluator+strictVM |
| Every OCEAN dimension/strain/value/trust affects weights | reactions native controls, both engines |
| Captain-only menus reach science/rest/relief outcomes | installed scripted offline sessions |
| First miss generates once, identical repeat never calls AI | fixture AI followed by empty-fixture replay |
| Corrupt cache/output, busy lock, budget and journal failures visible | integration harness |
| Exact host recording replay independent of cache/provider | journal NDJSON extraction + parity |
| Existing mechanics unchanged | crew/social validate + mutations |
| Formatting, budgets, quality, proof limits | fmt/strict quality/verify report |
| Selected GLM Flash available, second request cached | attended maximum2-call live smoke |
| Independent evaluation and CI green | evaluator report + PR checks before merge |

## Axiom compliance

| Axiom | Score | Reason |
|---|---:|---|
| A1 Determinism | +1 | Explicit seed, pure weights and banked live data |
| A2 Replay | +1 | Full recorded selection and inputs |
| A3 Effects | +1 | Pure core, FS/AI/IO/Env adapters |
| A4 Authority | +1 | Unchanged host validates all operations |
| A5 Bounded verification | +1 | Calls/files/text/inputs bounded |
| A6 Safe concurrency | +1 | Visible exclusive cache/run locks |
| A7 Machines first | +1 | Typed package and journal remain accessible |
| A8 Syntax | 0 | Existing language only |
| A9 Cost | +1 | Attempts and known/unknown usage separated |
| A10 Composability | +1 | Generic library, app-owned policy |
| A11 Failure | +1 | No silent substitution/regeneration |
| A12 Boundary | +1 | Generated text cannot mutate state |

Net+11; no hard violations. Numerical coefficients and policy are tuning fixtures,
not game canon. Personality drift, peer disagreement spreading, broad cache
matching, alien content and Godot presentation remain subsequent experiments.
No registry publication or modifications to active user/game branches.
