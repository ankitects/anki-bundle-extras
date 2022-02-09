#!/bin/bash
#
# Audio files must have been manually moved into dist/audio folder first.

mkdir -p ../dist
(cd dist && tar czvf ../../dist/audio-win-amd64.tar.gz .)
