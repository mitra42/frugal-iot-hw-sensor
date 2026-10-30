"""KiCad python: (1) DNP flags from the schematic for parts whose fitting changed (D31);
(2) '+' / '-' and a name on the silkscreen above the hand-soldered power connectors J6 (external 5 V,
e.g. a solar panel) and J4 (cell), one sign above each pad (D32). Run silk.py afterwards."""
import pcbnew
PCB = '../../frugal_iot_v02/frugal_iot_v02.kicad_pcb'
b = pcbnew.LoadBoard(PCB); mm = pcbnew.FromMM; V = pcbnew.VECTOR2I
FIT = {'J13', 'R18', 'C12', 'J4', 'J6'}   # J4, J6 fitted from D34
NOTE = {'R18': 'pull-up (e.g. DS18B20)', 'C12': 'filter (analog)'}   # as circuit.py
fp = {f.GetReference(): f for f in b.GetFootprints()}
# read everything first (pcbnew SWIG: no reads after mutating the board)
pads = lambda r: {p.GetNumber(): p.GetPosition() for p in fp[r].Pads()}
p6 = pads('J6'); top = fp['J6'].GetCourtyard(pcbnew.F_CrtYd).BBox().GetY() - mm(0.9)
p4 = pads('J4')
for r in FIT:
    fp[r].SetDNP(False)
    fp[r].SetAttributes(fp[r].GetAttributes() & ~pcbnew.FP_EXCLUDE_FROM_BOM & ~pcbnew.FP_EXCLUDE_FROM_POS_FILES)
for r, n in NOTE.items():
    for fld in fp[r].GetFields():
        if fld.GetName() == 'Note': fld.SetText(n)
for t in list(b.GetDrawings()):                     # re-runnable: drop our earlier labels
    if t.GetClass() == 'PCB_TEXT' and t.GetLayer() == pcbnew.F_SilkS and t.GetText() in ('+', '-', '5V IN', 'CELL', '+5V'):
        b.Remove(t)
def text(s, x, y, h):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(V(mm(h), mm(h))); t.SetTextThickness(mm(max(0.15, h * 0.17))); t.SetPosition(V(int(x), int(y))); b.Add(t)
# J6 (external 5 V): above each pad, clear of the block's outline
text('+', p6['1'].x, top, 1.4); text('-', p6['2'].x, top, 1.4)
# J4 (cell): either side of the pin row, outboard of the pads
text('-', p4['1'].x - mm(3.3), p4['1'].y, 1.4); text('+', p4['2'].x + mm(3.3), p4['2'].y, 1.4)
pcbnew.SaveBoard(PCB, b); print('ok')
