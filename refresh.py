#!/usr/bin/env python3
"""Nightly refresh: re-check the airline whose official page was checked longest ago.

Steps: pick airline (oldest last_checked/last_verified) -> fetch its official page(s)
-> extract policy-relevant text -> hash -> compare with stored hash -> update JSON
(+ Updates entry when changed) -> rebuild site -> write reports/YYYY-MM-DD.md.

It never edits policy values automatically (no guessing): a detected change sets
needs_review=true so a human can update the fields from the official page.
It does NOT commit or push: see publish_hook() below.

Usage:
  python3 refresh.py               # nightly: one airline
  python3 refresh.py --slug delta  # a specific airline
  python3 refresh.py --all         # every airline (e.g. to set baselines)
  python3 refresh.py --no-build --dry-run
Cron example (03:00 local):  0 3 * * * cd /workspace/petsite && /usr/bin/python3 refresh.py >> reports/cron.log 2>&1
"""
import argparse
import datetime as dt
import difflib
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "airlines"
SNAP = ROOT / "data" / "snapshots"
REPORTS = ROOT / "reports"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
TZ = dt.timezone(dt.timedelta(hours=9))  # site owner's zone (UTC+9)
KEYWORDS = re.compile(r"(pet|cat|dog|bird|animal|carrier|kennel|crate|cabin|hold|cargo|fee|charge|\$|€|eur|usd|cad|"
                      r"\bkg\b|\blb|\bcm\b|inch|\bin\b|breed|brachycephalic|snub|weight|embargo|not permitted|prohibit|"
                      r"allowed|accepted|service animal|assistance dog)", re.I)
BLOCK_MARKERS = ("just a moment", "access denied", "enable javascript and cookies", "page cannot be found",
                 "page not found", "attention required")


def today():
    return dt.datetime.now(TZ).date().isoformat()


