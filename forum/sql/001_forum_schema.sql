-- PetPolicyCheck forum: schema, row-level security, moderation pre-filter, rate limits.
-- Run once in the Supabase SQL editor (or `supabase db push`). Idempotent-ish: safe to re-run
-- on an empty project; tables use IF NOT EXISTS, functions/policies are replaced.
--
-- Status workflow:  every insert -> 'pending' (invisible to the public)
--                   keyword pre-filter (this file) -> 'rejected' (slurs, NSFW, politics, spam) or
--                   'flagged' (external links, borderline terms) instantly
--                   moderator bot (forum/moderate.py, every ~30 min) or the owner (admin.html) ->
--                   'published' / 'rejected' / 'flagged'
--                   3 reports on a published item -> 'flagged' (hidden) automatically
-- Only the service role (moderate.py, edge function) and admins (via moderate_item()) change status.

create extension if not exists pgcrypto;

-- ------------------------------------------------------------------ tables
create table if not exists public.profiles (
  id           uuid primary key references auth.users (id) on delete cascade,
  display_name text not null check (char_length(display_name) between 2 and 40),
  role         text not null default 'user' check (role in ('user', 'admin')),
  banned       boolean not null default false,
  created_at   timestamptz not null default now()
);
create unique index if not exists profiles_display_name_ci on public.profiles (lower(display_name));

create table if not exists public.posts (
  id           uuid primary key default gen_random_uuid(),
  author_id    uuid not null default auth.uid() references public.profiles (id) on delete cascade,
  lang         text not null default 'en' check (lang ~ '^[a-z]{2}$'),
  title        text not null check (char_length(btrim(title)) between 5 and 140),
  body         text not null check (char_length(btrim(body)) between 30 and 8000),
  transport    text not null check (transport in ('plane_cabin','plane_hold','train','subway','bus_intercity','bus_city','car','taxi','ferry','other')),
  weather      text check (weather in ('hot','cold','mild','rainy','snowy')),
  season       text check (season in ('spring','summer','autumn','winter')),
  carrier      text check (carrier in ('soft_bag','hard_crate','none_harness','stroller','other')),
  species      text not null check (species in ('dog','cat')),
  breed        text check (char_length(breed) <= 60),
  weight       text check (weight in ('w_lt5','w5_8','w8_15','w15_25','w25_40','w_gt40')),
  airline_slug text check (airline_slug ~ '^[a-z0-9-]{2,40}$'),
  operator     text check (char_length(operator) <= 80),
  route_from   text check (char_length(route_from) <= 60),
  route_to     text check (char_length(route_to) <= 60),
  trip_date    date check (trip_date between date '2000-01-01' and (current_date + 1)),
  status       text not null default 'pending' check (status in ('pending','published','rejected','flagged')),
  mod_reason   text check (char_length(mod_reason) <= 300),
  moderated_at timestamptz,
  report_count integer not null default 0,
  created_at   timestamptz not null default now()
);
create index if not exists posts_status_created on public.posts (status, created_at desc);
create index if not exists posts_author on public.posts (author_id, created_at desc);

create table if not exists public.comments (
  id           uuid primary key default gen_random_uuid(),
  post_id      uuid not null references public.posts (id) on delete cascade,
  author_id    uuid not null default auth.uid() references public.profiles (id) on delete cascade,
  body         text not null check (char_length(btrim(body)) between 2 and 3000),
  status       text not null default 'pending' check (status in ('pending','published','rejected','flagged')),
  mod_reason   text check (char_length(mod_reason) <= 300),
  moderated_at timestamptz,
  report_count integer not null default 0,
  created_at   timestamptz not null default now()
);
create index if not exists comments_post on public.comments (post_id, created_at);
create index if not exists comments_status on public.comments (status, created_at);
create index if not exists comments_author on public.comments (author_id, created_at desc);

create table if not exists public.reports (
  id           uuid primary key default gen_random_uuid(),
  reporter_id  uuid not null default auth.uid() references public.profiles (id) on delete cascade,
  target_type  text not null check (target_type in ('post','comment')),
  target_id    uuid not null,
  reason       text check (char_length(reason) <= 500),
  created_at   timestamptz not null default now(),
  unique (reporter_id, target_type, target_id)
);
create index if not exists reports_target on public.reports (target_type, target_id);

