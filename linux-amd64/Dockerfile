FROM debian:11-slim

# jan 26 2022
ARG fcitx_commit=3d21a1c8b4e286dcfd955662366858ddf4823d02
ARG fcitx5_commit=fabc749efe84998a6a586444305ec5150dd38ac0

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
    bash \
    curl \
    g++ \
    gcc \
    git \
    ca-certificates \
    cmake \
    extra-cmake-modules \
    make \
    pkg-config \
    libxkbcommon-dev \
    libx11-dev \
    libfcitx5core-dev \
    libgl-dev \
    gettext \
    libdbus-1-dev \
    patchelf \ 
    fcitx-libs-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -d /state -m -u 998 user
USER user
WORKDIR /state

RUN git clone https://github.com/fcitx/fcitx5-qt.git \
    && cd fcitx5-qt \
    && git checkout ${fcitx5_commit} \
    && cd ~/ && git clone https://github.com/fcitx/fcitx-qt5.git \
    && cd fcitx-qt5 \
    && git checkout ${fcitx_commit}

COPY entrypoint.sh .
ENTRYPOINT ["/state/entrypoint.sh"]
