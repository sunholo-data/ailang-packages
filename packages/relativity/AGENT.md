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
  brightness of stars, the CMB in every direction, and absolute luminances
  (cd/m^2) and the naked-eye threshold for exposing a rendered sky.
- Schwarzschild black holes: shadow size, deflection, gravitational shift,
  clocks and circular orbits, tides across a length, hover acceleration and
  power (closed forms), and exact null geodesics seen by a static observer at
  r >= 2 r_s (the exact form and images require r >= 2; the integrator alone
  works for r > 1.5): the lens map, image positions, Einstein angle, magnification,
  inverse lens-table rows (`geodesic`, 0.10.0).

It is pure: no effects, deterministic, and the same results on the VM and the
interpreter.

Do NOT use it for:
- Orbital mechanics or Newtonian gravity.
- Rotating (Kerr) black holes.
- Per-frame ray tracing. `geodesic` integrates one ray per call (hundreds to
  thousands of RK4 steps); bake a table offline and interpolate it per pixel.
- Massive-particle geodesics (free fall), charged holes, accretion disks.

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
import pkg/sunholo/relativity/optics (Vec3, aberrate, doppler, cmbSeenTemperatureApparent)
import pkg/sunholo/relativity/blackbody (pointFluxRatio, rgbUnitLuminance, photopicRadiance)
import pkg/sunholo/relativity/photometry (teffFromBpRp, teffFromBV, vFromG, illuminanceFromV, luminanceFromSurfaceMag, pointThresholdIlluminance, limitingMagnitude)
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