-- Configurable pre-filter terms (edit rows in the Table Editor; no redeploy needed).
-- match_mode: 'word' = whole word, case-insensitive (Latin scripts)
--             'substring' = anywhere in the text (use for Korean, where particles attach to words)
--             'regex' = POSIX regex, case-insensitive
-- action:     'reject' = rejected immediately; 'flag' = hidden, waits for the moderator with priority
create table if not exists public.moderation_terms (
  id         bigint generated always as identity primary key,
  term       text not null,
  lang       text not null default 'en',
  category   text not null check (category in ('slur','nsfw','violence','politics','spam','link','other')),
  action     text not null default 'reject' check (action in ('reject','flag')),
  match_mode text not null default 'word' check (match_mode in ('word','substring','regex')),
  enabled    boolean not null default true,
  unique (term, match_mode)
);

-- ------------------------------------------------------------------ helpers
create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin' and not p.banned);
$$;

create or replace function public.can_post() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.profiles p where p.id = auth.uid() and not p.banned);
$$;

-- True when the request comes from an end user through the API (JWT role anon / authenticated).
-- False for the service role (moderate.py, edge function) and the SQL editor (no JWT).
-- Uses the JWT claim, not current_user, because it is called inside SECURITY DEFINER triggers.
create or replace function public._is_end_user() returns boolean
language sql stable set search_path = '' as $$
  select coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'role', '') in ('anon', 'authenticated');
$$;

-- First matching pre-filter term: reject terms win over flag terms.
create or replace function public.moderation_scan(txt text)
returns table (action text, category text, term text)
language sql stable security definer set search_path = '' as $$
  select t.action, t.category, t.term
  from public.moderation_terms t
  where t.enabled and coalesce(txt, '') <> '' and (
        (t.match_mode = 'substring' and strpos(lower(txt), lower(t.term)) > 0)
     or (t.match_mode = 'regex' and txt ~* t.term)
     or (t.match_mode = 'word' and txt ~* ('(^|[^[:alnum:]_])'
            || regexp_replace(t.term, '([.^$*+?()\[\]{}|\\-])', '\\\1', 'g')
            || '($|[^[:alnum:]_])')))
  order by (t.action = 'reject') desc, t.id
  limit 1;
$$;

-- ------------------------------------------------------------------ triggers: posts / comments
create or replace function public.forum_before_insert() returns trigger
language plpgsql security definer set search_path = '' as $$
declare
  hit record;
  txt text;
  n int;
begin
  if public._is_end_user() then
    -- authors cannot choose their own id, status or moderation fields
    new.author_id    := auth.uid();
    new.status       := 'pending';
    new.mod_reason   := null;
    new.moderated_at := null;
    new.report_count := 0;
    new.created_at   := now();
    if new.author_id is null then
      raise exception 'not_signed_in' using errcode = '42501';
    end if;
    -- DB-level rate limits
    if tg_table_name = 'posts' then
      select count(*) into n from public.posts where author_id = new.author_id and created_at > now() - interval '24 hours';
      if n >= 5 then raise exception 'rate_limit_posts' using errcode = 'P0001', hint = 'max 5 posts per 24 hours'; end if;
    else
      select count(*) into n from public.comments where author_id = new.author_id and created_at > now() - interval '24 hours';
      if n >= 30 then raise exception 'rate_limit_comments' using errcode = 'P0001', hint = 'max 30 comments per 24 hours'; end if;
      if not exists (select 1 from public.posts p where p.id = new.post_id and p.status = 'published') then
        raise exception 'post_not_open' using errcode = 'P0001';
      end if;
    end if;
  end if;
  -- instant keyword pre-filter
  if tg_table_name = 'posts' then
    txt := concat_ws(E'\n', new.title, new.body, new.breed, new.operator, new.route_from, new.route_to);
  else
    txt := new.body;
  end if;
  select * into hit from public.moderation_scan(txt);
  if found then
    new.status := case when hit.action = 'reject' then 'rejected' else 'flagged' end;
    new.mod_reason := 'auto:' || hit.category;
    new.moderated_at := now();
  end if;
  return new;
