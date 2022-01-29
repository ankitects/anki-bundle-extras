#!/bin/bash

set -e

rm -rf dist/audio
mkdir -p dist/audio
cd dist/audio
mkdir libs
cp /opt/homebrew/bin/mpv .
cp /opt/homebrew/bin/lame .
dylibbundler -x mpv -d libs -p @executable_path/libs/ -b
for f in dist/audio/{mpv,lame,libs/*}; do
    codesign --remove-signature $f
    codesign -vvvv -o runtime -s 'Developer ID Application:' $f
done
