#!/usr/bin/env python3
"""Independent reference values for sunholo/relativity 0.4.0 (journey plans
and Higgs-bubble energetics). Standard library only.

Every expected number in journey_plan_test.ail and medium_test.ail comes from
here, never from the AILANG under test. Each value is computed twice:

  * float64, with the closed forms of the M2 design (stapledons-godot
    design_docs/planned/r1/m2-journey-core.md, rows 1-9 and the readout
    table), which reproduces the design's printed 16-17 digits; and
  * 50-digit Decimal arithmetic from the same exact float inputs, so the
    float64 value is also checked against the true value (relative <= 1e-13).

Canon check values (HB-n) are from stapledons-design physics/higgs-bubble.md.

Usage:
  python3 tools/journey_ref.py          # print every check row
  python3 tools/journey_ref.py --check  # also assert design digits; exit 1 on mismatch

Units: journey in c = 1, light-years, Julian years; medium in SI.
"""
import math
import sys
from decimal import Decimal, getcontext

getcontext().prec = 50

# ---------------------------------------------------------------- constants
G1 = 1.032295275553596             # 9.80665 m/s^2 in c per Julian year
A_BOOST = 7.5e5 * G1               # design default boost_g = 7.5e5 g
C_SI = 299792458.0                 # m/s
M_P = 1.67262192369e-27            # kg, CODATA 2018 (m_p c^2 = 1.50328e-10 J)
LY_M = 9460730472580800.0          # m, IAU (Julian year x c)
YR_S = 31557600.0                  # s, Julian year
AU_M = 149597870700.0              # m, IAU 2012
T_CMB = 2.725                      # K, higgs-bubble HB-5
D_ACEN = 4.37                      # ly, HB-4
N_ISM = 1.0e5                      # m^-3 (0.1 cm^-3, HB-3)
R_BUB = 100.0                      # m, HB-1


# ------------------------------------------------------- float64 closed forms
def acosh1p(u):
    return math.log1p(u + math.sqrt(u * (2.0 + u)))


def rapidity_of_one_minus_beta(e):
    return 0.5 * (math.log(2.0 - e) - math.log(e))


def plan_flip(d, a):
    p = acosh1p(a * d / 2.0)
    return dict(phi=p, ship=2.0 * p / a, earth=2.0 * math.sinh(p) / a,
                tauBurn=p / a, tauCoast=0.0, dBurn=d / 2.0, dCoast=0.0,
                tBurn=math.sinh(p) / a,
                fellBack=False)


def plan_bcb(d, a, phic):
    dburn = 2.0 * math.sinh(phic / 2.0) ** 2 / a
    if 2.0 * dburn >= d:
        r = plan_flip(d, a)
        r["fellBack"] = True
        return r
    dcoast = d - 2.0 * dburn
    return dict(phi=phic,
                ship=2.0 * phic / a + dcoast / math.sinh(phic),
                earth=2.0 * math.sinh(phic) / a + dcoast / math.tanh(phic),
                tauBurn=phic / a, tauCoast=dcoast / math.sinh(phic),
                dBurn=dburn, dCoast=dcoast, tBurn=math.sinh(phic) / a,
                fellBack=False)


# ------------------------------------------------------ 50-digit references
D = Decimal


def dsinh(x):
    e = x.exp()
    return (e - 1 / e) / 2


def dcosh(x):
    e = x.exp()
    return (e + 1 / e) / 2


def dtanh(x):
    return dsinh(x) / dcosh(x)


def dacosh1p(u):
    return (1 + u + (u * (2 + u)).sqrt()).ln()


def dplan(d, a, phic=None):
    d, a = D(d), D(a)
    if phic is not None:
        phic = D(phic)
        dburn = (dcosh(phic) - 1) / a
        if 2 * dburn < d:
            dcoast = d - 2 * dburn
            return dict(phi=phic, ship=2 * phic / a + dcoast / dsinh(phic),
                        earth=2 * dsinh(phic) / a + dcoast / dtanh(phic),
                        dCoast=dcoast, dBurn=dburn)
    p = dacosh1p(a * d / 2)
    return dict(phi=p, ship=2 * p / a, earth=2 * dsinh(p) / a, dCoast=D(0),
                dBurn=d / 2)


