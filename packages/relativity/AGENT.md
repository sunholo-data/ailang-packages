# AGENT.md: sunholo/relativity

## When to use

Use this package for anything where objects move close to light speed or sit
near a black hole and the numbers must be physically right:
- Trip planning: ship time vs home time for accelerate / coast / decelerate
  profiles, and the phase boundaries and closed-form motion a stepped
  simulation needs (`plan*`, `phaseAt`, `motionAt`).
- Higgs-bubble energetics (a pocket whose wall mirrors massive particles and
  passes light): photon-drive energy, interstellar-medium drag, load and glow,
  the trip energy ledger, the forward CMB temperature.
- Relativistic motion stepped in a simulation.
- What a fast-moving observer sees: aberration, Doppler shift, the colour and
  brightness of stars.
- Closed-form Schwarzschild quantities: shadow size, deflection, gravitational
  shift.

It is pure: no effects, deterministic, and the same results on the VM and the
interpreter.

Do NOT use it for:
- Orbital mechanics or Newtonian gravity.
- Rotating (Kerr) black holes.
- Full ray tracing through curved spacetime. Only closed forms and weak-field
  deflection are here; exact null-geodesic deflection is planned.

## Units and conventions

- **Units:** c = 1. Distances in light-years and times in Julian years, so
  `standardGravity()` = 1.0323 c/yr is 1 g. Any consistent unit system works
  if you pass your own acceleration.
- **Speed as rapidity φ:** β = tanh φ, γ = cosh φ. Use
  `kinematics.rapidityOfBeta` to convert. Everything is written in rapidity
  with the cancellations removed, so it stays accurate at γ in the millions.
  Never compute `1.0 - beta` yourself near c; use `oneMinusBeta(phi)`.
- **`n`:** unit vector from the observer **toward** the source, in the rest
  frame. `bh` is the unit direction of the observer's velocity.
- **`D`:** Doppler factor ν_seen/ν_emitted. D > 1 means blueshift.
- **`medium` is SI:** n in m^-3, R in m, m_eff in kg, accelerations in m/s^2
  (`accelSI` converts c/yr), distances in light-years (the journey unit).
  Results in J, N, W, W/m^2.
- **Schwarzschild module:** radii in units of r_s = 2GM/c² (the horizon is at
  r = 1). Angles in radians.

## Quick start

```ailang
import pkg/sunholo/relativity/kinematics (Motion, rest, accelerate, standardGravity, betaOf, gammaOf, rapidityOfOneMinusBeta)
import pkg/sunholo/relativity/journey (flipAndBurn, burnCoastBurn, planBurnCoastBurn, phaseAt, motionAt)
import pkg/sunholo/relativity/medium (tripEnergy, mirrorDragForce, accelSI)
import pkg/sunholo/relativity/optics (Vec3, aberrate, doppler)
import pkg/sunholo/relativity/blackbody (pointFluxRatio, rgbUnitLuminance)
import pkg/sunholo/relativity/photometry (teffFromBpRp, vFromG, illuminanceFromV)
import pkg/sunholo/relativity/schwarzschild (shadowAngularRadius)

-- Sol to alpha Centauri at 1 g, flip at the midpoint:
let trip = flipAndBurn(4.37, standardGravity());   -- shipTime 3.582, galaxyTime 6.003, peakBeta 0.9517

-- Boost-cruise-brake at 7.5e5 g (unfelt) to 1 - beta = 1e-6, with its ledger:
let a = 750000.0 * standardGravity();
let p = planBurnCoastBurn(4.37, a, rapidityOfOneMinusBeta(0.000001));
-- p.trip.shipTime 0.006196 (2.263 days), p.trip.galaxyTime 4.370, p.tauBurn, p.dCoast ...
let m = motionAt(p, tau);                           -- exact state at proper time tau
let e = tripEnergy(p, 1.0, 100000.0, 100.0);        -- m_eff 1 kg, n 0.1 cm^-3, R 100 m: e.total 1.510e19 J

-- Step a ship one tick (exact for any step size):
let m2 = accelerate(m, standardGravity(), 0.01);    -- m2.phi, m2.tau (ship yr), m2.t (galaxy yr), m2.x (ly)

-- Where a star at rest-frame direction n appears, and how its light shifts:
let seen = aberrate(n, heading, m2.phi);
let d = doppler(n, heading, m2.phi);
let brightness = pointFluxRatio(5700.0, d);         -- visual-band flux, seen / at rest
let colour = rgbUnitLuminance(5700.0 * d);          -- linear sRGB, Y = 1
```

## Exported surface

