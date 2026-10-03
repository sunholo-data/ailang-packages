#!/usr/bin/env python3
"""Independent reference values for sunholo/celestial 0.1.0, part 1
(kepler, ephemeris, frames). Standard library only; no network.

Every check in kepler_test.ail, ephemeris_test.ail and frames_test.ail is a
published date or constant. This script is the second-language oracle: it
re-derives each check with independent code paths and asserts that the
published values are reproduced within the tests' tolerances, so a bug the
AILANG VM and interpreter would share is caught here.

Independent paths (not a transliteration of the AILANG):
  * Kepler: solved by bisection to the last bit (the package uses Newton);
    the package's fixed 8-step Newton from E0 = M + e sin M is also simulated
    over a dense (M, e) grid to prove the 1e-14 residual claim.
  * Galactic frame: built from the Hipparcos *angles* (alpha_G 192.85948,
    delta_G 27.12825, l_Omega 32.93192 deg; ESA SP-1200 Vol 1 sec 1.5.3) by
    spherical trigonometry, not from the 3x3 matrix the package uses.
  * Positions: Standish & Williams (1992) Table 2a/2b, evaluated in 50-digit
    Decimal for the elements; event times (oppositions, Saturn's ring-plane
    crossings) found by bisection on the geometric condition.

Published inputs (copied from the sources, cited at each constant):
  JPL SSD "Approximate Positions of the Planets", Tables 2a, 2b
    https://ssd.jpl.nasa.gov/planets/approx_pos.html (fetched 2026-10-03)
  JPL SSD "Planetary Satellite Mean Elements" (Moon DE405/LE405; Io JUP365)
    https://ssd.jpl.nasa.gov/sats/elem/ (fetched 2026-10-03)
  IAU WGCCRE 2015: Archinal et al. 2018, Celest. Mech. Dyn. Astr. 130:22
  IAU 2006 obliquity at J2000: 84381.406 arcsec (Capitaine et al. 2003)

Published check values (the targets the AILANG tests assert):
  Jupiter opposition 2023-11-03; Mars opposition 2020-10-13 (+-2 d)
  Saturn equinoxes (Sun ring-plane crossings) 2009-08-11, 2025-05-06 (+-10 d)
  Lunar distance extremes 356,375-406,720 km (Meeus, Astronomical
    Algorithms 2nd ed., ch. 50 / Astronomical Tables of the Sun, Moon
    and Planets): the mean orbit must stay inside
  Io sidereal period 1.769137786 d (NASA NSSDC Jovian satellite fact sheet)
  North ecliptic pole in galactic coordinates (96.38, 29.81) deg
  Obliquities to orbit (NASA NSSDC planetary fact sheet): Earth 23.44,
    Saturn 26.73 deg
  Moon apsidal period 8.85 yr = 3232.6 d

Usage:
  python3 tools/orbits_ref.py          # print every check row
  python3 tools/orbits_ref.py --check  # also assert; exit 1 on any mismatch
"""
import math
import sys
from decimal import Decimal, getcontext

getcontext().prec = 50

D2R = math.pi / 180.0
J2000 = 2451545.0
AU_KM = 149597870.7                    # IAU 2012 B2
EPS0 = 84381.406 / 3600.0 * D2R        # IAU 2006 obliquity at J2000
K_GAUSS = 0.01720209895                # Gaussian gravitational constant

# ------------------------------------------------------------------ Table 2a
# a(au) e I L long.peri long.node, then the per-century rates (Standish 1992)
T2A = {
    "EMB": ("1.00000018 0.01673163 -0.00054346 100.46691572 102.93005885 -5.11260389",
            "-0.00000003 -0.00003661 -0.01337178 35999.37306329 0.31795260 -0.24123856"),
    "Mars": ("1.52371243 0.09336511 1.85181869 -4.56813164 -23.91744784 49.71320984",
             "0.00000097 0.00009149 -0.00724757 19140.29934243 0.45223625 -0.26852431"),
    "Jupiter": ("5.20248019 0.04853590 1.29861416 34.33479152 14.27495244 100.29282654",
                "-0.00002864 0.00018026 -0.00322699 3034.90371757 0.18199196 0.13024619"),
    "Saturn": ("9.54149883 0.05550825 2.49424102 50.07571329 92.86136063 113.63998702",
               "-0.00003065 -0.00032044 0.00451969 1222.11494724 0.54179478 -0.25015002"),
}
# Table 2b: b c s f
T2B = {
    "Jupiter": "-0.00012452 0.06064060 -0.35635438 38.35125000",
    "Saturn": "0.00025899 -0.13434469 0.87320147 38.35125000",
}

