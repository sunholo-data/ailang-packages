# sunholo/relativity

Pure special- and general-relativity maths for AILANG: trip times and
phase-by-phase trip plans, exact relativistic motion, Higgs-bubble energetics
(photon drive, interstellar-medium drag and glow, forward CMB), what a fast observer sees (aberration, Doppler colour and
brightness), and closed-form Schwarzschild black-hole quantities.

```sh
ailang install sunholo/relativity
ailang pkg-docs sunholo/relativity   # AGENT.md: usage, units, pitfalls
```

It was built as the physics core of the Stapledon's Voyage rebuild, where the
visuals have to be physically right. It is general-purpose and has no effects.

`photometry` converts Gaia BP-RP or Johnson B-V dwarf colours to temperature, Gaia G to Johnson V, magnitudes to lux and surface brightness to cd/m², and gives the naked-eye point-source threshold against a background (Crumey 2014). `blackbody.photopicRadiance` is a blackbody's absolute luminance in cd/m², `optics.cmbSeenTemperature` the CMB temperature seen in any direction at any speed, and `optics.apparentDisc` the apparent centre and size of a nearby sphere (a planet on a fast pass).

`blackbody_photometry` approximates white dwarfs as blackbodies: Gaia BP-RP to temperature (about 4% hot, 10% band) and to Johnson V (about 0.1 mag).

`journey` plans boost-cruise-brake and flip-and-burn trips with their phase boundaries (`planBurnCoastBurn`, `planFlipAndBurn`, `phaseAt`, `motionAt`). `medium` gives the Higgs-bubble energetics in SI: photon-drive energy, elastic-mirror ISM drag, load, glow (mean and angular profile, `glowEmittanceAt`) the trip energy ledger and the power to hover against gravity (`hoverPower`).
