#!/usr/bin/env python3
"""Independent test oracle for planet_model's explicitly adopted approximation.

Consumes complete JSON emitted by planet_model_validation_test.main; never
produces package or game data. Uses a second language to check mass-grid support,
conditional CDF quantiles, finite endpoints and the chosen prior/likelihood.
This validates the 128-cell approximation, not the published Forecaster posterior.
"""
import json
import math
import sys
from pathlib import Path


def central_radius(mass):
    # Chen & Kipping (2017), arXiv:1603.08614v2 Table 1 pp7–9.
    # Connected power-law offsets independently composed in log space.
    log_mass = math.log(mass)
    log_break1 = math.log(2.04)
    log_break2 = math.log(0.414 * 317.82838)
    if log_mass <= log_break1:
        log_radius = math.log(1.008) + 0.279 * log_mass
    elif log_mass <= log_break2:
        log_radius = math.log(1.008) + 0.279 * log_break1 + 0.589 * (log_mass - log_break1)
    else:
        log_radius = (math.log(1.008) + 0.279 * log_break1
                      + 0.589 * (log_break2 - log_break1) - 0.044 * (log_mass - log_break2))
    return math.exp(log_radius)


def conditional_grid(radius, count=128):
    result = []
    for index in range(count):
        mass = math.exp(math.log(0.001) + (index + 0.5) * math.log(4200000.0) / count)
        centre = central_radius(mass)
        fraction = 0.0403 if mass <= 2.04 else 0.146 if mass <= 0.414 * 317.82838 else 0.0737
        sigma = fraction * centre
        density = math.exp(-0.5 * ((radius - centre) / sigma) ** 2) / sigma
        result.append((mass, density))
    normalization = math.fsum(density for _, density in result)
    assert math.isfinite(normalization) and normalization > 0
    return [(mass, density / normalization) for mass, density in result]


def validate(path):
    rows = json.loads(Path(path).read_text())
    uniforms = [0.0, 2.0 ** -53, 0.001, 0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 0.999999, 1.0 - 2.0 ** -53]
    assert len(rows) == 65
    checks = 0
    for row_index, (radius, *masses) in enumerate(rows):
        assert radius == 0.5 + 15.5 * row_index / 64.0
        assert len(masses) == len(uniforms)
        assert all(math.isfinite(mass) and 0 < mass < 4200 for mass in masses)
        assert masses == sorted(masses)
        grid = conditional_grid(radius)
        for uniform, actual in zip(uniforms, masses):
            index = min(range(len(grid)), key=lambda i: abs(math.log(grid[i][0] / actual)))
            assert math.isclose(actual, grid[index][0], rel_tol=3e-14)
            # fsum and the log-space oracle have different rounding from the
            # sequential float CDF. Allow only that absolute CDF roundoff.
            below = math.fsum(weight for _, weight in grid[:index])
            through = below + grid[index][1]
            assert below <= uniform + 5e-14, (radius, uniform, actual, below)
            assert through >= uniform - 5e-14, (radius, uniform, actual, through)
            checks += 1
    print(f"planet_model oracle: {len(rows)} radii, {checks} conditional quantiles; finite/support/CDF/endpoints agree")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: planet_model_ref.py <validation-grid.json>")
    validate(sys.argv[1])
