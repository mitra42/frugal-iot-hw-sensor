# Frugal-IoT V0.2 — decision log

Status: **laid out and routed (15 Oct 2026, revision 2)** — DRC: 0 unconnected, 0 clearance, schematic parity 0; JLCPCB files in `fabrication/`; for review before ordering. Successor to Frugal IoT v0.1 (`../frugal-iot-v0.1/`),
redesigned for JLCPCB assembly (PCBA) instead of hand soldering. Cost matters more here than on the
irrigation board (`../irrigation-layout-oct-2026/`), whose power design it borrows.

## Decided

**D1 — Module: ESP32-C3-WROOM-02U-N4** (C2926676, $2.75 @10 / $2.25 @100, Oct 2026). U.FL antenna —
on-board PCB antennas don't reach far enough (Mitra). Castellated edge pads, so no X-ray inspection
(JLCPCB charges X-ray per leadless part: $1.64 @1–10, $0.49 @51–200). Alternative: C3-MINI-1U-N4
(C2911374, $2.80). C6 not needed — the C3 has enough pins (D3).

**D2 — Same board height as v0.1 (37 mm), length as short as the parts allow.** Single-sided SMD assembly.

**D3 — C3 pin map** (same USB/UART use as the C3-Pico):

| GPIO | use |
|---|---|
| 18, 19 | USB D−/D+ (native USB, no USB-UART chip) |
| 20, 21 | UART0 RX/TX → J3 (Modbus or other serial). Note: ROM boot log appears on TX at reset |
| 9 | BOOT button (input after boot) |
| 6, 7 | I2C SDA/SCL → J2 |
| 0, 1 | Sensor 1, sensor 2 (ADC1) → J2 |
| 3 | Battery sense (ADC1) |
| 5 | 3V3_SW enable |
| 8 | Status LED (strapping pin, LED to 3V3 keeps it high) |
| 2 | → J3 (ADC1; strapping — on-board pull-up, sensor must not pull low at boot) |
| 4 | → J3 (ADC1) |
| 10 | Flying-wire pad; becomes RS485 DE/RE if Modbus is fitted |

**D4 — J2 (main sensor connector, fitted), pin order as v0.1:**
1 GND · 2 SDA (GPIO6) · 3 SCL (GPIO7) · 4 3V3_SW · 5 GND · 6 S1 (GPIO0) · 7 3V3_SW · 8 GND · 9 S2 (GPIO1) · 10 3V3_SW

**D5 — J3 (spares, footprint only, unfitted), same layout as J2:**
1 GND · 2 RX (GPIO20) · 3 TX (GPIO21) · 4 3V3_SW · 5 GND · 6 GPIO2 · 7 3V3_SW · 8 GND · 9 GPIO4 · 10 3V3_SW.
A plug wired for a J2 position fits the same J3 position. TX is the C3's output. With the Modbus option
fitted (D13), pins 2–3 become RS485 A/B via solder bridges.

**D6 — Terminals stay through-hole XY308-2.54.** SMD terminal blocks exist at JLCPCB (WAGO 2059,
3 mm, $0.22/pole; JILN JL212V-SMT, 3.5 mm, 10P $1.69, low stock) but cost more than XY308 + hand
soldering (~$0.023/joint).

**D7 — Power:** USB-C (16-pin, data needed for programming) 5 V → TP4056 (Preferred, no feeder fee)
→ cell → load sharing (P-FET + Schottky, as irrigation) → **ME6211C33** LDO (C82942, $0.06, 500 mA,
~60 µA quiescent — accepted; same as the C3-Pico) → 3V3 → AO3401 high-side switch → 3V3_SW (off at
reset, small bulk cap for inrush). No 12 V, no 5V_SW, no 5 V on connectors.

**D8 — Charge current jumper:** 4.7 kΩ PROG (~250 mA) default; solder bridge adds a parallel 4.7 kΩ
(~500 mA).

**D9 — No USB ESD protection chip** (as the C3-Pico; Mitra has never lost one through USB).

**D10 — USB only for charging**, plus two through-holes beside the USB-C at 2.54 mm for external
wiring or a hand-soldered XY308-2P later.

**D11 — Battery: unfitted JST-PH through-hole footprint** ($0) — solder leads or fit a connector by
hand. Fitted alternatives cost $0.35–0.40/board at 10 (mostly the feeder fee).

**D12 — Battery protection: XB5353A** (C80628, $0.09) — one chip with integrated MOSFETs, replacing
DW01A + FS8205A (one feeder fee instead of two). Current limits to be checked in its datasheet.

