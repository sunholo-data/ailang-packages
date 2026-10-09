# sunholo/content_library

Experimental pure content selection, independent of any game or provider. It validates short dialogue bundles and selects labels and wording using explicit weighted draws. It does not generate content, store files, choose actions, or grant authority. Structural validation cannot establish whether generated dialogue is factually supported.

## Quick example

```ailang
import pkg/sunholo/content_library/library (pickLabel, nextRoll)
-- Caller order defines CDF order; intervals include their left edge.
let choice = pickLabel([{label:"accept",weight:1},{label:"defer",weight:3}],0.25)
-- choice = Ok("defer")
let draw = nextRoll(1)
-- draw = Ok({seed:48271,roll:48271.0/2147483647.0})
```

`pickLabel`, `pickVariant`, `nextRoll`, `decodeGenerated`, `decodeBundle`, and `starterBundle` return `Result[T,string]`. `cacheKey` returns the SHA256 hexadecimal hash of the exact caller-defined signature; `encodeBundle` returns JSON. `nextRoll` returns the exported `SeedRoll` record. No hidden random state exists. Park–Miller multiplier 48271 is deterministic, not cryptographic. Commit the proposed seed only when the caller commits the associated action.

## Wire boundary

Generated output must contain exactly:

```json
{"schema":"generated_dialogue/1","variants":[{"id":"yes-1","label":"accept","text":"I can do that.","weight":1}]}
```

Supply 1–4 variants per legal label, at most 16 overall. Every legal label must occur; unknown labels and duplicate variant IDs fail. IDs/labels are nonempty and at most 64 characters, dialogue 1–512 characters without ASCII controls including DEL, and integer weights 1–1000. Rolls must be finite in `[0,1)`; seed 1–2147483646. Signatures are nonempty and at most 32768 characters; complete JSON bodies and encoded bundles at most 65536. Usage is integer 0–1000000000. Both JSON boundaries enforce a single complete object and exact unique required keys.

`decodeGenerated(raw,signature,legal,model,inputTokens,outputTokens)` attaches caller metadata, origin `ai`, and prompt version `crew-dialogue-v1`. Generated JSON cannot supply those fields. Persisted `content_bundle/1` has exactly `schema,key,signature,origin,model,promptVersion,inputTokens,outputTokens,variants`. `decodeBundle(body,signature,legal)` binds the complete signature and its key. Since signatures are opaque, the adapter must also check the AI bundle's model against the expected caller model. Neither decoding nor token metadata proves provider provenance: the persistence/provider boundary belongs to the caller.

`starterBundle(signature,legal)` is explicitly `authored`, model `synthetic:starter-v1`, and zero usage. Its text is generic labelled placeholders; it must never be represented as AI-generated dialogue. `pickVariant` validates the bounded variant set before sampling alternate wording for the selected label. It never selects another response label. Selection follows caller list order with strict CDF boundaries and an endpoint fallback for floating point rounding.

## Verification

```sh
ailang check --package .
ailang test --package .
ailang test --package . --bytecode --strict-bytecode
ailang fmt --check library.ail library_test.ail
ailang pkg quality --strict .
ailang verify --package .
```

Tests cover strict schema, duplicate fields/IDs, finite sampling and exact edges, legal-label completeness, explicit seed stepping, wire/text bounds, controls, token metadata, cache invalidation, and authored origins. Export contracts state observable invariants; Result/record/higher-order and floating-point contracts may be skipped by the current SMT verifier. Native passing controls are not a proof of all executions.

Current v0.52.0 verification: 14 named controls pass on both evaluator and strictVM (zero fallback), four inline controls and seven generated contract properties pass; two Bundle properties lack generators. SMT proves `rollOK`; seven obligations skip on higher-order/JSON/hash builtins, and `nextRoll` hits an encoder error identifying a named record inside Result. That error is a verifier limitation, not a discharged obligation. Strict quality reports no gates but its printed contract summary omits this encoder error. No pure `_smoke.ail` is supplied; the application integration owns boot tests. Registry overlap checking was unavailable under sandbox DNS. Local minimal reproductions are retained for feedback; an attempted shared-inbox report was blocked by automatic approval review.