end $$;

drop trigger if exists posts_before_insert on public.posts;
create trigger posts_before_insert before insert on public.posts
  for each row execute function public.forum_before_insert();
drop trigger if exists comments_before_insert on public.comments;
create trigger comments_before_insert before insert on public.comments
  for each row execute function public.forum_before_insert();

-- ------------------------------------------------------------------ triggers: reports
create or replace function public.reports_after_insert() returns trigger
language plpgsql security definer set search_path = '' as $$
declare n int;
begin
  select count(*) into n from public.reports where target_type = new.target_type and target_id = new.target_id;
  if new.target_type = 'post' then
    update public.posts set report_count = n,
           status = case when n >= 3 and status = 'published' then 'flagged' else status end,
           mod_reason = case when n >= 3 and status = 'published' then 'auto:reports' else mod_reason end,
           moderated_at = case when n >= 3 and status = 'published' then now() else moderated_at end
     where id = new.target_id;
  else
    update public.comments set report_count = n,
           status = case when n >= 3 and status = 'published' then 'flagged' else status end,
           mod_reason = case when n >= 3 and status = 'published' then 'auto:reports' else mod_reason end,
           moderated_at = case when n >= 3 and status = 'published' then now() else moderated_at end
     where id = new.target_id;
  end if;
  return null;
end $$;

create or replace function public.reports_before_insert() returns trigger
language plpgsql security definer set search_path = '' as $$
declare n int;
begin
  if public._is_end_user() then
    new.reporter_id := auth.uid();
    new.created_at := now();
    select count(*) into n from public.reports where reporter_id = new.reporter_id and created_at > now() - interval '24 hours';
    if n >= 20 then raise exception 'rate_limit_reports' using errcode = 'P0001'; end if;
  end if;
  if new.target_type = 'post' and not exists (select 1 from public.posts where id = new.target_id) then
    raise exception 'report_target_missing' using errcode = 'P0001';
  end if;
  if new.target_type = 'comment' and not exists (select 1 from public.comments where id = new.target_id) then
    raise exception 'report_target_missing' using errcode = 'P0001';
  end if;
  return new;
end $$;

drop trigger if exists reports_before_insert on public.reports;
create trigger reports_before_insert before insert on public.reports
  for each row execute function public.reports_before_insert();
drop trigger if exists reports_after_insert on public.reports;
create trigger reports_after_insert after insert on public.reports
  for each row execute function public.reports_after_insert();

-- ------------------------------------------------------------------ profiles: auto-create on sign-up
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = '' as $$
declare
  want text := btrim(regexp_replace(coalesce(new.raw_user_meta_data ->> 'display_name', ''), '[[:cntrl:]<>]', '', 'g'));
  name text;
  i int := 0;
begin
  -- Never use the Google full name by default (privacy): only an explicitly chosen display name.
  if char_length(want) < 2 or char_length(want) > 40 or exists (select 1 from public.moderation_scan(want)) then
    want := 'Traveller-' || substr(replace(new.id::text, '-', ''), 1, 6);
  end if;
  name := want;
  while exists (select 1 from public.profiles where lower(display_name) = lower(name)) loop
    i := i + 1;
    name := left(want, 34) || '-' || i;
  end loop;
  insert into public.profiles (id, display_name) values (new.id, name);
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

create or replace function public.profiles_before_update() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if public._is_end_user() then
    new.display_name := btrim(new.display_name);
    if exists (select 1 from public.moderation_scan(new.display_name)) then
      raise exception 'display_name_not_allowed' using errcode = 'P0001';
    end if;
  end if;
  return new;
end $$;

drop trigger if exists profiles_before_update on public.profiles;
create trigger profiles_before_update before update on public.profiles
  for each row execute function public.profiles_before_update();

