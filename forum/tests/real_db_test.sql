-- Self-test of the forum schema on the REAL project. Safe: everything runs inside one transaction that is
-- always rolled back (the block ends by raising an exception carrying the result), so no test user, post,
-- comment or report survives. Run in the SQL editor or: psql ... -f forum/tests/real_db_test.sql
-- Expected final message: "FORUM SELF-TEST: N passed, 0 failed".
begin;
do $test$
declare
  u1 uuid := gen_random_uuid(); u2 uuid := gen_random_uuid(); u3 uuid := gen_random_uuid(); u4 uuid := gen_random_uuid();
  ok int := 0; bad int := 0; fails text := '';
  pid uuid; st text; n int; v text;
begin
  -- helpers are inline: as_user(uid) = set local role authenticated + JWT claims
  insert into auth.users (id, email, raw_user_meta_data, aud, role) values
    (u1, 'forum-selftest-1@example.invalid', '{"display_name":"SelftestOne"}', 'authenticated', 'authenticated'),
    (u2, 'forum-selftest-2@example.invalid', '{"display_name":"윤석열"}', 'authenticated', 'authenticated'),
    (u3, 'forum-selftest-3@example.invalid', '{}', 'authenticated', 'authenticated'),
    (u4, 'forum-selftest-4@example.invalid', '{}', 'authenticated', 'authenticated');

  select display_name into v from public.profiles where id = u1;
  if v = 'SelftestOne' then ok := ok + 1; else bad := bad + 1; fails := fails || ' profile_autocreate'; end if;
  select display_name into v from public.profiles where id = u2;
  if v like 'Traveller-%' then ok := ok + 1; else bad := bad + 1; fails := fails || ' political_display_name_replaced'; end if;

  -- anon: cannot insert, sees nothing unpublished
  execute 'set local role anon';
  perform set_config('request.jwt.claims', '{"role":"anon"}', true);
  begin
    insert into public.posts (title, body, transport, species) values ('anon post title', 'anon body that is long enough to pass checks', 'car', 'dog');
    bad := bad + 1; fails := fails || ' anon_insert_allowed';
  exception when insufficient_privilege then ok := ok + 1;
  end;
  begin
    perform role from public.profiles limit 1;
    bad := bad + 1; fails := fails || ' anon_reads_profile_role';
  exception when insufficient_privilege then ok := ok + 1;
  end;

  -- user 1 posts
  execute 'reset role';
  execute 'set local role authenticated';
  perform set_config('request.jwt.claims', json_build_object('role', 'authenticated', 'sub', u1)::text, true);
  insert into public.posts (title, body, transport, species, lang) values ('Selftest clean post', 'A calm train trip with our cat in a soft carrier, no problems.', 'train', 'cat', 'en') returning id, status into pid, st;
  if st = 'pending' then ok := ok + 1; else bad := bad + 1; fails := fails || ' clean_not_pending'; end if;
  insert into public.posts (title, body, transport, species) values ('Selftest politics', 'The election and Trump made the airport crowded with our dog.', 'plane_cabin', 'dog') returning status into st;
  if st = 'rejected' then ok := ok + 1; else bad := bad + 1; fails := fails || ' en_politics_not_rejected'; end if;
  insert into public.posts (title, body, transport, species, lang) values ('셀프테스트 욕설', '기차에서 어떤 사람이 씨발 이라고 해서 강아지가 놀랐어요 정말로요.', 'train', 'dog', 'ko') returning status into st;
  if st = 'rejected' then ok := ok + 1; else bad := bad + 1; fails := fails || ' ko_slur_not_rejected'; end if;
  insert into public.posts (title, body, transport, species) values ('Selftest link', 'Great pet taxi, see https://example.com for details about the trip.', 'taxi', 'dog') returning status into st;
  if st = 'flagged' then ok := ok + 1; else bad := bad + 1; fails := fails || ' link_not_flagged'; end if;
  insert into public.posts (title, body, transport, species, lang) values ('시발역 셀프테스트', '서울역 시발역에서 고양이와 함께 출발했어요. 아주 조용한 여행이었어요.', 'train', 'cat', 'ko') returning status into st;
  if st = 'pending' then ok := ok + 1; else bad := bad + 1; fails := fails || ' sibal_station_false_positive'; end if;
  begin  -- 6th post in 24 h
    insert into public.posts (title, body, transport, species) values ('Selftest sixth', 'This sixth post should hit the daily limit of five posts.', 'car', 'dog');
    bad := bad + 1; fails := fails || ' rate_limit_missing';
  exception when raise_exception then ok := ok + 1;
  end;
  begin
    update public.posts set status = 'published' where id = pid;
    bad := bad + 1; fails := fails || ' user_can_update_status';
  exception when insufficient_privilege then ok := ok + 1;
  end;
  begin
    insert into public.comments (post_id, body) values (pid, 'comment on a pending post');
    bad := bad + 1; fails := fails || ' comment_on_pending_allowed';
  exception when raise_exception then ok := ok + 1;
  end;
  select count(*) into n from public.posts where author_id = u1;
  if n = 5 then ok := ok + 1; else bad := bad + 1; fails := fails || ' author_sees_own=' || n; end if;

  -- anon cannot see pending
  execute 'reset role';
  execute 'set local role anon';
  perform set_config('request.jwt.claims', '{"role":"anon"}', true);
  select count(*) into n from public.posts where id = pid;
  if n = 0 then ok := ok + 1; else bad := bad + 1; fails := fails || ' anon_sees_pending'; end if;

  -- moderator (no JWT, like moderate.py over the pooler) publishes
  execute 'reset role';
  perform set_config('request.jwt.claims', '', true);
  update public.posts set status = 'published', mod_reason = 'selftest', moderated_at = now() where id = pid;
  execute 'set local role anon';
  perform set_config('request.jwt.claims', '{"role":"anon"}', true);
  select count(*) into n from public.posts where id = pid;
  if n = 1 then ok := ok + 1; else bad := bad + 1; fails := fails || ' anon_cannot_see_published'; end if;

  -- 3 reports hide it
  foreach v in array array[u2::text, u3::text, u4::text] loop
    execute 'reset role';
    execute 'set local role authenticated';
    perform set_config('request.jwt.claims', json_build_object('role', 'authenticated', 'sub', v)::text, true);
    insert into public.reports (target_type, target_id, reason) values ('post', pid, 'selftest');
  end loop;
  execute 'reset role';
  perform set_config('request.jwt.claims', '', true);
  select status into st from public.posts where id = pid;
  if st = 'flagged' then ok := ok + 1; else bad := bad + 1; fails := fails || ' reports_did_not_hide'; end if;

  -- RLS flags on every table
  select count(*) into n from pg_class where relnamespace = 'public'::regnamespace and relrowsecurity
    and relname in ('profiles', 'posts', 'comments', 'reports', 'moderation_terms');
  if n = 5 then ok := ok + 1; else bad := bad + 1; fails := fails || ' rls_not_enabled'; end if;

  raise exception 'FORUM SELF-TEST: % passed, % failed%', ok, bad, case when bad > 0 then ':' || fails else '' end;
end
$test$;
rollback;
