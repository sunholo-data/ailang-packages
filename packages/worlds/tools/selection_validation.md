# Universe selection: validation, 2026-11-12

AILANG v0.56.1 (`05c860a`), teaching prompt v0.16.11. Everything below was run
on this tree; nothing is assumed. Nothing in `selection.ail` or
`epoch_statistics.ail` was tuned to a printed figure.

## What is being checked

- `selection.ail`: the draw, the dial of a draw, the prior means, three
  statements of luck, the acceptance statistics and the prior probability of
  an acceptance region.
- `epoch_statistics.ail` (the 0.3.0 additions): ended-state bins, the
  late-contact share, the closed form for a lineage rate.
- That no 0.2.0 output changed.

## 1. The prior probability of a region against an independent oracle

`tools/selection_oracle.py` (Python, standard library) restates the priors and
the acceptance test from the registry and computes each probability two ways
that share nothing with the package: a Monte Carlo of the priors (1e7 draws,
seed 20261112), and the area of the accepted (minds, tech) pairs found by
clipping the unit square, integrated over the life quantile and the lifetime
quantile by nested adaptive Gauss-Kronrod. It writes
`selection_reference_test.ail`. The reference is stated to 1e-9 of each value;
the largest difference between its two starting grids in this run was 2.0e-11.

Tolerances, fixed before the package's first run: the package within 1e-8 of
the oracle's quadrature (its own doubling change included), and within 3
standard errors of the Monte Carlo.

`grid = 1`. "Change" is the package's `error`: the move from 1 to 2 panels a
piece. "Gap" is |package − oracle| / oracle. `z` is (Monte Carlo − package) in
standard errors.

| Region | Bands | p (package) | Change | Gap | Monte Carlo | z |
|---|---|---|---|---|---|---|
| nearOne | found ≤ 300 within 1,000 ly | 0.982719314819 | 1.0e-12 | 1.3e-14 | 0.9827381 ± 4.1e-5 | +0.46 |
| nearlyEmpty | found ≤ 1e-6 within 1,000 ly | 0.461222511650 | 2.0e-12 | 4.7e-13 | 0.4614423 ± 1.6e-4 | +1.39 |
| endedOnly | ended ≥ 2 | 0.174530368522 | 0 | 9.9e-15 | 0.1744265 ± 1.2e-4 | −0.87 |
| found3 | found ≥ 3 within 1,000 ly | 0.125540297719 | 1.2e-13 | 3.4e-13 | 0.1254957 ± 1.0e-4 | −0.43 |
| gapAboveRange | found ≥ 3, late ≤ 30, gap 1e9 yr | 0.0674536165510 | 1.4e-13 | 1.4e-12 | 0.0674411 ± 7.9e-5 | −0.16 |
| product1e5 | product ≥ 1e5 | 0.0608226577828 | 9.6e-13 | 1.7e-12 | 0.0608154 ± 7.6e-5 | −0.10 |
| threeBands | found 1–50, ended 0.5–500, late 0.01–5; three reach knots; gap 2,000 yr | 0.0195689255887 | 1.6e-14 | 2.6e-12 | 0.0195707 ± 4.4e-5 | +0.04 |
| lateOnly | late 1–2 within 3,000 ly; two reach knots; gap 5e4 yr | 0.0189705755633 | 3.3e-13 | 4.0e-12 | 0.0189525 ± 4.3e-5 | −0.42 |
| narrow | found 3–5, ended 1–3, late ≥ 0.02; gap 1e4 yr | 0.00162993731236 | 9.3e-17 | 3.5e-12 | 0.0016252 ± 1.3e-5 | −0.37 |
| product32e6 | product ≥ 3.2e7 | 2.79606842636e-4 | 1.3e-14 | 9.6e-12 | 2.763e-4 ± 5.3e-6 | −0.63 |
| tail1e5 | found ≥ 12 within 81.5 ly | 2.56137925856e-5 | 1.1e-15 | 4.8e-12 | 2.70e-5 ± 1.6e-6 | +0.84 |
| tail1e6 | found ≥ 16 within 81.5 ly | 2.18384126128e-6 | 8.3e-17 | 8.3e-12 | 2.2e-6 ± 4.7e-7 | +0.03 |

The largest gap is 9.6e-12 and the largest |z| is 1.39. The settings are in
the generated file. "product" is fLife·fMinds·fTech·L, obtained by setting
`hzWorlds` to the window so that `found` is the product itself.

**The package's two routes.** `productTail` (a sum of three uniforms under one
integral over life) and `acceptanceProbability` (a sum of two under the
two-dimensional rule) agree to 1e-9 at thresholds 1, 200, 1e5 and 3.2e7
(native test); `productTail` agrees with the oracle to 1e-8 at 3.2e7 and 1e5.

