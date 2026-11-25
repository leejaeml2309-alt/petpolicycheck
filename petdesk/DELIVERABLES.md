# DELIVERABLES — Pet Desk Starter (one promise = one way to deliver it)

Rule applied: built today, or removed from the promise. Times = work time today (agent); "credits" = no paid service added (Supabase free tier, Gumroad's own features).

| # | Promise on /pro/ (Starter) | How it's delivered | Status | Time / credits |
|---|---|---|---|---|
| 1 | 1-month free trial, card required, automatic charge at the end, reminder 48 h before | Gumroad's "Offer a free trial: 1 month" on the new product (art. 82) | **Marc's setting** (GUMROAD-SETTINGS A4) | 5 min, $0 |
| 2 | Access right after checkout | License key block on the Gumroad content page and receipt → /pro/desk/ | **Built** (desk in 6 languages + Edge Function) — Gumroad block = Marc's setting | done; $0 |
| 3 | 1 seat | Each login rotates a server session_nonce; the old device is logged out ("session_replaced") | **Built + tested** | done |
| 4 | Up to 15 dual-language passports / month | Server quota (SQL function with a lock, 15/calendar month), print sheet with 2 passports + agency header + reference PD-YYYYMM-… | **Built + tested** for **EN / ES / IT**. | done |
| 4b | (was: any 2 of the 6 languages) | The passport engine only has ES/IT translations; FR/DE/JA print in English | **Removed from the promise** → "(EN / ES / IT)". Adding FR+DE = Traducteur overlays (~40 KB of text per language) | ~1 day per language, later |
| 5 | 50-state & international maps | Existing public maps, linked from the Desk ("Your Starter tools") | **Exists** (public) | 0 |
| 6 | 30-airline fee & under-seat comparator | Existing /airlines/compare/ (30 airlines), linked from the Desk | **Exists** (public) | 0 |
| 7 | (was: 5 automated rule-change alerts) | Email alerts need SMTP + cron, which we don't have | **Removed** → reworded as "Watchlist of up to 5 airlines in your Desk, with every logged rule change flagged" | — |
| 7b | Watchlist of 5 airlines | Saved server-side (max 5, SQL trigger), flags entries from /{lang}/updates.html for those airlines | **Built + tested** | done |
| 8 | Cancel any time, access until the end of the period | Gumroad "Manage membership" (art. 192) + the Desk re-checks Gumroad (on login and every 6 h; ping optional) → "access until <date>", then closed | **Built + tested (mocked)** | done |
| 9 | 14-day refund on the first payment | Marc in Gumroad (refund) → the Desk denies access as soon as Gumroad reports "refunded" | **Built** (denial tested, mocked) | 0 |
| 10 | Welcome / reminder / cancellation emails | Gumroad receipt text + content page; Gumroad's own 48 h email; Gumroad cancellation confirmation | **Drafts** (EMAILS.md). Own reminder: **blocked** (Workflows $100 rule / no SMTP) | 10 min Marc |

⚠ Value: the passport, maps and comparator are free and public. What Starter adds is the agency header + dual-language pack, the reference log, the monthly allowance and the watchlist. Worth checking with Marc that this is enough for $49.

## Delivery order
1. Marc: create the Gumroad product (GUMROAD-SETTINGS A1–A8) → send me the product_id and permalink. *(15 min)*
2. Marc's OK → I apply `petdesk/sql/001_petdesk_starter.sql`, set the secrets, `supabase functions deploy petdesk --no-verify-jwt`, run the advisors. *(15 min)*
3. Test purchase with a 100% code (D13) on the live function, before the site is published. *(15 min)*
4. Marc's OK → merge the branch to main + deploy the site. *(10 min)*
5. Hide Starter on tamiv (B9). Optional ping (C11).
6. Later: FR/DE passport overlays; email alerts if SMTP is added.
