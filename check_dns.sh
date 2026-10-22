#!/usr/bin/env bash
# Check Gabia DNS for petpolicycheck.com against GitHub Pages requirements.
command -v dig >/dev/null || { echo "dig not found: install dnsutils (apt) / bind (brew)"; exit 2; }
DOMAIN=${1:-petpolicycheck.com}
TARGET=leejaeml2309-alt.github.io
WANT="185.199.108.153 185.199.109.153 185.199.110.153 185.199.111.153"
ok=0
for ns in "" "@8.8.8.8" "@1.1.1.1"; do
  got=$(dig +short $ns A "$DOMAIN" | sort | tr '\n' ' ' | sed 's/ $//')
  echo "A $DOMAIN ${ns:-(local)}: ${got:-<none>}"
done
got=$(dig +short @8.8.8.8 A "$DOMAIN" | sort | tr '\n' ' ' | sed 's/ $//')
if [ "$got" = "$WANT" ]; then echo "OK: apex A records match the 4 GitHub IPs"; else echo "FAIL: apex A expected [$WANT]"; ok=1; fi
cname=$(dig +short @8.8.8.8 CNAME "www.$DOMAIN" | sed 's/\.$//')
echo "CNAME www.$DOMAIN: ${cname:-<none>}"
if [ "$cname" = "$TARGET" ]; then echo "OK: www is CNAME to $TARGET"; else echo "FAIL: www should be CNAME to $TARGET"; ok=1; fi
aaaa=$(dig +short @8.8.8.8 AAAA "$DOMAIN"); [ -n "$aaaa" ] && echo "WARN: AAAA records exist ($aaaa) - remove unless they are GitHub's 2606:50c0:800x::153"
exit $ok