**The oracle was wrong once, and the package showed it.** The first version of
the oracle started its adaptive rule from 16 panels in the life quantile and
trusted the rule's own error estimate. For `tail1e5` it reported
2.5613790105e-5 with an estimated error of 2e-10; the package gave
2.5613792585e-5 by both of its routes, a gap of 1e-7. A third computation
settled it: in this corner the probability is E[(δ + log10 fLife)³₊]/216 with
δ = 8 − log10(threshold), which composite Simpson in the log-rate gives as
2.5613792585480215e-5 at 20,000 and at 80,000 points (…222e-5 at 320,000).
The oracle now integrates every cell from two different starting grids and
states their difference; the package was not changed. The oracle's other
first-run values moved by at most 4.5e-10.

**A gross-error check on the draw and the test.** Seeded uniforms (four
Park-Miller streams, one per factor) go through `drawParams` and `accepts`; the
frequency is within 4 binomial standard errors of `acceptanceProbability` for
the three-band region (20,000 draws) and for a lower bound, an upper bound and
a late band (8,000 each). This is not the validation of p. Four standard
errors at 20,000 draws is about ±20 % of p for the 0.0196 region: the check
catches a swapped slot, a missing log or a wrong factor between
`statisticsOf` (linear) and `acceptanceProbability` (logarithmic), and nothing
finer. The validation is the oracle's table above. 8,000 draws give the share
that `dialOf` refuses within 4 standard errors of
Φ((−100 + log10 0.632)/50) = 2.25 %.

**Where the grid matters.** With the fixed panel ends through the bend of
log10 fLife removed (an experiment on a scratch copy, not a shipped state),
`productTail(1e5)` at grid 1 reports a change of 8.0e-11 and at grid 2 a
change of 2.4e-16. With them in place the rule is at rounding level at grid 1,
which is why several rows report a change of 0. A reported change of 0 means
"no change on doubling", not "exact": the gaps above are the measured
accuracy, and they are bounded by the oracle's own 2e-11.

## 2. The three statements of luck, as computed

From `ailang run --strict-bytecode --entry luckProbe selection_test.ail`.

Prior means: life 0.5019999124, minds 0.1446200625 (LW-47p: 0.1446), tech
0.2149757685 (LW-48p: 0.2150), lifetime 7,238,234 yr (LW-46p: 7.238e6).
Product of the means 112,967.7; product of the medians 199.894. The mean sits
2.752 dex above the median (seti-factors §3.8: "2.75").

The calibrated universe of seti-factors §2.2 (every fraction 1, L = 3.2e7 yr):

| Statement | Value | Review's estimate |
|---|---|---|
| Over the product of the medians | 5.204 dex | 5.2 |
| Over the prior mean of the product | 2.452 dex | "about 2.5" |
| Prior probability of a product at least as large (proposed LW-55p) | 2.79606842635e-4, **one in 3,576.5**; change on doubling 0 | "about 2.9e-4", one in 3,500 |

The same probability at a threshold of 10^7.5 (3.162e7) is 2.88440e-4, one in
3,467. The design's "one in 15 to 20 after the rulings" cannot be computed
here: its bands, reach share and radius are outputs of the lab that do not
exist yet.

For orientation only, and not a setting anyone has ruled on: the prior
probability that the expected number of living technological worlds inside a
radius is at least 3, with every one of them findable (reach share 1) and
0.20 habitable-zone worlds a star.

| Radius | p | One in | Change on doubling |
|---|---|---|---|
| 81.5 ly | 0.00129582 | 771.7 | 6.5e-14 |
| 81.5 ly, at least 5 | 0.000505156 | 1,979.6 | 2.4e-14 |
| 326 ly | 0.0401328 | 24.92 | 1.1e-12 |
| 1,000 ly | 0.125540 | 7.966 | 1.2e-13 |
| 3,000 ly | 0.225438 | 4.436 | 5.6e-17 |
| 10,000 ly | 0.323455 | 3.092 | 1.3e-13 |

Also: P(product ≥ the median product) = 0.273940 (it is not one half: the
product's median is below the product of the medians, because the life prior
puts 42 % of its mass under 1e-10); P(product ≥ the prior mean product) =
0.0578733, one in 17.3.

## 3. Closed forms in `epoch_statistics`

From `ailang run --strict-bytecode --entry closedFormProbe
epoch_closed_forms_test.ail`.

| Row | Printed | Computed |
|---|---|---|
| LW-49p, mean remnant persistence | 1.086e6 yr | 1,085,627.63 |
| LW-50p, remnant share at saturated fractions | 1.63e-4 | 1.628441e-4 |
| LW-51p, baseline living share | 3.998e-8 | 3.997881e-8 |

