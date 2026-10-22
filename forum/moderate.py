#!/usr/bin/env python3
"""Moderator-bot CLI for the PetPolicyCheck forum.

  python3 forum/moderate.py list [--limit N]
  python3 forum/moderate.py set post|comment <id> published|rejected|flagged|pending [reason]
  python3 forum/moderate.py terms            # current pre-filter terms (JSON)
  python3 forum/moderate.py check            # which backend is used and whether it connects

Backends (env FORUM_MODERATE_BACKEND = auto | db | rest, default auto):
  db   - direct Postgres through the Supabase session pooler with `psql` (must be installed).
         Settings: forum/db.json (non-secret: hosts, port, user, dbname). Password: the file named by
         env SUPABASE_DB_PASSWORD_FILE (default /home/box/.supabase_db_password). No service-role key needed.
  rest - Supabase REST API with the secret/service-role key in env SUPABASE_SERVICE_ROLE_KEY.
  auto - db if the password file exists, else rest; if db cannot connect and a key is set, falls back to rest.

`list` prints JSON: {"items": [...]} with every post/comment that needs a decision:
  status pending or flagged, plus published items that have reports (report_count > 0).
Each item: id, type, status, lang, title (posts), body, categories (posts), post_id/post_title (comments),
author {id, display_name}, created_at, report_count, reports [{reason, created_at}], mod_reason.

The URL comes from config.json forum.supabase_url (or env SUPABASE_URL). The service-role key is
secret: env only, never in config.json or the repo. Stdlib only.
"""
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUSES = ("published", "rejected", "flagged", "pending")
CATS = ("transport", "weather", "season", "carrier", "species", "breed", "weight",
        "airline_slug", "operator", "route_from", "route_to", "trip_date")


def die(msg, code=2):
    print(json.dumps({"error": msg}), file=sys.stderr)
    sys.exit(code)


def conf():
    url = os.environ.get("SUPABASE_URL", "").strip()
    if not url:
        try:
            url = (json.loads((ROOT / "config.json").read_text()).get("forum") or {}).get("supabase_url", "").strip()
        except (OSError, ValueError):
            url = ""
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url:
        die("forum.supabase_url is empty in config.json (or set SUPABASE_URL)")
    if not key:
        die("SUPABASE_SERVICE_ROLE_KEY is not set")
    return url.rstrip("/"), key


def rest(method, path, params=None, body=None):
    url, key = conf()
    q = ("?" + urllib.parse.urlencode(params, safe="(),.*:")) if params else ""
    req = urllib.request.Request(f"{url}/rest/v1/{path}{q}", method=method,
                                 data=None if body is None else json.dumps(body).encode())
    req.add_header("apikey", key)
    if not key.startswith("sb_"):  # legacy JWT keys also go in Authorization; new sb_secret_ keys use apikey only
        req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    if method == "PATCH":
        req.add_header("Prefer", "return=representation")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as ex:
        die(f"HTTP {ex.code} on {method} {path}: {ex.read().decode()[:500]}", 1)
    except urllib.error.URLError as ex:
        die(f"network error on {method} {path}: {ex.reason}", 1)


# ---------------------------------------------------------------- direct Postgres backend (psql)
DB_CONF = Path(os.environ.get("FORUM_DB_CONF") or Path(__file__).resolve().parent / "db.json")
PW_FILE = os.environ.get("SUPABASE_DB_PASSWORD_FILE", "/home/box/.supabase_db_password")


class DbError(Exception):
    pass


