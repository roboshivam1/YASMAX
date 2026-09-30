"""
File: tools/serve.py

Serves YASMAX on this computer with browser caching turned OFF.

Why not `python3 -m http.server`? Browsers cache JavaScript files, and a
Web Worker (web/js/worker.js) is cached especially stubbornly. After you
paste new code, the browser can keep running the OLD files. This server
tells the browser never to keep a copy ("Cache-Control: no-store"), so a
normal reload always runs exactly the files on disk.

Why a server at all? Browsers refuse to run workers and modules from a
file:// page, so even the offline download needs this tiny local server.
Everything stays on your computer (it only listens on 127.0.0.1).

Usage:
    python3 tools/serve.py                     serve web/ (development)
    python3 tools/serve.py 8080                another port
    python3 serve.py --dir app --open          the offline download: serve
                                               app/ and open the browser
"""

from __future__ import annotations

import argparse
import functools
import http.server
import threading
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DIR = HERE.parent / "web"


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".wasm": "application/wasm",
        ".webmanifest": "application/manifest+json",
    }

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args: object) -> None:
        pass  # keep the terminal quiet; errors still show in the browser


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve YASMAX locally.")
    parser.add_argument("port", nargs="?", type=int, default=8000)
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR, help="folder to serve")
    parser.add_argument("--open", action="store_true", help="open the browser")
    args = parser.parse_args()

    folder = args.dir if args.dir.is_absolute() else (Path.cwd() / args.dir)
    if not (folder / "index.html").exists():
        raise SystemExit(f"No index.html in {folder}")
    handler = functools.partial(NoCacheHandler, directory=str(folder))
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        url = f"http://localhost:{args.port}/"
        print(f"YASMAX is running at {url}")
        print("Keep this window open while you use it. Press Ctrl+C to stop.")
        if args.open:
            threading.Timer(0.8, webbrowser.open, [url]).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
