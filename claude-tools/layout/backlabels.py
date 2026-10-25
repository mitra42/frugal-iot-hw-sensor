"""KiCad python: name every connector pin on the BACK silkscreen, beside its pad, so a board can be wired
without the docs (Mitra, D33): G = GND, V = 3V3_SW, SDA/SCL, A/B (RS485), a bare number = that GPIO,
+/- with SOLAR (J6) and CELL (J4), and an LED symbol (anode -> cathode) at J7. Re-runnable."""
import pcbnew
PCB = '../../frugal_iot_v02/frugal_iot_v02.kicad_pcb'
TITLE = 'Frugal-IoT V0.2'
b = pcbnew.LoadBoard(PCB); mm = pcbnew.FromMM; V = pcbnew.VECTOR2I
NET = {'GND': 'G', '+3V3_SW': 'V', '/I2C_SDA': 'SDA', '/I2C_SCL': 'SCL', '/J3_P2': 'A', '/J3_P3': 'B',
       '/SENS1': '0', '/SENS2': '1', '/GPIO2': '2', '/GPIO4': '4', '/GPIO10': '10'}
# ---- read everything first (pcbnew SWIG: no reads after mutating the board) ----
fps = {f.GetReference(): f for f in b.GetFootprints()}
def pads(ref): return [(p.GetNumber(), p.GetPosition().x, p.GetPosition().y, p.GetNetname()) for p in fps[ref].Pads()]
P = {r: pads(r) for r in ('J2', 'J12', 'J3', 'J13', 'J5', 'J6', 'J4', 'J7')}
e = b.GetBoardEdgesBoundingBox(); CX = (e.GetX() + e.GetRight()) / 2; CY = (e.GetY() + e.GetBottom()) / 2
old = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.B_SilkS and not (d.GetClass() == 'PCB_TEXT' and d.GetText() == TITLE)]
# ---- mutate ----
for d in old: b.Remove(d)
def text(s, x, y, h=1.0, near=None):
    """Back-side text centred at (x, y); with near=(px, side) its inner edge sits 1.2 mm from the pad."""
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(pcbnew.B_SilkS); t.SetMirrored(True)
    t.SetTextSize(V(mm(h), mm(h))); t.SetTextThickness(mm(max(0.15, h * 0.16)))
    t.SetPosition(V(int(x), int(y))); w = t.GetBoundingBox().GetWidth()
    if near:
        px, side = near; t.SetPosition(V(int(px + side * (mm(1.25) + w / 2)), int(y)))
    b.Add(t); return t
def line(x0, y0, x1, y1, w=0.15):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.B_SilkS)
    s.SetStart(V(int(x0), int(y0))); s.SetEnd(V(int(x1), int(y1))); s.SetWidth(mm(w)); b.Add(s)
# terminal blocks along the short edges: label on the inboard side of each pad
for ref in ('J2', 'J12', 'J3', 'J13'):
    for num, x, y, net in P[ref]:
        side = 1 if x < CX else -1
        text(NET[net], x, y, near=(x, side))
# J5 (top edge): label below each pad
for num, x, y, net in P['J5']: text(NET[net], x, y + mm(1.9))
# J6 (bottom edge, external 5 V / solar) and J4 (cell): polarity above each pad, name above that
for ref, name, plus in (('J6', 'SOLAR', 'VBUS'), ('J4', 'CELL', 'VBAT')):
    xs = []
    for num, x, y, net in P[ref]:
        text('+' if net == plus else '-', x, y - mm(2.1), 1.4); xs.append(x); yy = y
    text(name, sum(xs) / 2, yy - mm(3.9), 1.0)
# J7 (external LED, pin 1 = anode, pin 2 = cathode): diode symbol beside the pads, pointing anode -> cathode
(n1, x1, y1, _), (n2, x2, y2, _) = sorted(P['J7'])
side = 1 if x1 < CX else -1
gx = x1 + side * mm(2.2); a, k = (y1, y2) if n1 == '1' else (y2, y1)
d = 1 if k > a else -1; h = mm(0.7)
mid_a, mid_k = a + d * mm(0.75), a + d * mm(1.75)
line(gx, a, gx, mid_a); line(gx, mid_k, gx, k)                          # leads
line(gx - h, mid_a, gx + h, mid_a); line(gx - h, mid_a, gx, mid_k); line(gx + h, mid_a, gx, mid_k)   # triangle
line(gx - h, mid_k, gx + h, mid_k)                                    # bar (cathode)
text('LED', gx + side * mm(2.2), (a + k) / 2, 0.8)
pcbnew.SaveBoard(PCB, b); print('back labels placed')
