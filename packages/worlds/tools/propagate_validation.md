# Prediction at arrival: validation, 2026-11-12

AILANG v0.56.1 (`05c860a`), teaching prompt v0.16.11. Everything below was run;
nothing is assumed. Nothing in `propagate.ail` was tuned to these results.

## What is being checked

`propagate.ail` has two propagators for a belief over the eight planet states:

- `propagate(belief, rates, years)`: a continuous-time Markov chain.
  `transitionRates(params)` gives the chain derived from the history parameters.
- `propagateExact(belief, params, years)`: the conditional law of the sampler in
  `history.ail` itself, given only the state a world is seen in.

The module header derives both. This note measures three things: that the chain
solver is right, that the exact law is the sampler's law, and how far the chain
is from the sampler.

## 1. The chain solver against closed forms and an oracle

Native tests, to 1e-12 per state (design AC5):

| Chain | Analytic solution | Rates and times |
|---|---|---|
| Two states, A ⇄ B | `b/(a+b) + a/(a+b) exp(-(a+b)t)` | 3 rate pairs × 13 times, `(a+b)t` from 1e-6 to 1e9 |
| Three states, A → B → C | `a/(b-a) (exp(-at) - exp(-bt))`, and `a t exp(-at)` when `a = b` | 3 rate pairs × 10 times |
| Three states, B ← A → C | exits split as `b : c` of `1 - exp(-(b+c)t)` | 2 rate pairs × 7 times |

`tools/propagate_ref.py` (Python, standard library, 50-digit decimals, Taylor
series with scaling and squaring) recomputes the baseline generator and the
chain from a mixed belief at 12 intervals from 1 to 1e11 years:

```text
chain rows: worst error 5.438e-16 (limit 1e-13)
```

Composition (`a` then `b` against `a+b`) holds within 1e-12 per state at nine
pairs from 1 to 1e9 years.

## 2. The exact law against the sampler

Seeded histories are drawn with `historyOf` and read with `stateAt` (test
module, Park-Miller generator, seed 20261112). A history is kept when it is in
the seen state at epoch 0, and tallied at two later times. Tolerance, fixed
before the first run: each state within 4 binomial standard errors of the
predicted probability, plus 2/n.

Parameters: the first three blocks use the baseline times (L = 1e5 yr, window
5e9 yr, traces 1e3–1e7 yr) with every world a lineage. The Complex block uses
L = 5e4 yr, window 2e6 yr, traces 2e4–2e5 yr and half of complex biospheres
hosting a lineage, so that emergence is visible.

`z` is (sampler − exact) in standard errors. States that are zero in all three
columns are omitted.