| Module | Exports |
|---|---|
| `hyper` | `sinh cosh tanh atanh acosh acosh1p expm1 log1p sinhc absf`. Accurate near 0; std/math has none of these |
| `kinematics` | `Motion {phi,tau,t,x}`, `rest`, `accelerate(m, a, dtau)`, `coast`, `standardGravity`, `betaOf`, `gammaOf`, `oneMinusBeta`, `gammaOfBeta`, `rapidityOfBeta`, `rapidityOfOneMinusBeta` |
| `journey` | `Trip {distance, shipTime, galaxyTime, peakBeta, peakGamma}`, `flipAndBurn(d, a)`, `burnCoastBurn(d, a, maxBeta)`, `coastAt(d, beta)`, `TripPlan {trip, a, phiPeak, tauBurn, tauCoast, tauTotal, dBurn, dCoast, fellBack}`, `planBurnCoastBurn(d, a, phiCruise)`, `planFlipAndBurn(d, a)`, `TripPhase` (`Accelerating Coasting Decelerating Arrived`), `phaseAt(p, tau)`, `motionAt(p, tau)` |
| `medium` | `cSI protonMassKg lightYearM julianYearS astronomicalUnitM cmbTemperatureK accelSI`, `photonDriveEnergy(mEff, phi)`, `loadScale(n, phi)`, `kineticFlux(n, phi)`, `mirrorDragForce(n, phi, r)`, `mirrorDragPower(n, phi, r)`, `cruiseDragEnergy(n, phi, r, dCoast)`, `glowInwardFlux(n, phi, eps, fIn)`, `TripEnergy {boost, brake, drag, total}`, `tripEnergy(p, mEff, n, r)`, `brakeHoldsAgainstDrag(mEff, a, n, phi, r)` |
| `optics` | `Vec3`, `aberrate`, `deaberrate`, `doppler`, `dopplerApparent`, `gammaOnePlusBetaCos`, `cosSeen`, `dot`, `norm`, `normalize`, `forwardDoppler`, `cmbForwardTemperature` |
| `blackbody` | `XYZ`, `RGB`, `cmf`, `planck`, `xyz`, `luminance`, `chromaticity`, `rgbUnitLuminance`, `pointFluxRatio`, `surfaceBrightnessRatio` |
| `photometry` | `teffFromBpRp`, `gMinusV`, `bpRpInTable`, `vFromG`, `illuminanceFromV`, `fluxRatioFromMags` |
| `photometry_table` | Generated Gaia BP-RP, Teff, G-V and spectral-type node lists |
| `blackbody_photometry` | `bbTeffMin`, `bbTeffMax`, `bbBpRp`, `bbGMinusV`, `bbBpRpInvertible`, `bbClampTeff`, `bbTeffFromBpRp`, `bbTeffFromBpRpExact`, `bbGMinusVFromBpRp`, `bbVFromG` |
| `blackbody_photometry_table` | Generated Gaia G/BP/RP and Bessell-Murphy V response samples, zero points and the 61-node colour table |
| `schwarzschild` | `photonSphere` (1.5), `criticalImpact` (3√3/2), `shadowAngularRadius(r)`, `weakDeflection(b)`, `staticObserverBlueshift(r)`, `staticClockRate(r)`, `pi` |

## Trip plans: `plan*` or the totals?

- Need only the totals (ship time, home time, peak speed)? `flipAndBurn`,
  `burnCoastBurn` and `coastAt` are fine; they are the plans' `.trip`.
- Stepping a voyage, switching phase at an exact proper time, or checking a
  stepped voyage against the closed form? Use `planBurnCoastBurn` /
  `planFlipAndBurn`, then `phaseAt(p, tau)` and `motionAt(p, tau)`.
  Boundaries are `tauBurn`, `tauBurn + tauCoast`, `tauTotal`, left-closed
  (exactly at `tauBurn` the ship is `Coasting`).
- **Cruise speed goes in as a rapidity, never as beta near c.** For a speed
  stated as its distance from c, use `rapidityOfOneMinusBeta(1e-6)`
  (gamma 707.107), not `rapidityOfBeta(0.999999)`.
- `fellBack` is true when the trip was too short to reach the cruise speed and
  became flip-and-burn; `phiPeak` is then the rapidity actually reached.
- `motionAt` is exact at each boundary and at arrival. Inside the brake the
  proper time is only known to an ulp of `tauTotal`, so phi there carries an
  absolute error of about a * ulp(tauTotal) (input precision, not the formula).

## Higgs-bubble energetics (`medium`)

