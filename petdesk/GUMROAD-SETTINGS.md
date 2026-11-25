# Gumroad settings for Marc — Pet Desk Starter (I did not log in or change anything on Gumroad)

## Status 25 Nov 2026, 09:20 KST
- Created by Marc (unpublished): product_id `Qtlp1phQoytjW-w_I-h0Og==`, https://petpolicycheck.gumroad.com/l/petdesk-starter, $49/month + $468/year, monthly by default, 1-month free trial, License key block + text in Content, receipt button « Open my Pet Desk key ». → A1–A8 done.
- The product_id is built into the deployed `petdesk` function (no secret needed; the `GUMROAD_STARTER_PRODUCT_IDS` secret would override it).
- **Old product tamiv:** Marc checked that the Gumroad balance is 0, so there are presumably no active Starter subscribers on tamiv → no migration needed (B9: only hide/retire the Starter tier).
- **Refund:** Gumroad's refund policy is one setting for the whole product (https://gumroad.com/help/article/335-custom-refund-policy); there is no "first payment only" option. The site's terms, refund policy and /pro/ FAQ now say the 14-day refund applies to **every payment (first payment and renewals)**, counted from that payment. Product setting text to use: « 14-day money-back guarantee on every payment: request a refund within 14 days of any charge (first payment or renewal) via your receipt or contact@petpolicycheck.com. »


Sources (official Gumroad pages, read on 25 Nov 2026):
- Memberships and free trials: https://gumroad.com/help/article/82-membership-products
- License keys: https://gumroad.com/help/article/76-license-keys
- Ping / resource subscriptions: https://gumroad.com/ping, https://gumroad.com/api
- Workflows: https://gumroad.com/help/article/131-using-workflows-to-send-automated-updates
- Receipts and access: https://gumroad.com/help/article/199-how-do-i-access-my-purchase, https://gumroad.com/help/article/204, https://gumroad.com/help/article/192, https://gumroad.com/help/article/282
- Custom receipt: https://gumroad.com/blog/p/customizable-receipts

## A. New product (separate from the current "tamiv" 3-tier product)
1. New product → type **Membership**. Name: `Pet Desk Starter · Advisor`.
2. Custom URL / permalink: **petdesk-starter**. The site links to `https://petpolicycheck.gumroad.com/l/petdesk-starter?wanted=true`. If you choose another permalink, tell me and I'll change the link in 1 place (petdesk/apply_starter_trial.py, then re-run).
3. One tier only (Starter). Recurrence: **Monthly $49** and **Yearly $468**. Default = Monthly.
   - Yearly link: the site sends the "yearly" toggle to `…/l/petdesk-starter?yearly=true&wanted=true`. **This parameter is NOT documented in the help pages I read.** After you create the product, open that URL: if the checkout doesn't preselect yearly, tell me and I'll point the yearly button to the plain product page (the buyer then picks yearly at checkout).
4. Settings → **Offer a free trial: ON → 1 month** (Gumroad only offers 1 week or 1 month; art. 82).
   What Gumroad does by itself (art. 82): the card is required; the charge happens automatically at the end of the trial (after 28–31 days for "1 month"); an email goes to the buyer **48 h before** the charge; you get an email when someone cancels; a customer who cancels during a first trial can't get a second trial; turning the trial off later does not affect current trials.
5. **Content tab** (what the buyer sees after checkout; the "View content" button in the receipt, art. 199/204):
   - Insert the **License key** block (art. 76).
   - Under it, paste this text and link:
     > **Open your Pet Desk:** https://petpolicycheck.com/pro/desk/ — paste the license key above. One seat: logging in on a new device closes the previous session. Your free month ends on the date shown in your Desk; Gumroad emails you 48 h before the first charge. Manage or cancel: "Manage membership" in your receipt or your Gumroad Library.
6. **Receipt tab** (blog "customizable receipts"):
   - Custom message (≤ 500 characters): see EMAILS.md §1.
   - Button text (≤ 26 characters): `Open my Pet Desk key`.
7. Refund policy on the product (Settings → « Specify a refund policy for this product », art. 335): 14 days, on every payment — text above.
8. After saving, copy the **product_id** (Product → Content → License key block, or the product's Settings; art. 76 says products created after 9 Jan 2023 require product_id) and send it to me. It goes into the `GUMROAD_STARTER_PRODUCT_IDS` secret of the Supabase function, not into the site.

## B. Existing "tamiv" product (Starter / Pro / Enterprise)
9. The site no longer links to tamiv. To avoid a second way in: **hide the Starter tier on tamiv** (or unpublish tamiv once you confirm there are no active members).
   ⚠ If tamiv has active Starter members, they have no license on the new product: tell me, and I'll add their product_id to the allowed list (1 env change) or we migrate them by hand.
10. Pro and Enterprise: no change needed on Gumroad (the site now shows "Request onboarding" by email).

## C. Optional
11. Settings → Advanced → **Ping / resource subscriptions**: URL `https://uouccgyeujtmbeeneuwq.supabase.co/functions/v1/petdesk/gumroad-ping?s=<PETDESK_PING_SECRET>` for sale, refund, dispute, cancellation, subscription_ended, subscription_restarted, subscription_updated. Without this, access still closes correctly, but up to 6 h late (the Desk re-checks with Gumroad every 6 h and on every login).
12. Workflows ("Member cancels", "Purchase"): ⚠ Gumroad doesn't send workflow emails until the account has **earned $100 after fees and received a payout** (art. 131), and a workflow can't be tested with a test purchase (use a 100% discount code). Drafts in EMAILS.md §3–4.

## D. Test purchase (100% discount code, before publishing the site) — checklist
13. Create a 100% discount code (art. 131: workflows/emails can't be checked with a normal "test purchase").
14. Open https://petpolicycheck.gumroad.com/l/petdesk-starter?wanted=true → checkout opens directly, monthly selected, trial "1 month free" shown, card asked.
15. Open https://petpolicycheck.gumroad.com/l/petdesk-starter?yearly=true&wanted=true → **does it preselect yearly ($468)?** (undocumented). If not, tell me: the yearly button will point to the plain product page.
16. Complete the purchase → receipt shows the license key, the custom text and the « Open my Pet Desk key » button; the content page shows the License key block.
17. Paste the key at https://petpolicycheck.com/pro/desk/ — ⚠ the site isn't published yet, so for now I'll test the key against the deployed function directly (send me the key privately, or run the curl in PREVIEW.md yourself). Expected: status **trial**, with an approximate end date ≈ purchase date + 1 month. **Key point to check: what Gumroad's license API returns during a trial** (subscription fields, sale_timestamp).
18. Log in from a 2nd browser → the 1st must be logged out (1 seat).
19. Issue 1 passport (EN+ES) → print sheet with agency name + reference.
20. Cancel via « Manage membership » → the Desk shows « access until <date> »; Gumroad sends the cancellation emails (you + buyer).
21. Refund the test sale in Gumroad → the Desk must refuse the key (« refunded ») at the next check (login or ≤ 6 h).
22. Afterwards: delete the test account row if you want (I can do it: `petdesk_accounts` where license_last4 = …), and delete the 100% code.