| Seen | Years on | Kept | State | Sampler | Exact | z | Chain | Chain − sampler |
|---|---|---|---|---|---|---|---|---|
| Technological | 5e4 | 4000 | Complex | 0.1182 | 0.1194 | -0.2 | 0.0072 | -0.1110 |
| Technological | 5e4 | 4000 | Technological | 0.5068 | 0.5000 | +0.9 | 0.6065 | +0.0998 |
| Technological | 5e4 | 4000 | Remnant | 0.2540 | 0.2556 | -0.2 | 0.2879 | +0.0339 |
| Technological | 5e4 | 4000 | Transcended | 0.0553 | 0.0500 | +1.5 | 0.0393 | -0.0159 |
| Technological | 5e4 | 4000 | Ecocide | 0.0658 | 0.0750 | -2.2 | 0.0590 | -0.0067 |
| Technological | 2e5 | 4000 | Complex | 0.3962 | 0.4065 | -1.3 | 0.0732 | -0.3231 |
| Technological | 2e5 | 4000 | Technological | 0.0000 | 0.0000 | 0.0 | 0.1353 | +0.1353 |
| Technological | 2e5 | 4000 | Remnant | 0.3508 | 0.3435 | +1.0 | 0.5753 | +0.2246 |
| Technological | 2e5 | 4000 | Transcended | 0.1110 | 0.1000 | +2.3 | 0.0865 | -0.0245 |
| Technological | 2e5 | 4000 | Ecocide | 0.1420 | 0.1500 | -1.4 | 0.1297 | -0.0123 |
| PreTech | 4e4 | 3118 | PreTech | 0.2595 | 0.2594 | 0.0 | 0.3594 | +0.0999 |
| PreTech | 4e4 | 3118 | Technological | 0.7405 | 0.7406 | 0.0 | 0.5105 | -0.2301 |
| PreTech | 4e4 | 3118 | Remnant | 0.0000 | 0.0000 | 0.0 | 0.0963 | +0.0963 |
| PreTech | 4e4 | 3118 | Transcended | 0.0000 | 0.0000 | 0.0 | 0.0130 | +0.0130 |
| PreTech | 4e4 | 3118 | Ecocide | 0.0000 | 0.0000 | 0.0 | 0.0195 | +0.0195 |
| PreTech | 3e5 | 3118 | Complex | 0.4262 | 0.4187 | +0.9 | 0.1062 | -0.3201 |
| PreTech | 3e5 | 3118 | Technological | 0.0000 | 0.0000 | 0.0 | 0.0810 | +0.0810 |
| PreTech | 3e5 | 3118 | Remnant | 0.3316 | 0.3313 | 0.0 | 0.5828 | +0.2511 |
| PreTech | 3e5 | 3118 | Transcended | 0.0997 | 0.1000 | 0.0 | 0.0919 | -0.0079 |
| PreTech | 3e5 | 3118 | Ecocide | 0.1424 | 0.1500 | -1.2 | 0.1378 | -0.0046 |
| Remnant | 1e5 | 1986 | Complex | 0.0463 | 0.0560 | -1.9 | 0.0880 | +0.0417 |
| Remnant | 1e5 | 1986 | Remnant | 0.9537 | 0.9440 | +1.9 | 0.9120 | -0.0417 |
| Remnant | 3e6 | 1986 | Complex | 0.6360 | 0.6612 | -2.4 | 0.9366 | +0.3007 |
| Remnant | 3e6 | 1986 | Remnant | 0.3640 | 0.3388 | +2.4 | 0.0632 | -0.3008 |
| Complex | 2e5 | 5429 | Complex | 0.9525 | 0.9539 | -0.5 | 0.9582 | +0.0057 |
| Complex | 2e5 | 5429 | PreTech | 0.0123 | 0.0108 | +1.1 | 0.0104 | -0.0020 |
| Complex | 2e5 | 5429 | Technological | 0.0144 | 0.0138 | +0.3 | 0.0126 | -0.0018 |
| Complex | 2e5 | 5429 | Remnant | 0.0122 | 0.0138 | -1.0 | 0.0111 | -0.0011 |
| Complex | 2e5 | 5429 | Transcended | 0.0039 | 0.0031 | +1.1 | 0.0031 | -0.0008 |
| Complex | 2e5 | 5429 | Ecocide | 0.0048 | 0.0046 | +0.2 | 0.0047 | -0.0001 |
| Complex | 8e5 | 5429 | Complex | 0.9072 | 0.9100 | -0.7 | 0.9157 | +0.0085 |
| Complex | 8e5 | 5429 | PreTech | 0.0122 | 0.0108 | +1.0 | 0.0099 | -0.0022 |
| Complex | 8e5 | 5429 | Technological | 0.0147 | 0.0138 | +0.6 | 0.0127 | -0.0020 |
| Complex | 8e5 | 5429 | Remnant | 0.0146 | 0.0162 | -1.0 | 0.0150 | +0.0005 |
| Complex | 8e5 | 5429 | Transcended | 0.0217 | 0.0197 | +1.1 | 0.0187 | -0.0031 |
| Complex | 8e5 | 5429 | Ecocide | 0.0297 | 0.0295 | +0.1 | 0.0280 | -0.0017 |

