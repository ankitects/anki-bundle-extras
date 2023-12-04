#!/bin/bash
#
# Expects to be run on arm64 machine.
#

qtbase=~/Local/Qt
desktop=../../anki
qtver=6.6.1
qtvershort=6.6

python3 prepare-qt.py $qtbase/$qtver $desktop arm64/dist/pyqt6
arch -arch x86_64 python3 prepare-qt.py $qtbase/$qtver $desktop amd64/dist/pyqt6

mkdir -p ../dist
(cd arm64/dist/pyqt6 && tar -c --use-compress-program 'zstd --long -19 -T0' -vf ../../../../dist/pyqt${qtvershort}-mac-arm64.tar.zst .)
(cd amd64/dist/pyqt6 && tar -c --use-compress-program 'zstd --long -19 -T0' -vf ../../../../dist/pyqt${qtvershort}-mac-amd64.tar.zst .)
