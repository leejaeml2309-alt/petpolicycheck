set -e
sudo -u postgres psql -qc "drop database if exists forume2e" -c "create database forume2e"
sudo -u postgres psql -q -d forume2e -c "do \$\$begin if not exists (select from pg_roles where rolname='authenticator') then create role authenticator login password 'authpw' noinherit; end if; end\$\$;"
sudo -u postgres psql -q -v ON_ERROR_STOP=1 -d forume2e -f /workspace/petsite-forum/forum/tests/supabase_stub.sql 2>&1 | grep -v "already exists" || true
sudo -u postgres psql -q -d forume2e -c "grant anon, authenticated, service_role to authenticator;"
sudo -u postgres psql -q -v ON_ERROR_STOP=1 -d forume2e -f /workspace/petsite-forum/forum/sql/001_forum_schema.sql 2>&1 | grep -v NOTICE || true
sudo -u postgres psql -q -v ON_ERROR_STOP=1 -d forume2e -f /workspace/petsite-forum/forum/sql/002_moderation_terms.sql
echo SETUP_DONE
