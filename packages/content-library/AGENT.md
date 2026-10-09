# Content library agent guide

Package: sunholo/content_library 0.1.0 (experimental), module `sunholo/content_library/library`. Public API is pure. Read README.md for exact wire fields, bounds, and provenance boundary.

Use Result-returning selection/decoder APIs at input boundaries. The caller owns signatures, expected-model validation, seed publication, persistence, provider calls and all action authority. Do not add game state, AI, FS, IO or random effects here. Do not loosen unique keys, legal label completeness, ASCII control checks or single-object framing. Caller label/variant order is deliberate and stable.

`pickLabel(xs,roll)` returns a label; `pickVariant(bundle,label,roll)` returns a Variant; `nextRoll(seed)` returns SeedRoll. `decodeGenerated` attaches caller model/usage and AI origin. `decodeBundle` validates stored signature+key; expected model is separately checked by adapter. `starterBundle` returns labelled authored placeholder text. None of these establishes semantic accuracy or trusted provider provenance.

Run package check, native controls on evaluator and strictVM without fallback, format, strict package quality and verifier. Record skipped proof obligations honestly. See the game repository's CLAUDE.md and AILANG package skill for authoring rules. No publication is implied by developing this experimental package.
