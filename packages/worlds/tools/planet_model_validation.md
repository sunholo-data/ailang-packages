# Synthetic inference validation, 2026-11-02

This independently checks the implementation and its source transcription.
It does not establish that the adopted synthesis prior reproduces nature or
Forecaster's posterior.

## Primary sources and qualifications

- [Pecaut & Mamajek's dwarf sequence](https://www.pas.rochester.edu/~emamajek/EEM_dwarf_UBVIJHK_colors_Teff.txt),
  version 2022.04.16, Msun column. Downloaded source SHA256:
  `1de2edeec17bb3346e0e4e70b999de5ee29947df38474e64cddb7cfacc164b7f`.
  All 18 selected (Teff,Msun) knots match the source exactly. This is a sparse
  selection, not the complete sequence: comparing omitted F0V–M9V nodes gives
  a maximum relative interpolation difference of 6.34% at M5.5V, 2930 K
  (source 0.123 Msun, sparse interpolation 0.1308 Msun). Classification as a dwarf
  is the caller's responsibility; `dwarfInTable` checks temperature only.
  This is not Mann 2019's K-band relation.
- [Chen & Kipping 2017, arXiv 1603.08614v2](https://arxiv.org/pdf/1603.08614v2),
  Table 1 pp 7–9, supplies the coefficient/transition medians and fractional
  dispersions. Section 2.3 Eq 3 models normal scatter in log10 radius. The
  implementation explicitly adopts a different linear-radius Gaussian and a
  128-cell log-uniform mass prior on .001–4200 Earth masses. It omits
  hyperparameter uncertainty. `centralRadiusEarth` means the connected curve
  from componentwise median coefficients, not an arithmetic mean or the full
  posterior's predictive median. The conditional sampler is labelled as an
  approximation and applies only to synthetic planets.

Both approximations need to retain those labels in downstream provenance.
No observational archive value is authorized to be replaced by this model.
The substitution of a sparse dwarf-temperature relation for the design's
Mann/K-band relation remains a model choice for the attended review.

## Numerical evidence

AILANG v0.56.0 (`e1ef997`), teaching prompt v0.16.11:

```text
✓ 14 files checked, all passed!
29 tests: 29 passed, 0 failed, 0 skipped
bytecode: 28 named-test bodies ran on the VM, 0 fell back to the evaluator
planet_model oracle: 65 radii, 780 conditional quantiles; finite/support/CDF/endpoints agree
```

The six independent validation tests cover all 18 stellar knots; nine
70-digit Decimal evaluations of the central curve; continuity from both
sides at both break masses; temperature boundaries/NaN rejection; 65 radii
from .5–16 Earth radii by 12 uniforms including 0, 2^-53 and 1-2^-53; monotonic
conditional quantiles; and 513 log-mass points from.001–4200 Earth masses.
The Python oracle reconstructs the connected curve in log space and uses
`math.fsum` for the independently computed conditional CDF. It checks grid
support and both sides of every returned quantile. The oracle is test-only
and produces no package or game data.

Complete JSON emitted by `planet_model_validation_test.main`, with runtime
contracts enabled, is byte-identical between interpreter and strict VM:
SHA256 `b02d988bd7f9512e231fe0fa00142553fa27373328ef54f07f51ce9e0aa7071f`.
Every scalar is serialized; no truncated `show` comparison is used.

From this package directory, reproduce with `$AILANG` set to the pinned binary:

```sh
"$AILANG" run --caps IO --verify-contracts --entry main planet_model_validation_test.ail > /tmp/planet-model-interp.json
"$AILANG" run --caps IO --strict-bytecode --verify-contracts --entry main planet_model_validation_test.ail > /tmp/planet-model-vm.json
cmp /tmp/planet-model-interp.json /tmp/planet-model-vm.json
python3 tools/planet_model_ref.py /tmp/planet-model-vm.json
```

Full quality now reports **no gates**, after celestial 0.6.0 became available:
compile 14 files;0/10 contracts verified,0 refuted,13 uncontracted;
missing_postcondition 4,unsupported_encoding 6; interface v2 `52f8d317b227…`
(47 signatures); effects max/rank IO with ceiling declared; release/docs present;
23/23 pure exports; native 29 passed, 0 failed, 0 skipped; staged smoke passed.
PUB016 lists 10 skipped contracts and PUB011 lists13 uncontracted exports.
No proof or publication is claimed by this validation.
