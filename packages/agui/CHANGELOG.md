# Changelog

## 0.2.2

`input.ail` imports `isOk` from `std/result` for the contract of `decodeAll`. The codecs are unchanged.

Earlier AILANG releases never type-checked `requires`/`ensures` clauses, so these mistakes compiled. sunholo-data/ailang#2283 type-checks them. Once it ships, every program that imports this package would fail to compile. The fix also compiles on the current release, v0.60.2.
