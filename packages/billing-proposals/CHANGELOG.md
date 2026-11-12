# Changelog

## 0.3.3

`proposal.ail` and `proposal_summary.ail` import `length` from `std/string` for their contracts. Depends on billing_entitlements 0.4.3. The proposal logic is unchanged.

Earlier AILANG releases never type-checked `requires`/`ensures` clauses, so these mistakes compiled. sunholo-data/ailang#2283 type-checks them. Once it ships, every program that imports this package would fail to compile. The fix also compiles on the current release, v0.60.2.

`summarizeProposal`'s contracts moved onto a new private `buildSummary` helper whose parameters are all primitive types. The property-test framework has no generator for types imported from dependencies (`Plan`, or the catalog `list[{key: string, plan: Plan}]`), so the contract-derived properties on `summarizeProposal` never ran and failed the `ailang test` gate with "no generator". The public API is unchanged; the same properties now execute 100 cases each on `buildSummary`.