# ------------------------------------------------------------------ rows
PHI09 = math.atanh(0.9)
PHI099 = math.atanh(0.99)
PHICAP = rapidity_of_one_minus_beta(1.0e-6)
A_ROW5 = PHI099 / (600.0 / YR_S)   # HB-30: 10 ship-minutes to 0.99c
D_GL559 = 4.35667304258651

TRIP_ROWS = [
    # name, d, a, phiCruise (None = flip)
    ("row1 aCen 0.9c", D_ACEN, A_BOOST, PHI09),
    ("row2 aCen 0.99c", D_ACEN, A_BOOST, PHI099),
    ("row3 aCen cap", D_ACEN, A_BOOST, PHICAP),
    ("row4 0.001 ly cap (falls back)", 0.001, A_BOOST, PHICAP),
    ("row5 aCen 0.99c a=phi/600s", D_ACEN, A_ROW5, PHI099),
    ("row6 aCen flip 1 g", D_ACEN, G1, None),
    ("row7 Gl 559 flip 1 g", D_GL559, G1, None),
    ("row8 100 ly 1 g cruise 0.99", 100.0, G1, PHI099),
    ("row9 1000 ly 1 g gamma 707.1 (falls back)", 1000.0, G1, math.acosh(707.1)),
    # extra: short flip, a*d/2 = 5e-10, where acosh(1 + u) loses digits
    ("short flip 1e-9 ly at 1 g", 1.0e-9 / G1, G1, None),
    # extra: low-speed cruise, where (cosh(phi) - 1)/a loses digits of dBurn
    ("low-speed cruise d 1 a 1 phi 1e-6", 1.0, 1.0, 1.0e-6),
]

# Design rows 1-9 as printed (phi or None, ship-yr, Earth-yr).
DESIGN_TRIP = [
    (1.4722194895832204, 2.116489782091437, 4.8555571747021204),
    (2.6466524123622457, 0.6226958707592057, 4.414143655383168),
    (7.254328619262047, 0.006196277986522204, 4.370006949593909),
    (6.654436202069182, 1.7190007186656455e-05, 0.001002579912238613),
    (2.6466524123622457, 0.6227168354229866, 4.414153879485825),
    (None, 3.5823937227478337, 6.00250277725247),
    (None, 3.5780871495240905, 5.988497264963769),
    (2.6466524123622457, 17.696001151818983, 102.69103232505418),
    (None, 13.448622327743177, 1001.9355569687548),
]


def trip(row):
    _, d, a, phic = row
    return plan_flip(d, a) if phic is None else plan_bcb(d, a, phic)


def dtrip(row):
    _, d, a, phic = row
    return dplan(d, a, phic)


# ----------------------------------------------------------- medium (SI)
def load_scale(n, phi):
    return n * math.sinh(phi) ** 2 * M_P * C_SI ** 3


def kinetic_flux(n, phi):
    return n * math.sinh(phi) * 2.0 * math.sinh(phi / 2.0) ** 2 * M_P * C_SI ** 3


def drag_force(n, phi, r):
    return n * math.sinh(phi) ** 2 * M_P * C_SI ** 2 * math.pi * r * r


def drag_energy(n, phi, r, d_ly):
    return n * math.sinh(phi) * M_P * C_SI ** 2 * math.pi * r * r * d_ly * LY_M


def glow_in(n, phi, eps, fin):
    return eps * fin * kinetic_flux(n, phi) / 4.0


def photon_energy(m, phi):
    return m * C_SI ** 2 * phi


def readouts(phi):
    p = plan_bcb(D_ACEN, A_BOOST, phi)
    boost = photon_energy(1.0, p["phi"])
    drag = drag_energy(N_ISM, p["phi"], R_BUB, p["dCoast"])
    total = 2.0 * boost + drag
    f = drag_force(N_ISM, phi, R_BUB)
    return dict(boost=boost, drag=drag, total=total, totalKg=total / C_SI ** 2,
                load=load_scale(N_ISM, phi), glow=glow_in(N_ISM, phi, 1e-9, 0.5),
                force=f, power=f * C_SI, tfwd=T_CMB * math.exp(phi))


