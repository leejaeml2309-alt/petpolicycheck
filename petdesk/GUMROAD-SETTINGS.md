# Gumroad settings for Marc — Pet Desk Starter (to do by Marc; I did not log in or change anything on Gumroad)

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
7. Refund policy on the product: 14 days on the first payment (same as /refund-policy.html).
8. After saving, copy the **product_id** (Product → Content → License key block, or the product's Settings; art. 76 says products created after 9 Jan 2023 require product_id) and send it to me. It goes into the `GUMROAD_STARTER_PRODUCT_IDS` secret of the Supabase function, not into the site.

## B. Existing "tamiv" product (Starter / Pro / Enterprise)
9. The site no longer links to tamiv. To avoid a second way in: **hide the Starter tier on tamiv** (or unpublish tamiv once you confirm there are no active members).
   ⚠ If tamiv has active Starter members, they have no license on the new product: tell me, and I'll add their product_id to the allowed list (1 env change) or we migrate them by hand.
10. Pro and Enterprise: no change needed on Gumroad (the site now shows "Request onboarding" by email).

## C. Optional
11. Settings → Advanced → **Ping / resource subscriptions**: URL `https://uouccgyeujtmbeeneuwq.supabase.co/functions/v1/petdesk/gumroad-ping?s=<PETDESK_PING_SECRET>` for sale, refund, dispute, cancellation, subscription_ended, subscription_restarted, subscription_updated. Without this, access still closes correctly, but up to 6 h late (the Desk re-checks with Gumroad every 6 h and on every login).
12. Workflows ("Member cancels", "Purchase"): ⚠ Gumroad doesn't send workflow emails until the account has **earned $100 after fees and received a payout** (art. 131), and a workflow can't be tested with a test purchase (use a 100% discount code). Drafts in EMAILS.md §3–4.

## D. Test purchase (after A, before publishing the site)
13. Create a 100% discount code. Buy Starter with it on the **yearly and monthly** options, then check:
    - the license key shows in the receipt and the content page;
    - the key opens https://petpolicycheck.com/pro/desk/ (after Supabase deploy);
    - **what the license verify API returns during a trial** (I couldn't test this with a real key; my code treats sale_timestamp + 1 month as the trial end, and the reminder date comes from Gumroad);
    - cancel from "Manage membership": the Desk should show "access until …".
