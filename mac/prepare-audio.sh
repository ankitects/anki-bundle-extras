#!/bin/bash
#
# Audio files must have been manually moved into {arm,amd}64/dist folders first.

mkdir -p ../dist
(cd arm64/dist/audio && tar czvf ../../../../dist/audio-mac-arm64.tar.gz .)
(cd amd64/dist/audio && tar czvf ../../../../dist/audio-mac-amd64.tar.gz .)
