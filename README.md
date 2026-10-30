# Frugal-IoT V0.2

A simple, un-opinionated, multi-purpose sensor board, that can be wired to sensors using most common interfaces (I2C, ModBus, OneWire, Analog) with onboard charging and external antenna.

**Status:** revision 4 (28 Oct 2026): 64 × 37 mm, 2 layers, routed, DRC clean; J4 (cell) and J6 (5 V in) now fitted (D34); JLCPCB files ready for the first order.

## Hardware Features

* ESP32-C3-WROOM-02U
* U.FL socket for external antenna. 
* USB-C for power and programming (e.g. using a $10 security camera solar panel)
* Protected charger circuitry for a single LiPo cell (~250mA), will work with really small cells (e.g. salvaged from vapes) or by adding a solder bridge can charge an 18650 cell at ~500mA
* Sensors controlled by a switched 3.3V sensor rail, allowing much lower power consumption in sleep.
* I2C support on J1 
* Two sensor inputs on J12 can be used for analog, OneWire etc, pads to add pull up resistor or smoothing capacitor if required.
* Two extra sensors on J13 (not soldered by default) 
* RS485(Modbus) on J3, (can be omitted to save ~USD1.00, or to get three more pins for sensors.
* 37mm * 64mm board with connectors mostly at the ends, so that it can fit inside a 40mm pipe as an affordable enclosure. 

## Software features

The board can be flashed with any software, but its designed to work well with [Frugal-IoT](https://github.com/mitra42/frugal-iot) which has the following features. 

* Support for a very wide and expanding range of sensors 
* Integrates with Frugal-IoT cloud, and UX on phone or laptop
* Plug and play MQTT interface, treats remote sensors and actuators the same as local ones 
* Captive WiFi portal for local configuration
* Local controls for on-device automation configured through the UX.
* Multilingual support on both captive portal and UX
* Automatic Over-The-Air (OTA) updates for unattended devices.
* Power management for really long life for sensors that report at long intervals.
* mDNS, for device to device signalling when the Internet is down
* NTP integration for accurate clock
* Fully Open-Source (i.e. not crippleware) 

## Files

| | |
|---|---|
| `SCHEMATIC.pdf` | schematic, one sheet |
| `BOM.csv` | bill of materials with LCSC (JLCPCB) part numbers; DNP = not fitted |
| `COST-ESTIMATE.txt` | JLCPCB cost for 10 and 100 boards, and the saving without Modbus |
| `PCB-LAYOUT.pdf` | 3D views and both copper layers |
| `DECISIONS.md` | design decisions and why |
| `fabrication/` | files to order from JLCPCB — see its README |
| `frugal_iot_v02/` | KiCad 10 project |
| `firmware/` | PlatformIO env for frugal-iot-demo + board variant (pins_arduino.h) |
| `claude-tools/` | scripts Claude uses to regenerate the design — reviewers can ignore |

The schematic is generated from `claude-tools/schematic/circuit.py`: changes made by Claude go there, not into
the .kicad_sch. Regenerate: `buildlib.py`, `run_draw_bg.sh` (log must end `VERIFY OK`), `run_kicad.sh`,
then `jlc_dump.sh` and `python3 cost_estimate.py > ../../COST-ESTIMATE.txt` (see ../irrigation-layout-oct-2026/claude-tools/README.md for the method).

If the fabrication and KiCad directories are not available wherever you find this, please let me know (mitra@mitra.biz) and I'll send you them. 