T_MIN, T_MAX = -50.0, 10.0             # 3000 BC .. 3000 AD in Julian centuries


def jd_gregorian(y, m, d):
    """Fliegel & Van Flandern (1968) integer JDN, then -0.5 for 0h."""
    a = (14 - m) // 12
    yy = y + 4800 - a
    mm = m + 12 * a - 3
    jdn = d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045
    return jdn - 0.5


def standish(body, jd):
    """Heliocentric ecliptic J2000 position (au) and the mean-orbit flag."""
    el = [Decimal(x) for x in T2A[body][0].split()]
    rt = [Decimal(x) for x in T2A[body][1].split()]
    t = (jd - J2000) / 36525.0
    tc = min(max(t, T_MIN), T_MAX)
    T = Decimal(repr(t))
    Tc = Decimal(repr(tc))
    a, e, inc, L, wbar, node = (el[i] + rt[i] * Tc for i in range(6))
    L = el[3] + rt[3] * T                 # the phase keeps advancing
    M = L - wbar
    if body in T2B:
        b, c, s, f = (Decimal(x) for x in T2B[body].split())
        ft = float(f * Tc) * D2R
        M += b * Tc * Tc + c * Decimal(repr(math.cos(ft))) + s * Decimal(repr(math.sin(ft)))
    M = float(M % 360) * D2R
    a, e = float(a), float(e)
    inc, wbar, node = float(inc) * D2R, float(wbar) * D2R, float(node) * D2R
    w = wbar - node
    E = kepler_bisect(M, e)
    xp = a * (math.cos(E) - e)
    yp = a * math.sqrt(1 - e * e) * math.sin(E)
    return perifocal_to_frame(xp, yp, inc, node, w), (t < T_MIN or t > T_MAX)


def perifocal_to_frame(xp, yp, inc, node, w):
    # Composed as three explicit rotations (Rz(node) Rx(inc) Rz(w)).
    x1 = xp * math.cos(w) - yp * math.sin(w)
    y1 = xp * math.sin(w) + yp * math.cos(w)
    y2 = y1 * math.cos(inc)
    z2 = y1 * math.sin(inc)
    x3 = x1 * math.cos(node) - y2 * math.sin(node)
    y3 = x1 * math.sin(node) + y2 * math.cos(node)
    return (x3, y3, z2)


def kepler_bisect(M, e):
    """E - e sin E = M by bisection on [M - e, M + e] (f is monotone)."""
    lo, hi = M - e - 1e-300, M + e + 1e-300
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid - e * math.sin(mid) - M < 0:
            lo = mid
        else:
            hi = mid
        if hi - lo <= 0:
            break
    return 0.5 * (lo + hi)


