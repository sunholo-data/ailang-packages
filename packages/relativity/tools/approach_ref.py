#!/usr/bin/env python3
"""Independent reference values for sunholo/relativity 0.9.0 (timed legs and the
final-approach trip profile). Standard library only.

Every expected number in approach_test.ail comes from here, never from the AILANG
under test: float64 closed forms, each cross-checked against 50-digit Decimal
(relative <= 1e-12). Units: c = 1, light-years, Julian years.

Usage: python3 tools/approach_ref.py
"""
import math
from decimal import Decimal as D, getcontext
getcontext().prec = 50

YR_S = 31557600.0
LY_KM = 9460730472580.8
AU_KM = 149597870.7

def dsinh(x):
    e = x.exp(); return (e - 1 / e) / 2
def dcosh(x):
    e = x.exp(); return (e + 1 / e) / 2

def timed_distance(tb, tc, phi):
    s = math.sinh(phi / 2.0)
    return 2.0 * tb * 2.0 * s * s / phi + tc * math.sinh(phi)

def solve(d, tb, tc):
    lo, hi = 0.0, 1.0
    while timed_distance(tb, tc, hi) < d:
        hi *= 2.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if timed_distance(tb, tc, mid) < d: lo = mid
        else: hi = mid
    return (lo + hi) / 2.0

def dsolve(d, tb, tc):
    d, tb, tc = D(d), D(tb), D(tc)
    f = lambda p: 2 * tb * (dcosh(p) - 1) / p + tc * dsinh(p)
    lo, hi = D(0), D(1)
    while f(hi) < d: hi *= 2
    for _ in range(170):
        mid = (lo + hi) / 2
        if f(mid) < d: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def plan(d, a, pc, aa, pa):
    sc, sa = math.sinh(pc / 2.0), math.sinh(pa / 2.0)
    dburn = 2.0 * sc * sc / a
    dbrake = 2.0 * (sc * sc - sa * sa) / a
    dapp = 2.0 * sa * sa / aa
    dcoast = d - dburn - dbrake - dapp
    tb, tbr, ta = pc / a, (pc - pa) / a, pa / aa
    shc, sha = math.sinh(pc), math.sinh(pa)
    tc = dcoast / shc
    return dict(dBurn=dburn, dCoast=dcoast, dApproach=dapp, tauBurn=tb, tauCoast=tc, tauApproach=ta,
                tauTotal=tb + tc + tbr + ta,
                galaxyTime=shc / a + dcoast / math.tanh(pc) + (shc - sha) / a + sha / aa)

def show(name, v, dv=None):
    if dv is not None:
        rel = abs(D(v) - dv) / abs(dv)
        assert rel <= D("1e-12"), (name, v, dv, rel)
    print(f"{name} = {v!r}")

# Sun -> Jupiter, 4.4 AU, boost 30 s, cruise 60 s (stapledons D-46)
d_jup = 4.4 * AU_KM / LY_KM
tb, tc = 30.0 / YR_S, 60.0 / YR_S
phi = solve(d_jup, tb, tc); show("jupiter_phi", phi, dsolve(d_jup, tb, tc))
show("jupiter_beta", math.tanh(phi))
a = phi / tb; show("jupiter_a", a)
# Earth -> Sun 0.99 AU and the short Callisto hop 0.0126 AU
d_sun = 0.99 * AU_KM / LY_KM
show("sun_phi", solve(d_sun, tb, tc), dsolve(d_sun, tb, tc))
d_cal = 0.0126 * AU_KM / LY_KM
show("callisto_phi", solve(d_cal, tb, tc), dsolve(d_cal, tb, tc))
# Jupiter's approach: begins where Jupiter is 4 deg across (centre distance R/sin 2 deg),
# minus the 2 R stand-off, and lasts 25 s.
R = 71492.0
xa = (R / math.sin(math.radians(2.0)) - 2.0 * R) / LY_KM
ta = 25.0 / YR_S
pa = solve(2.0 * xa, ta, 0.0); show("approach_phi", pa, dsolve(2.0 * xa, ta, 0.0))
show("approach_beta", math.tanh(pa))
aa = pa / ta; show("approach_a", aa)
show("approach_x", xa)
p = plan(d_jup, a, phi, aa, pa)
for k in ["dBurn", "dCoast", "dApproach", "tauBurn", "tauCoast", "tauApproach", "tauTotal", "galaxyTime"]:
    show("plan_" + k, p[k])
show("plan_tauTotal_s", p["tauTotal"] * YR_S)
