"""Placement for Frugal-IoT V0.2. Plain python (no KiCad needed).
Inputs: fp.json (fpmeasure.py), ../schematic/out/netlist.xml, blocks.json. Output: placement.json, metrics.
Board: L x 37 mm, origin top-left, y down (KiCad). Rotation in KiCad degrees (CCW on screen).
Decisions: 37 mm high as v0.1 (D2); J2+J12 on the left edge, J3+J13 on the right edge, wire entries outward;
USB-C, J6 (aux 5 V holes) and J4 (cell) on the bottom edge; J5 on the top edge; 4x M2 holes at the corners;
all SMD on the top side."""
import json, math, sys, xml.etree.ElementTree as ET
from collections import defaultdict
W = float(sys.argv[1]) if len(sys.argv) > 1 else 64.0
H = 37.0
FP = json.load(open('fp.json'))
NL = ET.parse('../schematic/out/netlist.xml').getroot()
NETS = defaultdict(list)
for n in NL.iter('net'):
    for node in n.iter('node'): NETS[n.get('name')].append((node.get('ref'), node.get('pin')))
POUR = {'/GND', 'GND'}
HOLE_R = 2.8                                   # M2: 4.9 mm keep-out + margin
HOLES = {'H1': (2.5, 2.5), 'H2': (W - 2.5, 2.5), 'H3': (2.5, H - 2.5), 'H4': (W - 2.5, H - 2.5)}
EDGE = 0.6

def rot_pt(x, y, r):
    a = math.radians(r); c, s = round(math.cos(a), 9), round(math.sin(a), 9)
    return x * c + y * s, -x * s + y * c
def rect_of(ref, x, y, r):
    b = FP[ref]['bbox']
    pts = [rot_pt(px, py, r) for px in (b[0], b[2]) for py in (b[1], b[3])]
    xs = [x + p[0] for p in pts]; ys = [y + p[1] for p in pts]
    return [min(xs), min(ys), max(xs), max(ys)]
def pads_of(ref, x, y, r):
    return {k: (x + rot_pt(*v, r)[0], y + rot_pt(*v, r)[1]) for k, v in FP[ref]['pads'].items()}

P = {}
# ---------------- anchors ----------------
# Terminal blocks: wire entry is local +y. Left edge rot -90 (entry -x, pins run down from pin 1);
# right edge rot 90 (entry +x, pins run up). Two 5-way blocks butt together at 2.54 mm pitch.
PX = 3.95                                       # pin row 3.95 mm in: body front flush with the board edge
Y0 = H / 2 - 11.43                              # centres the 10-way pair vertically
P['J2'] = (PX, Y0, -90); P['J12'] = (PX, Y0 + 12.7, -90)
P['J3'] = (W - PX, Y0 + 22.86, 90); P['J13'] = (W - PX, Y0 + 10.16, 90)
# Module along the top, pins at its ends; U.FL socket on the module itself
XU = 27.0
P['U4'] = (XU, 8.3, 0)
# Bottom edge: USB-C mouth (local +y) down, below the module's USB pins; J6 holes beside it; J4 cell connector
P['J1'] = (XU + 11.5, H - 3.65, 0)
P['J6'] = (XU + 19.7, H - 3.95, 0)
P['J4'] = (13.5, H - 6.5, 0)
# Top edge, right: J5 (GND / GPIO10 / 3V3_SW), entry up
P['J5'] = (W - 10.6, 3.95, 180)

BLK = json.load(open('blocks.json'))
for r in ('J2', 'J12', 'J3', 'J13', 'U4', 'J1', 'J6', 'J4', 'J5'): BLK.pop(r, None)
R = lambda x0, y0, x1, y1: (x0, y0, x1, y1)
REGION = {
    'mcu':   R(8.0, 0.0, 46.0, 21.0),
    'usb':   R(30.0, 24.0, 52.0, H),
    'chg':   R(8.0, 19.0, 34.0, H),
    'pwr':   R(8.0, 13.0, 48.0, 33.0),
    'conn':  R(8.0, 0.0, W - 8.0, H),
    'rs485': R(44.0, 8.0, W - 8.0, H),
}
NEAR = {'C1': ('U1', '4'), 'C2': ('U1', '5'), 'C3': ('U2', '3'), 'C4': ('U3', '1'), 'C5': ('U3', '5'),
        'C7': ('Q2', '3'), 'C8': ('U4', '1'), 'C9': ('U4', '1'), 'C10': ('U4', '2'), 'C13': ('U5', '8'),
        'R1': ('J1', 'A5'), 'R2': ('J1', 'B5'), 'R3': ('U1', '2'), 'R4': ('U1', '2'), 'JP1': ('R4', '2'),
        'R11': ('U4', '2'), 'R12': ('U4', '8'), 'R13': ('U4', '16'), 'R14': ('U4', '7'),
        'R16': ('U4', '5'), 'R17': ('U4', '6'), 'C6': ('R9', '1'), 'R10': ('Q2', '1'),
        'JP2': ('J3', '2'), 'JP3': ('J3', '3')}