Ended bins at the baseline medians, per habitable-zone world: Remnant
3.255e-7, Ecocide 1.499e-4, Transcended 9.994e-5. Twenty thousand histories
drawn by `historyOf` put all three bins within 4 standard errors of
`endedShares` (a parameter set chosen so each bin is 4–6 % of worlds).

seti-factors §3.4, A = 6.4e-3 held fixed:

| L (yr) | Lineages | One every (yr) | Ends within 16,000 yr | Ends in 600 yr | Remnant share |
|---|---|---|---|---|---|
| 3.2e7 | 1 | 5e9 | 0.05 % | 0.001875 % (printed 0.002) | 0.01628 % (printed 0.016) |
| 1e6 | 32 | 1.5625e8 (printed 156 million) | 1.6 % | 0.06 % | 0.521 % (printed 0.5) |
| 1e5 | 320 | 1.5625e7 (printed 15.6 million) | **16 %** (printed 15) | 0.6 % | 5.21 % (printed 5) |
| 1e4 | 3,200 | 1.5625e6 (printed 1.56 million) | **100 %** (printed 80) | 6 % | 23.16 % (printed 23) |

The two bold cells are the table's, not the model's: 15 % and 80 % are
1 − exp(−0.16) and 1 − exp(−1.6), a memoryless lifetime. `history.ail` gives
every civilisation exactly L years, so one that is alive now ends within G
years with probability min(1, G/L). The test asserts the model's values and,
separately, that the printed ones are the exponential form. The remnant column
caps the trace time at the quiet interval between lineages (spacing minus L);
capping at the spacing itself gives the same printed figures (23.25 % in the
last row).

## 4. Deliberate faults

`sh tools/selection_mutants.sh` copies the package to a scratch directory,
applies one fault, and runs `selection_test`, `selection_reference_test` and
`epoch_closed_forms_test` on the bytecode VM. A control (an edit that changes
nothing) must pass first. The number after each file is how many of its tests
fail.

| # | Fault | Result | Tests failing |
|---|---|---|---|
| 1 | minds prior lower bound 0.001 -> 0.002 | killed | selection 8, selection_reference 13, epoch_closed_forms 2 |
| 2 | life prior width 50 -> 49 dex | killed | selection 1, selection_reference 14 |
| 3 | draw: minds and tech read each other's uniform | killed | selection 5 |
| 4 | draw: complex-life clamp at 1 dropped | killed | selection 4 |
| 5 | dialOf: round-trip check dropped | killed | selection 2 |
| 6 | dialOf: round-trip tolerance 1e-12 -> 1e-3 | killed | selection 1 |
| 7 | statistics: ended-sign time not held to the window | killed | selection 2 |
| 8 | probability: ended-sign time not held to the window | killed | selection 1 |
| 9 | luck over the mean uses the median lifetime | killed | selection 1 |
| 10 | Gauss-Legendre: one weight 0.1 % high | killed | selection 6, selection_reference 14 |
| 11 | Normal density constant 0.1 % high | killed | selection 1, selection_reference 14 |
| 12 | mass at fLife = 1 dropped | killed | selection 7, selection_reference 14 |
| 13 | mass below the lowest kink dropped | killed | selection 2, selection_reference 2 |
| 14 | sum of uniforms: a subset sign not flipped | killed | selection 8, selection_reference 8 |
| 15 | survival taken as 1 - cdf in the upper tail | killed | selection 1, selection_reference 1 |
| 16 | band: lower edge exclusive | killed | selection 1 |
| 17 | band: upper edge exclusive | killed | selection 1 |
| 18 | statistics: late share not capped at 1 | killed | selection 2 |
| 19 | probability: late line not capped at the gap | killed | selection 1, selection_reference 2 |
| 20 | probability: band edge enters without its log | killed | selection 5, selection_reference 10 |
| 21 | probability: found line loses the lifetime | killed | selection 5, selection_reference 10 |
| 22 | probability: hzWorlds/window inverted | killed | selection 5, selection_reference 10 |
| 23 | probability: reach knots not used as panel ends | killed | selection 3, selection_reference 3 |
| 24 | probability: line crossings not used as panel ends | killed | selection 6, selection_reference 11 |
| 25 | convergence rule 1e-6 -> 1e-3 | killed | selection 1 |
| 26 | expectedDraws of an empty region returns a number | killed | selection 1 |
| 27 | ended bins: ecocide given the transcendence share | killed | epoch_closed_forms 3 |
| 28 | ended bins: window edge ignored | killed | epoch_closed_forms 3 |
| 29 | late share: cap at 1 dropped | killed | epoch_closed_forms 2 |
| 30 | lineages: traces capped at the spacing, not the quiet gap | killed | epoch_closed_forms 1 |
| 31 | lineages: overlap not refused | killed | epoch_closed_forms 1 |

