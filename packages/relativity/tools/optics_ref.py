#!/usr/bin/env python3
"""Independent reference values for sunholo/relativity 0.6.x
optics.apparentDisc and medium.hoverPower. Standard library only.

Every expected number in optics_disc_test.ail comes from here, never from the
AILANG under test. The method is deliberately different from the package's:

  * the package aberrates the two meridian edge points theta -/+ alpha with
    the half-angle law tan(theta'/2) = e^-phi tan(theta/2) and takes their
    mean and half-difference;
  * this oracle builds the rest-frame circle in 3D (720 points plus a
    golden-section search), Lorentz-transforms every photon direction with
    the 4-vector law cos theta' = (cos theta + beta) / (1 + beta cos theta)
    (transverse part divided by gamma (1 + beta cos theta)), finds the
    nearest and farthest image points from the axis, and checks that every
    image point lies on the circle so defined (the outline is a circle,
    RS-Q5) to 1e-30 rad.

All arithmetic is 60-digit Decimal with series trig, so the float64 package
is checked against the true value. Values are printed in degrees.

Usage:
  python3 tools/optics_ref.py           # print every check row
  python3 tools/optics_ref.py --check   # also assert the M5 design's
                                        # printed oracle digits; exit 1 on mismatch
"""
import sys
from decimal import Decimal as D, getcontext

getcontext().prec = 60
ONE = D(1)
TWO = D(2)


def pi():
    # Machin: pi = 16 atan(1/5) - 4 atan(1/239)
    return 16 * atan_small(ONE / 5) - 4 * atan_small(ONE / 239)


def atan_small(x):
    # Taylor series, |x| <= 0.5
    getcontext().prec += 5
    s, t, k, x2 = D(0), x, 1, x * x
    while True:
        term = t / k
        if abs(term) < D(10) ** -(getcontext().prec + 2):
            break
        s += term
        t *= -x2
        k += 2
    getcontext().prec -= 5
    return +s


def atan(x):
    if x < 0:
        return -atan(-x)
    if x > 1:
        return PI / 2 - atan(ONE / x)
    # halve the argument twice: atan x = 2 atan(x / (1 + sqrt(1 + x^2)))
    y = x / (1 + (1 + x * x).sqrt())
    y = y / (1 + (1 + y * y).sqrt())
    return 4 * atan_small(y)


def acos(c):
    # acos c = 2 atan( sqrt(1 - c) / sqrt(1 + c) ), exact to the precision
    if c <= -1:
        return PI
    return 2 * atan((1 - c).sqrt() / (1 + c).sqrt())


def sin(x):
    x = x % (2 * PI)
    getcontext().prec += 5
    s, t, k = D(0), x, 1
    while abs(t) > D(10) ** -(getcontext().prec + 2):
        s += t
        t *= -x * x / ((k + 1) * (k + 2))
        k += 2
    getcontext().prec -= 5
    return +s


def cos(x):
    return sin(x + PI / 2)


PI = pi()
DEG = PI / 180


def lorentz(n, beta):
    """Apparent direction (toward the source) for an observer moving along +z."""
    gamma = ONE / (1 - beta * beta).sqrt()
    den = gamma * (1 + beta * n[2])
    return (n[0] / den, n[1] / den, (n[2] + beta) / (1 + beta * n[2]))


def circle_point(theta, alpha, psi):
    c0 = (sin(theta), D(0), cos(theta))
    e1 = (cos(theta), D(0), -sin(theta))
    e2 = (D(0), ONE, D(0))
    ca, sa, cp, sp = cos(alpha), sin(alpha), cos(psi), sin(psi)
    return tuple(ca * c0[i] + sa * (cp * e1[i] + sp * e2[i]) for i in range(3))


def image_z(theta, alpha, beta, psi):
    return lorentz(circle_point(theta, alpha, psi), beta)[2]


