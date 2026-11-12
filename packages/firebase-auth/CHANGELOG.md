# Changelog

## 0.1.3

`firebase_jwt.ail` imports `length` from `std/string`. The `requires` clauses of `verifyFirebaseJWT` and `verifyFirebaseJWTFull` called `length` without the import. The verification code is unchanged.

Earlier AILANG releases never type-checked `requires`/`ensures` clauses, so these mistakes compiled. sunholo-data/ailang#2283 type-checks them. Once it ships, every program that imports this package would fail to compile. The fix also compiles on the current release, v0.60.2.