-- The sky in absolute units, per pixel with apparent direction nSeen:
let tCmb = cmbSeenTemperatureApparent(nSeen, heading, m2.phi);  -- 3853.7 K on the pole at the cap
let cmbLum = photopicRadiance(tCmb);                -- cd/m^2 (0 at 2.725 K, 1.984e8 at 3853.7 K)
let skyLum = luminanceFromSurfaceMag(22.0);         -- 1.725e-4 cd/m^2
let vLim = limitingMagnitude(skyLum, 2.0);          -- faintest visible star, field factor 2
```

## Exported surface

| Module | Exports |
|---|---|
| `hyper` | `sinh cosh tanh atanh acosh acosh1p expm1 log1p sinhc absf`. Accurate near 0; std/math has none of these |
| `kinematics` | `Motion {phi,tau,t,x}`, `rest`, `accelerate(m, a, dtau)`, `coast`, `standardGravity`, `betaOf`, `gammaOf`, `oneMinusBeta`, `gammaOfBeta`, `rapidityOfBeta`, `rapidityOfOneMinusBeta` |
| `journey` | `Trip {distance, shipTime, galaxyTime, peakBeta, peakGamma}`, `flipAndBurn(d, a)`, `burnCoastBurn(d, a, maxBeta)`, `coastAt(d, beta)`, `TripPlan {trip, a, phiPeak, tauBurn, tauCoast, tauTotal, dBurn, dCoast, fellBack, aApproach, phiApproach, tauApproach, dApproach}`, `planBurnCoastBurn(d, a, phiCruise)`, `planFlipAndBurn(d, a)`, `planBurnCoastBrakeApproach(d, a, phiCruise, aApproach, phiApproach)` (0.9.0), `TripPhase` (`Accelerating Coasting Decelerating Arrived`; the approach is `Decelerating`), `phaseAt(p, tau)`, `motionAt(p, tau)`, `inApproach(p, tau)`, `rapidityForTimedLeg(d, tBoost, tCruise)`, `rapidityForTimedApproach(d, tApproach)` |
| `medium` | `cSI protonMassKg lightYearM julianYearS astronomicalUnitM cmbTemperatureK accelSI`, `photonDriveEnergy(mEff, phi)`, `loadScale(n, phi)`, `kineticFlux(n, phi)`, `mirrorDragForce(n, phi, r)`, `mirrorDragPower(n, phi, r)`, `cruiseDragEnergy(n, phi, r, dCoast)`, `glowInwardFlux(n, phi, eps, fIn)`, `glowEmittanceAt(n, phi, eps, fIn, cosTheta)`, `glowTemperatureAt(n, phi, cosTheta)`, `glowRadianceAt(n, phi, eps, fIn, cosTheta)`, `glowEfficacyAt(n, phi, cosTheta)`, `glowLuminanceAt(n, phi, eps, fIn, cosTheta)`, `TripEnergy {boost, brake, drag, total}`, `tripEnergy(p, mEff, n, r)`, `brakeHoldsAgainstDrag(mEff, a, n, phi, r)`, `hoverPower(mEffKg, gMs2)` |
| `optics` | `Vec3`, `aberrate`, `deaberrate`, `doppler`, `dopplerApparent`, `gammaOnePlusBetaCos`, `cosSeen`, `dot`, `norm`, `normalize`, `forwardDoppler`, `cmbForwardTemperature`, `cmbSeenTemperature`, `cmbSeenTemperatureApparent`, `angleSeen(theta, phi)`, `ApparentDisc {centre, radius}`, `apparentDisc(cosTheta, alpha, phi)` |
| `blackbody` | `XYZ`, `RGB`, `cmf`, `planck`, `xyz`, `luminance`, `chromaticity`, `rgbUnitLuminance`, `pointFluxRatio`, `surfaceBrightnessRatio`, `photopicRadiance`, `stefanBoltzmannSI`, `luminousEfficacy(kelvin)` |
| `photometry` | `teffFromBpRp`, `gMinusV`, `bpRpInTable`, `teffFromBV`, `bvInTable`, `vFromG`, `illuminanceFromV`, `vFromIlluminance`, `fluxRatioFromMags`, `luminanceFromSurfaceMag`, `surfaceMagFromLuminance`, `pointThresholdIlluminance`, `limitingMagnitude` |
| `photometry_table` | Generated Gaia BP-RP, Teff, G-V and spectral-type node lists, and the Johnson B-V and Teff node lists |
| `blackbody_photometry` | `bbTeffMin`, `bbTeffMax`, `bbBpRp`, `bbGMinusV`, `bbBpRpInvertible`, `bbClampTeff`, `bbTeffFromBpRp`, `bbTeffFromBpRpExact`, `bbGMinusVFromBpRp`, `bbVFromG` |
| `blackbody_photometry_table` | Generated Gaia G/BP/RP and Bessell-Murphy V response samples, zero points and the 61-node colour table |
| `schwarzschild` | `photonSphere` (1.5), `criticalImpact` (3√3/2), `shadowAngularRadius(r)`, `weakDeflection(b)`, `staticObserverBlueshift(r)`, `staticClockRate(r)`, `pi`; 0.10.0: `impactFromStaticAngle(r, psi)`, `turningRadius(b)`, `weakDeflection2(b)`, `weakDeflectionFinite(r, psi)`, `strongDeflectionBbar`, `circularOrbitSpeed(r)`, `circularOrbitClockRate(r)`, `orbitalAngularVelocity(r)`, `movingClockRate(r, beta)`, `radialCoordinateRate(r, beta)`, `hoverAcceleration(r)`, `rsPerSolarMassMetres`, `tidalRadial(r)`, `tidalTransverse(r)`, `tidalRadialOrbit(r)`, `tidalAccelSI(mSun, r, lenM)`, `tidalOrbitAccelSI(mSun, r, lenM)`, `tidalSafeRadius(mSun, lenM, aMax)`, `tidalMinMass(lenM, r, aMax)`, `hoverAccelSI(mSun, r)`, `hoverPowerPerKg(mSun, r)` |
| `geodesic` | 0.10.0. `Ray {escaped, dphi}`, `Binet {u, v}`, `InvSample {dpsi, slope}`; integrator `binetStep`, `escapeAzimuth(r, psi, h)`, `lensDeflection(r, psi, h)`, `deflectionFromInfinity(b, h)`, `integrateRay`; capture `escapes(r, psi)`; exact `carlsonRF(x, y, z)`, `deflectionExact(b)`, `escapeAzimuthExact(r, psi)`, `deflectionExactAt(r, psi)`; lens map `lensRegular(r, psi, h)`, `imageAngle(r, beta, order)`, `einsteinAngle(r)`, `imageMagnification(r, psi)`, `inverseRow(r, nFwd, nOut)`, `inverseRowLogMin` |

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
- `glowEmittanceAt(n, phi, eps, fIn, cosTheta)` is the glow's angular profile
  (0.6.0): eps fIn K max(0, cos theta) W/m^2 at the wall element whose outward
  normal is at theta from the travel direction, ship frame. The pole value
  (cosTheta = 1) is exactly 4 x `glowInwardFlux` (bit for bit) and its sphere
  mean is `glowInwardFlux`. Renderers that draw the glow should take the pole
  value from this function and mirror only the max(0, cos) shape, never
  multiply `glowInwardFlux` by 4 themselves. cosTheta is clamped to [0, 1], so
  a dot product that rounds to 1.0000000000000002 gives the pole; NaN
  cosTheta gives NaN.
- The glow's spectrum (0.8.0, stapledons D-30): the wall is a greybody of
  emissivity eps (Kirchhoff: it absorbs almost no light, so it emits almost
  none), so eps cancels in the energy balance and
  `glowTemperatureAt(n, phi, cosTheta)` = (K max(0, cos theta) / sigma)^(1/4):
  1357.5 K on the pole at 0.99c, 14,114 K at 1 - beta = 1e-6, cos^(1/4) off
  the pole. eps and fIn set only the brightness. `glowRadianceAt` = emittance
  / pi (Lambertian), `glowEfficacyAt` = `blackbody.luminousEfficacy` at that
  temperature (0.0233 lm/W at 0.99c, 43.7 at the cap), and `glowLuminanceAt`
  = radiance x efficacy in cd/m^2. Colour: `blackbody.rgbUnitLuminance(T)`;
  guard it with luminance > 0, since below about 25 K the visible integral is
  0 and the colour is 0/0. Canon eps is 1e-11 (D-29): the 0.99c pole is then
  1.65e-4 of a 23.5 mag/arcsec^2 dark sky and the cap pole 3.61e3 of it.
  The blackbody is a game stand-in (real GeV impacts are not thermal).
- `hoverPower(mEffKg, gMs2)` = m_eff |g| c (W): holding still (or on a
  planned line) against an unfelt acceleration g costs the photon drive
  F c with F = m_eff |g| (higgs-bubble.md §10, HB-90). 0.1254 m/s^2 (50,000 km
  above Earth) is 3.759e7 W per kg of m_eff; Sgr A* at 3 r_s is 1.44e14 W/kg.
  Linear in both arguments, so a stepped hold sums it times dtau per tick.

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

`teffFromBV` does the same from Johnson B-V (for bright stars Gaia
saturates on): the same table's B-V column, O3V-M9V (B-V -0.33-2.17,
44,900-2,380 K), clamped, NaN to the cool end, `bvInTable` for the range.
It is a dwarf relation: approximate for giants, and B-V carries almost no
temperature information for O stars or late M dwarfs.

## Sky photometry in absolute units

For exposing a rendered sky, every source needs a luminance in cd/m^2 (or an
illuminance in lux for point sources), never a ratio against a rest value:
- `blackbody.photopicRadiance(T)`: a blackbody's luminance, 683 lm/W x
  integral B_lambda ybar (CIE 1931 fit, 360-830 nm). 0 for T <= 0, NaN and
  the CMB's 2.725 K, so it never divides by ~0 (unlike
  `surfaceBrightnessRatio(2.725, D)`). Finite for every input including
  +Inf: Rayleigh-Jeans (linear in T) at very high T, flat above the Planck
  temperature 1.416784e32 K, where `planck` clamps (0.5.2; +Inf before).
- `optics.cmbSeenTemperature(n, bh, phi)` takes the rest-frame direction (like
  `doppler`); `cmbSeenTemperatureApparent(nSeen, ...)` takes the apparent
  direction (like `dopplerApparent`): use it per pixel. The CMB's seen
  luminance is `photopicRadiance(cmbSeenTemperatureApparent(...))`.
- **Sideways is dark in the ship frame.** At apparent 90 deg, D = 1/gamma
  (T_CMB / gamma, starlight redshifted). D = 1 at
  cos theta' = (1 - 1/gamma)/beta, about 3 deg from the pole at gamma 707.
  The "gamma at 90 deg" value (gamma T_CMB) is for the REST-frame 90 deg,
  which appears asin(1/gamma) from the pole.
- `photometry.luminanceFromSurfaceMag(mu)`: V mag/arcsec^2 to cd/m^2 on the
  package zero point (V = -13.98 at 1 lux).
- `photometry.pointThresholdIlluminance(lb)`: the naked-eye threshold (lux)
  for a point source on a background of lb cd/m^2, field factor 1, from
  Crumey (2014) MNRAS 442, 2600, Eqs. 53 (scotopic, lb <= 0.0708) and 33
  (photopic), flat below 1e-5 cd/m^2. `limitingMagnitude(lb, f)` is the
  faintest V; Crumey takes f = 2 as a typical observer (6.19 at 2e-4 cd/m^2).
  lb is photopic luminance; Crumey's scotopic colour correction is not
  applied. **Not monotone over 0.022-0.108 cd/m^2**: Crumey's scotopic fit
  peaks at 0.02184 cd/m^2 and dips 22% to the 0.0708 split, and the photopic
  branch regains the peak only at 0.1077, so there a brighter background can
  give a fainter limit (4.78 at 0.0218, 4.90 at 0.05, F = 2). Dark skies
  (1e-4-1e-3) and bright glow (>> 1 cd/m^2) are unaffected; do not invert
  the threshold for lb across that window.

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

## Nearby spheres: `apparentDisc`

- `apparentDisc(cosTheta, alpha, phi)` takes a sphere of angular radius
  alpha (rad, 0 to pi/2) whose centre is at REST-frame polar angle theta from
  the heading, and returns `{centre, radius}` of its image (rad, centre
  measured from the heading). Aberration is conformal, so the outline stays
  a circle; a Lorentz-squashed disc never appears.
- **The apparent centre is not the aberrated centre.** At 0.9c, theta 90,
  alpha 5: centre 25.928 deg, radius 2.184 deg, while the centre's own ray
  appears at 25.842 deg. Draw the disc at `centre`; use `angleSeen(theta,
  phi)` only for a point (the body's centre of mass, a label).
- Astern discs are magnified (0.9c, theta 150: radius 9.940 deg), ahead
  they shrink (0.99c: 0.707 deg). D at the disc's apparent centre is
  `dopplerApparent` of that direction (2.2871, 7.0623, 0.4981 for the three).
- `angleSeen` uses tan(theta'/2) = e^-phi tan(theta/2): no 1 - beta, exact at
  the cap and next to both poles (acos(cosSeen) loses digits there). A disc
  over a pole keeps the pole inside its image (centre < radius).
- Near the forward pole at the cap, `dopplerApparent` itself carries about
  gamma^2 ulp of rounding (1.3e-11 relative at gamma 707); the disc angles do
  not.

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

## Black holes: geodesics, tides, hover (0.10.0)

- **Conventions.** r and b in r_s. The observer is static at r; psi is a
  ray's angle from the direction **toward** the hole in the observer's frame;
  b = r sin psi / sqrt(1 - 1/r) (`impactFromStaticAngle`). The deflection
  seen at r is delta = dphi - (pi - psi); the source of the ray at psi lies at
  F = psi - delta from the hole direction (negative: the far side).
- **Integrator or exact form?** `escapeAzimuth`/`lensDeflection`/`lensRegular`
  (RK4, step h in azimuth) is the general method the spec names; use it in
  offline tools (h = 0.005 is about 5e-7 rad worst case). The exact form
  (`escapeAzimuthExact`, `deflectionExact`, `deflectionExactAt`) is the
  oracle: use it in checks, image solving and inverse rows; it and everything
  built on it (images, magnification, inverse rows) require r >= 2. Never call
  either per frame or per pixel (an integrator call is up to thousands of RK4
  steps, capped at 4e6).
- **Capture is analytic.** `escapes(r, psi)`: outgoing rays escape, ingoing
  rays escape iff b > b_c (valid for r >= 1.5). A captured ray has
  `escaped = false`; `lensDeflection` and `deflectionExactAt` are NaN there.
- **Near the shadow edge** delta diverges like -ln(psi - alpha_sh). Tables
  store `lensRegular` = delta + ln tanh((psi - alpha_sh)/alpha_sh), finite
  from 1e-8 alpha_sh to the antipode; add the singular term back analytically.
  Float64 sets a floor there: at b = b_c (1 + 1e-8) one ulp of b moves delta
  by ~1e-9.
- **Weak field.** 2/b (`weakDeflection`) is 1.5 % low at b = 100; use
  `weakDeflection2` (2.7e-4) or the exact form. Beyond r = 1e6 the finite
  observer's (1 + cos psi)/b (`weakDeflectionFinite`) is within 1e-3 relative.
- **Images.** `imageAngle(r, beta, 0)` is the primary, order 1 the secondary
  on the far side; `einsteinAngle(r)` (beta = 0) is 29.83 deg at 10 r_s,
  61.89 deg at 3 r_s, 2.60 deg at 1000 r_s. `imageMagnification` is the point
  magnification at an image.
- **Inverse rows.** `inverseRow(r, 16384, n)` gives n samples uniform in F
  on [-pi, pi] (F = beta finds order 0, F = -beta order 1): psi - alpha_sh
  and dpsi/dF, monotone by construction (Fritsch-Carlson).
- **Tides and hover (SI).** Mass in solar masses, lever in metres, results in
  m/s^2 (divide by 9.80665 for g). `tidalAccelSI` is the static or radially
  moving value, `tidalOrbitAccelSI` the circular-orbit one (1.5x at 3 r_s).
  The Higgs-bubble wall does not shield tides; the pocket does not feel the
  hover acceleration, but the drive pays `hoverPowerPerKg` per kg of m_eff.
  A crewed hover at 3 r_s needs M >= 1.97e5 Msun for <= 0.1 g over 100 m
  (`tidalMinMass`); Sgr A* gives 2.1e-4 g.

## Precision and verification

- Floats are outside Z3's decidable fragment. The `requires`/`ensures` here
  are runtime assertions (`ailang run --verify-contracts`), not proofs.
- The tests check against closed-form or published reference values: the
  CIE Planckian locus, the relativistic rocket equations and the Schwarzschild
  metric. The 0.4.0 plan and energetics values come from tools/journey_ref.py
  (float64 closed forms checked against 50-digit Decimal) to 1e-12 relative,
  and the 0.7.0 apparent-disc and hover values from tools/optics_ref.py (the
  rest-frame circle Lorentz-transformed point by point in 60-digit Decimal,
  outline circular to 1e-30 rad) to 1e-12 relative,
  and the canon higgs-bubble HB-n values to their printed digits. The 0.5.0
  sky photometry values come from tools/photometry_ref.py: a 0.05 nm Simpson
  quadrature with exact SI constants, the official CIE 1931 ybar table, the
  platinum-point candela, 50-digit Decimal CMB temperatures and Crumey's
  printed limits. The 0.6.0 glow profile values come from tools/glow_ref.py
  (60-digit Decimal from the exact float inputs; the 1/4 sphere mean checked
  by an independent quadrature in theta). The 0.8.0 glow spectrum values come
  from tools/glow_spectrum_ref.py (60-digit Decimal; sigma from exact SI
  h, k, c; Stefan-Boltzmann checked by integrating Planck's law; the efficacy
  peak checked against the CIE blackbody maximum). The 0.10.0 geodesic,
  tide and hover values come from stapledons-godot tools/geodesic_ref.py
  (an independent Python RK4 integrator, Carlson R_F in float64 and a
  50-digit Decimal truth with Newton-polished roots; IAU 2015 GM_sun).
- NaN: the interpreter answers NaN >= x with true (ailang#1419), the VM with
  false. Functions here test NaN first or are written with `<` so both engines
  agree; `_smoke.ail`'s `wdDigest`, `journeyDigest`, `photometryDigest`,
  `glowDigest`, `discDigest`, `glowSpectrumDigest`, `approachDigest`, `schwarzschildDigest` and `lensDigest` check that bit for bit.
- Colours use the Wyman–Sloan–Shirley (2013) fit to the CIE 1931 colour
  matching functions, which is accurate to about 0.002 in chromaticity.
