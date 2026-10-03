#!/usr/bin/env python3
"""Independent reference values for sunholo/celestial 0.1.0: part 1
(kepler, ephemeris, frames) and part 2 (lighttime, gravity, reflect, rings;
its sources and independent methods are listed above part2() below); and
0.2.0's Earth-Moon barycentre split (sources above earth_moon() below).
Standard library only; no network (the Horizons values were fetched once
and are copied in with their query).

Every check in the *_test.ail files is a published date or constant, or a
closed-form identity. This script is the second-language oracle: it
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

    part2()
    earth_moon()

    if "--check" in sys.argv and FAILS:
        print("FAILED: " + ", ".join(FAILS))
        sys.exit(1)


# ====================================================================== part 2
# lighttime, gravity, reflect, rings. Independent paths:
#   * light time: bisection on c s = |x_obs(t) - x_src(t - s)| (the package
#     iterates a fixed point 4 times); positions from this file's 50-digit
#     Standish elements; checked against JPL Horizons.
#   * gravity: SI units throughout (m, m^3/s^2), not km and AU.
#   * reflect: disc integrals by brute force over a 2-D grid of the visible
#     disc in the observer's frame (normal, cos i, cos e per cell), not the
#     separable photometric-coordinate integral the package uses; Bond albedo
#     by a 2-D grid over the sphere.
#   * rings: the single-scattering layer integrated numerically through its
#     depth (sources at optical depth t, attenuated in and out), not the
#     closed forms.
#
# Published inputs for part 2 (cited at each use):
#   JPL Horizons (DE441), observer 500@399, quantities 9,19,20,21 (fetched
#     2026-10-03): https://ssd.jpl.nasa.gov/api/horizons.api?format=text&
#     COMMAND='599'&EPHEM_TYPE='OBSERVER'&CENTER='500@399'&
#     START_TIME='2023-11-03'&STOP_TIME='2023-11-04'&STEP_SIZE='1d'&
#     QUANTITIES='9,19,20,21'   (and COMMAND='699', 2023-08-27)
#     Jupiter 2023-11-03 00:00 UT: APmag -2.910, r 4.974517268850,
#       delta 3.98256409999321 au, 1-way LT 33.12197563 min, phase 0.2857 deg
#     Saturn 2023-08-27 00:00 UT: delta 8.76304564804493 au,
#       1-way LT 72.88002832 min
#   IAU 2015 Resolution B3 nominal GM and radii (Prsa et al. 2016, AJ 152, 41)
#   NASA NSSDC planetary fact sheets: surface gravity Earth 9.80, Jupiter
#     24.79 m/s^2
#   Mallama, Krobusek & Pavlov 2017, Icarus 282, 19: Jupiter p_V 0.538
#   Mallama & Hilton 2018, Astron. Comput. 25, 10: Jupiter V(1,0) -9.395
#   The Sun: V -26.74; visual zero point V -13.98 at 1 lux
#   Russell 1916, ApJ 43, 173: Lambert phase integral q = 3/2
#   NASA NSSDCA Saturnian Rings Fact Sheet (updated 2022-04-19): ring radii
#     and optical depths; Colwell et al. 2010, Icarus 206, 646 (Cassini
#     UVIS): B ring core tau > 5

C_KMS = 299792.458
C_AUD = C_KMS * 86400.0 / AU_KM


def light_time_bisect(src, obs, t):
    lo, hi = 0.0, 1.0                  # days; < 1 d for anything inside 170 au
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if C_AUD * mid - math.dist(obs, src(t - mid)) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def light_time_fixed4(src, obs, t):
    s = 0.0
    for _ in range(4):
        s = math.dist(obs, src(t - s)) / C_AUD
    return s


def accel_si(gm_si, r_m):
    return gm_si / (r_m * r_m)


def lambert_phase(a):
    return (math.sin(a) + (math.pi - a) * math.cos(a)) / math.pi


def disc_brightness(alpha, k, rho, n=600):
    """Intensity (R = 1, E = 1) of a Minnaert sphere at phase alpha, by a grid
    over the visible disc in the observer's frame: view along +x, the Sun at
    (cos a, sin a, 0)."""
    s = (math.cos(alpha), math.sin(alpha), 0.0)
    h = 2.0 / n
    tot = 0.0
    for i in range(n):
        y = -1.0 + (i + 0.5) * h
        for j in range(n):
            z = -1.0 + (j + 0.5) * h
            rr = y * y + z * z
            if rr >= 1.0:
                continue
            x = math.sqrt(1.0 - rr)                  # cos e
            ci = x * s[0] + y * s[1]
            if ci <= 0.0:
                continue
            L = rho * ci ** k * x ** (k - 1.0) / math.pi
            tot += L * h * h                         # projected area element
    return tot


def sphere_bond(k, rho, n=400):
    """Reflected power over incident (E pi R^2) for a Minnaert sphere: grid
    over the lit hemisphere in mu0 and, per patch, the plane albedo by a
    1-D grid over emergent mu."""
    def plane(mu0, m=2000):
        return sum(2.0 * math.pi * (rho * mu0 ** k * ((j + 0.5) / m) ** (k - 1.0) / math.pi) * ((j + 0.5) / m) / m
                   for j in range(m)) / mu0
    return sum(2.0 * plane((i + 0.5) / n) * ((i + 0.5) / n) / n for i in range(n))


def ring_layer(w0, P, tau, mu0, mu, lit, n=20000):
    """I/F of a single-scattering slab: sources at depth t lit by
    e^(-t/mu0), seen through e^(-t/mu) (lit face) or e^(-(tau-t)/mu) (unlit),
    I/F = w0 P / (4 mu) int_0^tau ... dt, midpoint rule (relative error
    ~ (tau/n)^2 (1/mu + 1/mu0)^2 / 24, < 1e-7 for the cases below)."""
    h = tau / n
    tot = 0.0
    for i in range(n):
        t = (i + 0.5) * h
        out = t if lit else tau - t
        tot += math.exp(-t / mu0) * math.exp(-out / mu) * h
    return w0 * P / (4.0 * mu) * tot


def part2():
    # ---- light time
    sec = 86400.0
    check("c: 1 au of light in 499.004784 s", abs(sec / C_AUD - 499.00478383615643) < 1e-9, "%.9f s" % (sec / C_AUD))
    kg = K_GAUSS
    n = kg / math.sqrt(5.2 ** 3)
    circ = lambda t: (5.2 * math.cos(n * t), 5.2 * math.sin(n * t), 0.0)
    s = light_time_bisect(circ, (1.0, 0.0, 0.0), 0.0)
    disp = math.dist(circ(-s), circ(0.0)) * AU_KM
    check("idealised Jupiter (r 5.20, delta 4.20): lag ~2094 s (design), package value 4.2 au / c",
          abs(s * sec - 2094.0) < 3.0 and abs(s * sec - 4.2 * 499.00478383615643) < 0.01,
          "%.4f s; fixed-point x4 %.4f s" % (s * sec, light_time_fixed4(circ, (1.0, 0.0, 0.0), 0.0) * sec))
    check("idealised Jupiter: drawn 27,400 km (0.38 R_J) behind", abs(disp - 27400.0) < 100 and abs(disp / 71492 - 0.38) < 0.005,
          "%.1f km = %.4f R_J" % (disp, disp / 71492.0))
    for body, (y, m, d), lt_min, tol in [("Jupiter", (2023, 11, 3), 33.12197563, 3.0),
                                         ("Saturn", (2023, 8, 27), 72.88002832, 6.0)]:
        t = jd_gregorian(y, m, d)
        src = lambda tt, b=body: standish(b, tt)[0]
        obs = standish("EMB", t)[0]
        s = light_time_bisect(src, obs, t) * sec
        s4 = light_time_fixed4(src, obs, t) * sec
        check("%s %04d-%02d-%02d light time vs Horizons %.4f s (+-%g s)" % (body, y, m, d, lt_min * 60, tol),
              abs(s - lt_min * 60) < tol and abs(s4 - s) < 1e-6, "bisection %.4f s, fixed-point x4 %.4f s" % (s, s4))
    # contraction at v/c = 0.04: error exactly (v/c)^4
    v = 6.9
    fast = lambda t: (10.0 + v * (t - 50.0), 0.0, 0.0)
    want = 10.0 / (C_AUD + v)
    err = abs(light_time_fixed4(fast, (0.0, 0.0, 0.0), 50.0) - want) / want
    check("4 fixed-point steps at v/c 0.04 leave (v/c)^4 = 2.5e-6", 2e-6 < err < 3e-6, "%.3e (pred %.3e)" % (err, (v / C_AUD) ** 4))

    # ---- gravity (SI)
    GM_E, GM_J, R_E, R_J = 3.986004e14, 1.2668653e17, 6.3781e6, 7.1492e7
    g1 = accel_si(GM_E, R_E + 5.0e7)
    g2 = accel_si(GM_J, 1.5 * R_J)
    check("g at 50,000 km above Earth ~0.1254 m/s^2", abs(g1 - 0.1254) < 1e-4, "%.6f m/s^2" % g1)
    check("g at 1.5 R_J ~11.0 m/s^2", abs(g2 - 11.0) < 0.05, "%.4f m/s^2" % g2)
    check("surface gravity Earth 9.798 / Jupiter 24.79 (NSSDC)",
          abs(accel_si(GM_E, R_E) - 9.798) < 1e-3 and abs(accel_si(GM_J, R_J) - 24.79) < 0.01,
          "%.4f / %.4f m/s^2" % (accel_si(GM_E, R_E), accel_si(GM_J, R_J)))
    tide = 2 * 1.3271244e20 * 5.63781e7 / (AU_KM * 1e3) ** 3
    print("  solar tide at 56,378 km from Earth (1 au): <= %.3e m/s^2; solar pull %.4e m/s^2" % (tide, accel_si(1.3271244e20, AU_KM * 1e3)))
    print("  design hold example: m_eff |g| c at 50,000 km = %.3e W/kg" % (g1 * C_KMS * 1e3))

    # ---- reflect
    e1 = 10 ** (-0.4 * (-26.74 + 13.98))
    check("E_sun(1 au) from V -26.74 = 1.2706e5 lux (design wrote 1.261e5)", abs(e1 - 127057.41) < 0.01, "%.4f lux" % e1)
    check("Lambert Phi(0)=1, Phi(pi/2)=1/pi, Phi(pi)=0",
          lambert_phase(0) == 1.0 and abs(lambert_phase(math.pi / 2) - 1 / math.pi) < 1e-15 and abs(lambert_phase(math.pi)) < 1e-15, "")
    nq = 20000
    q = sum(2 * lambert_phase((i + 0.5) * math.pi / nq) * math.sin((i + 0.5) * math.pi / nq) * math.pi / nq for i in range(nq))
    check("Lambert phase integral q = 3/2 (Russell 1916)", abs(q - 1.5) < 1e-6, "%.8f" % q)
    for k in (1.0, 0.9, 1.3):
        rho = 0.4 * (2 * k + 1) / 2
        I0 = disc_brightness(0.0, k, rho)
        check("2-D disc grid: Minnaert k %.1f opposition brightness = p (rho = p(2k+1)/2)" % k, abs(I0 - 0.4) < 2e-3, "%.5f vs 0.4" % I0)
    for k in (1.0, 1.2):
        I0 = disc_brightness(0.0, k, 1.0)
        for a_deg in (30.0, 90.0, 140.0):
            a = math.radians(a_deg)
            ph = disc_brightness(a, k, 1.0) / I0
            # separable 1-D form (the package's): int (cos(L-a) cos L)^k dL / same at 0
            m = 20000
            def lk(al):
                lo = al - math.pi / 2
                hh = (math.pi / 2 - lo) / m
                return sum(max(math.cos(lo + (j + 0.5) * hh - al) * math.cos(lo + (j + 0.5) * hh), 0.0) ** k * hh for j in range(m))
            sep = lk(a) / lk(0.0)
            ref = lambert_phase(a) if k == 1.0 else sep
            check("Minnaert k %.1f phase at %g deg: 2-D disc grid vs separable form" % (k, a_deg),
                  abs(ph - sep) < 3e-3 and abs(sep - ref) < 1e-6, "grid %.5f, separable %.6f, Lambert %.6f" % (ph, sep, lambert_phase(a)))
    for k in (1.0, 1.25):
        b = sphere_bond(k, 0.6)
        check("Bond albedo of the Minnaert sphere = 4 rho/(k+1)^2 (k %.2f)" % k, abs(b - 2.4 / (k + 1) ** 2) < 2e-3, "%.5f vs %.5f" % (b, 2.4 / (k + 1) ** 2))

    def jup_v(r, d, a_deg):
        R = 71492.0
        E = e1 * 0.538 * (R / (d * AU_KM)) ** 2 * lambert_phase(math.radians(a_deg)) / r ** 2
        return -26.74 - 2.5 * math.log10(E / e1)
    v = jup_v(5.20, 4.20, 0.0)
    vmh = 5 * math.log10(5.20 * 4.20) - 9.395
    check("Jupiter at opposition r 5.20 delta 4.20 p 0.538: V -2.77 (Mallama-Hilton %.3f)" % vmh,
          abs(v + 2.77) < 0.01 and abs(v - vmh) < 0.1, "%.4f" % v)
    vh = jup_v(4.974517268850, 3.98256409999321, 0.2857)
    check("Jupiter 2023-11-03: V within 0.1 of Horizons -2.910", abs(vh + 2.910) < 0.1, "%.4f" % vh)

    # ---- rings
    w0, P = 0.5, 1.3
    for tau, mu0, mu in [(0.8, 0.3, 0.5), (0.1, 0.45, 0.7), (2.0, 0.2, 0.9)]:
        num = ring_layer(w0, P, tau, mu0, mu, True)
        cf = w0 * P * mu0 / (4 * (mu + mu0)) * (1 - math.exp(-tau * (1 / mu + 1 / mu0)))
        check("ring lit face: depth integral = closed form (tau %g)" % tau, abs(num - cf) < 1e-7 * cf, "%.10f vs %.10f" % (num, cf))
        num = ring_layer(w0, P, tau, mu0, mu, False)
        cf = w0 * P * mu0 / (4 * (mu - mu0)) * (math.exp(-tau / mu) - math.exp(-tau / mu0))
        check("ring unlit face: depth integral = closed form (tau %g)" % tau, abs(num - cf) < 1e-7 * cf, "%.10f vs %.10f" % (num, cf))
    num = ring_layer(w0, P, 0.7, 0.45, 0.45, False)
    lim = w0 * P * 0.7 * math.exp(-0.7 / 0.45) / (4 * 0.45)
    check("ring unlit face at mu = mu0: depth integral = w0 P tau e^(-tau/mu0)/(4 mu0)", abs(num - lim) < 1e-8 * lim, "%.12f vs %.12f" % (num, lim))
    thick = ring_layer(w0, P, 60.0, 0.45, 0.7, True, n=200000)
    ls = w0 * P / 4 * 0.45 / (0.45 + 0.7)
    check("ring lit face tau 60 -> Lommel-Seeliger", abs(thick - ls) < 1e-6 * ls, "%.10f vs %.10f" % (thick, ls))
    mu_s = math.sin(math.radians(26.73))
    check("Saturn solstice: A ring (tau 0.4-1.0) passes 11-41 %, B core (tau > 5) < 0.002 %",
          0.10 < math.exp(-1.0 / mu_s) and math.exp(-0.4 / mu_s) < 0.42 and math.exp(-5.0 / mu_s) < 2e-5,
          "%.3f-%.3f, %.2e" % (math.exp(-1.0 / mu_s), math.exp(-0.4 / mu_s), math.exp(-5.0 / mu_s)))
    # ring-plane crossing by marching the ray (not the closed form)
    B, phi = math.radians(26.73), math.radians(-20.0)
    p = (60268.0 * math.cos(phi), 0.0, 60268.0 * math.sin(phi))
    sd = (math.cos(B), 0.0, math.sin(B))
    lo, hi = 0.0, 1e6
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if p[2] + mid * sd[2] < 0:
            lo = mid
        else:
            hi = mid
    r = math.hypot(p[0] + lo * sd[0], p[1] + lo * sd[1])
    check("Saturn solstice: latitude -20 deg sees the Sun through r = 97,564 km (B ring)", abs(r - 97564.0) < 1.0 and 91975 <= r < 117507, "%.3f km" % r)


# ====================================================================== 0.2.0
# The Earth-Moon barycentre split: Earth = EMB - mu r_geo,
# Moon = EMB + (1 - mu) r_geo, mu = 1 / (1 + EMRAT).
#
# Published inputs:
#   JPL DE440/DE441 EMRAT = GM_Earth / GM_Moon = 81.3005682214972154
#     (Park, Folkner, Williams & Boggs 2021, AJ 161, 105; the DE440 header)
#   JPL Horizons (DE441) state vectors, fetched 2026-10-03, no network here:
#     https://ssd.jpl.nasa.gov/api/horizons.api?format=text&EPHEM_TYPE='VECTORS'&
#     COMMAND='<c>'&CENTER='<o>'&TLIST='2451545.0','2460251.5','2461041.5'&
#     TLIST_TYPE='JD'&TIME_TYPE='TDB'&REF_PLANE='ECLIPTIC'&REF_SYSTEM='ICRF'&
#     OUT_UNITS='AU-D'&VEC_TABLE='2'
#     with (<c>, <o>) = ('399','500@3') Earth from the EMB,
#     ('301','500@399') Moon from the Earth, ('3','500@10') EMB from the Sun,
#     ('399','500@10') Earth from the Sun. Ecliptic J2000, AU, AU/day, TDB.
#
# Independent paths: the split in 50-digit Decimal (the package works in
# float64); the Moon from this file's sat_pos (bisection Kepler, angle-built
# plane rotation) and the EMB from its Decimal Standish elements.
EMRAT = Decimal("81.3005682214972154")
MU_D = 1 / (1 + EMRAT)

# jd: Earth-from-EMB (pos, vel), Moon-from-Earth, EMB-from-Sun, Earth-from-Sun
HORIZONS_EM = {
    2451545.0: (
        (("2.368491119575935E-05", "2.233430558007885E-05", "-2.946006074095761E-06"),
         ("-4.516013502075859E-06", "5.129716424248584E-06", "8.074718811302325E-08")),
        (("-1.949281649686695E-03", "-1.838126040073046E-03", "2.424579738820632E-04"),
         ("3.716704773167968E-04", "-4.221785765308054E-04", "-6.645539463989926E-06")),
        (("-1.771587841839055E-01", "9.672193524609504E-01", "-1.139275508446145E-06"),
         ("-1.720310905522688E-02", "-3.163911860749114E-03", "2.424167134816753E-08")),
        (("-1.771350992727098E-01", "9.672416867665306E-01", "-4.085281582511366E-06"),
         ("-1.720762506872895E-02", "-3.158782144324866E-03", "1.049888594613343E-07"))),
    2460251.5: (
        (("7.521145924737144E-06", "-3.105875615656290E-05", "-2.890284150579967E-06"),
         ("6.840320504037754E-06", "1.287689518855818E-06", "-1.529613449632012E-07")),
        (("-6.189945832826651E-04", "2.556153279938051E-03", "2.378720279143189E-04"),
         ("-5.629622642994656E-04", "-1.059775790947002E-04", "1.258880560639592E-05")),
        (("7.603704946134947E-01", "6.374383439575997E-01", "-4.026850683718436E-05"),
         ("-1.133301968054092E-02", "1.311972952785614E-02", "-6.519930732839620E-07")),
        (("7.603780157594194E-01", "6.374072852014431E-01", "-4.315879098775194E-05"),
         ("-1.132617936003689E-02", "1.312101721737500E-02", "-8.049544182482179E-07"))),
    2461041.5: (
        (("-1.172237227825803E-05", "-2.675406958804738E-05", "-2.579028812853566E-06"),
         ("7.047824369809083E-06", "-2.953442517052326E-06", "-3.919449783556250E-08")),
        (("9.647578994045626E-04", "2.201875129333777E-03", "2.122555367574619E-04"),
         ("-5.800399503606030E-04", "2.430699973629355E-04", "3.225729443022998E-06")),
        (("-1.742697585483051E-01", "9.677856743241913E-01", "-5.686608136245510E-05"),
         ("-1.721159519305110E-02", "-3.113653580027250E-03", "2.763727760594844E-07")),
        (("-1.742814809205833E-01", "9.677589202546031E-01", "-5.944511017526243E-05"),
         ("-1.720454736868129E-02", "-3.116607022544302E-03", "2.371782782240443E-07"))),
}


def dvec(t):
    return [Decimal(x) for x in t]


def dnorm(v):
    return math.sqrt(sum(float(c) ** 2 for c in v))


def moon_geo_km(jd):
    p, _ = sat_pos(384400.0, 0.0554, 318.15, 135.27, 5.16, 125.08,
                   360.0 / 27.322, 360.0 / (5.997 * 365.25), -360.0 / (18.600 * 365.25),
                   270.0, 90.0 - math.degrees(EPS0), jd)
    return p


def earth_moon():
    mu = float(MU_D)
    print("  mu = 1/(1 + EMRAT) = %s" % format(MU_D, ".20f"))
    for jd, (e_emb, m_geo, emb, earth) in sorted(HORIZONS_EM.items()):
        for k, what in ((0, "pos"), (1, "vel")):
            ee, mg, eb, ea = dvec(e_emb[k]), dvec(m_geo[k]), dvec(emb[k]), dvec(earth[k])
            # DE441's own ratio Earth-from-EMB / Moon-from-Earth is -mu
            ratio = [-a / b for a, b in zip(ee, mg)]
            worst = max(abs(r / MU_D - 1) for r in ratio)
            check("JD %.1f %s: DE441 Earth-from-EMB = -mu Moon-from-Earth (1e-12)" % (jd, what),
                  worst < Decimal("1e-12"), "ratio %s, rel %.1e" % (format(ratio[0], ".16f"), worst))
            # split Horizons' EMB with Horizons' Moon -> Horizons' Earth and Earth + Moon
            es = [b - MU_D * m for b, m in zip(eb, mg)]
            ms = [b + (1 - MU_D) * m for b, m in zip(eb, mg)]
            de = dnorm([a - b for a, b in zip(es, ea)])
            dm = dnorm([a - (b + m) for a, b, m in zip(ms, ea, mg)])
            tol = 1e-13 if k == 0 else 1e-15
            check("JD %.1f %s: split of Horizons EMB + Moon = Horizons Earth, Earth + Moon (%g)" % (jd, what, tol),
                  de <= tol and dm <= tol, "earth %.2e moon %.2e" % (de, dm))
            # identities, exact in Decimal
            rel = [a - b for a, b in zip(ms, es)]
            bar = [(1 - MU_D) * a + MU_D * b for a, b in zip(es, ms)]
            check("JD %.1f %s: moon - earth = r_geo and (1-mu) earth + mu moon = EMB (1e-40)" % (jd, what),
                  max(abs(a - b) for a, b in zip(rel, mg)) < Decimal("1e-40")
                  and max(abs(a - b) for a, b in zip(bar, eb)) < Decimal("1e-40"), "")
        # mean-element path: -mu r_geo(mean elements) vs Horizons Earth-from-EMB
        p = moon_geo_km(jd)
        off = [-mu * c for c in p]
        h = [float(c) * AU_KM for c in dvec(e_emb[0])]
        err = math.dist(off, h)
        check("JD %.1f: mean-element Earth-from-EMB within 200 km of Horizons" % jd, err < 200.0,
              "package-style %.1f km, Horizons %.1f km, error %.1f km" % (math.hypot(*off), math.hypot(*h), err))
        # the Earth's heliocentric error, Standish EMB split vs Horizons Earth:
        # informational (dominated by Standish's own EMB error)
        sb = standish("EMB", jd)[0]
        ex = [b * AU_KM + o for b, o in zip(sb, off)]
        hx = [float(c) * AU_KM for c in dvec(earth[0])]
        print("  JD %.1f Earth (Standish EMB split) vs Horizons Earth: %.0f km; EMB unsplit vs Horizons Earth: %.0f km (info)"
              % (jd, math.dist(ex, hx), math.dist([b * AU_KM for b in sb], hx)))


if __name__ == "__main__":
    main()
