"""KiCad python: for checking JLCPCB's assembly preview. Prints each part's centre, rotation, and where pin 1
(cathode for diodes/LEDs) sits relative to the centre (board view, +x right, +y down), plus the pin-1 net."""
import pcbnew
b = pcbnew.LoadBoard('../../frugal_iot_v02/frugal_iot_v02.kicad_pcb'); t = pcbnew.ToMM
for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    r = f.GetReference()
    if f.IsDNP() or r[0] == 'H' or r.startswith('JP'): continue
    c = f.GetPosition(); pads = {p.GetNumber(): p for p in f.Pads()}
    out = []
    for n in ('1', 'A1', 'K', 'A'):
        if n in pads:
            p = pads[n]; q = p.GetPosition()
            out.append(f"pad {n} at ({t(q.x-c.x):+.2f},{t(q.y-c.y):+.2f}) net {p.GetNetname()}")
    print(r, f.GetFPID().GetLibItemName(), f"rot {f.GetOrientationDegrees():.0f}", ' | '.join(out))