def golden(f, a, b, sign):
    """Extremum of sign*f on [a, b] (maximise)."""
    g = (D(5).sqrt() - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = sign * f(c), sign * f(d)
    for _ in range(300):
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = sign * f(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = sign * f(d)
    return (a + b) / 2


def ang(u, v):
    dot = sum(u[i] * v[i] for i in range(3))
    nu = sum(x * x for x in u).sqrt()
    nv = sum(x * x for x in v).sqrt()
    return acos(dot / (nu * nv))


def disc(theta_deg, alpha_deg, beta):
    theta, alpha = D(theta_deg) * DEG, D(alpha_deg) * DEG
    f = lambda psi: image_z(theta, alpha, beta, psi)
    # coarse scan for the extremes, then golden section around each
    n = 720
    zs = [(f(2 * PI * k / n), k) for k in range(n)]
    kmax = max(zs)[1]
    kmin = min(zs)[1]
    step = 2 * PI / n
    pmax = golden(f, step * (kmax - 1), step * (kmax + 1), 1)
    pmin = golden(f, step * (kmin - 1), step * (kmin + 1), -1)
    tnear, tfar = acos(f(pmax)), acos(f(pmin))
    centre, radius = (tnear + tfar) / 2, (tfar - tnear) / 2
    # circularity: every image point is radius from the centre direction
    cdir = (sin(centre), D(0), cos(centre))
    dev = max(abs(ang(lorentz(circle_point(theta, alpha, 2 * PI * k / 90), beta), cdir) - radius)
              for k in range(90))
    aberrated = acos((cos(theta) + beta) / (1 + beta * cos(theta)))
    return centre / DEG, radius / DEG, aberrated / DEG, dev


def hover_rows():
    c = D(299792458)
    gm_sun = D("1.32712440018e20")         # IAU nominal GM_sun, m^3/s^2
    m = D("4.297e6")                        # HB-10
    gm = gm_sun * m
    rs = 2 * gm / (c * c)                   # HB-82
    r = 3 * rs
    a = gm / (r * r * (1 - rs / r).sqrt())  # HB-88
    return rs, a, a * c                     # HB-90 (m_eff = 1 kg)


GEOMETRIES = [
    # (label, theta deg, alpha deg, beta, design printed (centre, radius, D at centre))
    ("RS-24/25 beta 0.9 theta 90 alpha 5", 90, 5, D("0.9"), ("25.928", "2.184", "2.2871")),
    ("RS-26/27 beta 0.99 theta 90 alpha 5", 90, 5, D("0.99"), ("8.140", "0.707", "7.0623")),
    ("RS-28/29 beta 0.9 theta 150 alpha 5", 150, 5, D("0.9"), ("82.021", "9.940", "0.4981")),
    ("cap 1-beta 1e-6 theta 90 alpha 5", 90, 5, 1 - D("1e-6"), None),
    ("beta 0.5 theta 30 alpha 10", 30, 10, D("0.5"), None),
]


def main():
    check = "--check" in sys.argv
    ok = True
    for label, th, al, beta, want in GEOMETRIES:
        c, r, ab, dev = disc(th, al, beta)
        print(f"{label}: centre {c:.17e} deg  radius {r:.17e} deg  "
              f"aberrated centre {ab:.17e} deg  circle dev {dev:.1e} rad")
        gamma = ONE / (1 - beta * beta).sqrt()
        dc = ONE / (gamma * (1 - beta * cos(c * DEG)))
        print(f"  D at the apparent centre 1/(gamma (1 - beta cos c')) = {dc:.17e}")
        if dev > D("1e-30"):
            ok = False
            print("  FAIL: outline is not a circle to 1e-30")
        if check and want is not None:
            if f"{c:.3f}" != want[0] or f"{r:.3f}" != want[1] or f"{dc:.4f}" != want[2]:
                ok = False
                print(f"  FAIL: design printed {want}")
    # Discs centred on the axis: the image is a cap about the same pole, of
    # radius theta'(alpha) ahead and pi - theta'(pi - alpha) astern.
    for label, th, beta in [("on-axis ahead beta 0.9 alpha 5", 0, D("0.9")),
                            ("on-axis astern beta 0.9 alpha 5", 180, D("0.9"))]:
        al = D(5) * DEG
        edge = al if th == 0 else PI - al
        t = acos((cos(edge) + beta) / (1 + beta * cos(edge)))
        r = t if th == 0 else PI - t
        print(f"{label}: centre {th} deg  radius {r / DEG:.17e} deg")
    rs, a, p = hover_rows()
    print(f"HB-82 r_s {rs:.6e} m  HB-88 a_hover(3 r_s) {a:.17e} m/s^2  HB-90 P/m_eff {p:.17e} W/kg")
    print(f"hoverPower(1, 0.1254) = 0.1254 c = {D('0.1254') * D(299792458)} W")
    if check:
        if f"{a:.2e}" != "4.82e+5" or f"{p:.2e}" != "1.44e+14":
            ok = False
            print("  FAIL: HB-88 / HB-90 printed digits")
    if not ok:
        sys.exit(1)
    if check:
        print("check: OK")


if __name__ == "__main__":
    main()