- Photon drive: one boost or brake to phi costs m_eff c^2 phi (ship frame).
- ISM drag is on a **specular sphere**, n sinh^2(phi) m_p c^2 pi R^2, half a
  flat face-on mirror's. Holding cruise radiates F c per unit proper time, so
  `cruiseDragEnergy` = n sinh(phi) m_p c^2 pi R^2 d.
- `tripEnergy` charges drag over `p.dCoast`, not the full distance: the drag
  work in the boost and brake cancels as a pair (exact while
  `brakeHoldsAgainstDrag`), and the ledger then closes at arrival.
- `glowInwardFlux` is the mean over the inner wall, eps fIn K / 4.

## Photometry

Use `photometry` to estimate a **main-sequence dwarf** temperature in Kelvin
from Gaia BP-RP colour, infer Johnson V magnitude from Gaia G, or convert
visual magnitudes to lux and dimensionless flux ratios. Magnitudes and colours
are dimensionless logarithmic quantities; illuminance is in lux. The source
is Pecaut & Mamajek's dwarf sequence, version 2022.04.16:
https://www.pas.rochester.edu/~emamajek/EEM_dwarf_UBVIJHK_colors_Teff.txt

The source's complete Gaia colour rows cover B9V–M9.5V. To keep BP-RP
strictly increasing and temperature decreasing, the generated interpolation
table drops M9V and M9.5V and covers B9V–M8.5V (BP-RP -0.12–5.10).
`teffFromBpRp` and `gMinusV` clamp outside this range; use `bpRpInTable`
to detect extrapolation. The relation is for main-sequence dwarfs only, not
white dwarfs or giants.

## White-dwarf (blackbody) photometry

Use `blackbody_photometry` for the Gaia BP-RP of a **white dwarf**, or of any
source you choose to approximate as a blackbody: `bbTeffFromBpRp(bpRp)` gives
a blackbody temperature in K and `bbVFromG(g, bpRp)` gives Johnson V. Do not
use it for main-sequence stars (use `photometry`) or for physical white-dwarf
temperatures. Accuracy against 1,780 real white dwarfs within 50 pc: T_eff is
typically about 4% too hot, up to about +17% above 25 kK (99.2% within 10%);
V is good to about +-0.1 mag. Treat results as approximate.

- Bracket 3,000-100,000 K. `bbTeffFromBpRp` clamps to it (exactly 3000.0 or
  100000.0, also for NaN and +-infinity) and `bbBpRpInvertible` says whether
  the colour was inside it; `bbClampTeff` carries the proved range contract.
- `bbGMinusVFromBpRp` clamps to the end nodes; NaN gives the 3000 K end node.
- `bbTeffFromBpRp` is a 61-node table (interpolation error at most 5e-4
  relative in T). `bbTeffFromBpRpExact` (48 bisections, about 9,000 `planck`
  calls per call) is for tests and tools only.
- Convention: Gaia EDR3 Vega-mag, photon counting, published zero points.

## Physics notes that trip people up

- **Stars crowd forward.** A star at 90° appears at acos(β) ahead of the
  observer (25.84° at 0.9c). If your stars move backward as speed rises, you
  have applied the photon-propagation formula to a source direction.
- **Doppler angles.** Use the *rest-frame* angle with `doppler`, and the
  *apparent* angle with `dopplerApparent`. Mixing them is a classic bug.
- **Point sources vs extended sources.** A star's visual flux scales as
  (Y(D·T)/Y(T))/D²; bolometrically that is D², not D³ or D⁴. For sky and
  nebula surface brightness, use `surfaceBrightnessRatio`; bolometrically that
  is D⁴.
- **Black-hole shadow size.** The shadow is about 2.6 r_s across in impact
  parameter, not r_s, and from r = 3 r_s it is exactly π/4.

## Precision and verification

- Floats are outside Z3's decidable fragment. The `requires`/`ensures` here
  are runtime assertions (`ailang run --verify-contracts`), not proofs.
- The tests check against closed-form or published reference values: the
  CIE Planckian locus, the relativistic rocket equations and the Schwarzschild
  metric. The 0.4.0 plan and energetics values come from tools/journey_ref.py
  (float64 closed forms checked against 50-digit Decimal) to 1e-12 relative,
  and the canon higgs-bubble HB-n values to their printed digits.
- NaN: the interpreter answers NaN >= x with true (ailang#1419), the VM with
  false. Functions here test NaN first or are written with `<` so both engines
  agree; `_smoke.ail`'s `wdDigest` and `journeyDigest` check that bit for bit.
- Colours use the Wyman–Sloan–Shirley (2013) fit to the CIE 1931 colour
  matching functions, which is accurate to about 0.002 in chromaticity.
