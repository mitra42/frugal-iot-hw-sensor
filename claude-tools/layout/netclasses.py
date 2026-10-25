"""Write net classes + board rules into the V0.2 .kicad_pro (JLCPCB 2-layer capable)."""
import json
p = '../../frugal_iot_v02/frugal_iot_v02.kicad_pro'
d = json.load(open(p))
def cls(name, clr, w, via=0.6, drill=0.3, dpw=0.2, dpg=0.25, prio=0):
    return {"name": name, "clearance": clr, "track_width": w, "via_diameter": via, "via_drill": drill,
            "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": dpw, "diff_pair_gap": dpg,
            "diff_pair_via_gap": 0.25, "wire_width": 6, "bus_width": 12, "line_style": 0,
            "schematic_color": "rgba(0, 0, 0, 0.000)", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": prio}
d['net_settings'] = {
    "classes": [cls('Default', 0.2, 0.25, prio=2147483647), cls('Power', 0.2, 0.5, via=0.8, drill=0.4, prio=1),
                cls('PowerFine', 0.2, 0.3, via=0.6, drill=0.3, prio=1),
                cls('USB', 0.15, 0.25, dpw=0.25, dpg=0.15, prio=2)],
    "meta": {"version": 4},
    "net_colors": None,
    "netclass_assignments": None,
    "netclass_patterns": [{"netclass": "Power", "pattern": n} for n in ['GND', 'VBAT', '/VSYS', '/CELL_NEG']] +
        [{"netclass": "PowerFine", "pattern": n} for n in ['+3V3', '+3V3_SW', 'VBUS']] +
        [{"netclass": "USB", "pattern": "/USB_*"}]}
bd = d.setdefault('board', {}).setdefault('design_settings', {})
bd.setdefault('rules', {}).update({"min_clearance": 0.15, "min_track_width": 0.15, "min_via_diameter": 0.5,
    "min_through_hole_diameter": 0.3, "min_hole_to_hole": 0.25, "min_copper_edge_clearance": 0.3,
    "min_hole_clearance": 0.25, "min_silk_clearance": 0.0, "min_text_height": 0.8, "min_text_thickness": 0.08,
    "min_resolved_spokes": 1})
json.dump(d, open(p, 'w'), indent=2)
print('ok')