31 faults, 31 killed, none survived; the control passes. Run time 3 min 41 s.
Three were added after review: the round-trip tolerance loosened to 1e-3 (it
survived the first 125 tests), and the ended-sign bound removed from
`statisticsOf` and from `acceptanceProbability`.

## 5. Existing outputs

`unchanged_probe_test.ail` prints the outputs of every export that existed in
0.2.0: quantiles of six priors at 14 uniforms, `applyDial` and `luckDex` at 40
dials, the disc counts at 12 radii, 3,000 histories from `historyOf` with
their states at three epochs and their `epochs`, both propagators and the
kernel at 24 (state, interval) pairs, `historyProbabilities` at 40 dials, the
occurrence and planet-model functions. It was run in the untouched 0.2.0 tree
(`origin/main` at `88f8079`, before any edit, celestial 0.6.0), in a checkout
of 0.2.1 (`6b0f2d1`, celestial 0.7.0) and in this tree:

```text
311423 bytes, sha256 554f3108f369bee9c031e2748bdbace0d7a699e3cab091f788fd12cd46a23c91
identical: 0.2.0 on the VM, 0.2.1 on the VM, 0.3.0 on the VM, 0.3.0 on the interpreter
```

`_smoke.ail` prints its first 11 lines unchanged, then three new lines and a
longer OK line. The eight 0.2.0 test files are untouched; the new tests are in
new files.

## 6. VM and interpreter

```text
$ ailang check --package .
✓ 24 files checked, all passed!
$ ailang test --package .
129 tests: 129 passed, 0 failed, 0 skipped (6m12s)
$ ailang test --strict-bytecode --package .
→ bytecode: 126 named-test bodies ran on the VM, 0 fell back to the evaluator; inline tests and properties run on the evaluator
129 tests: 129 passed, 0 failed, 0 skipped (19.2s)
```

0.2.0 and 0.2.1 had 65 tests; the 64 new ones are `selection_test` (37),
`selection_reference_test` (16), `epoch_closed_forms_test` (10) and the probe's
one. Four probes and the smoke program are byte-identical between `ailang run`
and `ailang run --strict-bytecode` (compared with `cmp`): `referenceProbe`
(2,315 bytes), `luckProbe` (1,312), `closedFormProbe` (682), `unchangedProbe`
(311,423), `_smoke.ail`.

Cost: the 12 reference regions take 1.2 s on the VM (about 0.1 s a call at
grid 1) and about 9 s a call on the interpreter, which is why the interpreter
suite takes about six minutes.

Two toolchain problems were met and reported, neither worked around in package
logic: the effect checker's "internal invariant: missing callback row" for a
record of closures used inside a lambda (ailang#2314; the lines of a region are
data here, an ADT tag and a float, not closures), and the strict VM's
256-register limit for one function, reached by `_smoke.ail`'s `main` when
three printlns were added (ailang#2315; the new lines are in their own
function).

## To repeat

```sh
ailang lock && ailang check --package .
ailang test --package . && ailang test --strict-bytecode --package .
python3 -I tools/selection_oracle.py | cmp - selection_reference_test.ail   # about 3 minutes; the table regenerates
ailang run --strict-bytecode --entry referenceProbe selection_reference_test.ail   # section 1
ailang run --strict-bytecode --entry luckProbe selection_test.ail                  # section 2
ailang run --strict-bytecode --entry closedFormProbe epoch_closed_forms_test.ail   # section 3
sh tools/selection_mutants.sh                                                       # section 4
ailang run --strict-bytecode --entry unchangedProbe unchanged_probe_test.ail > after.txt   # section 5; cmp with a 0.2.0 checkout
ailang pkg quality . && ailang publish --dry-run
```

## What is not claimed

- That the acceptance test predicts what a voyage finds. That is the lab's
  stratified validation (design, "Validating the test against voyages").
- That `error` bounds the numerical error. It is the change on doubling.
- That a draw's fLife is exactly Normal in the log-rate: `quantileOf` uses
  Acklam's approximation (relative error about 1e-9 in z). The probability is
  that of the stated prior; a frequency of draws differs from it by that much.
- Anything about the real universe. Every probability here is over the priors
  of `baseline-2026.11`, with the canon lifetime bound of 1e8 yr.
- `lineageShares` is not a model of how lineages arise. It is the arithmetic of
  evenly spaced lineages, as the design repo's table used it.
