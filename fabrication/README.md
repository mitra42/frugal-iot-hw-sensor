# Frugal-IoT V0.2 — JLCPCB order files (28 Oct 2026)

Board: 64 × 37 mm, 2 layers, 1.6 mm FR-4, 1 oz copper, 4 × M2 holes. Min track 0.25 mm, min clearance 0.15 mm
(USB pair) / 0.2 mm elsewhere, min drill 0.3 mm — all JLCPCB standard.

| File | Upload where |
|---|---|
| `gerbers.zip` | PCB order — "Add gerber file" |
| `BOM_JLCPCB.csv` | PCB Assembly — BOM (Comment, Designator, Footprint, LCSC Part #) |
| `CPL_JLCPCB.csv` | PCB Assembly — CPL / pick-and-place (Designator, Mid X, Mid Y, Layer, Rotation) |

55 placed parts, 26 part numbers, RS485, J4 (cell) and J6 (5 V in) included (D34). Not fitted (excluded from
both files): J5, J7 (external LED), R19, C11 and the solder jumpers.

**Before paying, check JLCPCB's assembly preview.** The CPL already corrects for JLCPCB's models (D35); the pink
dot marks pin 1. Expected: U1 bottom-right, U5 top-left, U2 and U3 bottom-left, Q1 bottom-right, Q2 and D5
top-right, U4 top-left; D3's band at the top; LED cathodes D1 right, D2 bottom, D4 right; every terminal-block
screw and J4/J6 over its own pads. Tick "Confirm parts placement" (~$0.45) as well.

Assembly: Economic, top side only. J2 + J12 and J3 + J13 (pairs of XY308-2.54-5P that butt together as 10-way blocks), J4 and J6 are
through-hole and hand-soldered by JLCPCB — or untick them and solder yourself.

Without Modbus (saves ≈ $1.30 per board at 10): set U5, C13, R20–R23, D5 and J3 to DNP in
`claude-tools/schematic/circuit.py` and regenerate the files (DECISIONS D29).

Regenerate: `claude-tools/layout/fab.sh` on the Mac (DRC + Gerbers + drill + placement + BOM), then
`python3 claude-tools/layout/jlc_files.py`.
