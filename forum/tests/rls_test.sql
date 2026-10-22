\set ON_ERROR_STOP 0
\set u1 '11111111-1111-1111-1111-111111111111'
\set u2 '22222222-2222-2222-2222-222222222222'
\set ad '33333333-3333-3333-3333-333333333333'
insert into auth.users (id, raw_user_meta_data) values (:'u1', '{"display_name":"Mina"}'), (:'u2', '{"display_name":"mina"}'), (:'ad', '{"display_name":"윤석열"}');
select display_name, role from public.profiles order by display_name;
update public.profiles set role = 'admin' where id = :'ad';

-- as user 1
set role authenticated; select set_config('request.jwt.claims', '{"role":"authenticated","sub":"11111111-1111-1111-1111-111111111111"}', false);
insert into public.posts (title, body, transport, species, lang) values ('Seoul to Jeju with my Shih Tzu', 'The cabin crew were lovely and the carrier fit under the seat without trouble.', 'plane_cabin', 'dog', 'en') returning status, mod_reason;
insert into public.posts (title, body, transport, species, lang) values ('KTX 부산 여행', '강아지와 KTX를 탔어요. 이재명 얘기는 하지 맙시다 그래도 정말 좋았어요 다들 친절했어요.', 'train', 'dog', 'ko') returning status, mod_reason;
insert into public.posts (title, body, transport, species) values ('Taxi from ICN', 'Visit www.example.com for a cheap pet taxi from Incheon airport to Seoul.', 'taxi', 'cat') returning status, mod_reason;
insert into public.posts (title, body, transport, species) values ('시발역 이야기', '서울역 시발역에서 출발했어요. 고양이와 함께 기차 여행, 정말 조용했어요!', 'train', 'cat') returning status, mod_reason;
-- cannot set status / author
insert into public.posts (title, body, transport, species, status) values ('x', 'y', 'car', 'dog', 'published');
-- bad category
insert into public.posts (title, body, transport, species) values ('Bad category here', 'This body is long enough to pass the length check okay.', 'rocket', 'dog');
-- rate limit: 4 posts so far, 5th ok, 6th fails
insert into public.posts (title, body, transport, species) values ('Car trip one', 'Drove three hours with two cats in hard crates, all fine.', 'car', 'cat') returning status;
insert into public.posts (title, body, transport, species) values ('Car trip two', 'Drove three hours with two cats in hard crates, all fine.', 'car', 'cat') returning status;
-- user can't update status
update public.posts set status = 'published';
select count(*) as own_visible from public.posts;
-- user can rename self, not to a slur, not change role
update public.profiles set display_name = 'Mina K' where id = auth.uid();
update public.profiles set display_name = '병신' where id = auth.uid();
update public.profiles set role = 'admin' where id = auth.uid();
-- user can't read moderation_terms or call moderate_item
select count(*) from public.moderation_terms;
select public.moderate_item('post', (select id from public.posts limit 1), 'published', null);
reset role;

-- anon sees nothing yet
set role anon; select set_config('request.jwt.claims', '{"role":"anon"}', false);
select count(*) as anon_visible from public.posts;
insert into public.posts (title, body, transport, species) values ('anon post', 'anon body long enough to pass the checks', 'car', 'dog');
reset role;

-- service role (moderate.py) publishes the first post
set role service_role; select set_config('request.jwt.claims', '{"role":"service_role"}', false);
update public.posts set status = 'published', mod_reason = 'bot: ok', moderated_at = now() where title like 'Seoul to Jeju%';
reset role;

-- anon now sees exactly 1, comments of user 2
set role anon; select set_config('request.jwt.claims', '{"role":"anon"}', false);
select title, status from public.posts;
select p.title, a.display_name from public.posts p join public.profiles a on a.id = p.author_id;
select role from public.profiles;  -- must fail: role column not granted
reset role;

set role authenticated; select set_config('request.jwt.claims', '{"role":"authenticated","sub":"22222222-2222-2222-2222-222222222222"}', false);
insert into public.comments (post_id, body) select id, 'Great tip, thanks!' from public.posts where status = 'published' returning status;
insert into public.comments (post_id, body) select id, 'Comment on a pending post' from public.posts where title like 'Car trip one' ;
insert into public.reports (target_type, target_id, reason) select 'post', id, 'spam' from public.posts where status = 'published';
insert into public.reports (target_type, target_id, reason) select 'post', id, 'again' from public.posts where status = 'published';
reset role;
-- two more reporters (service inserts as other users to simulate) -> auto-flag
insert into auth.users (id) values ('44444444-4444-4444-4444-444444444444'), ('55555555-5555-5555-5555-555555555555');
set role authenticated;
select set_config('request.jwt.claims', '{"role":"authenticated","sub":"44444444-4444-4444-4444-444444444444"}', false);
insert into public.reports (target_type, target_id) select 'post', id from public.posts where title like 'Seoul to Jeju%';
select set_config('request.jwt.claims', '{"role":"authenticated","sub":"55555555-5555-5555-5555-555555555555"}', false);
select count(*) as visible_before_3rd from public.posts where status = 'published';
reset role;
insert into public.reports (reporter_id, target_type, target_id) select '55555555-5555-5555-5555-555555555555', 'post', id from public.posts where title like 'Seoul to Jeju%';
select title, status, report_count, mod_reason from public.posts where title like 'Seoul to Jeju%';

-- admin RPC
set role authenticated; select set_config('request.jwt.claims', '{"role":"authenticated","sub":"33333333-3333-3333-3333-333333333333"}', false);
select count(*) as admin_sees_all from public.posts;
select public.moderate_item('post', (select id from public.posts where title like 'Seoul to Jeju%'), 'published', 'admin: reviewed reports');
select title, status from public.posts where status = 'published';
reset role;
-- 6th post rate limit
set role authenticated; select set_config('request.jwt.claims', '{"role":"authenticated","sub":"11111111-1111-1111-1111-111111111111"}', false);
insert into public.posts (title, body, transport, species) values ('Car trip three', 'Drove three hours with two cats in hard crates, all fine.', 'car', 'cat');
delete from public.posts where title = 'Car trip two';
select count(*) as after_delete from public.posts where author_id = auth.uid();
reset role;
