#!/bin/bash
#
# Expects to be run on arm64 machine.
#

qtbase=~/Local/Qt
desktop=../../dtop

python3 prepare-qt.py $qtbase/6.2.3 $desktop arm64/dist/pyqt6
arch -arch x86_64 python3 prepare-qt.py $qtbase/6.2.3 $desktop amd64/dist/pyqt6

mkdir -p ../dist
(cd arm64/dist/pyqt6 && tar czvf ../../../../dist/pyqt6.2-mac-arm64.tar.gz .)
(cd amd64/dist/pyqt6 && tar czvf ../../../../dist/pyqt6.2-mac-amd64.tar.gz .)
