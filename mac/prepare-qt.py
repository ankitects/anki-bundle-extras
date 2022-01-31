#!/usr/bin/env python
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#
# PyQt munges the layout of the Qt .framework files, presumably to make them run
# correctly in command-line Python invocations. These fail to codesign, so we
# use the libs distributed directly by Qt. We sign the PyQt Python libs at the same
# time, and do the signing in advance, so the entire PyQt folder can be copied
# into the bundle quickly.
#
# To update:
#
# - Use the official Qt installer to install 5.14.x and 6.2.x. Install latest
#   base macOS, plus the following modules:
#
#     - WebEngine
#     - WebChannel
#     - Positioning
#     - Multimedia

from __future__ import annotations

from enum import Enum
import shutil
import sys, os
import re
from pathlib import Path
from typing import Iterator
import subprocess
import platform


class Arch(Enum):
    arm64 = "arm64"
    amd64 = "x86_64"

    @staticmethod
    def current() -> Arch:
        return Arch.arm64 if platform.machine() == "arm64" else Arch.amd64


def get_pyqt_root(qt_major: int) -> Path:
    repo = "pyqt6" if qt_major == 6 else "pyqt514"
    # ensure pyqt is downloaded
    subprocess.run(
        ["bazel", "query", f"@{repo}//:*"],
        cwd=anki_repo,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    # get folder
    base = (
        subprocess.run(
            ["bazel", "info", "output_base"],
            cwd=anki_repo,
            check=True,
            capture_output=True,
        )
        .stdout.decode("utf8")
        .strip()
    )
    path = Path(base) / "external" / repo / f"PyQt{qt_major}"
    return path


def lipo(path: Path, target_arch: Arch):
    if qt_version == "qt5":
        return
    handle = subprocess.run(
        ["lipo", path, "-thin", target_arch.value, "-output", str(path) + ".tmp"],
        capture_output=True,
    )
    if handle.returncode == 0:
        shutil.move(str(path) + ".tmp", path)
    elif b"must be a fat file" not in handle.stderr:
        raise Exception(handle.stderr)


def codesign(path: Path, extra_args: list[str] = None) -> None:
    codesign_args = [
        "codesign",
        "-vvvv",
        "-o",
        "runtime",
        "-s",
        "Developer ID Application:",
        *(extra_args or []),
        str(path),
    ]
    subprocess.run(codesign_args, check=True)


def process_pyqt(
    target_arch: Arch, pyqt_src: Path, pyqt_lib_folder: Path, resource_folder: Path
) -> None:
    skip_pyqt_prefixes = [
        "QtDesigner",
        "QtOpenGL",
        "QtOpenGLWidgets",
        "QtPositioning",
        "QtNfc",
        "QtBluetooth",
        "QtHelp",
        "QtQml",
        "QtQuick",
        "QtQuick3D",
        "QtQuickWidgets",
        "QtRemoteObjects",
        "QtSensors",
        "QtSerialPort",
        "QtSql",
        "QtTest",
        "QtWebEngineQuick",
        "QtXml",
        "__pycache__",
    ]

    for path in pyqt_src.iterdir():
        include = not path.is_dir()
        for prefix in skip_pyqt_prefixes:
            if path.name.startswith(prefix):
                include = False
        if path.name.endswith(".py") and path.name != "__init__.py":
            include = False
        if path.name.endswith(".pyi") or path.name == "py.typed":
            include = False

        if include:
            dest = pyqt_lib_folder / path.name
            if not dest.parent.exists():
                dest.parent.mkdir(parents=True)

            shutil.copy2(path, dest)
            if path.name != "__init__.py":
                lipo(dest, target_arch)
                codesign(dest)

    # move top level init into correct place
    init_in_lib = pyqt_lib_folder / "__init__.py"
    resources_path = resource_folder / "pyqt_init.py"
    shutil.move(init_in_lib, resources_path)
    os.symlink("../../../Resources/pyqt_init.py", init_in_lib)


def process_translations(qt_bin_path: Path, resource_folder: Path):
    translations_src = qt_bin_path / "translations"
    translations_dst = resource_folder / "qt_translations"
    translations_dst.mkdir(parents=True)

    for path in translations_src.iterdir():
        if re.match(r"qtbase", path.name):
            shutil.copy2(path, translations_dst.joinpath(path.name))


def process_plugins(
    qt_bin_path: Path, pyqt_lib_folder: Path, qt_major: int, target_arch: Arch
) -> None:
    plugin_src = qt_bin_path / "plugins"
    if qt_major == 6:
        plugin_dst = pyqt_lib_folder / "Qt6/plugins"
    else:
        plugin_dst = pyqt_lib_folder / "Qt/plugins"
    if not plugin_dst.exists():
        plugin_dst.mkdir(parents=True)
    subprocess.run(
        [
            "rsync",
            "-a",
            "--delete",
            "--exclude",
            "sqldrivers",
            "--exclude",
            "qmltooling",
            "--exclude",
            "designer",
            str(plugin_src) + "/",
            plugin_dst,
        ]
    )
    for root, _dirnames, fnames in os.walk(plugin_dst):
        for fname in fnames:
            if fname.endswith(".dylib"):
                path = Path(root) / fname
                lipo(path, target_arch)
                codesign(path)


qt_framework_skip_prefixes = [
    "QtConcurrent",
    "QtDesigner",
    "QtHelp",
    "QtLabs",
    "QtTest",
    "QtUiTools",
    "QtUiPlugin",
    "QtRepParser",
    "QtXml",
]


def allowed_frameworks(framework_src: Path) -> Iterator[Path]:
    for path in framework_src.iterdir():
        if not path.name.endswith(".framework"):
            continue

        include = True
        for skip in qt_framework_skip_prefixes:
            if path.name.startswith(skip):
                include = False

        if include:
            yield path


def process_frameworks(qt_bin_path: Path, output_root: Path, target_arch: Arch) -> None:
    if not output_root.exists():
        output_root.mkdir(parents=True)
    framework_src = qt_bin_path / "lib"
    framework_dst = output_root / "Frameworks"
    if not framework_dst.exists():
        framework_dst.mkdir(parents=True)

    frameworks = list(allowed_frameworks(framework_src))
    for framework in frameworks:
        # must preserve links
        subprocess.run(
            [
                "rsync",
                "-a",
                "--delete",
                "--exclude",
                "Headers",
                framework,
                framework_dst,
            ],
            check=True,
        )

        # locate actual library and sign it
        for fname in (
            framework_dst.joinpath(framework.name)
            .joinpath("Versions")
            .joinpath("Current")
            .iterdir()
        ):
            if fname.name.startswith("Qt"):
                lipo(fname, target_arch)

    # lipo the webengine helper
    lipo(
        framework_dst
        / "QtWebEngineCore.framework/Versions/Current/Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess",
        target_arch,
    )

    # sign the helper first
    codesign(
        framework_dst
        / "QtWebEngineCore.framework/Versions/Current/Helpers/QtWebEngineProcess.app",
        extra_args=[
            "--entitlements",
            str(
                Path(__file__)
                .resolve()
                .with_name("entitlements.qtwebengineprocess.xml")
            ),
        ],
    )

    # sign all frameworks
    for framework in frameworks:
        codesign(framework_dst / framework.name)


qt_path, anki_repo, output_root = (
    Path(sys.argv[1]),
    Path(sys.argv[2]),
    Path(sys.argv[3]),
)
qt_version = qt_path.name
qt_major = 6 if qt_version.startswith("6.") else 5
resource_folder = output_root / "Resources"
pyqt_lib_folder = output_root / f"MacOS/lib/PyQt{qt_major}"
if qt_major == 6:
    qt_bin_path = qt_path / "macos"
else:
    qt_bin_path = qt_path / "clang_64"
target_arch = Arch.current()
if output_root.exists():
    shutil.rmtree(output_root)
output_root.mkdir(parents=True)
resource_folder.mkdir()
pyqt_root = get_pyqt_root(qt_major)
process_pyqt(target_arch, pyqt_root, pyqt_lib_folder, resource_folder)
process_translations(qt_bin_path, resource_folder)
process_plugins(qt_bin_path, pyqt_lib_folder, qt_major, target_arch)
process_frameworks(qt_bin_path, output_root, target_arch)
