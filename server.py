import os, json, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

API_KEY = os.environ.get("HD_API_KEY", "CAMBIA_QUESTA_CHIAVE")
PORT = int(os.environ.get("PORT", "8080"))
STATE = {"updated_at": 0, "instances": {}}

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type="application/json; charset=utf-8"):
        raw = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self._send(204, "")

    def do_GET(self):
        if self.path == "/health":
            self._send(200, json.dumps({"ok": True, "updated_at": STATE["updated_at"]}))
            return
        if self.path == "/api/state":
            self._send(200, json.dumps(STATE, ensure_ascii=False))
            return
        self._send(404, json.dumps({"ok": False, "error": "not_found"}))

    def do_POST(self):
        if self.path != "/api/update":
            self._send(404, json.dumps({"ok": False, "error": "not_found"}))
            return
        if self.headers.get("X-API-Key", "") != API_KEY:
            self._send(401, json.dumps({"ok": False, "error": "unauthorized"}))
            return
        try:
            n = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(n).decode("utf-8"))
            iid = str(data.get("id", ""))
            if not iid:
                raise ValueError("missing id")
            data["last_seen"] = time.time()
            STATE["instances"][iid] = data
            STATE["updated_at"] = time.time()
            self._send(200, json.dumps({"ok": True}))
        except Exception as e:
            self._send(400, json.dumps({"ok": False, "error": str(e)}))

    def log_message(self, fmt, *args):
        print(fmt % args)

if __name__ == "__main__":
    print("HayDay realtime server listening on", PORT)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
