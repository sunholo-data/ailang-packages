#!/usr/bin/env python3
"""Independent numerical oracle, never a production data pipeline.

Scalar spherical gnomonic equations check the AILANG Cartesian tangent-basis
implementation. The real DR1 field's metadata and source queries are cited in
projection_test.ail. Uses only Python's standard library.
"""
import json
import math
import os
from pathlib import Path
import subprocess

RAD = math.pi / 180
RA0, DEC0 = 52.7887505 * RAD, -52.5 * RAD
SCALE = 2.777777777778e-5


def pixel_to_sky(x, y):
    xi, eta = -(x + 5951) * SCALE * RAD, (y - 3975) * SCALE * RAD
    rho = math.hypot(xi, eta)
    c = math.atan(rho)
    dec = math.asin(math.cos(c) * math.sin(DEC0) + eta * math.sin(c) * math.cos(DEC0) / rho)
    ra = RA0 + math.atan2(xi * math.sin(c), rho * math.cos(DEC0) * math.cos(c) - eta * math.sin(DEC0) * math.sin(c))
    return ra / RAD % 360, dec / RAD


def sky_to_pixel(ra, dec):
    a, d = ra * RAD, dec * RAD
    denom = math.sin(DEC0) * math.sin(d) + math.cos(DEC0) * math.cos(d) * math.cos(a - RA0)
    xi = math.cos(d) * math.sin(a - RA0) / denom / RAD
    eta = (math.cos(DEC0) * math.sin(d) - math.sin(DEC0) * math.cos(d) * math.cos(a - RA0)) / denom / RAD
    return -5951 - xi / SCALE, 3975 + eta / SCALE


def separation(ra, dec):
    a, d = ra * RAD, dec * RAD
    b, e = 52.5 * RAD, -52.6 * RAD
    hav = math.sin((d - e) / 2) ** 2 + math.cos(d) * math.cos(e) * math.sin((a - b) / 2) ** 2
    return 2 * math.asin(math.sqrt(hav)) / RAD


def main():
    root = Path(__file__).resolve().parent.parent
    binary = os.environ.get("AILANG", "ailang")
    result = subprocess.run([binary, "run", "--quiet", "--relax-modules", "--entry", "projectionProbe", "--args-json", "24", "_smoke.ail"], cwd=root, check=True, capture_output=True, text=True, timeout=90)
    actual = json.loads(result.stdout)
    assert len(actual) == 125, len(actual)
    max_pixel = 0.0
    max_angle = 0.0
    for row, k in enumerate(range(24, -1, -1)):
        x, y = 1 + 29 * k, 1 + 17 * k
        ra, dec = pixel_to_sky(x, y)
        px, py = sky_to_pixel(ra, dec)
        expected = (ra, dec, px, py, separation(ra, dec))
        for i, value in enumerate(expected):
            error = abs(actual[row * 5 + i] - value)
            if i in (2, 3):
                max_pixel = max(max_pixel, error)
                assert error < 1e-6, (row, i, actual[row * 5 + i], value)
            else:
                max_angle = max(max_angle, error)
                assert error < 1e-10, (row, i, actual[row * 5 + i], value)
    print(f"projection oracle: 125 values checked, max_pixel_error={max_pixel:.3g}, max_angle_error_deg={max_angle:.3g}")


if __name__ == "__main__":
    main()