def psql(sql, variables=None, host=None):
    """Run SQL with psql and return stdout. Password goes through PGPASSWORD in the child env only."""
    if not shutil.which("psql"):
        raise DbError("psql is not installed (apt-get install postgresql-client)")
    try:
        c = json.loads(DB_CONF.read_text())
        pw = Path(PW_FILE).read_text().strip()
    except OSError as ex:
        raise DbError(f"cannot read db settings or password file: {ex.__class__.__name__}")
    hosts = [host] if host else c["hosts"]
    last = ""
    for h in hosts:
        env = dict(os.environ, PGPASSWORD=pw, PGCONNECT_TIMEOUT=str(c.get("connect_timeout", 8)),
                   PGSSLMODE=c.get("sslmode", "require"), PGAPPNAME="forum-moderate")
        args = ["psql", "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-h", h, "-p", str(c.get("port", 5432)),
                "-U", c["user"], "-d", c.get("dbname", "postgres")]
        for k, v in (variables or {}).items():
            args += ["-v", f"{k}={v}"]
        r = subprocess.run(args, input=sql, capture_output=True, text=True, env=env, timeout=60)
        if r.returncode == 0:
            return r.stdout
        last = (r.stderr or "").replace(pw, "***").strip()
        if "could not connect" not in last and "timeout" not in last and "could not translate" not in last \
                and "Connection refused" not in last and "Tenant or user not found" not in last:
            break  # a real SQL error: do not retry another host
    raise DbError(last[:500] or "psql failed")


QUEUE_SQL = """
with p as (
  select p.*, json_build_object('id', a.id, 'display_name', a.display_name) as author
  from public.posts p join public.profiles a on a.id = p.author_id
  where p.status in ('pending', 'flagged') or p.report_count > 0
  order by p.created_at limit :lim),
c as (
  select c.*, json_build_object('id', a.id, 'display_name', a.display_name) as author,
         json_build_object('title', po.title, 'status', po.status) as post
  from public.comments c join public.profiles a on a.id = c.author_id join public.posts po on po.id = c.post_id
  where c.status in ('pending', 'flagged') or c.report_count > 0
  order by c.created_at limit :lim),
r as (
  select target_type, target_id, reason, created_at from public.reports
  where target_id in (select id from p union all select id from c))
select json_build_object(
  'posts', coalesce((select json_agg(to_jsonb(p) order by p.created_at) from p), '[]'),
  'comments', coalesce((select json_agg(to_jsonb(c) order by c.created_at) from c), '[]'),
  'reports', coalesce((select json_agg(to_jsonb(r) order by r.created_at) from r), '[]'));
"""

SET_SQL = """
update public.{table} set status = :'st', mod_reason = :'reason', moderated_at = now()
where id = :'id'::uuid returning json_build_object('id', id, 'status', status, 'mod_reason', mod_reason);
"""


def use_db():
    mode = os.environ.get("FORUM_MODERATE_BACKEND", "auto").lower()
    if mode == "db":
        return True
    if mode == "rest":
        return False
    return Path(PW_FILE).exists() and DB_CONF.exists()


def db_or_rest(fn_db, fn_rest):
    if use_db():
        try:
            return fn_db()
        except DbError as ex:
            if os.environ.get("FORUM_MODERATE_BACKEND", "auto").lower() == "auto" and os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
                print(json.dumps({"warning": f"db backend failed, using REST: {ex}"}), file=sys.stderr)
                return fn_rest()
            die(f"db backend: {ex}", 1)
    return fn_rest()


def queue_db(limit):
    d = json.loads(psql(QUEUE_SQL, {"lim": int(limit)}).strip())
    return d["posts"], d["comments"], d["reports"]


def queue_rest(limit):
    need = "or=(status.in.(pending,flagged),report_count.gt.0)"
    key, val = need.split("=", 1)
    posts = rest("GET", "posts", {"select": "*,author:profiles(id,display_name)", key: val,
                                  "order": "created_at.asc", "limit": str(limit)}) or []
    comments = rest("GET", "comments", {"select": "*,author:profiles(id,display_name),post:posts(title,status)",
                                        key: val, "order": "created_at.asc", "limit": str(limit)}) or []
    ids = [p["id"] for p in posts] + [c["id"] for c in comments]
    reports = []
    if ids:
        reports = rest("GET", "reports", {"select": "target_type,target_id,reason,created_at",
                                          "target_id": f"in.({','.join(ids)})", "order": "created_at.asc"}) or []
    return posts, comments, reports


