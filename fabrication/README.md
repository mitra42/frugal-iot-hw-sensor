# Frugal-IoT V0.2 — JLCPCB order files (15 Oct 2026)

Board: 64 × 37 mm, 2 layers, 1.6 mm FR-4, 1 oz copper, 4 × M2 holes. Min track 0.25 mm, min clearance 0.15 mm
(USB pair) / 0.2 mm elsewhere, min drill 0.3 mm — all JLCPCB standard.

| File | Upload where |
|---|---|
| `gerbers.zip` | PCB order — "Add gerber file" |
| `BOM_JLCPCB.csv` | PCB Assembly — BOM (Comment, Designator, Footprint, LCSC Part #) |
| `CPL_JLCPCB.csv` | PCB Assembly — CPL / pick-and-place (Designator, Mid X, Mid Y, Layer, Rotation) |

53 placed parts, 24 part numbers, RS485 included. Not fitted (excluded from both files): J4 (cell), J5,
J6 (aux 5 V), J7 (external LED), R19, C11 and the solder jumpers.

**Before paying, check part rotations in JLCPCB's assembly preview** (SOT-23, SOT-23-5, SOIC-8, the USB-C and
the terminal blocks are the usual suspects), or tick "Confirm parts placement" (~$0.45). Check the module's
(U4) pin-1 mark.

Assembly: Economic, top side only. J2 + J12 and J3 + J13 (pairs of XY308-2.54-5P that butt together as 10-way blocks) are
through-hole and hand-soldered by JLCPCB — or untick them and solder yourself.

Without Modbus (saves ≈ $1.27 per board at 10): set U5, C13, R20–R23, D5 and J3 to DNP in
`claude-tools/schematic/circuit.py` and regenerate the files (DECISIONS D29).

Regenerate: `claude-tools/layout/fab.sh` on the Mac (DRC + Gerbers + drill + placement + BOM), then
`python3 claude-tools/layout/jlc_files.py`.