**D13 — Modbus: transceiver laid out on the board, fitted per order (option B)** — superseded by D29 (now fitted by default). SP3485EN (Basic) +
PSM712 (Basic) + 120 Ω termination on a solder jumper + bias resistors; DE/RE on GPIO10. Solder bridges
select RS485 A/B or raw RX/TX on J3 pins 2–3. Default order leaves the transceiver parts off the JLCPCB
BOM, so the board is then TTL serial on J3 (external RS485 module, as with the C3-Pico). Cost when fitted
≈ $0.65/board @10, $0.45 @100. Most RS485 sensors need their own 5–24 V supply — this board has only
3V3_SW, so that supply is external.

**D14 — J5 replaced by a 3-pad unfitted footprint: GND · GPIO10 · 3V3_SW** (same triplet order as J2/J3).
GPIO10 is the RS485 DE/RE line when the Modbus option is fitted, so this position is only spare without it.
v0.1's J5 signals: LED → on-board (D15); Modbus TX/RX → J3; SPI and DAC dropped (no pins; C3 has no DAC).

**D15 — Status LED on GPIO8 on-board, plus two pads (3V3, LED cathode after the series resistor) for an
off-board LED in the enclosure** (Mitra: often off-board). Leave the on-board LED unfitted if only the
external one is used.

**D16 — No J6 (GND pads) or J7 (3V3_SW pads)** — nothing to connect to them (Mitra).

**D17 — 3V3_SW switched by GPIO5 directly (active low):** nRAIL_EN drives the AO3401 gate, R10 100k pulls it
up so the rail is off through reset and boot. Because the P-FET's source is +3V3, a 3.3 V GPIO turns it fully
off — no N-FET needed (one part fewer than the irrigation board). Firmware: GPIO5 LOW = sensors on.

**D18 — J2 and J3 are each two XY308-2.54-5P blocks side by side** (JLCPCB has no 10-way XY308; two of one
part number = one feeder fee). References J2 + J12 (pins 1–5, 6–10) and J3 + J13 — KiCad references can't
end in a letter. Silkscreen to number the positions 1–10.

**D19 — XB5353A checked against its datasheet:** VDD (3) = cell +, GND (2) = cell −, VM (4, 5) = pack − =
board GND, VT (1) open; one 100 nF at VDD. Thresholds 4.30 V / 2.4 V, discharge over-current 3 A, 54 mΩ.

**D20 — TP4056 TEMP tied to GND** (no cell thermistor input), to save parts.

**D21 — (superseded by D29)** RS485 parts were DNP by default.

**D22 — Cost (JLCPCB Economic, live prices 15 Oct 2026):** ≈ $8.85/board for 10, ≈ $5.40 for 100, with a
bare-PCB placeholder (irrigation board's quote) until layout. Modbus option adds ≈ $0.67 / $0.49 per board.
See COST-ESTIMATE.txt.

## Layout (15 Oct 2026)

**D23 — Board 64 × 37 mm** (was 60; widened in D30 to make room for reference labels). J2 + J12 on the left edge and J3 + J13 on the right, wire entries outward, pin 1 of
J2 at the top and pin 1 of J3 at the bottom (each block read facing its wire entry). Module along the top
middle, USB-C, J6 and J4 on the bottom edge, J5 top right. 4 × M2 holes 2.5 mm in from each corner, in the
strips beside the terminal blocks (as v0.1). Well inside the 100 × 100 mm price break.

**D24 — Silkscreen:** "Frugal-IoT V0.2" (now 2.5 mm on the back, D32), and "1" / "10" at the ends of each 10-way pair.

**D25 — Net classes:** Power 0.5 mm (GND, VBAT, VSYS, CELL_NEG), PowerFine 0.3 mm (VBUS, +3V3, +3V3_SW — must
enter the USB-C's 0.5 mm-pitch pads), USB pair 0.25 / 0.15 mm, signals 0.25 mm. Max currents ~0.5 A.

**D26 — Routing as the irrigation board:** GND left to the pours on both layers (fan-out vias, stitching,
island vias), the rest by Freerouting 2.1.0 (pass 9 of 30 kept). Verified independently (all nets whole)
and by KiCad DRC. Module thermal-pad vias widened from 0.2 to 0.3 mm drill (JLCPCB standard), which makes
KiCad flag U4 as differing from its library copy — expected.

**D27 — GND pads cut off from the pour by routing are rejoined** with a short track or a via beside the pad
(`island_pads.py` + `rescue.py`; `via_near.py` if boxed in). Six pads on the current routing.

**D28 — Accepted DRC notes (49):** J2/J12 and J3/J13 are two blocks that butt together, so their courtyards,
silkscreen and pad clearances overlap (40 notes); connector silkscreen at the board edge where the parts are
flush with it (8); U4 library difference (1, D26). No copper, clearance, hole or connection errors.

## Revision 2 (15 Oct 2026, after Mitra's review)

**D29 — RS485 / Modbus fitted by default** (U5 SP3485EN, C13, R20–R23, D5 PSM712) **and J3 (pins 1–5) fitted**
so A/B have a terminal. JP2/JP3 re-wired so the factory bridge (pads 1–2) gives RS485: J3 pin 2 = A, pin 3 = B;
cut 1–2 and bridge 2–3 for UART0 RX/TX on J3 (U5 must then be left off, as its RO pin drives RX). J13 (pins 6–10)
stays unfitted. **A board without Modbus can leave out U5, C13, R20–R23, D5 and J3 and save ≈ $1.27 per board at
10, ≈ $0.97 at 100** (COST-ESTIMATE.txt); no other change needed (JP2/JP3 then select nothing useful until bridged
2–3 for UART). Total then ≈ $9.93 / $6.36 per board (10 / 100); see D31 for the current figure.

**D30 — Every part labelled next to itself** (Mitra: unlabelled resistor pairs below U5, right of JP4, left of U4;
C6 label unclear). Parts now packed with 0.7 mm between courtyards (was 0.5) on a 64 mm board, and `silk.py`
places each 0.8 mm reference hugging its own part: clear of all pads, silk, other labels and big parts, and at
least 0.6 mm nearer its own part than any other (0.3 mm, then 0.05 mm only where nothing else fits). All 63
references placed on the silkscreen; mounting-hole labels hidden.

## Revision 3 (22 Oct 2026, after Mitra's review)

**D31 — Now fitted:** J13 (J3 positions 6–10: GPIO2, GPIO4 with GND/3V3_SW), R18 (4.7k pull-up on SENS1, J2
pin 6 — e.g. a DS18B20) and C12 (100 nF filter on SENS2, J2 pin 9 — analog). R19 and C11 stay unfitted
options. 53 placed parts; ≈ $10.49 per board for 10, ≈ $6.85 for 100 (bare PCB still a placeholder).

**D32 — Polarity marked on the hand-soldered power connectors:** "+" / "−" (1.4 mm) above J6's pads (pin 1 =
+5 V, pin 2 = GND; for an external 5 V supply such as a solar panel) and either side of J4's pads (pin 2 = cell +,
pin 1 = cell −). To make room the board title moved to the back silkscreen, 2.5 mm, where nothing else is
printed. (J1 is the USB-C; the hand-soldered pair is J4 and J6.)

