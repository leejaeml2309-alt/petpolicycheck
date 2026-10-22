#!/usr/bin/env bash
# Read-only checks of the REAL project over HTTPS with the public (publishable) key: anon sees only
# published rows, cannot insert, cannot read moderation_terms / profile roles. Creates nothing.
set -u
CFG="$(dirname "$0")/../../config.json"
URL=$(python3 -c "import json;print(json.load(open('$CFG'))['forum']['supabase_url'])")
KEY=$(python3 -c "import json;print(json.load(open('$CFG'))['forum']['supabase_anon_key'])")
pass=0; fail=0
chk(){ if eval "$2"; then pass=$((pass+1)); echo "PASS $1"; else fail=$((fail+1)); echo "FAIL $1 ($3)"; fi; }
r=$(curl -s "$URL/rest/v1/posts?select=id,status&status=neq.published" -H "apikey: $KEY")
chk "anon sees no unpublished posts" '[ "$r" = "[]" ]' "$r"
r=$(curl -s "$URL/rest/v1/comments?select=id&status=neq.published" -H "apikey: $KEY")
chk "anon sees no unpublished comments" '[ "$r" = "[]" ]' "$r"
code=$(curl -s -o /tmp/rr.json -w "%{http_code}" -X POST "$URL/rest/v1/posts" -H "apikey: $KEY" -H "Content-Type: application/json" \
  -d '{"title":"anon test title","body":"anon test body that is long enough to pass","transport":"car","species":"dog"}')
chk "anon insert refused" '[ "$code" = "401" ] || [ "$code" = "403" ]' "$code $(cat /tmp/rr.json)"
code=$(curl -s -o /tmp/rr.json -w "%{http_code}" "$URL/rest/v1/moderation_terms?select=id&limit=1" -H "apikey: $KEY")
chk "anon cannot read moderation_terms" '[ "$code" = "401" ] || [ "$code" = "403" ]' "$code $(cat /tmp/rr.json)"
code=$(curl -s -o /tmp/rr.json -w "%{http_code}" "$URL/rest/v1/profiles?select=role&limit=1" -H "apikey: $KEY")
chk "anon cannot read profile roles" '[ "$code" = "401" ] || [ "$code" = "403" ]' "$code $(cat /tmp/rr.json)"
code=$(curl -s -o /tmp/rr.json -w "%{http_code}" "$URL/rest/v1/profiles?select=display_name&limit=1" -H "apikey: $KEY")
chk "anon can read display names" '[ "$code" = "200" ]' "$code $(cat /tmp/rr.json)"
code=$(curl -s -o /tmp/rr.json -w "%{http_code}" -X POST "$URL/rest/v1/rpc/moderate_item" -H "apikey: $KEY" -H "Content-Type: application/json" \
  -d '{"p_type":"post","p_id":"00000000-0000-0000-0000-000000000000","p_status":"published"}')
chk "anon cannot call moderate_item" '[ "$code" != "200" ] && [ "$code" != "204" ]' "$code"
echo "REST self-test: $pass passed, $fail failed"; [ "$fail" = 0 ]
