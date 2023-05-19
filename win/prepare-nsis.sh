#!/bin/bash
#
# A mirror of some plugins available on the NSIS wiki:
#
# https://nsis.sourceforge.io/NsProcess_plugin (implicit zlib license: https://forums.winamp.com/forum/developer-center/nsis-discussion/207975-nsprocess-plugin/page5?postcount=68#post4378893)
# https://nsis.sourceforge.io/UnicodePathTest_plug-in (LGPL)

mkdir -p ../dist
cd ../dist
curl -Lo nsprocess.7z 'http://forums.winamp.com/attachment.php?attachmentid=48936&d=1309248568'
7z x nsprocess.7z Plugin/nsProcess.dll
rm nsprocess.7z
curl -Lo unicode.zip 'https://nsis.sourceforge.io/mediawiki/images/a/a7/UnicodePathTest_1.0.zip'
unzip unicode.zip Plugin/UnicodePathTest.dll
rm unicode.zip
cd Plugin
tar -cvf - * | zstd --long -19 -T0 > ../nsis.tar.zst
cd ..
rm -rf Plugin
