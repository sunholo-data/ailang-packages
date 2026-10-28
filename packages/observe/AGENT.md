# AGENT.md: sunholo/observe

## When to use

Use this package when something far away is seen or heard by light, and the
delay or the rate matters:
- When the light now arriving left a static source: `seenAt(t, obs, src)`
  = t − |obs − src| (the newest news from home, its age).
- When a signal sent after a ship left catches it on a straight outbound
  cruise: `catchUp(delta, oneMinusBeta)` = delta / (1 − β).
- How much history from home a moving ship receives per second of its own:
  `earthRate(pos, heading, phi)`, the Doppler factor γ(1 + β cos θ) for home's
  direction. Below 1 receding (e^−φ straight away), above 1 approaching.
- Relaying a plan via home: a plan sent from port a reaches home |a| later,
  and home's reply reaches port b |b| after that. `linkWindow(a, b, legT,
  covered)` is the wait at b after arriving, max(0, |a| + |b| − legT);
  `triangleExcess(a, b)` is the pure geometry |a| + |b| − |ab|.
- Whether a point is on the ray of a beam home aims at a port:
  `onBeamLine(port, p, angTol)`.

It is pure: no effects, deterministic, and the same bits on the bytecode VM
(`--strict-bytecode`) and the interpreter.

Do NOT use it for:
- Moving sources. `seenAt` is exact only for sources static in the frame. For
  Solar System bodies use `sunholo/celestial`'s `lighttime` (a retarded-time
  iteration).
- Aberration, the Doppler factor of an arbitrary direction, or 1 − β itself:
  use `sunholo/relativity` (`optics`, `kinematics`).
- Accelerating legs in `catchUp`: it assumes the whole outbound path is a
  straight cruise at one β from departure.
- Signal strength, noise or link budgets (a later version).

## Units and conventions

- **c = 1. Light-years, years**, the galaxy (rest) frame, float64.
- **Home is the origin.** Every position is measured from it.
- **heading** is a unit vector along the ship's velocity; **phi** is its
  rapidity (β = tanh φ), 0 ≤ φ ≤ 700.
- **Pass 1 − β, never compute it.** `catchUp` takes 1 − β; get it from
  `kinematics.oneMinusBeta(phi)` (exact at γ in the millions). `1.0 - beta`
  rounds to 0 near c.
- **At home** (|pos| < `atSolLy()` = 1e-12 ly) `earthRate` takes home's
  direction as −heading: leaving home reads e^−φ, continuous with just outside,
  and a ship at rest reads 1.

## Pitfalls

- `triangleExcess` is not the wait when b lies on a beam's ray: a port beyond
  a or between home and a gives an excess of 2|a| or more, but home is already
  aiming along that ray. Test coverage with `onBeamLine` and pass it to
  `linkWindow` as `covered`.
- `covered` is the beam home was aiming when the plan was sent (the previous
  plan's port), not the one it aims at when the ship arrives: by then home has
  usually heard the new plan, and every port would look covered.
- Choose `angTol` for the beam, not for float64: the atan2 form resolves
  angles down to about 1e-15 rad, so 1e-7 rad (about 4 AU off a 40 ly ray) is a
  physical choice.
- `onBeamLine` excludes home itself and the far side of home (p · port ≤ 0).
- `linkWindow` needs the leg's galaxy time T from your journey model; at high
  γ, T ≈ |ab| and the wait is the triangle excess.

## Example

```ailang
import pkg/sunholo/observe/lightcone (earthRate, linkWindow, onBeamLine)
import pkg/sunholo/relativity/kinematics (rapidityOfOneMinusBeta)

-- 40 ly out, cruising straight away at beta = 0.999999: 7.0711e-4
earthRate({x: 40.0, y: 0.0, z: 0.0}, {x: 1.0, y: 0.0, z: 0.0}, rapidityOfOneMinusBeta(0.000001))
-- re-planned at a port 40 ly out to one 30 ly off at a right angle: wait 60 yr
linkWindow({x: 40.0, y: 0.0, z: 0.0}, {x: 40.0, y: 30.0, z: 0.0}, 30.0, false)
```

## Tests

`ailang test --package .` runs `lightcone_test.ail`: RS-26..RS-37 against
closed forms, the at-home guard, the 1e-8 rad resolution and the α Cen news
epoch. `_smoke.ail` prints `OK: ...` in a clean workdir, and its `linkProbe`
must print identical bytes on the strict VM and the interpreter.
