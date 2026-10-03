#!/usr/bin/env python3
"""Independent reference values for sunholo/relativity 0.6.0
(medium.glowEmittanceAt, the angular profile of the wall glow). Standard
library only.

Every expected number for glowEmittanceAt in medium_test.ail comes from here,
never from the AILANG under test.

Model (stapledons-design physics/higgs-bubble.md section 6, D-11, D-15): the
ISM is a proton beam along the travel direction with kinetic-energy flux
K = n gamma beta (gamma - 1) m_p c^3 on a face-on surface (ship frame). A
wall element whose outward normal is at angle theta from the travel direction
intercepts K max(0, cos theta) per unit wall area; a fraction eps of it
becomes light and a fraction f_in of that shines inward:

    glowEmittanceAt(n, phi, eps, fIn, cos theta) = eps fIn K max(0, cos theta)

Its mean over the sphere is eps fIn K / 4 = glowInwardFlux, because the
sphere mean of max(0, cos theta) is 1/4. The oracle checks that 1/4 by an
independent quadrature in theta (sin theta d theta, Simpson, 60 digits), not
in cos theta, and checks the mean against the projected-area argument:
power intercepted K pi R^2, spread over 4 pi R^2.

Each value is computed in 60-digit Decimal from the exact float64 inputs
(phi and cos theta as the package receives them), with gamma beta = sinh phi
and gamma - 1 = 2 sinh^2(phi / 2) evaluated by Decimal exp.

Usage:
  python3 tools/glow_ref.py          # print every check row
  python3 tools/glow_ref.py --check  # also assert the M4 design's printed
                                     # digits and HB-45, HB-61; exit 1 on
                                     # mismatch
"""
import math
import sys
from decimal import Decimal, getcontext

getcontext().prec = 60
D = Decimal

C_SI = D(299792458)                       # m/s, exact
M_P = D(1.67262192369e-27)                # kg, the package's float64 constant
N_ISM = D(100000)                         # m^-3 (0.1 cm^-3, HB-3)
EPS = D(1e-9)                             # D-15 default (float64 value)
F_IN = D(0.5)                             # M2 scenario default


def dsinh(x):
    e = x.exp()
    return (e - 1 / e) / 2


def kinetic_flux(n, phi):
    """K = n sinh(phi) 2 sinh^2(phi/2) m_p c^3 (W/m^2), Decimal."""
    phi = D(phi)
    h = dsinh(phi / 2)
    return n * dsinh(phi) * 2 * h * h * M_P * C_SI ** 3


def emittance(n, phi, eps, fin, cos_t):
    """Reference glowEmittanceAt: eps fIn K max(0, min(1, cos))."""
    c = max(D(0), min(D(1), D(cos_t)))
    return eps * fin * kinetic_flux(n, phi) * c


def mean_inward(n, phi, eps, fin):
    """glowInwardFlux by the projected-area argument: eps fIn K pi R^2 / (4 pi R^2)."""
    return eps * fin * kinetic_flux(n, phi) * D(1) / D(4)


def dcos(x):
    """Decimal cos by Taylor series (|x| <= pi)."""
    getcontext().prec += 5
    s, t, k = D(0), D(1), 0
    while True:
        s += t
        k += 2
        t = -t * x * x / (k * (k - 1))
        if abs(t) < D(10) ** -(getcontext().prec):
            break
    getcontext().prec -= 5
    return +s


def dsin(x):
    return dcos(DPI / 2 - x)


def dpi():
    """pi by Machin's formula."""
    def arctan_inv(m):
        x = D(1) / m
        s, t, k, x2 = D(0), x, 1, x * x
        while abs(t) > D(10) ** -65:
            s += t / k
            t = -t * x2
            k += 2
        return s
    return 16 * arctan_inv(5) - 4 * arctan_inv(239)


DPI = dpi()


