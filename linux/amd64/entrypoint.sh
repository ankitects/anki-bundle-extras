#!/bin/bash

set -e

qt5_ver=5.15.2
qt6_ver=6.2.2
fcitx_ver=5.0.9

build_and_copy() {
    qt=$1
    qt_capitalized=$2
    fcitx_suffix=$3

    make -j
    out=~/output/${qt}
    mkdir -p ${out}/{platforminputcontexts,dbusaddons}
    mv ${qt}/platforminputcontext/libfcitx${fcitx_suffix}platforminputcontextplugin.so ${out}/platforminputcontexts/
    mv ${qt}/dbusaddons/libFcitx${fcitx_suffix}${qt_capitalized}DBusAddons.so* ${out}/dbusaddons/
    pushd ${out}
    patchelf --set-rpath "\$ORIGIN/../../lib:\$ORIGIN/../dbusaddons" platforminputcontexts/*.so
    patchelf --set-rpath "\$ORIGIN/../../lib" dbusaddons/*.so
    popd
}

# fcitx4 qt5
cd ~/fcitx-qt5
cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_QT4=no \
    -DCMAKE_PREFIX_PATH=/qt/${qt5_ver}/gcc_64 .
build_and_copy qt5 Qt5 ""

# fcitx5 qt5
cd ~/fcitx5-qt
cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_QT4=no \
    -DCMAKE_PREFIX_PATH=/qt/${qt5_ver}/gcc_64 .
build_and_copy qt5 Qt5 5

# fcitx5 qt6
cd ~/fcitx5-qt
cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_QT4=no -DENABLE_QT5=no -DENABLE_QT6=yes \
   -DCMAKE_PREFIX_PATH=/qt/${qt6_ver}/gcc_64 .   
build_and_copy qt6 Qt6 5

cd ~/output && tar czf ../output.tar.gz .
