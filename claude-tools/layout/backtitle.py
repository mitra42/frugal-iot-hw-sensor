"""KiCad python: board title on the BACK silkscreen (the back carries no parts, so it can be large and is
never crowded out by the front's labels - D32). Removes any earlier front-side title."""
import pcbnew, sys
TEXT = sys.argv[1] if len(sys.argv) > 1 else 'Frugal-IoT V0.2'
PCB = '../../frugal_iot_v02/frugal_iot_v02.kicad_pcb'
b = pcbnew.LoadBoard(PCB); mm = pcbnew.FromMM; V = pcbnew.VECTOR2I
e = b.GetBoardEdgesBoundingBox(); cx, cy = (e.GetX() + e.GetRight()) // 2, (e.GetY() + e.GetBottom()) // 2
old = [d for d in b.GetDrawings() if d.GetClass() == 'PCB_TEXT' and d.GetText() == TEXT]
for d in old: b.Remove(d)
t = pcbnew.PCB_TEXT(b); t.SetText(TEXT); t.SetLayer(pcbnew.B_SilkS); t.SetMirrored(True)
t.SetTextSize(V(mm(2.5), mm(2.5))); t.SetTextThickness(mm(0.35)); t.SetPosition(V(cx, cy))
b.Add(t); pcbnew.SaveBoard(PCB, b); print('back title at board centre, removed', len(old), 'earlier')
