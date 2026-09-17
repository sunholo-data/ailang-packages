---
name: ailang-packages
description: Create, modify, validate or publish AILANG packages and package-based demos. Use for package manifests, imports, contracts, native tests, effects and registry releases.
---

# AILANG packages: discover before implementing

1. Run `ailang version` and `ailang docs package-authoring`. Read that guide before
   implementation; it consolidates the package workflow for the installed binary.
2. If the guide is unavailable, read the **complete** `ailang prompt`, including
   design principles, contracts, tests and packages near the end. If an AILANG core
   checkout is available, read its `.agents/skills/ailang-packages/SKILL.md` and the
   referenced resources. Otherwise use `ailang help`, `ailang test --help` and
   `ailang publish --help`; report unavailable tooling instead of guessing syntax.
3. Read the package's `ailang.toml` and `AGENT.md`. Query stdlib with
   `ailang docs std/<module>` / `ailang docs --all-functions <substring>` and package
   usage with `ailang pkg-docs <vendor/name>`. Use local binary/source documentation
   before web research for AILANG. Reproduce historical bug notes on this version.

## Implementation and evidence

Keep pure domain logic separate from effectful adapters. Write meaningful
`requires` / `ensures` for pure functions, native `tests [...]` and `properties [...]`
where applicable, and explicit effect ceilings and `@limit` budgets. Use the
binary guide for supported syntax and verification limits. Do not add vacuous
contracts solely to satisfy an inventory.

From the package root, run `ailang lock`, `ailang check --package .`, and
`ailang test --package .`. Package test discovery targets `*_test.ail`; also run
`ailang test path/to/module.ail` for inline tests in implementation modules. Inspect
counts and skips. Add relevant runtime/integration checks and contract verification;
report compile, test, proof and live-service outcomes separately.

Run `ailang pkg quality .` (`--json` for automation, `--strict` to make warn-level
badges block, `--no-run` to skip executing tests and `_smoke.ail`). It exists from
ailang v0.39.5+dev (2026-09-17); an older binary says `unknown pkg command 'quality'` —
upgrade rather than skip. It is the report the registry validator runs on upload:

| section | what it is | provenance |
|---|---|---|
| compile | `check --package` | server — a gate everywhere |
| contracts | Z3 `verified/total`; `PUB016` = contracts Z3 cannot encode (runtime assertions, not proofs); `PUB006` = a refuted contract, a gate everywhere; `PUB011` = exported functions without a contract | server |
| interface | signature-sensitive identity (v2); mismatch with the validator's = `PUB005` | server |
| effects | `max`, privilege `rank_max`; `PUB010` = no ceiling declared (unlimited) | server |
| release | `[release] kind` + `CHANGELOG.md` `## <version>` section (`PUB001`/`PUB002`, gates from v0.41.0) | server |
| docs / style | AGENT.md, `ai_summary`, pure-export ratio; `PUB021` = no parseable `[metadata] repository` → no inbox agent | server |
| tests / smoke | `*_test.ail` and `_smoke.ail` EXECUTED here; never by the validator | attested |

Report the numbers it prints, not a summary of them ("7/7 verified, 14 uncontracted,
21/21 tests, smoke ✓"). A passing compiler is not completion; a Z3-skipped contract is
not a proof. Exit 2 means `ailang publish` will refuse.

## Delivery

Use `./` for sibling module imports, `pkg/` for external package imports, and export
public types. Path dependencies are for local development; use registry versions
for released consumers. Regenerate local path locks after moving/cloning checkouts.
Read `ailang publish --help` before release. `ailang publish --dry-run` exercises
packaging only; it does not run the remote validator, tests or proofs. Publish
new dependency versions before dependents. Preserve the user's release scope.
