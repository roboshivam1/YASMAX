"""
File: tools/build_site.py

Builds the publishable YASMAX website into _site/ (used by GitHub Pages)
and, with --zip, the offline download dist/yasmax-offline-<version>.zip.

    python3 tools/build_site.py                  build _site/, Pyodide from the CDN
    python3 tools/build_site.py --zip            also build the offline download
    python3 tools/build_site.py --pyodide-dir D  copy Pyodide from folder D instead
                                                 (e.g. node_modules/pyodide)

Steps
-----
1. Build and self-test web/engine.zip (build_engine.py).
2. Copy web/ to _site/.
3. Put the Pyodide runtime in _site/pyodide/, so the site does not depend
   on the jsDelivr CDN and works fully offline (worker.js uses the local
   copy when it exists).
4. Draw the app icons (make_icons.py).
5. Stamp a build id into js/build.js and sw.js. The service worker keeps
   one cache per build id, so every deploy replaces the old offline copy.
6. Write precache.json: every file the service worker stores on first
   visit, so the app works offline right away.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import time
import urllib.request
import zipfile
from pathlib import Path

import build_engine
from make_icons import make_icons

ROOT = Path(__file__).resolve().parent.parent
WEB, SITE, DIST = ROOT / "web", ROOT / "_site", ROOT / "dist"
PYODIDE_VERSION = "314.0.7"  # keep in step with web/js/worker.js
PYODIDE_CDN = f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/"
PYODIDE_FILES = ["pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm",
                 "python_stdlib.zip", "pyodide-lock.json"]  # fmt: skip


def version() -> str:
    text = (ROOT / "engine" / "yasmax_engine" / "__init__.py").read_text()
    return re.search(r'__version__ = "([^"]+)"', text).group(1)


def build_id() -> str:
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()  # fmt: skip
    except (OSError, subprocess.CalledProcessError):
        rev = time.strftime("%Y%m%d%H%M%S")
    return f"{version()}-{rev}"


def fetch_pyodide(target: Path, source: Path | None) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for name in PYODIDE_FILES:
        if source:
            shutil.copy2(source / name, target / name)
        else:
            print(f"  downloading {name}")
            with urllib.request.urlopen(PYODIDE_CDN + name, timeout=120) as r:
                (target / name).write_bytes(r.read())


def stamp(path: Path, bid: str) -> None:
    text = path.read_text()
    new = text.replace('BUILD = "dev"', f'BUILD = "{bid}"')
    if new == text:
        raise SystemExit(f'No BUILD = "dev" line found in {path}')
    path.write_text(new)


def build_site(pyodide_dir: Path | None) -> str:
    build_engine.self_test(build_engine.build())
    shutil.rmtree(SITE, ignore_errors=True)
    shutil.copytree(WEB, SITE, ignore=shutil.ignore_patterns("dev", ".DS_Store", "pyodide", "icons"))
    print("Pyodide runtime:")
    fetch_pyodide(SITE / "pyodide", pyodide_dir)
    make_icons(SITE / "icons")
    bid = build_id()
    stamp(SITE / "js" / "build.js", bid)
    stamp(SITE / "sw.js", bid)
    files = sorted(p.relative_to(SITE).as_posix() for p in SITE.rglob("*") if p.is_file())
    files = ["./"] + [f for f in files if f not in ("sw.js", "precache.json")]
    (SITE / "precache.json").write_text(json.dumps(files, indent=1))
    (SITE / ".nojekyll").write_text("")  # GitHub Pages: serve files as they are
    size = sum(p.stat().st_size for p in SITE.rglob("*") if p.is_file()) / 1e6
    print(f"Built _site/ ({build_id()}): {len(files)} files, {size:.1f} MB")
    return bid


START_MAC = '#!/bin/sh\ncd "$(dirname "$0")"\npython3 serve.py --dir app --open\n'
START_LINUX = '#!/bin/sh\ncd "$(dirname "$0")"\npython3 serve.py --dir app --open\n'
START_WINDOWS = "@echo off\r\ncd /d %~dp0\r\npy serve.py --dir app --open\r\npause\r\n"
README_OFFLINE = """YASMAX offline download
=======================

Needs Python 3 (macOS: type python3 in Terminal once; if it offers to
install the developer tools, accept).

macOS:   double-click start-mac.command (first time: right-click > Open)
Linux:   run ./start-linux.sh
Windows: double-click start-windows.bat

Your browser opens YASMAX at http://localhost:8000. Keep the small
window open while you work; close it (or press Ctrl+C) to stop.

Easier: open the website once and install it as an app (see the user
guide). It then works offline without Python.
"""


def build_zip() -> Path:
    DIST.mkdir(exist_ok=True)
    out = DIST / f"yasmax-offline-{version()}.zip"
    extras = {
        "serve.py": ((ROOT / "tools" / "serve.py").read_text(), 0o644),
        "start-mac.command": (START_MAC, 0o755),
        "start-linux.sh": (START_LINUX, 0o755),
        "start-windows.bat": (START_WINDOWS, 0o644),
        "README.txt": (README_OFFLINE, 0o644),
    }
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, (text, mode) in extras.items():
            info = zipfile.ZipInfo(f"yasmax/{name}", date_time=build_engine.FIXED_TIME)
            info.external_attr = mode << 16
            zf.writestr(info, text)
        for p in sorted(SITE.rglob("*")):
            if p.is_file():
                zf.write(p, f"yasmax/app/{p.relative_to(SITE).as_posix()}")
    print(f"Built {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    ap.add_argument("--zip", action="store_true", help="also build the offline download")
    ap.add_argument("--pyodide-dir", type=Path, help="copy Pyodide from this folder")
    args = ap.parse_args()
    build_site(args.pyodide_dir)
    if args.zip:
        build_zip()
