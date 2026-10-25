import pcbnew
b = pcbnew.LoadBoard('../../frugal_iot_v02/frugal_iot_v02.kicad_pcb')
L = []
for f in b.GetFootprints():
    for p in f.Pads():
        q = p.GetBoundingBox(); L.append(((q.GetWidth() * q.GetHeight()) / 1e12, f.GetReference(), p.GetNumber(), q.GetWidth() / 1e6, q.GetHeight() / 1e6, p.IsOnLayer(pcbnew.F_Cu)))
for x in sorted(L, reverse=True)[:8]: print(x)
r = [f for f in b.GetFootprints() if f.GetReference() == 'R16'][0]
c = r.GetCourtyard(pcbnew.F_CrtYd); print('R16 cy', c.OutlineCount(), c.BBox().GetWidth() / 1e6, c.BBox().GetHeight() / 1e6, r.GetPosition().x / 1e6, r.GetPosition().y / 1e6)
