#!/bin/bash
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
T=/Users/mitra/Claude/frugal-layout/frugal-iot-v0.2/claude-tools/schematic
mkdir -p $T/out; cd $T && $PY draw.py "$@" > out/draw.log 2>&1
echo "exit $?" >> out/draw.log
