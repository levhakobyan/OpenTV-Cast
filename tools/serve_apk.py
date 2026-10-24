#!/usr/bin/env python3
"""Serve only the prepared public download files, on loopback for a tunnel."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

class Downloads(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".apk": "application/vnd.android.package-archive"}
    allowed = {"/", "/index.html", "/tv-bridge.apk", "/SHA256SUMS.txt"}

    def send_response(self, code, message=None):
        self._response_code = code
        super().send_response(code, message)

    def send_head(self):
        if unquote(urlsplit(self.path).path) not in self.allowed:
            self.send_error(404)
            return None
        return super().send_head()

    def list_directory(self, path):
        self.send_error(404)
        return None

    def end_headers(self):
        if (getattr(self, "_response_code", None) == 200
                and unquote(urlsplit(self.path).path) == "/tv-bridge.apk"):
            self.send_header("Content-Disposition", 'attachment; filename="OpenTV-Cast.apk"')
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8788)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if not (directory / "tv-bridge.apk").is_file():
        parser.error("Prepare the public download folder before starting the server")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Downloads, directory=str(directory)))
    print(f"OpenTV-Cast downloads: http://127.0.0.1:{server.server_address[1]}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