def dreadouts(phi):
    p = dplan(D_ACEN, A_BOOST, phi)
    ph = D(phi)
    c, mp, n, r = D(C_SI), D(M_P), D(N_ISM), D(R_BUB)
    pi = D(math.pi)  # the package uses the float64 pi literal
    sh = dsinh(ph)
    boost = c * c * ph
    drag = n * sh * mp * c * c * pi * r * r * p["dCoast"] * D(LY_M)
    k = n * sh * 2 * dsinh(ph / 2) ** 2 * mp * c ** 3
    f = n * sh * sh * mp * c * c * pi * r * r
    return dict(boost=boost, drag=drag, total=2 * boost + drag,
                totalKg=(2 * boost + drag) / (c * c),
                load=n * sh * sh * mp * c ** 3, glow=D("1e-9") * D("0.5") * k / 4,
                force=f, power=f * c, tfwd=D(T_CMB) * ph.exp())


DESIGN_READOUTS = {
    "0.9c": dict(boost=1.3231648905001936e17, drag=4.031443217698731e16,
                 total=3.0494741027702605e17, load=19212.82874513549,
                 glow=1.5052987296077217e-06, force=2.0133555741551197,
                 power=603588816.4039646, tfwd=11.877999621148337),
    "0.99c": dict(boost=2.3786925619268595e17, drag=1.3702577394591198e17,
                  total=6.127642863312838e17, load=221961.27278927868,
                  glow=2.4071942179266308e-05, force=23.25982143207345,
                  power=6973119039.76238, tfwd=38.44085554458952),
    "cap": dict(boost=6.519865414820472e17, drag=1.380061797390603e19,
                total=1.5104591056870126e19, load=2253353077.7286806,
                glow=0.2812710757763286, force=236133.9415328578,
                power=70791174749363.73, tfwd=3853.730994033574),
}
CRUISE = {"0.9c": PHI09, "0.99c": PHI099, "cap": PHICAP}


def relerr(got, want):
    want = float(want)
    return abs(got - want) / abs(want) if want != 0.0 else abs(got)


