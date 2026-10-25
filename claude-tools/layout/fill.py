import pcbnew
PCB = '../../frugal_iot_v02/frugal_iot_v02.kicad_pcb'
b = pcbnew.LoadBoard(PCB)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(PCB, b); print('filled')