**Result.** The exact law is inside the tolerance at all eight pairs; the
largest deviation is 2.4 standard errors (Remnant, 3e6 years). The two Remnant
rows lean the same way; they share one sample of 1986 histories, so that is one
fluctuation, not two. The Python oracle, with 400,000 histories per seen state
drawn by an independent re-implementation of the sampler, gives 0.9442 and
0.3386 for those two cells against the exact 0.9440 and 0.3388, and across 39
(state, interval) rows:

```text
exact rows: worst |kernel - monte carlo| / tolerance 0.449 (limit 1, 400000 histories per seen state)
```

where the tolerance is 5 standard errors + 1e-5.

**The chain is outside the tolerance at all six lineage pairs** (seen
Technological, PreTech or Remnant), by 0.04 to 0.32 in a probability. The test
`sampler vs propagate: the chain misses the same tolerance at all six lineage
pairs` pins that, so the two are not mistaken for one another. At the two
Complex pairs the chain is inside the tolerance: emergence at a constant
density is what a memoryless model does well.

One count threshold in the Remnant test was wrong when first written (it asked
for more than 2000 kept histories; a collapse ending and a surviving trace keep
about 0.75 × 0.1085 = 8.1 % of 24000, about 1950). It was corrected to 1500.
The sample, the seed and the statistical tolerance were not changed.

## 3. How far the chain is from the sampler

Largest gap in any one state's probability between `propagate` with
`transitionRates` and `historyKernel`, at the baseline (L = 1e5 yr), scanned
over 1 to 1e9 years at 40 points per decade:

| Seen | Largest gap | At |
|---|---|---|
| Technological | 0.368 (= exp(-1)) | 1e5 yr = L |
| PreTech | 0.523 | 1e5 yr |
| Remnant | 0.321 | 1.9e6 yr |
| Complex | 5.2e-7 | 2.0e6 yr |

By interval, as a fraction of L:

| Interval / L | Seen Technological | Seen PreTech | Seen Remnant |
|---|---|---|---|
| 0.001 | 5.0e-7 | 4.5e-6 | 4.2e-9 |
| 0.01 | 5.0e-5 | 4.5e-4 | 4.2e-7 |
| 0.03 | 1.0e-3 | 4.0e-3 | 1.3e-4 |
| 0.1 | 0.011 | 0.041 | 1.4e-3 |
| 0.3 | 0.057 | 0.169 | 6.9e-3 |
| 1 | 0.368 | 0.523 | 0.032 |
| 3 | 0.322 | 0.313 | 0.106 |

Why: a technological epoch lasts exactly L, so the time left when one is seen
is uniform on [0, L], and nothing is left after L. An exponential clock of mean
L has a tail. The pre-technological lead and the traces are log-uniform, and a
state seen at a random moment is more likely to be a long one. The PreTech
column is the lead (1e4–1e5 yr, the same scale as the baseline L), so its
fractions of L are specific to the baseline.

For the game's example (picture 212 years old, arrival in 655 years, baseline
L), seen Technological: exact 0.99133 technological, chain 0.99137. With a
dialled lifetime of 1e4 years the same 867 years is 8.7 % of L and the gap is 0.004
(exact 0.9133 technological, chain 0.9170).

## 4. VM and interpreter

`ailang test --package .` and `ailang test --strict-bytecode --package .` both
pass 53 tests (50 named-test bodies on the VM, none falling back). The three
probe outputs (`comparisonProbe`, `oracleProbe`, `gapProbe`) and `_smoke.ail`
are byte-identical between `ailang run` and `ailang run --strict-bytecode`.

## 5. Reproduce

```sh
ailang test --package . && ailang test --strict-bytecode --package .
ailang run --strict-bytecode --entry oracleProbe propagate_test.ail > probe.txt
python3 -I tools/propagate_ref.py probe.txt
ailang run --strict-bytecode --entry comparisonProbe propagate_test.ail   # section 2
ailang run --strict-bytecode --entry gapProbe propagate_test.ail          # section 3
```
