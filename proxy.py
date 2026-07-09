#!/usr/bin/env python3
"""Simple proxy server: serves frontend on / and proxies /api/ to backend."""

import http.server
import json
import os
import urllib.request
import urllib.error


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
BACKEND_URL = "http://127.0.0.1:8000"


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self._proxy("POST")
        else:
            self.send_error(404)

    def do_PUT(self):
        if self.path.startswith("/api/"):
            self._proxy("PUT")
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self._proxy("DELETE")
        else:
            self.send_error(404)

    def _proxy(self, method):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        # Build target URL, preserving query string
        target = BACKEND_URL + self.path

        req = urllib.request.Request(target, data=body, method=method)
        # Forward relevant headers
        for h in ("Content-Type", "Authorization", "Accept"):
            val = self.headers.get(h)
            if val:
                req.add_header(h, val)

        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                for h in ("Content-Type",):
                    val = resp.headers.get(h)
                    if val:
                        self.send_header(h, val)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_error(e.code, e.reason)
        except Exception as e:
            self.send_error(502, str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    server = http.server.HTTPServer(("0.0.0.0", port), ProxyHandler)
    print(f"Serving frontend on http://0.0.0.0:{port}")
    print(f"Proxying /api/* to {BACKEND_URL}")
    server.serve_forever()
