"""KiCad python: place every reference designator (0.8 mm / 0.12 mm) right next to its own part, so it can't be
read as belonging to a neighbour (Mitra, 15 Oct 2026: labels drifting up to 7 mm away were ambiguous).
Candidates hug the part's courtyard on each side (and sit inside big parts' outlines); a label must clear all
pads, silk graphics, other labels, big parts' outlines, holes and the edge, and must be nearer its own
courtyard than any other. Refs with no legal spot go to F.Fab and are listed (fix those by moving parts)."""
import pcbnew, math, json
PCB = '../../frugal_iot_v02/frugal_iot_v02.kicad_pcb'
b = pcbnew.LoadBoard(PCB); mm = pcbnew.FromMM; V = pcbnew.VECTOR2I
e = b.GetBoardEdgesBoundingBox(); EX0, EY0, EX1, EY1 = e.GetX() + mm(0.3), e.GetY() + mm(0.3), e.GetRight() - mm(0.3), e.GetBottom() - mm(0.3)
M = mm(0.12)
fps = list(b.GetFootprints())
padbox, silkpts, cy = [], [], {}
for f in fps:
    ref = f.GetReference()
    c = f.GetCourtyard(pcbnew.F_CrtYd)
    bb = c.BBox() if c.OutlineCount() else f.GetBoundingBox(False, False)
    cy[ref] = (bb.GetX(), bb.GetY(), bb.GetRight(), bb.GetBottom())
    for p in f.Pads():
        if p.IsOnLayer(pcbnew.F_Cu) or p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            q = p.GetBoundingBox(); padbox.append((q.GetX() - M, q.GetY() - M, q.GetRight() + M, q.GetBottom() + M))
    for g in f.GraphicalItems():
        if g.GetLayer() != pcbnew.F_SilkS or g.GetClass() in ('PCB_FIELD', 'PCB_TEXT'): continue
        q = g.GetBoundingBox()
        if g.GetClass() == 'PCB_SHAPE' and g.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            s, t = g.GetStart(), g.GetEnd(); n = max(1, int(math.hypot(t.x - s.x, t.y - s.y) / mm(0.2)))
            silkpts += [(s.x + (t.x - s.x) * i / n, s.y + (t.y - s.y) * i / n) for i in range(n + 1)]
        else:
            x0, y0, x1, y1 = q.GetX(), q.GetY(), q.GetRight(), q.GetBottom()
            n = max(1, int(max(x1 - x0, y1 - y0) / mm(0.2)))
            for i in range(n + 1):
                k = i / n
                silkpts += [(x0 + (x1 - x0) * k, y0), (x0 + (x1 - x0) * k, y1), (x0, y0 + (y1 - y0) * k), (x1, y0 + (y1 - y0) * k)]
for t in b.GetDrawings():                       # board-level silk text already placed (title, pin numbers)
    if t.GetLayer() == pcbnew.F_SilkS:
        q = t.GetBoundingBox(); padbox.append((q.GetX() - M, q.GetY() - M, q.GetRight() + M, q.GetBottom() + M))
placed = []
def rdist(px, py, r):
    dx = max(r[0] - px, 0, px - r[2]); dy = max(r[1] - py, 0, py - r[3]); return math.hypot(dx, dy)
def overlap(a, r, m=0): return a[0] < r[2] + m and r[0] < a[2] + m and a[1] < r[3] + m and r[1] < a[3] + m
WHY = {}
def ok(box, ref, inside_ok):
    x0, y0, x1, y1 = box
    if x0 < EX0 or y0 < EY0 or x1 > EX1 or y1 > EY1: return False
    if any(overlap(box, a) for a in padbox): WHY[ref+"pad"]=WHY.get(ref+"pad",0)+1; return False
    if any(overlap(box, a, M) for a in placed): return False
    for r2, c2 in cy.items():          # other parts: never over a hole or a big part's body; a small part's
        if r2 == ref: continue           # courtyard margin is fine as long as the label is nearer its own part
        big = (c2[2] - c2[0]) > mm(6) and (c2[3] - c2[1]) > mm(6)
        if (r2.startswith('H') or big) and overlap(box, c2): return False
    if any(x0 - M <= px <= x1 + M and y0 - M <= py <= y1 + M for px, py in silkpts): WHY[ref+"silk"]=WHY.get(ref+"silk",0)+1; return False
    cx, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
    own = rdist(cx, cy_, cy[ref])
    others = min(rdist(cx, cy_, c2) for r2, c2 in cy.items() if r2 != ref)
    if not own + mm(0.3) <= others: WHY[ref+"amb"]=WHY.get(ref+"amb",0)+1
    return own + mm(0.3) <= others
def candidates(f, r):
    ref = f.GetReference(); x0, y0, x1, y1 = cy[ref]
    w = x1 - x0; h = y1 - y0
    big = w > mm(6) and h > mm(6)
    out = []
    if big:                                      # inside a big part's outline, anywhere clear of its pads/silk
        cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
        pts = [(cxm + i * mm(0.5), cym + j * mm(0.5)) for i in range(-24, 25) for j in range(-24, 25)
               if x0 < cxm + i * mm(0.5) < x1 and y0 < cym + j * mm(0.5) < y1]
        pts.sort(key=lambda p: math.hypot(p[0] - cxm, p[1] - cym))
        out += [(x, y, a) for x, y in pts for a in (0, 90)]
    for gap in (mm(-0.2), mm(-0.1), mm(0.05), mm(0.3), mm(0.6), mm(1.0), mm(1.5)):   # may overlap own courtyard margin
        for ang in (0, 90):
            r.SetTextAngleDegrees(ang); r.SetPosition(V(0, 0)); tb = r.GetBoundingBox()
            tw, th = tb.GetWidth(), tb.GetHeight()
            steps = [0, -0.25, 0.25, -0.5, 0.5, -0.75, 0.75, -1.0, 1.0]
            for s in steps:
                out.append(((x0 + x1) / 2 + s * w, y0 - gap - th / 2, ang))          # above
                out.append(((x0 + x1) / 2 + s * w, y1 + gap + th / 2, ang))          # below
                out.append((x0 - gap - tw / 2, (y0 + y1) / 2 + s * h, ang))          # left
                out.append((x1 + gap + tw / 2, (y0 + y1) / 2 + s * h, ang))          # right
    return out
def area(f):
    x0, y0, x1, y1 = cy[f.GetReference()]; return (x1 - x0) * (y1 - y0)
fab = []; n = 0
for f in sorted(fps, key=area):                 # small parts first: they have the fewest options
    r = f.Reference()
    if f.GetReference().startswith('H'): r.SetVisible(False); continue
    r.SetLayer(pcbnew.F_SilkS); r.SetVisible(True)
    r.SetTextSize(V(mm(0.8), mm(0.8))); r.SetTextThickness(mm(0.12)); r.SetKeepUpright(True)
    found = None
    for x, y, ang in candidates(f, r):
        r.SetTextAngleDegrees(ang); r.SetPosition(V(int(x), int(y)))
        q = r.GetBoundingBox(); box = (q.GetX(), q.GetY(), q.GetRight(), q.GetBottom())
        if ok(box, f.GetReference(), True): found = box; break
    if found: placed.append(found); n += 1
    else:
        r.SetLayer(pcbnew.F_Fab); r.SetPosition(f.GetPosition()); fab.append(f.GetReference())
json.dump(dict(placed=n, to_fab=fab), open('/dev/null','w'))
print('placed', n, 'moved to F.Fab', fab)
print({k:v for k,v in WHY.items() if any(k.startswith(x) for x in ('SW1','U4','R21','C1','Q1'))})
