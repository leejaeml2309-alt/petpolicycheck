# PREVIEW — Pet Desk Starter (25 Nov 2026, KST)

**Nothing is published on the site.** (Supabase backend deployed with Marc's OK — see « Supabase: done ».) Branch `petdesk-starter-20261125`, commits `c0942619` (feature) → `bfa0685f` (SQL grants + docs) → `3b4a9e50` (shots) → `98afd3c8` (passport languages note) → see `git log` for the head (refund on every payment, deployed function, docs), local worktree `/workspace/petdesk-starter-wt`. No push (a hosted branch preview wouldn't show the Desk: the Edge Function isn't deployed). No Gumroad login, no Supabase migration, build.py not run, site/ = static/ (checked file by file), GA G-K45B2WNXMC only, header/footer/coral search icon unchanged.

## How to view it
```
cd /workspace/petdesk-starter-wt
/home/box/.deno/bin/deno run -A petdesk/tests/serve.ts 8765     # serves site/ + the real function code with Gumroad mocked
```
- http://127.0.0.1:8765/pro/ (and /fr/ /es/ /de/ /it/ /ja/pro/)
- http://127.0.0.1:8765/pro/desk/ → test keys: `TRIAL000-AAAA1111-BBBB2222-CCCC3333` (trial), `ACTIVE00-AAAA1111-BBBB2222-CCCC4444` (active yearly), `CANCEL00-AAAA1111-BBBB2222-CCCC5555` (cancelled, access until a date), `ENDED000-…-CCCC6666` / `FAILED00-…-CCCC7777` / `REFUND00-…-CCCC8888` (denied), `OTHERPRD-…-CCCC9999` (another product → denied).
- The server is running on the box right now.

## What changed
1. **/pro/ (6 languages):**
   - Starter: « Start your 1-month free trial » → `https://petpolicycheck.gumroad.com/l/petdesk-starter?wanted=true` (the real product created by Marc, unpublished; the yearly toggle → `?yearly=true&wanted=true`, **untested: check it in the test purchase**)
   - Starter line + FAQ « Which languages are the passports available in? » (+ JSON-LD): passports **currently in English, Spanish and Italian; other languages coming soon** (no date). Same note next to the Desk's language picker (6 languages).
   - Refunds: the notice and the FAQ say the 14-day refund applies to **every payment** (first payment and renewals), like the terms and the refund policy (6 languages). Gumroad's refund setting is per product (https://gumroad.com/help/article/335-custom-refund-policy)., the text under it says "card required, automatic charge, reminder 48 h before", plus a secondary Request onboarding.
   - Pro / Enterprise: no trial, no Gumroad checkout; the primary button is « Request onboarding » (mailto contact@petpolicycheck.com, subject per tier).
   - New notice, 11-question FAQ + matching JSON-LD FAQPage (added on fr/es/it, where there wasn't one).
   - Starter promises corrected (EN/ES/IT passports; watchlist instead of automated alerts).
2. **Terms, refund policy, privacy (6 languages):** trial section rewritten (card, automatic charge, cancellation, 14-day refund counted from the first payment); privacy now describes the license key check (sha256 fingerprint only, Supabase Seoul).
   - "Last updated: November 19, 2026" left as is → **set it to the publishing date** when merging.
3. **Home (6 languages + static/home-c.html):** "14-day trial" → "1-month free trial on Starter".
4. **Desk /pro/desk/ + print.html (6 languages, noindex):**
   - License key login, status (trial / active / cancelling + date), quota 15/month, dual-language passport (EN/ES/IT) with agency header and reference, recent passports, 5-airline watchlist, links to maps and the comparator, logout.
   - The print sheet only opens with a valid session (server check of the reference).
5. **Backend (files only, NOT applied):**
   - `petdesk/sql/001_petdesk_starter.sql`: 4 tables, RLS on with no policies, nothing exposed to anon/authenticated, SECURITY INVOKER quota function.
   - `petdesk/supabase/functions/petdesk/` (Edge Function).

## Why a license key + Edge Function (option b), and where verification runs
- Gumroad generates the key and shows it in the receipt and content page (art. 76): zero extra setup for the buyer.
- Supabase Auth (option a) would need its own SMTP for login emails (the default mailer only sends to team members), and we have none.
- Verification runs **server side**, in the `petdesk` Edge Function (Supabase project uouccgyeujtmbeeneuwq, Seoul):
  - It calls `POST https://api.gumroad.com/v2/licenses/verify` (product_id + license_key, `increment_uses_count=false`).
  - It decides access: refunded/chargeback → denied; cancel/end/fail date past → ended, future → "until <date>"; first month → trial.
  - It issues a signed 12 h session and re-checks Gumroad every 6 h.
  - The browser never decides access, and the quota is counted in the database.

## Supabase: done (Marc's OK 09:16 KST), project uouccgyeujtmbeeneuwq
- **Migration `petdesk_starter_001`** (= `petdesk/sql/001_petdesk_starter.sql`): created `petdesk_accounts`, `petdesk_passports`, `petdesk_watch`, `petdesk_gumroad_events` + functions `petdesk_issue_passport`, `petdesk_watch_limit` and trigger `petdesk_watch_limit`. RLS on, 0 policies, no access for anon/authenticated (checked), service_role only. Nothing existing touched.
- **Edge Function `petdesk`** v1, ACTIVE, verify_jwt off (own key/session check): https://uouccgyeujtmbeeneuwq.supabase.co/functions/v1/petdesk/
- **Secrets: none set.** The Supabase connector has no secrets tool and there is no CLI login on the box, so I couldn't set them. The function is built so none are required, and it fails closed:
  - Gumroad product_id: built into the code (public value). `GUMROAD_STARTER_PRODUCT_IDS` would override it.
  - Session signing key: derived server-side (HMAC-SHA256) from the service-role key that Supabase injects. `DESK_SESSION_SECRET` (≥ 32 chars) would override it. Without a strong key the function answers 503 not_configured.
  - Allowed origins: https://petpolicycheck.com and https://www.petpolicycheck.com built in (`PETDESK_ALLOWED_ORIGINS` overrides). Local tests use the local mock server, so 127.0.0.1 isn't needed.
  - `PETDESK_PING_SECRET`: not set → the optional Gumroad ping endpoint stays closed (403). Access still updates on every login and every 6 h.
  - To add dedicated secrets later: Supabase Dashboard → Edge Functions → Secrets (or give me a CLI access token). Changing `DESK_SESSION_SECRET` logs everyone out.
- **Advisors:** security: on the new objects only INFO « RLS enabled, no policy » ×4 (intended: deny-all, service-role only); no WARN on petdesk objects. Pre-existing forum WARNs (SECURITY DEFINER functions executable by anon/authenticated: can_post, forum_before_insert, handle_new_user, is_admin, moderate_item, profiles_before_update, reports_after_insert, reports_before_insert; leaked password protection off) and the INFO on moderation_terms — not touched (outside scope). Performance: INFO « unused index » on `petdesk_passports_acc_period` (new, empty table; normal) and on the forum's `comments_post`.
- **Smoke test (curl, live):** `GET /health` → 200 `{"ok":true,"configured":{"session_key":true,"product_ids":1,"ping":false}}`; login « hello » → 400 bad_key_format; well-formed fake key → 403 invalid (checked with Gumroad against the real product); fake session → 401 session; ping without secret → 403; GET login → 405; CORS preflight: allow-origin only for https://petpolicycheck.com, none for another origin. Tables still empty after the tests (0 rows).

## Tests
- `deno test -A petdesk/tests/core_test.ts` → **9/9 pass** (+ health and fail-closed without a strong key) (real function logic, mocked Gumroad): every subscription state, CORS, trial date, 1 seat, 15/month + 16th refused (429), invalid language pairs (EN+EN, EN+FR), watchlist > 5 refused, access closes after a re-check, ping secret + dedupe, `increment_uses_count=false` on every call.
- `python3 petdesk/tests/e2e.py` (Chrome, with a freshly started serve.ts — its in-memory store keeps the quota between runs) → **253/253 pass** (now also: passport-language line + FAQ per language, JSON-LD answers = visible FAQ for all 12 questions, Desk languages note, 14-day refund not limited to the first payment on terms/refund ×6); results in `e2e-results.json`:
  - each of the 6 /pro/ pages: no JS errors; Starter label; monthly href; yearly toggle and back; click opens the Gumroad product (intercepted); Pro and Ent have no Gumroad link and a mailto primary with the right subject; no old trial text visible; JSON-LD parses with FAQPage = 12 = visible FAQ; GA present and no AdSense.
  - home (6), terms/refund/privacy (6×3).
  - desk ×6 languages: gate, noindex, lang, trial login, route lists loaded, logout.
  - all keys (cancel, active, ended, failed, refund, other product, bad format).
  - 1 seat across 2 browsers; watchlist 6th refused + saved 5; agency name; issue → print with 2 passports + agency + ref; quota 15/15 disables Issue + server 429; print without a session → denied.
- `petdesk/sql/001_petdesk_starter.sql` + `petdesk/tests/sql_test.sql` on a **local** Postgres 17 (Supabase roles anon/authenticated/service_role recreated) → applies cleanly and re-applies (idempotent); 15 passports then 16th refused (quota_reached); 6th watch refused; unique refs; RLS on for all 4 tables; anon can neither read nor call the function; service_role can. This test found missing grants for service_role (sequences), now fixed.
- **Only mocked (not tested for real):**
  - the Gumroad checkout (intercepted; the product doesn't exist);
  - the Gumroad license API (fixtures shaped like the documented response; **the real response during a trial is still to check** with a test purchase);
  - the Supabase-js layer (index.ts) against the real Supabase project (the SQL was tested on local Postgres, not on Supabase);
  - the deployed Edge Function / CORS on the real domain;
  - Gumroad emails (receipt, 48 h reminder, cancellation);
  - mailto (href checked; no mail app opened).

## Shots (`/workspace/petdesk-starter-20261125/shots/`)
- pro-{en,fr,es,de,it,ja}-{1280,390}.png (3 tiers)
- desk-login-{1280,390}.png
- desk-app-{1280,390}.png, desk-app-fr-1280.png
- desk-print-{1280,390}.png
- desk-quota-full-1280.png
- desk-print-denied-1280.png

## Blockers / to flag
1. Gumroad product created (unpublished). `?yearly=true` is undocumented → check it during the test purchase (GUMROAD-SETTINGS D15).
2. Supabase done; secrets not set (not required; see above). The site (branch) is still unpublished: the Desk pages only exist on the branch.
3. Own trial reminder/cancellation emails: Gumroad Workflows are blocked until $100 earned + 1 payout (art. 131); no SMTP. Gumroad's own 48 h reminder covers the legal minimum.
4. Passports in FR/DE/JA: the engine has no translation → promise limited to EN/ES/IT. The "After landing" block is partly in English in the ES version (existing engine text).
5. tamiv: Gumroad balance 0 (checked by Marc) → presumably no active Starter members; just hide/retire the tier.
6. Value: the passport, maps and comparator are free and public (see DELIVERABLES).
7. The hidden passport iframes in the Desk/print add GA pageviews (GA only, no ads).
8. Legal "Last updated" dates to set at publishing. The site-wide banner says « 14-day refund on new paid plans »: still true, but narrower than « every payment »; left as is (banner text in 30+ pages, not in scope).
9. The old J10/J14 emails are obsolete (EMAILS.md §4).
10. Workflow: cloud agent not available here → done in a local worktree (no repo clone added; no git hooks in the repo).
