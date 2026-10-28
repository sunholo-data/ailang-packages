# sunholo/observe

Pure observation geometry for AILANG at c = 1: when the light from a static
source reaches an observer (the light cone), how long a signal takes to catch
a ship on a straight cruise, the triangle excess and link window of a plan
relayed via home, whether a point lies on a beam's ray from home, and the home
rate (Doppler factor for home's direction).

```sh
ailang install sunholo/observe
ailang pkg-docs sunholo/observe   # AGENT.md: usage, units, pitfalls
```

- `lightcone`: `seenAt`, `catchUp`, `triangleExcess`, `onBeamLine`,
  `linkWindow`, `earthRate`, and the vector helpers `sub` and `cross`.

Units: light-years, years, the galaxy frame, home at the origin. The Doppler
factor comes from [sunholo/relativity](../relativity/) (`optics`), and 1 − β
from its `kinematics.oneMinusBeta`; neither formula is repeated here.

It was built for the Stapledon's Voyage rebuild (Earth's signal, R3), where
every number on the comms console has to be physically right. The check values
are the stapledons-design relativity spec's RS-26..RS-37. It is pure, with the
same bits on the strict bytecode VM and the interpreter.
