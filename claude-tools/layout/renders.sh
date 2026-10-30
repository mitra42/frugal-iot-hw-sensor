#!/bin/bash
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
D=$(cd "$(dirname "$0")/../.." && pwd)/frugal_iot_v02
O=$D/../claude-tools/layout/out; mkdir -p $O; rm -f $O/renders.done
cd $D
$CLI pcb render --side top --width 2400 --height 2000 --quality high --floor -o $O/render_top.png frugal_iot_v02.kicad_pcb > $O/renders.log 2>&1
$CLI pcb render --side bottom --width 2400 --height 2000 --quality high --floor -o $O/render_bottom.png frugal_iot_v02.kicad_pcb >> $O/renders.log 2>&1
$CLI pcb export pdf --mode-single --layers F.Cu,F.Silkscreen,Edge.Cuts --drill-shape-opt 2 -o $O/copper_top.pdf frugal_iot_v02.kicad_pcb >> $O/renders.log 2>&1
$CLI pcb export pdf --mode-single --layers B.Cu,Edge.Cuts --mirror --drill-shape-opt 2 -o $O/copper_bottom.pdf frugal_iot_v02.kicad_pcb >> $O/renders.log 2>&1
touch $O/renders.done
