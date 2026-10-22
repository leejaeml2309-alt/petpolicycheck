# Forum setup (Supabase free tier)

The forum is part of the static site: build.py writes it under `/forum/` with the same templates, header,
footer and palette. Until step 9 is done, `/forum/` is a noindex "coming soon" page (no ads, no scripts,
not in the sitemap, no nav link), so nothing changes for visitors or the AdSense review.

Files in this folder:

| Path | What it is |
|---|---|
| `sql/001_forum_schema.sql` | Tables, check constraints, RLS, triggers (pending-by-default, keyword pre-filter, rate limits, 3-report auto-hide, profile auto-create), admin RPC |
| `sql/002_moderation_terms.sql` | Seed list for the instant keyword pre-filter (EN / KO / FR: slurs, NSFW, politics, spam, links) |
| `moderate.py` | Moderator-bot CLI (service role, REST): `list`, `set`, `terms` |
| `supabase/functions/moderate/` | OPTIONAL edge function: extra OpenAI moderation pass (off by default) |
| `forum_pages.py`, `js/forum.js`, `i18n/*.json`, `categories.json` | Pages, client script, UI strings (EN, KO), category codes |
| `tests/` | Local SQL/RLS tests and a browser end-to-end test (see tests/README.md) |

## 1. Project

Already created by the owner in the Supabase dashboard (region **Northeast Asia (Seoul)**). Note from
**Project Settings > API** (or **API Keys**):

- Project URL: `https://<ref>.supabase.co`
- Public key: the **publishable** key (`sb_publishable_...`) or the legacy **anon** key. Safe in the browser.
- Secret key: a **secret** key (`sb_secret_...`) or the legacy **service_role** key. Never put it in
  config.json, the repo or a web page. It is only for moderate.py (env var) and the edge function.

## 2. Database

SQL Editor > New query: paste and run `sql/001_forum_schema.sql`, then `sql/002_moderation_terms.sql`.
Both are idempotent (safe to re-run after an edit). Or with psql over the session pooler:

    PGPASSWORD="$(cat /home/box/.supabase_db_password)" psql "host=aws-1-ap-northeast-2.pooler.supabase.com port=5432 \
      user=postgres.uouccgyeujtmbeeneuwq dbname=postgres sslmode=require" -v ON_ERROR_STOP=1 \
      -f forum/sql/001_forum_schema.sql -f forum/sql/002_moderation_terms.sql

