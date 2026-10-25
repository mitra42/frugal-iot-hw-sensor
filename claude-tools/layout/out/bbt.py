import pcbnew
b = pcbnew.LoadBoard('../../frugal_iot_v02/frugal_iot_v02.kicad_pcb'); mm = pcbnew.FromMM; V = pcbnew.VECTOR2I
for ref in ('R21', 'SW1', 'C1'):
    f = [x for x in b.GetFootprints() if x.GetReference() == ref][0]; r = f.Reference()
    r.SetTextSize(V(mm(0.8), mm(0.8))); r.SetTextThickness(mm(0.12))
    for a in (0, 90):
        r.SetTextAngleDegrees(a); r.SetPosition(V(mm(100), mm(100))); q = r.GetBoundingBox()
        print(ref, f.GetOrientationDegrees(), a, q.GetX() / 1e6, q.GetY() / 1e6, q.GetWidth() / 1e6, q.GetHeight() / 1e6)
    cy = f.GetCourtyard(pcbnew.F_CrtYd).BBox(); print(' cy', cy.GetX()/1e6, cy.GetY()/1e6, cy.GetWidth()/1e6, cy.GetHeight()/1e6, 'pos', f.GetPosition().x/1e6, f.GetPosition().y/1e6)
    for p in f.Pads(): q = p.GetBoundingBox(); print('  pad', p.GetNumber(), q.GetX()/1e6, q.GetY()/1e6, q.GetWidth()/1e6, q.GetHeight()/1e6)
