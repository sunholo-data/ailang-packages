# sunholo/observe

Pure observation maths for AILANG: what reaches an observer, when, and what
it means.

- **When** (c = 1): when the light from a static source reaches an observer
  (the light cone), how long a signal takes to catch a ship on a straight
  cruise, the triangle excess and link window of a plan relayed via home,
  whether a point lies on a beam's ray from home, and the home rate (Doppler
  factor for home's direction).
- **How much** (SI): photons from a star or a planet into a telescope, the
  planet's contrast, zodiacal background, SNR and integration time, the inner
  working angle; how far a radio transmitter is heard; how much waste heat
  brightens a star in the infrared.
- **What it means** (a game model): Bayes over eight planet states from
  detections and non-detections, with their false positives.

```sh
ailang install sunholo/observe
ailang pkg-docs sunholo/observe   # AGENT.md: usage, units, pitfalls
```

- `lightcone`: `seenAt`, `catchUp`, `triangleExcess`, `onBeamLine`,
  `linkWindow`, `earthRate`, and the vector helpers `sub` and `cross`.
- `constants`: h, c, k, AU, parsec, light-year, jansky, mas, nominal solar,
  Earth and Jupiter values, `snrHint`, `snrStrong`.
- `photon`: `photonRate`, `planetContrast`, `lambertPhase`, `zodiRate`,
  `backgroundRate`, `snr`, `timeToSnrS`, `iwaLimitDistanceM`, `observable`,
  `planetBudget`, and the reference instrument.
- `link`: `sefdWm2Hz`, `linkSnr`, `integratedSnr`, `reachM`, `eirpFromErpW`.
- `wasteheat`: `wasteHeatFactor`, `wasteHeatExcess`, `wasteHeatFractionFor`.
- `belief`: `likelihood`, `confidence`, `posterior`, `pLifeCeiling`. A game
  model: every number in it is a design value, not a measurement.

Units: `lightcone` uses light-years, years, the galaxy frame, home at the
origin. `photon`, `link` and `wasteheat` use SI, with the unit in every
parameter name; their check values are the stapledons-design observation
registry's OB-1..OB-52. The Doppler
factor comes from [sunholo/relativity](../relativity/) (`optics`), and 1 − β
from its `kinematics.oneMinusBeta`; neither formula is repeated here.

It was built for the Stapledon's Voyage rebuild (Earth's signal, R3), where
every number on the comms console has to be physically right. The check values
are the stapledons-design relativity spec's RS-26..RS-37. It is pure, with the
same bits on the strict bytecode VM and the interpreter.
