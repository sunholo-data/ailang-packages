# Changelog

## 0.1.1

The `ensures` clause of `actors` states non-emptiness with `listLength(result) > 0`. `result != []` needs an `Eq` instance on a list of actor records, and there is none. The meaning is unchanged. Not published.

Earlier AILANG releases never type-checked `requires`/`ensures` clauses, so these mistakes compiled. sunholo-data/ailang#2283 type-checks them. Once it ships, every program that imports this package would fail to compile. The fix also compiles on the current release, v0.60.2.

## 0.1.0

- Installable `social-lab` command via `[bin]`; saved JEV/Nouls integration
  comparison and CLI installation/replay checks.

Standalone recorded ship and community social experiments with selectable policies,
custom NDJSON inputs, causal traces, outcome assertions, replay and strict-VM parity.
