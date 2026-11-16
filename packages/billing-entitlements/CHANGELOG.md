# Changelog

## 0.4.3

`plan.ail`, `entitlement.ail` and `capability_check.ail` import `length` from `std/string` for their contracts. The tests in `capability_check_test.ail` and `entitlement_test.ail` import the `length` they use. These tests failed to compile on every current release, and they all pass now. The policy code is unchanged.

Earlier AILANG releases never type-checked `requires`/`ensures` clauses, so these mistakes compiled. sunholo-data/ailang#2283 type-checks them. Once it ships, every program that imports this package would fail to compile. The fix also compiles on the current release, v0.60.2.