-- ------------------------------------------------------------------ admin RPC (manual fallback page)
create or replace function public.moderate_item(p_type text, p_id uuid, p_status text, p_reason text default null)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_admin() then
    raise exception 'admin_only' using errcode = '42501';
  end if;
  if p_status not in ('pending','published','rejected','flagged') then
    raise exception 'bad_status' using errcode = '22023';
  end if;
  if p_type = 'post' then
    update public.posts set status = p_status, mod_reason = left(coalesce(p_reason, 'admin'), 300), moderated_at = now() where id = p_id;
  elsif p_type = 'comment' then
    update public.comments set status = p_status, mod_reason = left(coalesce(p_reason, 'admin'), 300), moderated_at = now() where id = p_id;
  else
    raise exception 'bad_type' using errcode = '22023';
  end if;
  if not found then raise exception 'not_found' using errcode = 'P0002'; end if;
end $$;

-- ------------------------------------------------------------------ privileges
-- Supabase grants everything to anon/authenticated by default; tighten to exactly what the UI needs.
revoke all on public.profiles, public.posts, public.comments, public.reports, public.moderation_terms from anon, authenticated;

grant select (id, display_name, created_at) on public.profiles to anon, authenticated;
grant update (display_name) on public.profiles to authenticated;

grant select on public.posts, public.comments to anon, authenticated;
grant insert (lang, title, body, transport, weather, season, carrier, species, breed, weight,
              airline_slug, operator, route_from, route_to, trip_date) on public.posts to authenticated;
grant insert (post_id, body) on public.comments to authenticated;
grant delete on public.posts, public.comments to authenticated;

grant insert (target_type, target_id, reason) on public.reports to authenticated;
grant select (id, target_type, target_id, reason, created_at) on public.reports to authenticated;

revoke execute on function public.moderate_item(text, uuid, text, text) from public, anon;
grant execute on function public.moderate_item(text, uuid, text, text) to authenticated;
grant execute on function public.is_admin() to anon, authenticated;
revoke execute on function public.moderation_scan(text) from public, anon, authenticated;

-- ------------------------------------------------------------------ row-level security
alter table public.profiles enable row level security;
alter table public.posts enable row level security;
alter table public.comments enable row level security;
alter table public.reports enable row level security;
alter table public.moderation_terms enable row level security;  -- no policies: service role only

drop policy if exists profiles_read on public.profiles;
create policy profiles_read on public.profiles for select to anon, authenticated using (true);
drop policy if exists profiles_update_own on public.profiles;
create policy profiles_update_own on public.profiles for update to authenticated
  using (id = (select auth.uid())) with check (id = (select auth.uid()));

drop policy if exists posts_read on public.posts;
create policy posts_read on public.posts for select to anon, authenticated
  using (status = 'published' or author_id = (select auth.uid()) or (select public.is_admin()));
drop policy if exists posts_insert_own on public.posts;
create policy posts_insert_own on public.posts for insert to authenticated
  with check (author_id = (select auth.uid()) and (select public.can_post()));
drop policy if exists posts_delete_own on public.posts;
create policy posts_delete_own on public.posts for delete to authenticated
  using (author_id = (select auth.uid()) or (select public.is_admin()));

drop policy if exists comments_read on public.comments;
create policy comments_read on public.comments for select to anon, authenticated
  using ((status = 'published' and exists (select 1 from public.posts p where p.id = post_id and p.status = 'published'))
         or author_id = (select auth.uid()) or (select public.is_admin()));
drop policy if exists comments_insert_own on public.comments;
create policy comments_insert_own on public.comments for insert to authenticated
  with check (author_id = (select auth.uid()) and (select public.can_post()));
drop policy if exists comments_delete_own on public.comments;
create policy comments_delete_own on public.comments for delete to authenticated
  using (author_id = (select auth.uid()) or (select public.is_admin()));

drop policy if exists reports_insert_own on public.reports;
create policy reports_insert_own on public.reports for insert to authenticated
  with check (reporter_id = (select auth.uid()) and (select public.can_post()));
drop policy if exists reports_read_own on public.reports;
create policy reports_read_own on public.reports for select to authenticated
  using (reporter_id = (select auth.uid()) or (select public.is_admin()));
