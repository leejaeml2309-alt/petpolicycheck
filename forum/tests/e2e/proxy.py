# Serves the built site at / and proxies /rest/v1/* to PostgREST (stand-in for a Supabase project).
import http.server, urllib.request, sys, os
SITE = sys.argv[1]
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=SITE,**k)
    def _proxy(s):
        if not s.path.startswith("/rest/v1/"): return False
        n=int(s.headers.get("Content-Length") or 0); body=s.rfile.read(n) if n else None
        req=urllib.request.Request("http://localhost:3001"+s.path[8:],data=body,method=s.command)
        for k,v in s.headers.items():
            if k.lower() in ("host","content-length","connection","apikey"): continue
            req.add_header(k,v)
        try: r=urllib.request.urlopen(req); code=r.status; data=r.read(); hdrs=r.headers
        except urllib.error.HTTPError as e: code=e.code; data=e.read(); hdrs=e.headers
        s.send_response(code)
        for k,v in hdrs.items():
            if k.lower() in ("transfer-encoding","connection","content-length"): continue
            s.send_header(k,v)
        s.send_header("Content-Length",str(len(data))); s.end_headers(); s.wfile.write(data); return True
    def do_GET(s):
        if not s._proxy(): super().do_GET()
    def do_POST(s):
        if not s._proxy(): s.send_error(404)
    def do_PATCH(s):
        if not s._proxy(): s.send_error(404)
    def do_DELETE(s):
        if not s._proxy(): s.send_error(404)
    def do_HEAD(s):
        if not s._proxy(): super().do_HEAD()
    def log_message(s,*a): pass
http.server.ThreadingHTTPServer(("127.0.0.1",8800),H).serve_forever()
