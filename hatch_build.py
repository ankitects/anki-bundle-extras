import os
import shutil
import platform
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Build hook to copy platform-specific audio binaries."""
    
    def initialize(self, version, build_data):
        """Initialize the build hook and set platform tags."""
        # Determine platform and architecture from env vars or system detection
        system = os.environ.get("ANKI_AUDIO_TARGET_OS", platform.system()).lower()
        machine = os.environ.get("ANKI_AUDIO_TARGET_ARCH", platform.machine()).lower()
        
        # Set platform tags for wheel
        if system == "darwin":
            if machine == "arm64":
                src_dir = Path("mac/arm64/dist/audio/Resources")
                # Set wheel tags for macOS ARM64 with minimum macOS 11.0
                build_data["tag"] = "cp39-abi3-macosx_11_0_arm64"
            else:  # x86_64
                src_dir = Path("mac/amd64/dist/audio/Resources")
                # Set wheel tags for macOS x86_64 with minimum macOS 11.0
                build_data["tag"] = "cp39-abi3-macosx_11_0_x86_64"
            binary_files = ["mpv", "lame"]
            # Check for both 'lib' and 'libs' directories
            lib_dir = src_dir / "libs" if (src_dir / "libs").exists() else src_dir / "lib"
            lib_files = list(lib_dir.glob("*.dylib")) if lib_dir.exists() else []
        elif system == "windows":
            src_dir = Path("win/dist/audio")
            binary_files = ["mpv.exe", "lame.exe", "lame_enc.dll", "d3dcompiler_43.dll"]
            lib_files = []
            # Set wheel tags for Windows
            build_data["tag"] = "py3-none-win_amd64"
        else:
            # Linux or other - no binaries available
            return
        
        # Copy files to anki_audio directory
        dst_dir = Path(self.root) / "anki_audio"
        dst_dir.mkdir(exist_ok=True)
        
        # Copy main binaries
        for filename in binary_files:
            src_file = Path(self.root) / src_dir / filename
            if src_file.exists():
                shutil.copy2(src_file, dst_dir / filename)
        
        # Copy library files (for macOS) - preserve directory structure
        if lib_files:
            lib_dst_dir = dst_dir / lib_dir.name  # Use same dir name (lib or libs)
            lib_dst_dir.mkdir(exist_ok=True)
            for lib_file in lib_files:
                if lib_file.exists():
                    shutil.copy2(lib_file, lib_dst_dir / lib_file.name)
