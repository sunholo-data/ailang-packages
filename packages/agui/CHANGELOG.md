# Changelog

## 0.2.2

`input.ail` imports `isOk` from `std/result` for the contract of `decodeAll`. `decodeAll` now declares its decoder parameter as a function, `f: (Json) -> Result[b, string]`. It used to be the type variable `f`, which claimed any type at all while the body called it. Rigid signature type variables (sunholo-data/ailang#2304) reject that. The codecs are unchanged.

Earlier AILANG releases never type-checked `requires`/`ensures` clauses, so these mistakes compiled. sunholo-data/ailang#2283 type-checks them. Once it ships, every program that imports this package would fail to compile. The fix also compiles on the current release, v0.60.2.