def kepler_newton8(M, e):
    """The package's algorithm, simulated to test the residual claim."""
    E = M + e * math.sin(M)
    for _ in range(8):
        E = E - (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
    return E


def wrap(x):
    return math.atan2(math.sin(x), math.cos(x))


def lon(v):
    return math.atan2(v[1], v[0])


def bisect_time(f, t0, t1, n=80):
    f0 = f(t0)
    assert (f0 < 0) != (f(t1) < 0), "no sign change in bracket"
    for _ in range(n):
        tm = 0.5 * (t0 + t1)
        fm = f(tm)
        if (fm < 0) == (f0 < 0):
            t0, f0 = tm, fm
        else:
            t1 = tm
    return 0.5 * (t0 + t1)


# ---------------------------------------------------------------- frames
def ecl_to_eq(v):
    x, y, z = v
    return (x, y * math.cos(EPS0) - z * math.sin(EPS0), y * math.sin(EPS0) + z * math.cos(EPS0))


def eq_to_ecl(v):
    x, y, z = v
    return (x, y * math.cos(EPS0) + z * math.sin(EPS0), -y * math.sin(EPS0) + z * math.cos(EPS0))


def radec_to_galactic(ra, dec):
    """Spherical trig from the Hipparcos galactic pole and node angles."""
    ag, dg, lom = 192.85948 * D2R, 27.12825 * D2R, 32.93192 * D2R
    sb = math.sin(dec) * math.sin(dg) + math.cos(dec) * math.cos(dg) * math.cos(ra - ag)
    b = math.asin(sb)
    y = math.cos(dec) * math.sin(ra - ag)
    x = math.sin(dec) * math.cos(dg) - math.cos(dec) * math.sin(dg) * math.cos(ra - ag)
    l = (lom + math.pi / 2 - math.atan2(y, x)) % (2 * math.pi)  # l_Omega = l of the ascending node
    # The node convention: l = l_Omega + 90 deg - atan2(...). Check on the NGP
    # (b = 90) and the galactic centre (l = 0) below.
    return l, b


def unit_radec(ra, dec):
    return (math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec))


def vec_to_radec(v):
    return math.atan2(v[1], v[0]) % (2 * math.pi), math.asin(v[2] / math.sqrt(sum(c * c for c in v)))


# WGCCRE 2015 (Archinal et al. 2018), Table 2: Saturn, Jupiter (linear part), Earth
POLES = {
    "Saturn": (40.589, -0.036, 83.537, -0.004),
    "Jupiter": (268.056595, -0.006499, 64.495303, 0.002413),
    "Earth": (0.0, -0.641, 90.0, -0.557),
}


def pole_ecl(body, jd):
    ra0, ra1, de0, de1 = POLES[body]
    T = (jd - J2000) / 36525.0
    if body == "Jupiter":  # periodic terms Ja..Je
        J = [(99.360714, 4850.4046, 0.000117, 0.000050), (175.895369, 1191.9605, 0.000938, 0.000404),
             (300.323162, 262.5475, 0.001432, 0.000617), (114.012305, 6070.2476, 0.000030, -0.000013),
             (49.511251, 64.3000, 0.002150, 0.000926)]
        ra = ra0 + ra1 * T + sum(ar * math.sin((p + r * T) * D2R) for p, r, ar, _ in J)
        de = de0 + de1 * T + sum(ad * math.cos((p + r * T) * D2R) for p, r, _, ad in J)
    else:
        ra, de = ra0 + ra1 * T, de0 + de1 * T
    return eq_to_ecl(unit_radec(ra * D2R, de * D2R))


def orbit_normal(body, jd):
    el = [float(x) for x in T2A[body][0].split()]
    rt = [float(x) for x in T2A[body][1].split()]
    T = (jd - J2000) / 36525.0
    inc = (el[2] + rt[2] * T) * D2R
    node = (el[5] + rt[5] * T) * D2R
    return (math.sin(inc) * math.sin(node), -math.sin(inc) * math.cos(node), math.cos(inc))


def angle_deg(u, v):
    d = sum(a * b for a, b in zip(u, v)) / math.sqrt(sum(a * a for a in u) * sum(b * b for b in v))
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))


# ------------------------------------------------------------- satellites
def sat_pos(a_km, e, w0, M0, i, node0, ldot, wdot, ndot, pole_ra, pole_dec, jd):
    """JPL SSD mean elements: angles deg at epoch J2000.0, rates deg/day.
    ldot is the mean-longitude rate; dM/dt = ldot - wdot - ndot."""
    dt = jd - J2000
    w = (w0 + wdot * dt) * D2R
    node = (node0 + ndot * dt) * D2R
    M = ((M0 + (ldot - wdot - ndot) * dt) % 360.0) * D2R
    E = kepler_bisect(wrap(M), e)
    a = a_km
    xp, yp = a * (math.cos(E) - e), a * math.sqrt(1 - e * e) * math.sin(E)
    v = perifocal_to_frame(xp, yp, i * D2R, node, w)
    # Laplace plane -> ICRF equatorial: node of the plane on the equator at
    # ra + 90 deg, inclination 90 - dec. Then -> ecliptic.
    ninc = math.pi / 2 - pole_dec * D2R
    nnode = pole_ra * D2R + math.pi / 2
    x1, y1, z1 = v
    y2 = y1 * math.cos(ninc) - z1 * math.sin(ninc)
    z2 = y1 * math.sin(ninc) + z1 * math.cos(ninc)
    eqv = (x1 * math.cos(nnode) - y2 * math.sin(nnode), x1 * math.sin(nnode) + y2 * math.cos(nnode), z2)
    return eq_to_ecl(eqv), (w0 + node0 + M0 + ldot * dt) * D2R


