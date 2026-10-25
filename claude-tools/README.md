# claude-tools — how Claude regenerates and changes this design

Reviewers can ignore this folder. Same method and scripts as `../../irrigation-layout-oct-2026/claude-tools/`
(see its README for detail); everything runs on Mitra's Mac with KiCad 10. `out/` folders are scratch.

## Schematic — `schematic/`
Generated: edit `circuit.py` (parts, values, LCSC numbers, nets) and `dblk.py` (drawing), never the .kicad_sch.
`buildlib.py` (project symbols: VSYS/VBAT/+3V3_SW rails, XB5353A) → `run_draw_bg.sh` (log ends `VERIFY OK`)
→ `run_kicad.sh` (ERC, netlist, ../../SCHEMATIC.pdf, ../../BOM.csv) → `jlc_dump.sh` + `python3 cost_estimate.py
> ../../COST-ESTIMATE.txt`.

## PCB — `layout/`
**Small changes after a schematic edit: KiCad "Update PCB from Schematic", re-route the affected nets, then
`fab.sh`.** The full rebuild below discards all routing.
- Fabrication: `fab.sh` → `python3 jlc_files.py` (→ ../../fabrication/); `renders.sh` for PCB-LAYOUT.pdf views.
- Full rebuild: `pipeline.sh 60` (fpmeasure → place → build_pcb → netclasses → DRC); `prep_route.py` → `dsn_prep.py`
  → Freerouting 2.1.0 via `route/Route.java` (cloud, Java 21) → `route/check_ses.py` → copy to `out/routed.ses`
  → `post_route.sh` → `island_pads.py` + `rescue.py REF:PAD,...` / `via_near.py REF:PAD` for any GND pad left
  in a detached pour island → `pinnum.py`, `addtext.py` → `fab.sh`.
