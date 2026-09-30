"""
File: tools/serve.py

Serves the YASMAX web app locally with browser caching turned OFF.

Why not `python3 -m http.server`? Browsers cache JavaScript files, and a
Web Worker (web/js/worker.js) is cached especially stubbornly. After you
paste new code, the browser can keep running the OLD files, and new
features break in strange ways. This server tells the browser never to
keep a copy ("Cache-Control: no-store"), so a normal reload always runs
exactly the files on disk.

Usage, from the repo root:
    python3 tools/build_engine.py
    python3 tools/serve.py          (then open http://localhost:8000)
    python3 tools/serve.py 8080     (another port)
"""

from __future__ import annotations

import functools
import http.server
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".wasm": "application/wasm",
    }

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(NoCacheHandler, directory=str(WEB))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"YASMAX running at http://localhost:{port}  (Ctrl+C to stop)")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    main()
