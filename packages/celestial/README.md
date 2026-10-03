# sunholo/celestial

Pure solar-system mechanics for AILANG: Kepler's equation and orbit state
vectors, where the planets and their moons are on any date, the frame
rotations and rotation models that put them on a galactic sky, where they
are seen (light time), how hard they pull, and how bright they and their
rings are in reflected starlight.

```sh
ailang install sunholo/celestial
ailang pkg-docs sunholo/celestial   # AGENT.md: usage, units, pitfalls
```

- `kepler`: `solveKepler` (fixed 8-step Newton, residual < 1e-14 for
  e <= 0.97), `stateFromElements` (position and velocity), `driftingState`
  (the exact velocity of an orbit whose elements drift), vector helpers.
- `ephemeris`: the JPL approximate planetary elements (Standish & Williams
  1992, Tables 2a/2b, valid 3000 BC-3000 AD; outside it a labelled mean orbit),
  JPL satellite mean elements on their Laplace planes, `julianDate`.
- `frames`: ecliptic J2000 -> ICRS (IAU 2006 obliquity) -> galactic
  (Hipparcos 1997), and IAU WGCCRE 2015 pole and prime-meridian models.
- `lighttime`: the retarded time and position of a source seen by an
  observer (fixed 4-step iteration; checked against JPL Horizons).
- `gravity`: Newtonian point-mass acceleration in m/s^2 with IAU 2015
  nominal GM, refusing inside a body; the field relative to a body's centre
  for station-keeping.
- `reflect`: Lambert and Minnaert radiance and phase functions, tied to
  geometric and Bond albedo; a body's illuminance at the observer from the
  star's illuminance at 1 AU (a parameter: no photometry dependency).
- `rings`: classical single-scattering ring layer (lit and unlit faces,
  transmission), ring bands, and ring-shadow ray geometry.

Units: AU, days (TDB), km for satellite inputs, radians; float64 throughout.
No effects, deterministic, the same bits on the bytecode VM and the
interpreter, and no dependency on any other package (in particular not on
`sunholo/relativity`: photometric inputs are parameters). Radiance is in
cd/m^2 and illuminance in lux when the star's input is in lux.

It was built as the orbit core of the Stapledon's Voyage rebuild, and its
normative numbers are in the design repo's `physics/planets-spec.md`
(sunholo-data/stapledons-design). It is general-purpose.

Check values are published dates and constants; `tools/orbits_ref.py` is an
independent Python oracle (`python3 tools/orbits_ref.py --check`, recorded
in `tools/orbits_ref.out`).
