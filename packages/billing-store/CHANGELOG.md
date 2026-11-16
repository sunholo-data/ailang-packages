# Changelog

## 0.9.5

All six repositories import `length` from `std/string` for their `requires` clauses. Depends on billing_entitlements 0.4.3 and billing_proposals 0.3.3. The storage code is unchanged.

Earlier AILANG releases never type-checked `requires`/`ensures` clauses, so these mistakes compiled. sunholo-data/ailang#2283 type-checks them. Once it ships, every program that imports this package would fail to compile. The fix also compiles on the current release, v0.60.2.

## 0.9.4

Builds again on current AILANG. 0.9.3 was published against `sunholo/firestore` 0.7.2, whose
`client.ail` fails AILANG's strict check (`STRICT_FALLBACK_001`), so all six repositories failed to
compile. This release depends on firestore 0.7.3. The billing code is unchanged.
