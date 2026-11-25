# PREVIEW — Pet Desk Starter (25 Nov 2026, KST)

**Nothing is published.** Branch `petdesk-starter-20261125`, commits `c0942619` (feature) → `bfa0685f` (SQL grants + docs) → `3b4a9e50` (shots), local worktree `/workspace/petdesk-starter-wt`. No push (a hosted branch preview wouldn't show the Desk: the Edge Function isn't deployed). No Gumroad login, no Supabase migration, build.py not run, site/ = static/ (checked file by file), GA G-K45B2WNXMC only, header/footer/coral search icon unchanged.

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
   - Starter: « Start your 1-month free trial » → `https://petpolicycheck.gumroad.com/l/petdesk-starter?wanted=true` (**placeholder** until the product exists; the yearly toggle → `?yearly=true&wanted=true`), the text under it says "card required, automatic charge, reminder 48 h before", plus a secondary Request onboarding.
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

## Supabase steps (need Marc's OK — not done)
1. Apply `petdesk/sql/001_petdesk_starter.sql` to project uouccgyeujtmbeeneuwq (it only creates new `petdesk_*` objects; it touches nothing that exists).
2. Secrets:
   ```
   supabase secrets set --project-ref uouccgyeujtmbeeneuwq \
     GUMROAD_STARTER_PRODUCT_IDS=<product_id> \
     DESK_SESSION_SECRET=$(openssl rand -hex 32) \
     PETDESK_PING_SECRET=$(openssl rand -hex 16) \
     PETDESK_ALLOWED_ORIGINS=https://petpolicycheck.com,https://www.petpolicycheck.com
   ```
3. Deploy: `supabase functions deploy petdesk --project-ref uouccgyeujtmbeeneuwq --no-verify-jwt`. No JWT, because the site only has the publishable key; the function does its own key/session check and CORS.
4. Run the security + performance advisors, and do a test purchase (GUMROAD-SETTINGS D13).

## Tests
- `deno test -A petdesk/tests/core_test.ts` → **8/8 pass** (real function logic, mocked Gumroad): every subscription state, CORS, trial date, 1 seat, 15/month + 16th refused (429), invalid language pairs (EN+EN, EN+FR), watchlist > 5 refused, access closes after a re-check, ping secret + dedupe, `increment_uses_count=false` on every call.
- `python3 petdesk/tests/e2e.py` (Chrome, with a freshly started serve.ts — its in-memory store keeps the quota between runs) → **211/211 pass**; results in `e2e-results.json`:
  - each of the 6 /pro/ pages: no JS errors; Starter label; monthly href; yearly toggle and back; click opens the Gumroad product (intercepted); Pro and Ent have no Gumroad link and a mailto primary with the right subject; no old trial text visible; JSON-LD parses with FAQPage = 11 = visible FAQ; GA present and no AdSense.
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
1. The Gumroad product doesn't exist → the Starter button points to a placeholder; the `?yearly=true` parameter is undocumented (check it).
2. Supabase apply + deploy need Marc's OK (steps above). Until then, the live Desk can't open (so **don't publish the site before step 2**).
3. Own trial reminder/cancellation emails: Gumroad Workflows are blocked until $100 earned + 1 payout (art. 131); no SMTP. Gumroad's own 48 h reminder covers the legal minimum.
4. Passports in FR/DE/JA: the engine has no translation → promise limited to EN/ES/IT. The "After landing" block is partly in English in the ES version (existing engine text).
5. Possible active Starter members on tamiv → they need a decision (GUMROAD-SETTINGS B9).
6. Value: the passport, maps and comparator are free and public (see DELIVERABLES).
7. The hidden passport iframes in the Desk/print add GA pageviews (GA only, no ads).
8. Legal "Last updated" dates to set at publishing.
9. The old J10/J14 emails are obsolete (EMAILS.md §4).
10. Workflow: cloud agent not available here → done in a local worktree (no repo clone added; no git hooks in the repo).
