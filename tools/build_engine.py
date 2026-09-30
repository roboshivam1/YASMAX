"""
File: tools/build_engine.py

Packs the Python engine into web/engine.zip, the file the browser worker
downloads and unpacks into Pyodide's in-memory filesystem.

Run it from the repo root after every engine change:

    python3 tools/build_engine.py

What goes into the zip
----------------------
Only engine/yasmax_engine/**/*.py, stored under "yasmax_engine/", so that
unpacking into /engine gives /engine/yasmax_engine/... and
`import yasmax_engine` works once /engine is on sys.path.
Tests, caches and packaging files are left out, since the browser
doesn't need them.

The zip is deterministic: files are sorted and every timestamp is fixed.
So building twice without code changes gives byte-identical output,
which keeps git diffs and browser caches honest.

Self-test
---------
After building, the script imports the engine FROM THE ZIP (Python can
import straight from a zip file) in a fresh Python process and calls
api.boot(), exactly what the browser worker does. A missing file or an
import error fails the build here, with the real traceback, instead of
showing up later as "YASMAX could not start" in the browser.
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = ROOT / "engine" / "yasmax_engine"
OUTPUT = ROOT / "web" / "engine.zip"

# Any fixed date works; zip timestamps can't go earlier than 1980.
FIXED_TIME = (1980, 1, 1, 0, 0, 0)

# Imports the engine from the zip and boots it, like web/js/worker.js does.
SELF_TEST = """
import json, sys
sys.path.insert(0, sys.argv[1])
from yasmax_engine import api
info = json.loads(api.boot())
print(f"engine {info['engine_version']}: {len(info['commands'])} commands, "
      f"{len(info.get('isa', []))} opcodes")
"""


def collect_files() -> list[Path]:
    """All .py files in the package, sorted, skipping __pycache__."""
    files = [p for p in PACKAGE_DIR.rglob("*.py") if "__pycache__" not in p.parts]
    return sorted(files)


def build() -> Path:
    if not (PACKAGE_DIR / "__init__.py").exists():
        sys.exit(f"Engine package not found at {PACKAGE_DIR}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    files = collect_files()
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = Path("yasmax_engine") / path.relative_to(PACKAGE_DIR)
            info = zipfile.ZipInfo(arcname.as_posix(), date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())

    size_kb = OUTPUT.stat().st_size / 1024
    print(f"Built {OUTPUT.relative_to(ROOT)}: {len(files)} files, {size_kb:.1f} KB")
    return OUTPUT


def self_test(zip_path: Path) -> None:
    """Boot the engine from the zip in a clean process; exit 1 if it fails."""
    result = subprocess.run(
        [sys.executable, "-I", "-c", SELF_TEST, str(zip_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        zip_path.unlink(missing_ok=True)
        sys.exit(
            "\nSELF-TEST FAILED: the engine cannot start from engine.zip (deleted it).\n"
            "The traceback above names the file or import that is missing or broken."
        )
    print(f"Self-test OK: {result.stdout.strip()}")


if __name__ == "__main__":
    self_test(build())
