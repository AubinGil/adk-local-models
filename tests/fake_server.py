"""Loopback-only fixture replay server; never contacts a model server."""

from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

FIXTURES = Path(__file__).parent / "fixtures"


class FakeServer:
    def __init__(self, *replies, models_fixture="models.json"):
        self.replies = deque(replies or ["text.json"])
        self.requests = []
        self.responses = []
        self.headers = []
        self.models_reads = 0
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def do_GET(self):
                if self.path != "/v1/models":
                    self.send_error(404)
                    return
                owner.models_reads += 1
                self.reply((FIXTURES / models_fixture).read_bytes(),
                           500 if models_fixture == "error.json" else 200)

            def do_POST(self):
                if self.path != "/v1/chat/completions":
                    self.send_error(404)
                    return
                body = self.rfile.read(int(self.headers["Content-Length"]))
                owner.requests.append(body)
                owner.headers.append(dict(self.headers))
                fixture = owner.replies.popleft() if owner.replies else "text.json"
                status = 500 if fixture == "error.json" else 200
                raw = (FIXTURES / fixture).read_bytes()
                owner.responses.append(raw)
                self.reply(raw, status, fixture.endswith(".sse"))

            def reply(self, raw, status=200, sse=False):
                self.send_response(status)
                self.send_header("Content-Type", "text/event-stream" if sse else "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                # Split UTF-8, SSE lines, and JSON tokens across transport writes.
                for offset in range(0, len(raw), 7):
                    self.wfile.write(raw[offset:offset + 7])
                    self.wfile.flush()

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.base_url = f"http://127.0.0.1:{self.httpd.server_port}/v1"
        self.thread = Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join()
