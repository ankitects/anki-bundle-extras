#!/bin/bash

# build_wheels.sh - Build anki-audio wheels for all platforms
# Uses environment variables to control target platform
#
# You can also build individual wheels manually:
#   ANKI_AUDIO_TARGET_OS=darwin ANKI_AUDIO_TARGET_ARCH=arm64 uv build
#   ANKI_AUDIO_TARGET_OS=darwin ANKI_AUDIO_TARGET_ARCH=x86_64 uv build  
#   ANKI_AUDIO_TARGET_OS=windows ANKI_AUDIO_TARGET_ARCH=amd64 uv build

set -e

echo "Building anki-audio wheels for all platforms..."

# Clean up any existing builds
rm -rf dist/ anki_audio/
mkdir -p anki_audio
touch anki_audio/__init__.py

# Function to build wheel for specific platform
build_wheel() {
    local os=$1
    local arch=$2
    local description=$3
    
    echo "Building $description wheel..."
    
    # Clean for build
    rm -rf anki_audio/
    mkdir -p anki_audio
    touch anki_audio/__init__.py
    
    # Set environment variables and build
    ANKI_AUDIO_TARGET_OS="$os" ANKI_AUDIO_TARGET_ARCH="$arch" uv build --wheel
    
    echo "Built $description wheel"
    rm -rf anki_audio/
}

# Build all platforms
build_wheel "darwin" "arm64" "macOS ARM64"
build_wheel "darwin" "x86_64" "macOS x86_64"  
build_wheel "windows" "amd64" "Windows"

echo ""
echo "All wheels built successfully:"
ls -la dist/*.whl

echo ""
echo "Wheel sizes:"
du -h dist/*.whl