def sphere_mean_quadrature(m=2000):
    """(1/2) int_0^pi max(0, cos th) sin th d th, composite Simpson in theta.

    The integrand is cos th sin th on [0, pi/2] (zero beyond), so integrate
    there; Simpson's error is O(h^4), 8.5e-15 at m = 2000 panels, far below the
    1e-12 test tolerance.
    """
    a, b = D(0), DPI / 2
    h = (b - a) / m
    s = D(0)
    for i in range(m + 1):
        th = a + i * h
        f = dcos(th) * dsin(th)
        w = 1 if i in (0, m) else (4 if i % 2 else 2)
        s += w * f
    return s * h / 3 / 2


PHI099 = math.atanh(0.99)
PHICAP = 0.5 * (math.log(2.0 - 1.0e-6) - math.log(1.0e-6))  # rapidityOfOneMinusBeta(1e-6)
PHI05 = math.atanh(0.5)

ANGLES = [0.0, 45.0, 80.0, 90.0, 120.0]


def cos_deg(deg):
    """float64 cos theta as a caller passes it (math.cos of the radian angle)."""
    return math.cos(deg * math.pi / 180.0)


def fmt(x):
    return repr(float(x))


def main():
    check = "--check" in sys.argv
    ok = True

    q = sphere_mean_quadrature()
    print(f"sphere mean of max(0, cos theta) by theta-Simpson: {q:.20f} (exact 1/4)")
    if abs(q - D(1) / 4) > D(1e-14):
        print("FAIL: quadrature mean != 1/4")
        ok = False

    for name, phi in (("0.5c", PHI05), ("0.99c", PHI099), ("cap", PHICAP)):
        k = kinetic_flux(N_ISM, phi)
        mean = mean_inward(N_ISM, phi, EPS, F_IN)
        pole = emittance(N_ISM, phi, EPS, F_IN, 1.0)
        print(f"{name}: phi={fmt(phi)} K={fmt(k)} mean={fmt(mean)} pole={fmt(pole)} pole/mean={fmt(pole / mean)}")
        for deg in ANGLES:
            c = cos_deg(deg)
            print(f"  {name} theta={deg:g}deg cos={fmt(c)} emittance={fmt(emittance(N_ISM, phi, EPS, F_IN, c))}")
        if abs(pole / (4 * mean) - 1) > D(1e-50):
            print(f"FAIL: {name} pole != 4 mean")
            ok = False

    # HB-61 from the profile: eps for a 1 W/m^2 *mean* at the cap.
    hb61 = 1 / mean_inward(N_ISM, PHICAP, D(1), F_IN)
    print(f"HB-61 eps for mean 1 W/m^2 at cap: {fmt(hb61)}")

    if check:
        def printed(got, want, half, label):
            nonlocal ok
            good = abs(D(got) - D(want)) <= D(half)
            print(f"  check {label}: {fmt(got)} vs {want} +- {half}: {'ok' if good else 'MISMATCH'}")
            ok = ok and good

        print("design / canon digits:")
        printed(mean_inward(N_ISM, PHI099, EPS, F_IN), "2.40719e-5", "5e-11", "M4 glow_w_m2 0.99c")
        printed(emittance(N_ISM, PHI099, EPS, F_IN, 1.0), "9.62878e-5", "5e-11", "M4 glow_pole 0.99c (AC8 interim)")
        printed(emittance(N_ISM, PHI099, EPS, F_IN, 1.0), "9.6288e-5", "5e-10", "M4 G-M4-4 pole 0.99c")
        printed(emittance(N_ISM, PHICAP, EPS, F_IN, 1.0), "1.12508", "5e-6", "M4 G-M4-4 pole cap")
        printed(mean_inward(N_ISM, PHICAP, EPS, F_IN), "0.2813", "5e-5", "M4 mean at cap")
        printed(kinetic_flux(N_ISM, PHI099), "1.92576e5", "0.5", "M4 K 0.99c")
        printed(kinetic_flux(N_ISM, PHI099), "1.93e5", "500", "HB-45")
        printed(hb61, "3.6e-9", "5e-11", "HB-61")

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
