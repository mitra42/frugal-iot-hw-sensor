"""KiCad python: list GND pads sitting in small detached F.Cu/B.Cu pour islands (< 15 mm2) -> stdout 'REF:PAD,...'"""
import pcbnew
b = pcbnew.LoadBoard('../../frugal_iot_v02/frugal_iot_v02.kicad_pcb')
small = []
for z in b.Zones():
    if z.GetNetname() != 'GND': continue
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        if not z.IsOnLayer(layer): continue
        fp = z.GetFilledPolysList(layer)
        for i in range(fp.OutlineCount()):
            o = fp.Outline(i); a = abs(o.Area()) / 1e12
            if a < 15: small.append((layer, o, a))
hits = []
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetname() != 'GND': continue
        for layer, o, a in small:
            if p.IsOnLayer(layer) and o.PointInside(p.GetPosition()):
                hits.append(f'{f.GetReference()}:{p.GetNumber()}')
print(','.join(sorted(set(hits))))
