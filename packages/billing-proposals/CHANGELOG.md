# Changelog

## 0.3.3

`proposal.ail` and `proposal_summary.ail` import `length` from `std/string` for their contracts. Depends on billing_entitlements 0.4.3. The proposal logic is unchanged.

Earlier AILANG releases never type-checked `requires`/`ensures` clauses, so these mistakes compiled. sunholo-data/ailang#2283 type-checks them. Once it ships, every program that imports this package would fail to compile. The fix also compiles on the current release, v0.60.2.
