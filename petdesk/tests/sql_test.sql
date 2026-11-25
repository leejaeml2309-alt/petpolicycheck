-- psql -v ON_ERROR_STOP=1 -f tests/sql_test.sql  (local Postgres only; after 001_petdesk_starter.sql)
\set ON_ERROR_STOP 1
begin;
insert into petdesk_accounts(license_hash,license_last4,gumroad_product_id,status) values ('h_test','3333','PID','trial') returning id \gset
select count(*) as issued from (select (petdesk_issue_passport(:'id',('{"from":"US","to":"FR"}')::jsonb,array['en','es'],null,15)).* from generate_series(1,15)) s;
do $$ begin perform petdesk_issue_passport((select id from petdesk_accounts where license_hash='h_test'),'{}'::jsonb,array['en','it'],null,15); raise exception 'QUOTA NOT ENFORCED'; exception when others then if sqlerrm like '%QUOTA NOT%' then raise; end if; raise notice 'ok 16th refused: %', sqlerrm; end $$;
insert into petdesk_watch(account_id,slug) select :'id', s from unnest(array['delta','united','american','alaska','jetblue']) s;
do $$ begin insert into petdesk_watch(account_id,slug) values ((select id from petdesk_accounts where license_hash='h_test'),'spirit'); raise exception 'WATCH NOT LIMITED'; exception when others then if sqlerrm like '%NOT LIMITED%' then raise; end if; raise notice 'ok 6th watch refused: %', sqlerrm; end $$;
select count(distinct ref)=15 as refs_unique, min(ref) as sample_ref from petdesk_passports where account_id=:'id';
set local role anon;
do $$ begin perform 1 from petdesk_accounts; raise exception 'ANON CAN READ'; exception when insufficient_privilege then raise notice 'ok anon denied'; end $$;
do $$ begin perform petdesk_issue_passport(gen_random_uuid(),'{}'::jsonb,array['en','es'],null,15); raise exception 'ANON CAN EXEC'; exception when insufficient_privilege then raise notice 'ok anon cannot execute'; end $$;
reset role;
select relname, relrowsecurity from pg_class where relname like 'petdesk_%' and relkind='r' order by 1;
rollback;
begin;
insert into petdesk_accounts(license_hash,license_last4,gumroad_product_id,status) values ('h_svc','4444','PID','active') returning id \gset
set local role service_role;
select ref from petdesk_issue_passport(:'id','{"from":"US","to":"JP"}'::jsonb,array['en','it'],'c1',15);
insert into petdesk_watch(account_id,slug) values (:'id','delta');
select count(*) as svc_can_read from petdesk_accounts;
insert into petdesk_gumroad_events(resource_name,dedupe_key,payload) values ('sale','S1','{}');
rollback;
