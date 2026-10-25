"""KiCad python: add one GND via as close as possible to a GND pad (via may overlap the pad itself),
checked against all other-net copper on both layers. Usage: via_near.py REF:PAD [REF:PAD ...]"""
import pcbnew, math, sys
PCB = '../../frugal_iot_v02/frugal_iot_v02.kicad_pcb'
b = pcbnew.LoadBoard(PCB); mm = pcbnew.FromMM; V = pcbnew.VECTOR2I
CLR, R = mm(0.2), mm(0.3)
other = []
for t in b.GetTracks():
    if t.GetNetname() == 'GND': continue
    if t.GetClass() == 'PCB_VIA': other.append(('c', t.GetPosition().x, t.GetPosition().y, t.GetWidth() / 2))
    else: other.append(('s', t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetWidth() / 2))
pads = {}
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetname() == 'GND':
            pads[(f.GetReference(), p.GetNumber())] = p
        else:
            bb = p.GetBoundingBox(); other.append(('b', bb.GetX(), bb.GetY(), bb.GetRight(), bb.GetBottom()))
e = b.GetBoardEdgesBoundingBox()
def ok(x, y):
    if not (e.GetX() + mm(0.6) < x < e.GetRight() - mm(0.6) and e.GetY() + mm(0.6) < y < e.GetBottom() - mm(0.6)): return False
    for o in other:
        if o[0] == 'c' and math.hypot(x - o[1], y - o[2]) < o[3] + R + CLR: return False
        if o[0] == 'b' and o[1] - R - CLR < x < o[3] + R + CLR and o[2] - R - CLR < y < o[4] + R + CLR: return False
        if o[0] == 's':
            ax, ay, bx, by, w = o[1:]; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
            u = 0 if L2 == 0 else max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L2))
            if math.hypot(ax + u * dx - x, ay + u * dy - y) < w + R + CLR: return False
    return True
gnd = b.FindNet('GND'); res = {}
for a in sys.argv[1:]:
    r, n = a.split(':'); p = pads[(r, n)]; c = p.GetPosition()
    best = None
    for i in range(-30, 31):
        for j in range(-30, 31):
            x, y = c.x + mm(0.05) * i, c.y + mm(0.05) * j
            d = math.hypot(x - c.x, y - c.y)
            bb = p.GetBoundingBox()
            inpad = bb.GetX() - R < x < bb.GetRight() + R and bb.GetY() - R < y < bb.GetBottom() + R
            key = (1 if inpad else 0, d)
            if ok(x, y) and (best is None or key < best[3]): best = (d, x, y, key)
    if best is None: res[a] = 'none'; continue
    d, x, y, _ = best
    if _[0]: print(a, 'via overlaps the pad (via-in-pad)')
    v = pcbnew.PCB_VIA(b); v.SetPosition(V(int(x), int(y))); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(gnd); b.Add(v)
    if d > p.GetBoundingBox().GetWidth() / 2:
        t = pcbnew.PCB_TRACK(b); t.SetStart(c); t.SetEnd(V(int(x), int(y))); t.SetWidth(mm(0.3)); t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t)
    res[a] = round(d / 1e6, 2)
pcbnew.SaveBoard(PCB, b)
print(res)