def html_to_text(raw):
    t = re.sub(r"(?is)<(script|style|noscript|svg|header|footer|nav).*?</\1>", " ", raw)
    t = re.sub(r"(?i)<br\s*/?>|</(p|li|tr|h\d|div|td|th)>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    lines = [re.sub(r"\s+", " ", l).strip() for l in t.split("\n")]
    return [l for l in lines if l]


def relevant(lines):
    out = []
    for l in lines:
        if len(l) < 12 or "©" in l or "cookie" in l.lower():
            continue
        if KEYWORDS.search(l):
            out.append(l)
    return out


def fetch_urllib(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9",
                                               "Accept": "text/html,application/xhtml+xml"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8", "ignore")


def chrome_bin():
    for b in ("google-chrome", "chromium", "chromium-browser"):
        p = shutil.which(b)
        if p:
            return p
    return None


def fetch_chrome(url):
    b = chrome_bin()
    if not b:
        return None
    try:
        r = subprocess.run([b, "--headless=new", "--no-sandbox", "--disable-gpu", f"--user-agent={UA}",
                            "--virtual-time-budget=20000", "--dump-dom", url],
                           capture_output=True, text=True, timeout=90)
        return r.stdout
    except Exception:
        return None


def looks_blocked(lines):
    joined = " ".join(lines[:60]).lower()
    return any(m in joined for m in BLOCK_MARKERS)


def fetch(url):
    """Return (relevant_lines, method, error)."""
    err = None
    try:
        status, raw = fetch_urllib(url)
        lines = html_to_text(raw)
        rel = relevant(lines)
        if status == 200 and not looks_blocked(lines) and len(" ".join(rel)) > 400:
            return rel, "http", None
        err = f"http {status}: too little policy text or bot wall"
    except Exception as ex:  # HTTPError, timeout, ...
        err = f"http error: {ex}"
    raw = fetch_chrome(url)
    if raw:
        lines = html_to_text(raw)
        rel = relevant(lines)
        if not looks_blocked(lines) and len(" ".join(rel)) > 400:
            return rel, "headless-chrome", None
        err += "; headless-chrome: blocked or no policy text rendered"
    return None, None, err


def digest(lines):
    norm = "\n".join(re.sub(r"\s+", " ", l.lower()) for l in lines)
    return hashlib.sha256(norm.encode()).hexdigest()


def snap_path(slug, url):
    return SNAP / slug / (hashlib.sha1(url.encode()).hexdigest()[:12] + ".txt")


def pick(airlines):
    return min(airlines, key=lambda a: (a.get("last_checked") or a.get("last_verified") or "0000", a["slug"]))


def check_airline(a, dry):
    d = today()
    res = {"slug": a["slug"], "name": a["name"], "urls": [], "changed": False, "blocked": False}
    hashes = a.get("content_hashes") or {}
    ok_any, changed_urls = False, []
    for url in a.get("watch_urls") or [a["official_url"]]:
        lines, method, err = fetch(url)
        entry = {"url": url, "method": method, "error": err}
        if lines is None:
            entry["result"] = "FAILED"
            res["urls"].append(entry)
            continue
        ok_any = True
        h = digest(lines)
        old = hashes.get(url)
        sp = snap_path(a["slug"], url)
        if old is None:
            entry["result"] = "baseline recorded"
        elif old == h:
            entry["result"] = "unchanged"
        else:
            entry["result"] = "CHANGED"
            changed_urls.append(url)
            prev = sp.read_text().splitlines() if sp.exists() else []
            entry["diff"] = list(difflib.unified_diff(prev, lines, "previous", "current", lineterm="", n=0))[:80]
        hashes[url] = h
        if not dry:
            sp.parent.mkdir(parents=True, exist_ok=True)
            sp.write_text("\n".join(lines) + "\n")
        res["urls"].append(entry)
    a["content_hashes"] = hashes
    a["last_checked"] = d
    if not ok_any:
        res["blocked"] = True
        a["fetch_status"] = "blocked"
    elif changed_urls:
        res["changed"] = True
        a["needs_review"] = True
    else:
        # Page content matches what the stored values were verified against -> still verified today.
        if not a.get("needs_review"):
            a["last_verified"] = d
    return res, changed_urls


def publish_hook(changed_any):
    # ------------------------------------------------------------------
    # >>> FUTURE PUBLISH HOOK (disabled on purpose) <<<
    # When the GitHub repo + Pages are set up and `gh`/git credentials exist,
    # replace this body with e.g.:
    #   subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
    #   subprocess.run(["git", "commit", "-m", f"refresh {today()}"], cwd=ROOT, check=False)
    #   subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
    # Until then this script never commits or pushes.
    # ------------------------------------------------------------------
    print("[publish_hook] disabled: no git commit/push performed.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="do not write JSON/snapshots/updates")
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    paths = {p.stem: p for p in DATA.glob("*.json")}
    airlines = {s: json.loads(p.read_text()) for s, p in paths.items()}
    if args.slug:
        targets = [airlines[args.slug]]
    elif args.all:
        targets = sorted(airlines.values(), key=lambda a: a["slug"])
    else:
        targets = [pick(list(airlines.values()))]

    upd_path = ROOT / "data" / "updates.json"
    updates = json.loads(upd_path.read_text()) if upd_path.exists() else []
    results = []
    for a in targets:
        print(f"Checking {a['name']} ...", flush=True)
        r, changed_urls = check_airline(a, args.dry_run)
        results.append(r)
        if changed_urls:
            updates.append({"date": today(), "airline": a["name"], "slug": a["slug"], "official": True, "reviewed": False,
                            "summary": "Our checker detected a change in the policy-relevant text of the official page. Details are under review; confirm with the airline.",
                            "source_url": changed_urls[0]})
        if not args.dry_run:
            paths[a["slug"]].write_text(json.dumps(a, indent=2, ensure_ascii=False) + "\n")
    if not args.dry_run:
        upd_path.write_text(json.dumps(updates, indent=2, ensure_ascii=False) + "\n")

    built = False
    if not args.no_build and not args.dry_run:
        subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
        built = True

    REPORTS.mkdir(exist_ok=True)
    rp = REPORTS / f"{today()}.md"
    out = [f"# Refresh report {today()} (UTC+9)", "",
           f"Run at {dt.datetime.now(TZ).strftime('%Y-%m-%d %H:%M')} UTC+9. Site rebuilt: {'yes' if built else 'no'}. Dry run: {args.dry_run}.", ""]
    for r in results:
        state = "BLOCKED (no page could be read; last_verified NOT bumped)" if r["blocked"] else (
            "CHANGED (needs_review set; last_verified NOT bumped)" if r["changed"] else "no meaningful change (last_verified bumped)")
        out += [f"## {r['name']} (`{r['slug']}`): {state}", ""]
        for u in r["urls"]:
            out.append(f"- {u['url']}: **{u['result']}** via {u['method'] or 'n/a'}" + (f" ({u['error']})" if u.get("error") and u["result"] == "FAILED" else ""))
            if u.get("diff"):
                out += ["", "```diff", *u["diff"], "```"]
        out.append("")
    with rp.open("a") as f:
        f.write("\n".join(out) + "\n")
    print(f"Report: {rp}")
    publish_hook(any(r["changed"] for r in results))


if __name__ == "__main__":
    main()
