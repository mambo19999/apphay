import json, time
from server import STATE, API_KEY

def application(environ, start_response):
    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "GET")
    headers = [
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Headers", "Content-Type, X-API-Key"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Cache-Control", "no-store"),
    ]
    if method == "OPTIONS":
        start_response("204 No Content", headers)
        return [b""]
    if method == "GET" and path == "/health":
        body = json.dumps({"ok": True, "updated_at": STATE["updated_at"]}, ensure_ascii=False).encode()
        start_response("200 OK", headers + [("Content-Type","application/json"),("Content-Length",str(len(body)))])
        return [body]
    if method == "GET" and path == "/api/state":
        body = json.dumps(STATE, ensure_ascii=False).encode()
        start_response("200 OK", headers + [("Content-Type","application/json"),("Content-Length",str(len(body)))])
        return [body]
    if method == "POST" and path == "/api/update":
        if environ.get("HTTP_X_API_KEY","") != API_KEY:
            body=b'{"ok":false,"error":"unauthorized"}'
            start_response("401 Unauthorized", headers + [("Content-Type","application/json")])
            return [body]
        try:
            n=int(environ.get("CONTENT_LENGTH","0") or 0)
            data=json.loads(environ["wsgi.input"].read(n).decode())
            iid=str(data.get("id",""))
            if not iid: raise ValueError("missing id")
            data["last_seen"]=time.time()
            STATE["instances"][iid]=data
            STATE["updated_at"]=time.time()
            body=b'{"ok":true}'
            start_response("200 OK", headers + [("Content-Type","application/json")])
            return [body]
        except Exception as e:
            body=json.dumps({"ok":False,"error":str(e)}).encode()
            start_response("400 Bad Request", headers + [("Content-Type","application/json")])
            return [body]
    body=b'{"ok":false,"error":"not_found"}'
    start_response("404 Not Found", headers + [("Content-Type","application/json")])
    return [body]
