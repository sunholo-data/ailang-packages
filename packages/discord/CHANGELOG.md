# Changelog

## 0.5.1

The `ensures` clauses of `parseChannels` and `parseMessages` count the input list with `listLength`. They used the string `length`. `interactions.ail` imports `isOk` and `length`, and its private `decodeAll` declares the decoder as `f: (Json) -> Result[b, string]`. It used to be a type variable `f` that the body called, which rigid signature type variables (sunholo-data/ailang#2304) reject. The first contract of `decodeInteraction` matches on `result` instead of reading `result.kind` from a `Result`. The old form crashed the generated property test whenever valid JSON decoded to an `Err`. It now checks the same thing on `Ok`. This also commits `interactions.ail` and `interactions_test.ail` to the repository. They shipped in 0.5.0 but were never committed, so the source is restored from the published 0.5.0 package. The client and interaction code are unchanged.

Earlier AILANG releases never type-checked `requires`/`ensures` clauses, so these mistakes compiled. sunholo-data/ailang#2283 type-checks them. Once it ships, every program that imports this package would fail to compile. The fix also compiles on the current release, v0.60.2.
