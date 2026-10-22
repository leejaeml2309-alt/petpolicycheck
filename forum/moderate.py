#!/usr/bin/env python3
"""Moderator-bot CLI for the PetPolicyCheck forum (Supabase REST, service role).

  SUPABASE_SERVICE_ROLE_KEY=... python3 forum/moderate.py list [--limit N]
  SUPABASE_SERVICE_ROLE_KEY=... python3 forum/moderate.py set post|comment <id> published|rejected|flagged|pending [reason]
  SUPABASE_SERVICE_ROLE_KEY=... python3 forum/moderate.py terms            # current pre-filter terms (JSON)

`list` prints JSON: {"items": [...]} with every post/comment that needs a decision:
  status pending or flagged, plus published items that have reports (report_count > 0).
Each item: id, type, status, lang, title (posts), body, categories (posts), post_id/post_title (comments),
author {id, display_name}, created_at, report_count, reports [{reason, created_at}], mod_reason.

The URL comes from config.json forum.supabase_url (or env SUPABASE_URL). The service-role key is
secret: env only, never in config.json or the repo. Stdlib only.
"""
import json
import os
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


def cmd_list(limit=100):
    need = "or=(status.in.(pending,flagged),report_count.gt.0)"
    key, val = need.split("=", 1)
    posts = rest("GET", "posts", {"select": "*,author:profiles(id,display_name)", key: val,
                                  "order": "created_at.asc", "limit": str(limit)}) or []
    comments = rest("GET", "comments", {"select": "*,author:profiles(id,display_name),post:posts(title,status)",
                                        key: val, "order": "created_at.asc", "limit": str(limit)}) or []
    ids = [p["id"] for p in posts] + [c["id"] for c in comments]
    reps = {}
    if ids:
        for r in rest("GET", "reports", {"select": "target_type,target_id,reason,created_at",
                                         "target_id": f"in.({','.join(ids)})", "order": "created_at.asc"}) or []:
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
    reason = ("bot: " + reason.strip()) if reason.strip() else "bot"
    rows = rest("PATCH", "posts" if typ == "post" else "comments", {"id": f"eq.{item_id}"},
                {"status": status, "mod_reason": reason[:300],
                 "moderated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
    if not rows:
        die(f"{typ} {item_id} not found", 1)
    r = rows[0]
    print(json.dumps({"ok": True, "type": typ, "id": r["id"], "status": r["status"], "mod_reason": r["mod_reason"]}, ensure_ascii=False))


def cmd_terms():
    print(json.dumps(rest("GET", "moderation_terms", {"select": "*", "order": "id.asc"}), ensure_ascii=False, indent=1))


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
    else:
        die("usage: moderate.py list | set post|comment <id> <status> [reason] | terms")


if __name__ == "__main__":
    main(sys.argv[1:])
