#!/usr/bin/env python3
"""Generate the dwarf photometry table from Pecaut & Mamajek 2022.04.16.

Two node chains come from the same first dwarf table: Gaia BP-RP (with Teff
and G-V) and Johnson B-V (with Teff). Each chain keeps rows whose colour is
strictly increasing and whose Teff is strictly decreasing.
"""

import argparse
from pathlib import Path

SOURCE = "https://www.pas.rochester.edu/~emamajek/EEM_dwarf_UBVIJHK_colors_Teff.txt"


def parse_bv(path):
    """Rows (name, teff, b_minus_v) of the first table with numeric Teff and B-V."""
    rows = []
    dropped = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#SpT"):
            if in_table:
                break
            in_table = True
            continue
        if not in_table or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) < 12 or not fields[0].endswith("V"):
            continue
        name, temperature, colour = fields[0], fields[1], fields[8]
        if any(value.startswith("...") for value in (temperature, colour)):
            continue
        try:
            teff, b_minus_v = float(temperature), float(colour)
        except ValueError as exc:
            raise ValueError(f"bad numeric row: {line}") from exc
        if rows and b_minus_v <= rows[-1][2]:
            dropped.append((name, b_minus_v))
            continue
        if rows and teff >= rows[-1][1]:
            raise ValueError(f"temperature is not strictly decreasing at {name}")
        rows.append((name, teff, b_minus_v))
    if len(rows) < 2:
        raise ValueError("no usable B-V rows found")
    return rows, dropped


def parse(path):
    rows = []
    dropped = []
    in_table = False
    last_colour = float("-inf")
    last_teff = float("inf")
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#SpT"):
            if in_table:
                break
            in_table = True
            continue
        if not in_table or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) < 12 or not fields[0].endswith("V"):
            continue
        name, temperature, gv, colour = fields[0], fields[1], fields[10], fields[11]
        if any(value.startswith("...") for value in (temperature, gv, colour)):
            continue
        try:
            teff, g_minus_v, bp_rp = float(temperature), float(gv), float(colour)
        except ValueError as exc:
            raise ValueError(f"bad numeric row: {line}") from exc
        if bp_rp <= last_colour:
            dropped.append((name, bp_rp))
            continue
        if teff >= last_teff:
            raise ValueError(f"temperature is not strictly decreasing at {name}")
        rows.append((name, teff, g_minus_v, bp_rp))
        last_colour, last_teff = bp_rp, teff
    if len(rows) < 2:
        raise ValueError("no usable first dwarf table found")
    return rows, dropped


def literal(number):
    result = format(number, ".15g")
    return result if "." in result else (result.replace("e", ".0e") if "e" in result else result + ".0")


def render(rows, dropped, bv_rows, bv_dropped):
    lines = [
        "-- Pecaut & Mamajek, A Modern Mean Dwarf Stellar Color and Effective Temperature Sequence",
        "-- Version 2022.04.16",
        f"-- Source: {SOURCE}",
        "-- Generator: python3 tools/mamajek_to_ail.py --input EEM_dwarf_UBVIJHK_colors_Teff.txt --output photometry_table.ail",
        "-- First dwarf table only; rows lacking both Bp-Rp and G-V omitted.",
        "-- Strictly increasing Bp-Rp; dropped rows: " + (
            ", ".join(f"{name} ({literal(colour)})" for name, colour in dropped) if dropped else "none"
        ),
        "module sunholo/relativity/photometry_table",
        "",
    ]
    for function, index in (("bpRpNodes", 3), ("teffNodes", 1), ("gMinusVNodes", 2)):
        values = [literal(row[index]) for row in rows]
        lines += [f"export pure func {function}() -> [float] = ["]
        for start in range(0, len(values), 8):
            lines.append("  " + ", ".join(values[start:start + 8]) + ("," if start + 8 < len(values) else ""))
        lines += ["]", ""]
    lines += [
        f"-- Johnson B-V chain: {bv_rows[0][0]} to {bv_rows[-1][0]}, strictly increasing B-V; dropped rows: " + (
            ", ".join(f"{name} ({literal(colour)})" for name, colour in bv_dropped) if bv_dropped else "none"
        ),
        "",
    ]
    for function, index in (("bvNodes", 2), ("bvTeffNodes", 1)):
        values = [literal(row[index]) for row in bv_rows]
        lines += [f"export pure func {function}() -> [float] = ["]
        for start in range(0, len(values), 8):
            lines.append("  " + ", ".join(values[start:start + 8]) + ("," if start + 8 < len(values) else ""))
        lines += ["]", ""]
    names = [f'"{row[0]}"' for row in rows]
    lines += ["export pure func spectralTypes() -> [string] = ["]
    for start in range(0, len(names), 8):
        lines.append("  " + ", ".join(names[start:start + 8]) + ("," if start + 8 < len(names) else ""))
    lines += ["]", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rows, dropped = parse(args.input)
    bv_rows, bv_dropped = parse_bv(args.input)
    args.output.write_text(render(rows, dropped, bv_rows, bv_dropped), encoding="utf-8")
    print(f"Kept {len(rows)} rows: {rows[0][0]} to {rows[-1][0]}")
    print("Dropped rows: " + (
        ", ".join(f"{name} (Bp-Rp {literal(colour)})" for name, colour in dropped) if dropped else "none"
    ))
    print(f"B-V chain: kept {len(bv_rows)} rows: {bv_rows[0][0]} to {bv_rows[-1][0]}; dropped: " + (
        ", ".join(f"{name} ({literal(colour)})" for name, colour in bv_dropped) if bv_dropped else "none"
    ))


if __name__ == "__main__":
    main()