(The box's network currently only allows outbound HTTPS/443, so from the box use the SQL editor.)

Check: run `tests/real_db_test.sql` in the SQL editor. It creates test users/posts inside a transaction that is
always rolled back and ends with the error message `FORUM SELF-TEST: 17 passed, 0 failed` (nothing is kept).
Then, from any machine with HTTPS: `bash forum/tests/real_rest_test.sh` (read-only checks with the public key:
anon sees only published rows, cannot insert, cannot read roles/terms or call the admin RPC).

## 3. Auth: email + password

Authentication > Sign In / Providers > **Email**: enabled, **Confirm email** ON, minimum password length 8.

Authentication > **URL Configuration**:
- Site URL: `https://petpolicycheck.com/forum/account.html`
- Redirect URLs (add all):
  - `https://petpolicycheck.com/forum/account.html`
  - `https://petpolicycheck.com/forum/account.html?**`
  - (optional for local tests) `http://localhost:8000/forum/account.html?**`

Email sending: Supabase's built-in mailer is only for testing (a few emails per hour). Before opening the forum,
set **Authentication > Emails > SMTP Settings** to a real provider (e.g. Resend, Brevo or Amazon SES free tiers)
with a sender such as `no-reply@petpolicycheck.com` (needs the provider's DNS records on the domain).
Optional: edit the "Confirm signup" and "Reset password" templates (English + Korean text in the same email).

## 4. Auth: Google

1. Google Cloud Console > APIs & Services > OAuth consent screen: External, app name "PetPolicyCheck",
   support email, authorized domains `petpolicycheck.com` and `<ref>.supabase.co`, scopes `email`, `profile`, `openid`.
   Privacy policy URL `https://petpolicycheck.com/privacy.html`. Publish the app (In production).
2. Credentials > Create OAuth client ID > Web application.
   - Authorized JavaScript origins: `https://petpolicycheck.com`
   - Authorized redirect URI: `https://<ref>.supabase.co/auth/v1/callback`
3. Supabase > Authentication > Sign In / Providers > **Google**: enable, paste Client ID and Client Secret, save.

The forum never shows the Google name: new users get the display name they typed, or `Traveller-xxxxxx`
(Google sign-ups), which they can change in My account.

## 5. Make the owner an admin

Sign up once on the live forum (or Authentication > Users > Add user), confirm the email, then in SQL Editor:

    update public.profiles set role = 'admin'
    where id = (select id from auth.users where email = 'OWNER_EMAIL');

The admin sees the "Moderation queue" button in My account (`/forum/admin.html`, noindex).

## 6. Moderation (default: AI moderator bot every ~30 minutes)

Flow: every post/comment is inserted as `pending` (not public). The database pre-filter instantly sets
`rejected` (slurs, NSFW, obvious politics, commercial spam) or `flagged` (links, contact spam, profanity,
borderline words). The bot reviews `pending` + `flagged` + reported items and decides. 3 reports on a published
item hide it (`flagged`) until reviewed. Authors see "Your post will appear after moderation (usually within
30 minutes)" and, in My account, the status and a translated reason.

moderate.py has two backends (env `FORUM_MODERATE_BACKEND` = auto | db | rest, default auto):

- **db**: direct Postgres via the session pooler with `psql`. Non-secret settings in `forum/db.json`
  (hosts tried in order, port 5432, user `postgres.uouccgyeujtmbeeneuwq`, db `postgres`, sslmode require);
  password read from `SUPABASE_DB_PASSWORD_FILE` (default `/home/box/.supabase_db_password`). No API key needed.
- **rest**: HTTPS with the secret key in env `SUPABASE_SERVICE_ROLE_KEY` (`sb_secret_...` or legacy service_role JWT).
  Works where only port 443 is open (the box today).
- **auto**: db when the password file exists; if it can't connect and `SUPABASE_SERVICE_ROLE_KEY` is set, falls back to rest.

`python3 forum/moderate.py check` says which backend works.

    python3 /workspace/petsite-forum/forum/moderate.py list   # JSON queue: id, type, title, body, categories, author, reports
    python3 forum/moderate.py set post <id> published "ok"
    python3 forum/moderate.py set comment <id> rejected "politics: mentions an election"
    python3 forum/moderate.py terms                         # current pre-filter list

The URL is read from config.json `forum.supabase_url` (or env `SUPABASE_URL`). Start the reason with one of
`politics, slur, nsfw, violence, spam, link` when rejecting/flagging: the author then sees the matching message
in their language ("Political content isn't allowed on this forum." / "이 포럼에서는 정치 관련 내용을 다루지 않아요.").

Bot rules (same as the community rules page): publish on-topic, kind travel experiences/questions; reject
abuse, harassment, hate, violence, sexual/NSFW, politics (any country), ads/spam, other people's personal data;
flag (leave for the owner) anything uncertain or with external links that look legitimate. Publishing can be
reversed at any time with another `set`.

Pre-filter list: edit rows in Table Editor > `moderation_terms` (no redeploy). `match_mode` word (Latin),
substring (Korean) or regex; `action` reject or flag.

Manual fallback: `/forum/admin.html` with the admin account (Publish / Reject / Keep flagged).

Suspend a user: `update public.profiles set banned = true where display_name = '...';` (they can no longer post,
comment or report).

## 7. Optional: OpenAI edge function (off by default)

Only if you want an extra automatic pass before the bot. Needs the Supabase CLI:

    cd forum                                   # functions live in forum/supabase/functions
    supabase init                              # once, if forum/supabase/config.toml doesn't exist (answer No to extras)
    supabase login && supabase link --project-ref <ref>
    supabase functions deploy moderate --no-verify-jwt
    supabase secrets set WEBHOOK_SECRET=$(openssl rand -hex 24) MODERATION_PROVIDER=openai OPENAI_API_KEY=sk-... AUTO_PUBLISH=false

Database > Webhooks > Create: name `moderate-posts`, table `posts`, event INSERT, type Supabase Edge Function
`moderate`, HTTP header `x-webhook-secret: <WEBHOOK_SECRET>`. Repeat for `comments`.
With `MODERATION_PROVIDER=none` (default) or no OpenAI key the function does nothing and the bot decides.
`AUTO_PUBLISH=true` would let clean items go live without the bot (not recommended while the site is young).

## 8. Supabase free-tier notes

- Free projects pause after ~7 days without API activity; the 30-minute bot and the nightly build keep it awake.
- 500 MB database, 50k monthly active users: far above what the forum needs. No images are stored (text only).

## 9. Turn the forum on

In config.json:

    "forum": {
      "enabled": true,
      "supabase_url": "https://<ref>.supabase.co",
      "supabase_anon_key": "sb_publishable_...",
      "contact_email": "contact@petpolicycheck.com"
    }

Then `python3 build.py`, check `site/forum/`, commit and push to main (GitHub Pages deploys).
What changes when enabled: "Forum" in the main nav and footer on every page, forum pages under /forum/,
"From the forum" boxes on airline pages and carrier/crate guides (linking to the matching filters),
the forum section in the privacy policy (replacing "No accounts, no forms"), and sitemap entries for
/forum/, /forum/guidelines.html and every published post.

## 10. Search engines (pre-rendered posts)

Every `python3 build.py` reads published posts and comments with the public key (exactly what any visitor can
see) and writes them as static pages `/forum/p/<id>-<slug>.html` with DiscussionForumPosting JSON-LD, listed in
the sitemap; the forum index lists the newest 30 statically. The nightly `refresh.py` already rebuilds and
commits `site/` and `data/`, so posts published during the day become indexable the next night. New posts are
visible immediately to visitors through the live page (`post.html?id=`, noindex). If the API is unreachable at
build time, the last good copy (`data/forum_cache.json`) is used. `FORUM_PRERENDER=0 python3 build.py` skips the fetch.
For faster indexing, run `python3 build.py` + commit after each moderation batch.

## 11. Adding a language later (e.g. French)

1. Copy `i18n/en.json` to `i18n/fr.json` and translate the values (keep the keys). `_lang_name` is the switcher label.
2. To let authors tag posts as French, add `"fr"` to `categories.json` `lang` and add `cat.lang.fr` to every
   dictionary (the database already accepts any 2-letter code).
3. Rebuild. The switcher shows every dictionary automatically.
