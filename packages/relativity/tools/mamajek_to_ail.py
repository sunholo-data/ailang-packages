#!/usr/bin/env python3
"""Generate the dwarf photometry table from Pecaut & Mamajek 2022.04.16."""

import argparse
from pathlib import Path

SOURCE = "https://www.pas.rochester.edu/~emamajek/EEM_dwarf_UBVIJHK_colors_Teff.txt"


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


def render(rows, dropped):
    lines = [
        "-- Pecaut & Mamajek, A Modern Mean Dwarf Stellar Color and Effective Temperature Sequence",
        "-- Version 2022.04.16",
        f"-- Source: {SOURCE}",
        "-- Generator: python3 tools/mamajek_to_ail.py --input /tmp/stap_iter0_mamajek.txt --output photometry_table.ail",
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
    args.output.write_text(render(rows, dropped), encoding="utf-8")
    print(f"Kept {len(rows)} rows: {rows[0][0]} to {rows[-1][0]}")
    print("Dropped rows: " + (
        ", ".join(f"{name} (Bp-Rp {literal(colour)})" for name, colour in dropped) if dropped else "none"
    ))


if __name__ == "__main__":
    main()