NEAR_W = 6.0
ORDER = ['mcu', 'usb', 'chg', 'pwr', 'rs485', 'conn']
GAP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.7   # courtyard spacing: room for refdes labels (D30)
def free(rr, placed_rects, region):
    if rr[0] < max(EDGE, region[0]) or rr[1] < max(EDGE, region[1]) or rr[2] > min(W - EDGE, region[2]) \
            or rr[3] > min(H - EDGE, region[3]): return False
    for hx, hy in HOLES.values():
        cx = min(max(hx, rr[0]), rr[2]); cy = min(max(hy, rr[1]), rr[3])
        if math.hypot(cx - hx, cy - hy) < HOLE_R: return False
    for q in placed_rects:
        if rr[0] < q[2] + GAP and q[0] < rr[2] + GAP and rr[1] < q[3] + GAP and q[1] < rr[3] + GAP: return False
    return True
rects = {r: rect_of(r, *P[r]) for r in P}
def partners(ref):
    out = []
    for net, nodes in NETS.items():
        if net in POUR: continue
        mine = [p for r, p in nodes if r == ref]
        if not mine: continue
        w = 1.0 / max(1, len(nodes) - 1)
        for r, p in nodes:
            if r != ref and r in P: out.append((mine, pads_of(r, *P[r])[p], w))
    return out
def cost(ref, x, y, r, prt):
    pads = pads_of(ref, x, y, r)
    c = sum(w * min(math.dist(pads[m], q) for m in mine if m in pads) for mine, q, w in prt)
    if ref in NEAR and NEAR[ref][0] in P:
        q = pads_of(NEAR[ref][0], *P[NEAR[ref][0]])[NEAR[ref][1]]
        c += NEAR_W * min(math.dist(v, q) for v in pads.values())
    return c
area = lambda r: (FP[r]['bbox'][2] - FP[r]['bbox'][0]) * (FP[r]['bbox'][3] - FP[r]['bbox'][1])
def place_one(ref, region):
    prt = partners(ref)
    if ref in NEAR and NEAR[ref][0] in P:
        tx, ty = pads_of(NEAR[ref][0], *P[NEAR[ref][0]])[NEAR[ref][1]]
    elif prt:
        tw = sum(w for _, _, w in prt)
        tx = sum(q[0] * w for _, q, w in prt) / tw; ty = sum(q[1] * w for _, q, w in prt) / tw
    else:
        tx, ty = (region[0] + region[2]) / 2, (region[1] + region[3]) / 2
    tx = min(max(tx, region[0]), region[2]); ty = min(max(ty, region[1]), region[3])
    cands = []; first = None; step = 0.25
    for ring in range(0, 160):
        rad = ring * step
        if first is not None and rad > first + 3.0: break
        n = max(1, int(2 * math.pi * rad / step))
        for k in range(n):
            a = 2 * math.pi * k / n
            x = round((tx + rad * math.cos(a)) / 0.05) * 0.05; y = round((ty + rad * math.sin(a)) / 0.05) * 0.05
            for r in (0, 90, 180, 270):
                rr = rect_of(ref, x, y, r)
                if free(rr, rects.values(), region):
                    cands.append((cost(ref, x, y, r, prt), x, y, r))
                    if first is None: first = rad
    if not cands: return False
    c, x, y, r = min(cands)
    P[ref] = (x, y, r); rects[ref] = rect_of(ref, x, y, r); return True
for b in ORDER:
    todo = [r for r in FP if BLK.get(r) == b and r not in P]
    while todo:
        ready = [r for r in todo if r not in NEAR or NEAR[r][0] in P] or todo
        best = max(ready, key=lambda r: (round(sum(w for _, _, w in partners(r)), 3), area(r)))
        reg = list(REGION[b]); grow = 0
        while not place_one(best, reg):
            grow += 2; reg = [reg[0] - 2, reg[1] - 2, reg[2] + 2, reg[3] + 2]
            if grow > 40: sys.exit(f'cannot place {best} in {b}')
        if grow: print(f'  {best} ({b}) needed region +{grow} mm')
        todo.remove(best)
# ---------------- metrics ----------------
def mst(pts):
    if len(pts) < 2: return [], 0.0
    inn = [0]; edges = []; tot = 0.0
    rest = set(range(1, len(pts)))
    while rest:
        d, a, b = min((math.dist(pts[i], pts[j]), i, j) for i in inn for j in rest)
        edges.append((pts[a], pts[b])); tot += d; inn.append(b); rest.remove(b)
    return edges, tot
def cross(e, f):
    (a, b), (c, d) = e, f
    if len({a, b, c, d}) < 4: return False
    o = lambda p, q, r: (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0])
    return (o(a, b, c) * o(a, b, d) < 0) and (o(c, d, a) * o(c, d, b) < 0)
allpads = {r: pads_of(r, *P[r]) for r in P}
E = []; L = 0.0
for net, nodes in NETS.items():
    if net in POUR: continue
    pts = list({allpads[r][p] for r, p in nodes if p in allpads[r]})
    e, t = mst(pts); L += t; E += [(net, x) for x in e]
X = sum(1 for i in range(len(E)) for j in range(i + 1, len(E)) if E[i][0] != E[j][0] and cross(E[i][1], E[j][1]))
json.dump(dict(W=W, H=H, holes=HOLES, place={r: [round(v[0], 3), round(v[1], 3), v[2]] for r, v in P.items()}),
          open('placement.json', 'w'), indent=0)
print(f'board {W} x {H}: placed {len(P)}; ratsnest {L:.0f} mm excl. GND; crossings {X}')
