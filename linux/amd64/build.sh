#!/bin/bash

set -e

DOCKER_BUILDKIT=1 docker build --tag anki-deps .
# expects ~/Local/qt to contain official Qt 5.15/6.2 installs
docker run -it --name anki-deps \
    -v $HOME/Local/qt:/qt \
    anki-deps
mkdir -p ../../dist
docker cp anki-deps:/state/output.tar.gz ../../dist/qt-plugins-linux-amd64.tar.gz
docker container rm anki-deps
docker image rm anki-deps
