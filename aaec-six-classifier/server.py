from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from app.factory import create_classifier


ROOT = Path(__file__).parent
PUBLIC = ROOT / "web"
classifier = create_classifier()


class Handler(BaseHTTPRequestHandler):
    server_version = "AAECSixClassifier/0.1"

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._send_file(PUBLIC / "index.html", "text/html; charset=utf-8")
            return
        if path == "/health":
            self._send_json({"ok": True, "model": classifier.model_name})
            return

        target = (PUBLIC / unquote(path.lstrip("/"))).resolve()
        if not str(target).startswith(str(PUBLIC.resolve())) or not target.exists():
            self._send_json({"error": "not_found"}, status=404)
            return

        content_type = "text/plain; charset=utf-8"
        if target.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif target.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        self._send_file(target, content_type)

    def do_POST(self) -> None:
        if self.path != "/api/classify":
            self._send_json({"error": "not_found"}, status=404)
            return

        try:
            length = int(self.headers.get("content-length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
            text = str(payload.get("text", ""))
        except (ValueError, json.JSONDecodeError):
            self._send_json({"error": "invalid_json"}, status=400)
            return

        result = classifier.classify_text(text)
        status = 200 if result["ok"] else 422
        self._send_json(result, status=status)

    def log_message(self, format: str, *args: object) -> None:
        print("%s - %s" % (self.address_string(), format % args))

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("access-control-allow-origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str) -> None:
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    host = "127.0.0.1"
    port = 8008
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"AAEC six-class classifier MVP running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
