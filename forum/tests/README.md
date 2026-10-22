# Forum tests (local, no Supabase account needed)

- `supabase_stub.sql`: minimal stand-in for Supabase (roles anon/authenticated/service_role, `auth.users`, `auth.uid()`).
- `rls_test.sql`: RLS, rate limits, keyword pre-filter, report auto-hide, admin RPC. Run:

      createdb forumtest && psql -d forumtest -f supabase_stub.sql -f ../sql/001_forum_schema.sql -f ../sql/002_moderation_terms.sql
      psql -d forumtest -f rls_test.sql      # expected errors are part of the test (permission denied, rate_limit_posts ...)

- `e2e/`: full browser test against a local PostgREST (stand-in for Supabase REST) and the built site.
  Needs PostgreSQL, the `postgrest` binary at /tmp/postgrest, Google Chrome and `npm i puppeteer-core` in e2e/.
  `pgrst.conf` + `jwt.py` share a throwaway local JWT secret. Start PostgREST and `python3 proxy.py ../../../site`
  (serves the site and /rest/v1 on http://localhost:8800), set config.json `forum.supabase_url` to
  http://localhost:8800 and `forum.supabase_anon_key` to `python3 jwt.py anon`, then `bash seed.sh && node e2e.js`.
  Auth (GoTrue) is not emulated: sessions are injected into localStorage with locally signed JWTs.
  Restore config.json and delete data/forum_cache.json afterwards.
- Edge function: `cd ../supabase/functions/moderate && deno check index.ts && deno test --allow-env index_test.ts`.
