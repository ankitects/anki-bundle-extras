#!/bin/bash
#
# A mirror of some plugins available on the NSIS wiki:
#
# https://nsis.sourceforge.io/NsProcess_plugin (implicit zlib license: https://forums.winamp.com/forum/developer-center/nsis-discussion/207975-nsprocess-plugin/page5?postcount=68#post4378893)

mkdir -p ../dist
cd ../dist
curl -Lo nsprocess.7z 'http://forums.winamp.com/attachment.php?attachmentid=48936&d=1309248568'
7z x nsprocess.7z Plugin/nsProcess.dll
rm nsprocess.7z
cd Plugin
tar -cvf - * | zstd --long -19 -T0 > ../nsis.tar.zst
cd ..
rm -rf Plugin
