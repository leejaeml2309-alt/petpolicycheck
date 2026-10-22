#!/usr/bin/env bash
# Switch PetPolicyCheck from the github.io project path to the custom domain.
# Run only after the Gabia DNS records are in place (see check_dns.sh).
set -euo pipefail
cd "$(dirname "$0")"
REPO=leejaeml2309-alt/petpolicycheck
DOMAIN=petpolicycheck.com

python3 - "$DOMAIN" <<'PY'
import json, sys
p = "config.json"; c = json.load(open(p))
c["site_url"] = f"https://{sys.argv[1]}"; c["base_path"] = "/"
c.pop("base_url", None)
open(p, "w").write(json.dumps(c, indent=2, ensure_ascii=False) + "\n")
PY

python3 build.py            # writes site/CNAME automatically (custom_domain())
grep -qx "$DOMAIN" site/CNAME || { echo "site/CNAME missing/wrong"; exit 1; }
if grep -rl "leejaeml2309-alt.github.io" site >/dev/null; then
  echo "ERROR: old github.io URL still present in site/:"; grep -rl "leejaeml2309-alt.github.io" site; exit 1
fi

git add config.json build.py site
git commit -m "Switch to custom domain $DOMAIN"
git push origin main

gh api -X PUT "repos/$REPO/pages" -f cname="$DOMAIN"
echo "Custom domain set. Trying to enforce HTTPS..."
if gh api -X PUT "repos/$REPO/pages" -F https_enforced=true; then
  echo "HTTPS enforced."
else
  echo "NOTE: https_enforced failed (certificate probably not issued yet)."
  echo "Retry later:  gh api -X PUT repos/$REPO/pages -F https_enforced=true"
fi
gh api "repos/$REPO/pages" --jq '{cname, https_enforced, status, html_url}'
