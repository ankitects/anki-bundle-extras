#!/bin/bash

set -e

DOCKER_BUILDKIT=1 docker build --tag anki-deps .
# expects ~/Local/Qt to contain official Qt 5.15/6.2 installs
docker run -it --name anki-deps \
    -v $HOME/Local/Qt:/qt \
    anki-deps
docker cp anki-deps:/state/output.tar.gz linux-amd64.tar.gz
docker container rm anki-deps
docker image rm anki-deps
