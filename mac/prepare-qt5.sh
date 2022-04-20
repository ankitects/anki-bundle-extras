#!/bin/bash

qtbase=~/Local/Qt
desktop=../../anki

arch -arch x86_64 python3 prepare-qt.py $qtbase/5.14.2 $desktop amd64/dist/pyqt5

mkdir -p ../dist
(cd amd64/dist/pyqt5 && tar czvf ../../../../dist/pyqt5.14-mac-amd64.tar.gz .)