def main():
    check = "--check" in sys.argv
    bad = []

    def expect(label, got, want, tol):
        e = relerr(got, want)
        if e > tol:
            bad.append(f"{label}: got {got!r} want {float(want)!r} rel {e:.2e} > {tol:.0e}")

    print("# inputs")
    print(f"A_BOOST       = {A_BOOST!r}  (c/yr; 7.5e5 g)")
    print(f"PHI09         = {PHI09!r}")
    print(f"PHI099        = {PHI099!r}")
    print(f"PHICAP        = {PHICAP!r}  (gamma {math.cosh(PHICAP)!r})")
    print(f"A_ROW5        = {A_ROW5!r}  (c/yr; {A_ROW5 * C_SI / YR_S!r} m/s^2)")
    print(f"acosh1p(1e-10) = {acosh1p(1e-10)!r}  (50-digit {float(dacosh1p(D(1e-10)))!r})")
    print()
    print("# trip rows: phi | shipTime | galaxyTime | tauBurn | tauCoast | dBurn | dCoast | tBurn | fellBack")
    for i, row in enumerate(TRIP_ROWS):
        t, dt = trip(row), dtrip(row)
        print(f"{row[0]}: {t['phi']!r} | {t['ship']!r} | {t['earth']!r} | {t['tauBurn']!r} | "
              f"{t['tauCoast']!r} | {t['dBurn']!r} | {t['dCoast']!r} | {t['tBurn']!r} | {t['fellBack']}")
        for k in ("phi", "ship", "earth", "dBurn"):
            expect(f"{row[0]} {k} vs 50-digit", t[k], dt[k], 1e-13)
        if i < len(DESIGN_TRIP):
            dphi, dship, dearth = DESIGN_TRIP[i]
            if dphi is not None:
                expect(f"{row[0]} phi vs design", t["phi"], dphi, 0.0)
            expect(f"{row[0]} ship vs design", t["ship"], dship, 0.0)
            expect(f"{row[0]} earth vs design", t["earth"], dearth, 0.0)
    print()
    print("# readouts (aCen, n = 1e5 m^-3, R = 100 m, m_eff = 1 kg, eps = 1e-9, f_in = 1/2)")
    for name, phi in CRUISE.items():
        r, dr = readouts(phi), dreadouts(phi)
        print(f"{name}: " + ", ".join(f"{k}={v!r}" for k, v in r.items()))
        for k, v in DESIGN_READOUTS[name].items():
            expect(f"readout {name} {k} vs design", r[k], v, 1e-15)
            expect(f"readout {name} {k} vs 50-digit", r[k], dr[k], 1e-13)
    print()
    print("# canon HB values (higgs-bubble.md), computed")
    hb = {
        "HB-16 gamma 0.99c": math.cosh(PHI099),
        "HB-18 gamma cap": math.cosh(PHICAP),
        "HB-22 aCen 0.99c ship days": trip(TRIP_ROWS[1])["ship"] * 365.25,
        "HB-26 aCen cap ship days": trip(TRIP_ROWS[2])["ship"] * 365.25,
        "HB-23 felt 1 g to 0.99c ship-yr": PHI099 / G1,
        "HB-24 felt 1 g to cap ship-yr": PHICAP / G1,
        "HB-31 example boost a m/s^2": A_ROW5 * C_SI / YR_S,
        "HB-32 example boost a in g": A_ROW5 / G1,
        "HB-33 example boost galaxy min": math.sinh(PHI099) / A_ROW5 * YR_S / 60.0,
        "HB-34 example boost galaxy AU": 2.0 * math.sinh(PHI099 / 2) ** 2 / A_ROW5 * LY_M / AU_M,
        "HB-37 boost energy ratio": PHICAP / PHI099,
        "HB-38 load 0.5c": load_scale(N_ISM, math.atanh(0.5)),
        "HB-41 load 0.99c suns": load_scale(N_ISM, PHI099) / 1361.0,
        "HB-43 load cap suns": load_scale(N_ISM, PHICAP) / 1361.0,
        "HB-44 K 0.5c": kinetic_flux(N_ISM, math.atanh(0.5)),
        "HB-45 K 0.99c": kinetic_flux(N_ISM, PHI099),
        "HB-46 K cap": kinetic_flux(N_ISM, PHICAP),
        "HB-47 F 0.5c": drag_force(N_ISM, math.atanh(0.5), R_BUB),
        "HB-51 E_drag 0.5c full d": drag_energy(N_ISM, math.atanh(0.5), R_BUB, D_ACEN),
        "HB-52 E_drag 0.9c full d": drag_energy(N_ISM, PHI09, R_BUB, D_ACEN),
        "HB-53 E_drag 0.99c full d": drag_energy(N_ISM, PHI099, R_BUB, D_ACEN),
        "HB-54 E_drag 0.99c kg": drag_energy(N_ISM, PHI099, R_BUB, D_ACEN) / C_SI ** 2,
        "HB-55 E_drag cap full d": drag_energy(N_ISM, PHICAP, R_BUB, D_ACEN),
        "HB-56 E_drag cap kg": drag_energy(N_ISM, PHICAP, R_BUB, D_ACEN) / C_SI ** 2,
        "HB-61 eps for 1 W/m^2 at cap": 1.0 / glow_in(N_ISM, PHICAP, 1.0, 0.5),
        "V12 min m_eff brake holds (kg)": drag_force(N_ISM, PHICAP, R_BUB) / (A_BOOST * C_SI / YR_S),
    }
    for k, v in hb.items():
        print(f"{k}: {v!r}")
    if check:
        if bad:
            print("\nMISMATCH:\n" + "\n".join(bad))
            sys.exit(1)
        print("\nOK: design digits reproduced; float64 within 1e-13 of 50-digit references")


if __name__ == "__main__":
    main()