**D33 — Every connector pin named on the back silkscreen** (Mitra: wire up without the docs), beside its pad:
G = GND, V = 3V3_SW, SDA / SCL, A / B (RS485 on J3 pins 2–3), a bare number = that GPIO (J2: 0, 1; J13: 2, 4;
J5: 10), "+" / "−" with SOLAR (J6) and CELL (J4), and a diode symbol (anode → cathode) at J7. Labels are 1.0 mm,
read correctly with the board turned over. If JP2/JP3 are re-bridged for UART, J3 pins 2–3 become RX / TX.
`claude-tools/layout/backlabels.py` (re-runnable). No new DRC notes.

## Revision 4 (28 Oct 2026, before the first JLCPCB order)

**D34 — J4 and J6 fitted for this run** (Mitra): J4 = JST-PH 2-way right-angle (S2B-PH-K-S, C173752) for the
cell; J6 = XY308-2.54-2P screw terminal (C557685) for external 5 V, e.g. a solar panel. Both Extended and
through-hole, so JLCPCB hand-solders them: about $0.97 per board at 10 (mostly two $3.07 feeder fees), $0.36
at 100. Layout unchanged (footprints were already placed and marked with polarity, D32). 55 placed parts, 26
part numbers; ≈ $11.51 per board for 10, ≈ $7.16 for 100 (prices re-read 28 Oct; bare PCB still a
placeholder). Not all JST-PH cells are wired the same way: check the lead polarity against the "+" / "−" marks.
J5, J7, R19 and C11 remain unfitted.

**D35 — CPL corrected to match JLCPCB's part models** (Mitra's first pass through the assembly preview):
JLCPCB's models are rotated differently from KiCad's footprints, so `jlc_files.py` now adds 180° to SOT-23
(Q1, Q2, D5) and J4, −90° to SOT-23-5 U3 and SOIC-8 (U1, U5), and 180° to U2
(JLCPCB's XB5353A model is drawn differently from its ME6211, though both are SOT-23-5). The THT connectors' KiCad origin is
pin 1 but JLCPCB centres its model on the given point, which put J2/J12 two pins too high, J3/J13 two pins
too low, J6 half a pin left and J4 1 mm left; the CPL now gives the centre of each pin row. Expected
orientation (pin 1, or cathode): U1 bottom-right, U5 top-left, U2/U3 bottom-left, Q1 bottom-right, Q2/D5
top-right, U4 top-left; D3 band at the top; LED cathodes: D1 right, D2 bottom, D4 right.
