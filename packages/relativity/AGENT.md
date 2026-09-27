# AGENT.md: sunholo/relativity

## When to use

Use this package for anything where objects move close to light speed or sit
near a black hole and the numbers must be physically right:
- Trip planning: ship time vs home time for accelerate / coast / decelerate
  profiles.
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
- **Schwarzschild module:** radii in units of r_s = 2GM/c² (the horizon is at
  r = 1). Angles in radians.

## Quick start

```ailang
import pkg/sunholo/relativity/kinematics (Motion, rest, accelerate, standardGravity, betaOf, gammaOf)
import pkg/sunholo/relativity/journey (flipAndBurn, burnCoastBurn)
import pkg/sunholo/relativity/optics (Vec3, aberrate, doppler)
import pkg/sunholo/relativity/blackbody (pointFluxRatio, rgbUnitLuminance)
import pkg/sunholo/relativity/photometry (teffFromBpRp, vFromG, illuminanceFromV)
import pkg/sunholo/relativity/schwarzschild (shadowAngularRadius)

-- Sol to alpha Centauri at 1 g, flip at the midpoint:
let trip = flipAndBurn(4.37, standardGravity());   -- shipTime 3.582, galaxyTime 6.003, peakBeta 0.9517

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
| `hyper` | `sinh cosh tanh atanh acosh expm1 log1p sinhc absf`. Accurate near 0; std/math has none of these |
| `kinematics` | `Motion {phi,tau,t,x}`, `rest`, `accelerate(m, a, dtau)`, `coast`, `standardGravity`, `betaOf`, `gammaOf`, `oneMinusBeta`, `gammaOfBeta`, `rapidityOfBeta` |
| `journey` | `Trip {distance, shipTime, galaxyTime, peakBeta, peakGamma}`, `flipAndBurn(d, a)`, `burnCoastBurn(d, a, maxBeta)`, `coastAt(d, beta)` |
| `optics` | `Vec3`, `aberrate`, `deaberrate`, `doppler`, `dopplerApparent`, `gammaOnePlusBetaCos`, `cosSeen`, `dot`, `norm`, `normalize` |
| `blackbody` | `XYZ`, `RGB`, `cmf`, `planck`, `xyz`, `luminance`, `chromaticity`, `rgbUnitLuminance`, `pointFluxRatio`, `surfaceBrightnessRatio` |
| `photometry` | `teffFromBpRp`, `gMinusV`, `bpRpInTable`, `vFromG`, `illuminanceFromV`, `fluxRatioFromMags` |
| `photometry_table` | Generated Gaia BP-RP, Teff, G-V and spectral-type node lists |
| `schwarzschild` | `photonSphere` (1.5), `criticalImpact` (3√3/2), `shadowAngularRadius(r)`, `weakDeflection(b)`, `staticObserverBlueshift(r)`, `staticClockRate(r)`, `pi` |

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
- The 47 tests check against closed-form or published reference values: the
  CIE Planckian locus, the relativistic rocket equations and the Schwarzschild
  metric.
- Colours use the Wyman–Sloan–Shirley (2013) fit to the CIE 1931 colour
  matching functions, which is accurate to about 0.002 in chromaticity.