def cmd_list(limit=100):
    posts, comments, reports = db_or_rest(lambda: queue_db(limit), lambda: queue_rest(limit))
    reps = {}
    for r in reports:
        reps.setdefault((r["target_type"], r["target_id"]), []).append({"reason": r.get("reason"), "created_at": r["created_at"]})
    items = []
    for p in posts:
        items.append({"type": "post", "id": p["id"], "status": p["status"], "lang": p.get("lang"),
                      "title": p["title"], "body": p["body"], "categories": {k: p.get(k) for k in CATS if p.get(k) is not None},
                      "author": p.get("author"), "created_at": p["created_at"], "report_count": p.get("report_count", 0),
                      "reports": reps.get(("post", p["id"]), []), "mod_reason": p.get("mod_reason")})
    for c in comments:
        post = c.get("post") or {}
        items.append({"type": "comment", "id": c["id"], "status": c["status"], "post_id": c["post_id"],
                      "post_title": post.get("title"), "post_status": post.get("status"), "body": c["body"],
                      "author": c.get("author"), "created_at": c["created_at"], "report_count": c.get("report_count", 0),
                      "reports": reps.get(("comment", c["id"]), []), "mod_reason": c.get("mod_reason")})
    items.sort(key=lambda x: x["created_at"])
    counts = {}
    for it in items:
        k = "reported" if it["status"] == "published" else it["status"]
        counts[k] = counts.get(k, 0) + 1
    print(json.dumps({"counts": counts, "items": items}, ensure_ascii=False, indent=1))


def cmd_set(typ, item_id, status, reason=""):
    if typ not in ("post", "comment"):
        die("type must be post or comment")
    if status not in STATUSES:
        die(f"status must be one of {', '.join(STATUSES)}")
    import datetime as dt
    import re
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", item_id):
        die("id must be a uuid")
    reason = (("bot: " + reason.strip()) if reason.strip() else "bot")[:300]
    table = "posts" if typ == "post" else "comments"

    def via_db():
        out = psql(SET_SQL.format(table=table), {"st": status, "reason": reason, "id": item_id}).strip()
        return [json.loads(out)] if out else []

    def via_rest():
        return rest("PATCH", table, {"id": f"eq.{item_id}"},
                    {"status": status, "mod_reason": reason,
                     "moderated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
    rows = db_or_rest(via_db, via_rest)
    if not rows:
        die(f"{typ} {item_id} not found", 1)
    r = rows[0]
    print(json.dumps({"ok": True, "type": typ, "id": r["id"], "status": r["status"], "mod_reason": r["mod_reason"]}, ensure_ascii=False))


def cmd_terms():
    rows = db_or_rest(lambda: json.loads(psql("select coalesce(json_agg(t order by t.id), '[]') from public.moderation_terms t;").strip()),
                      lambda: rest("GET", "moderation_terms", {"select": "*", "order": "id.asc"}))
    print(json.dumps(rows, ensure_ascii=False, indent=1))


def cmd_check():
    if use_db():
        try:
            out = psql("select json_build_object('user', current_user, 'server_version', current_setting('server_version'),"
                       " 'forum_schema', to_regclass('public.posts') is not null);").strip()
            print(json.dumps({"backend": "db", "ok": True, **json.loads(out)}))
            return
        except DbError as ex:
            print(json.dumps({"backend": "db", "ok": False, "error": str(ex)}))
            if not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
                sys.exit(1)
    rows = rest("GET", "moderation_terms", {"select": "id", "limit": "1"})
    print(json.dumps({"backend": "rest", "ok": True, "terms_visible": rows is not None}))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    c = argv[0]
    if c == "list":
        lim = 100
        if "--limit" in argv:
            lim = int(argv[argv.index("--limit") + 1])
        cmd_list(lim)
    elif c == "set" and len(argv) >= 4:
        cmd_set(argv[1], argv[2], argv[3], " ".join(argv[4:]))
    elif c == "terms":
        cmd_terms()
    elif c == "check":
        cmd_check()
    else:
        die("usage: moderate.py list | set post|comment <id> <status> [reason] | terms | check")


if __name__ == "__main__":
    main(sys.argv[1:])
