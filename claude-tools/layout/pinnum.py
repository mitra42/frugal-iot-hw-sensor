"""KiCad python: silkscreen '1' and '10' at the ends of the J2+J12 and J3+J13 terminal pairs (D18)."""
import pcbnew
PCB = '../../frugal_iot_v02/frugal_iot_v02.kicad_pcb'
b = pcbnew.LoadBoard(PCB); mm = pcbnew.FromMM; V = pcbnew.VECTOR2I
pos = {}
for f in b.GetFootprints():
    for p in f.Pads(): pos[(f.GetReference(), p.GetNumber())] = p.GetPosition()
for ref, pad, label, dx, dy in (('J2', '1', '1', 2.6, -3.1), ('J12', '5', '10', 2.6, 3.1),
                                ('J3', '1', '1', -2.6, 3.1), ('J13', '5', '10', -2.6, -3.1)):
    c = pos[(ref, pad)]
    t = pcbnew.PCB_TEXT(b); t.SetText(label); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(V(mm(1.0), mm(1.0))); t.SetTextThickness(mm(0.15))
    t.SetPosition(V(c.x + mm(dx), c.y + mm(dy))); b.Add(t)
pcbnew.SaveBoard(PCB, b); print('ok')
