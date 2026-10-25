import pcbnew, json, sys
b = pcbnew.LoadBoard(sys.argv[1] if len(sys.argv) > 1 else '../../frugal_iot_v02/frugal_iot_v02.kicad_pcb')
json.dump([{"ref": f.GetReference(), "pad": p.GetNumber(), "net": str(p.GetNetname()),
            "x": p.GetPosition().x / 1e6, "y": p.GetPosition().y / 1e6} for f in b.GetFootprints() for p in f.Pads()],
          open('out/pads.json', 'w'))
print('ok')