FAILS = []


def check(name, ok, detail):
    print(("PASS " if ok else "FAIL ") + name + ": " + detail)
    if not ok:
        FAILS.append(name)


def main():
    # ---- kepler
    worst = 0.0
    worst_at = None
    for ie in range(0, 98):
        e = ie / 100.0
        for im in range(-2000, 2001):
            M = math.pi * im / 2000.0
            E = kepler_newton8(M, e)
            r = abs(E - e * math.sin(E) - M)
            if r > worst:
                worst, worst_at = r, (M, e)
            Eb = kepler_bisect(M, e)
            assert abs(E - Eb) < 1e-12 * max(1.0, abs(Eb)) or e > 0.9, (M, e, E, Eb)
    check("kepler newton8 residual e<=0.97", worst < 1e-14, "max %.3e at M=%.6f e=%.2f" % (worst, *worst_at))
    for (M, e) in [(0.01, 0.97), (1e-6, 0.97), (3.1, 0.97), (-0.5, 0.5), (2.0, 0.2)]:
        print("  E(%g, %g) = %.17g (bisection %.17g)" % (M, e, kepler_newton8(M, e), kepler_bisect(M, e)))

    # ---- calendar
    for (y, m, d, want) in [(2000, 1, 1, 2451544.5), (1987, 1, 27, 2446822.5), (2023, 11, 3, None),
                            (2020, 10, 13, None), (2009, 8, 11, None), (2025, 5, 6, None), (3001, 1, 1, None)]:
        jd = jd_gregorian(y, m, d)
        print("  JD %04d-%02d-%02d = %.1f" % (y, m, d, jd))
        if want is not None:
            check("calendar %04d-%02d-%02d" % (y, m, d), jd == want, "%.1f" % jd)

    # ---- oppositions: heliocentric longitudes equal
    for body, (y, m, d) in [("Jupiter", (2023, 11, 3)), ("Mars", (2020, 10, 13))]:
        ref = jd_gregorian(y, m, d)
        f = lambda t: wrap(lon(standish(body, t)[0]) - lon(standish("EMB", t)[0]))
        t = bisect_time(f, ref - 5, ref + 5)
        check("%s opposition %04d-%02d-%02d +-2 d" % (body, y, m, d), abs(t - ref) <= 2.0,
              "found JD %.4f, ref %.1f, diff %+.3f d" % (t, ref, t - ref))

    # ---- Saturn equinoxes: Sun direction perpendicular to the pole
    for (y, m, d) in [(2009, 8, 11), (2025, 5, 6)]:
        ref = jd_gregorian(y, m, d)
        def f(t):
            p = standish("Saturn", t)[0]
            n = pole_ecl("Saturn", t)
            return -sum(a * b for a, b in zip(p, n)) / math.sqrt(sum(a * a for a in p))
        t = bisect_time(f, ref - 30, ref + 30)
        check("Saturn equinox %04d-%02d-%02d +-10 d" % (y, m, d), abs(t - ref) <= 10.0,
              "found JD %.4f, ref %.1f, diff %+.3f d" % (t, ref, t - ref))

    # ---- obliquities
    # Jupiter is printed only: the fact sheet's 3.13 is not reproduced by the
    # WGCCRE pole against Table 2a's mean plane (3.112), so it is not a check.
    print("  Jupiter obliquity (info) %.5f deg" % angle_deg(pole_ecl("Jupiter", J2000), orbit_normal("Jupiter", J2000)))
    for body, orb, want in [("Earth", "EMB", 23.44), ("Saturn", "Saturn", 26.73)]:
        ob = angle_deg(pole_ecl(body, J2000), orbit_normal(orb, J2000))
        check("%s obliquity %.2f +-0.01" % (body, want), abs(ob - want) <= 0.01, "%.5f deg" % ob)

    # ---- mean-orbit flag
    j3001 = J2000 + 10 * 36525.0 + 365.25
    check("mean-orbit flag at 3000 AD + 1 yr", standish("Jupiter", j3001)[1] is True, "JD %.1f" % j3001)
    check("no flag at J2000", standish("Jupiter", J2000)[1] is False, "")

    # ---- galactic
    l0, b0 = radec_to_galactic(266.40499 * D2R, -28.93617 * D2R)   # Hipparcos GC direction
    print("  galactic centre -> l %.5f b %.5f (sanity: ~0, ~0)" % (math.degrees(l0) % 360, math.degrees(b0)))
    ra, dec = vec_to_radec(ecl_to_eq((0.0, 0.0, 1.0)))
    l, b = radec_to_galactic(ra, dec)
    print("  NEP ICRS ra %.8f dec %.8f" % (math.degrees(ra), math.degrees(dec)))
    print("  NEP galactic l %.8f b %.8f" % (math.degrees(l), math.degrees(b)))
    A = [(-0.0548755604, -0.8734370902, -0.4838350155), (0.4941094279, -0.4448296300, 0.7469822445),
         (-0.8676661490, -0.1980763734, 0.4559837762)]
    g = [sum(a * b for a, b in zip(r, ecl_to_eq((0.0, 0.0, 1.0)))) for r in A]
    lm, bm = math.degrees(math.atan2(g[1], g[0])) % 360, math.degrees(math.asin(g[2]))
    check("Hipparcos matrix agrees with the angle-built frame at the NEP (1e-6 deg)",
          abs(lm - math.degrees(l)) < 1e-6 and abs(bm - math.degrees(b)) < 1e-6, "matrix l %.8f b %.8f" % (lm, bm))
    check("NEP galactic vs published (96.38, 29.81) to 0.005 deg",
          abs(math.degrees(l) - 96.38) <= 0.005 and abs(math.degrees(b) - 29.81) <= 0.005, "")

    # ---- Moon
    mn, mx = 1e30, 0.0
    for k in range(0, 4000):
        jd = J2000 + k * 2.3
        p, _ = sat_pos(384400.0, 0.0554, 318.15, 135.27, 5.16, 125.08,
                       360.0 / 27.322, 360.0 / (5.997 * 365.25), -360.0 / (18.600 * 365.25),
                       270.0, 90.0 - math.degrees(EPS0), jd)
        r = math.sqrt(sum(c * c for c in p))
        mn, mx = min(mn, r), max(mx, r)
    check("Moon distance in 356375..406720 km", mn >= 356375 and mx <= 406720, "min %.1f max %.1f" % (mn, mx))

    pa = 360.0 / (360.0 / (5.997 * 365.25) - 360.0 / (18.600 * 365.25))
    check("Moon apsidal period 3232.6 +-5 d", abs(pa - 3232.6) <= 5.0, "%.2f d" % pa)

    # ---- Io: P (1.762732 d) is the anomalistic period, its apse regresses
    #      every 1.333 yr (forced by the Laplace resonance), node fixed.
    mdot = 360.0 / 1.762732
    wdot = -360.0 / (1.333 * 365.25)
    ldot = mdot + wdot
    P = 360.0 / ldot
    check("Io sidereal period 1.769137786 +-1e-4 d", abs(P - 1.769137786) <= 1e-4, "%.7f d" % P)
    print("  (prograde-apse reading would give %.5f d)" % (360.0 / (mdot - wdot)))

    if "--check" in sys.argv and FAILS:
        print("FAILED: " + ", ".join(FAILS))
        sys.exit(1)


if __name__ == "__main__":
    main()
