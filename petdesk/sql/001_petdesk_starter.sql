-- Pet Desk Starter: access by Gumroad license key, checked server-side by the
-- Edge Function `petdesk`. PREVIEW FILE — NOT APPLIED. Apply only after Marc's OK
-- (Supabase project uouccgyeujtmbeeneuwq, same project as the forum).
--
-- Security model
--  * RLS is ON for every table and there is NO policy for anon/authenticated:
--    the browser (publishable key) cannot read or write anything here.
--  * Only the Edge Function, running with the service-role key (never shipped
--    to the site), reads/writes these tables.
--  * We never store the raw license key: only sha256(key) + last 4 chars.

create extension if not exists pgcrypto;

create table if not exists public.petdesk_accounts (
  id                 uuid primary key default gen_random_uuid(),
  license_hash       text not null unique,          -- hex sha256 of the Gumroad license key
  license_last4      text not null,
  plan               text not null default 'starter' check (plan in ('starter')),
  gumroad_product_id text not null,
  gumroad_sale_id    text,
  subscription_id    text,
  email              text,                          -- purchase email returned by Gumroad
  recurrence         text,                          -- monthly | yearly
  sale_timestamp     timestamptz,                   -- start of the subscription (trial start)
  status             text not null default 'active'
                     check (status in ('trial','active','cancelling','ended','refunded')),
  access_until       timestamptz,                   -- set when Gumroad reports an end date
  agency_name        text check (char_length(agency_name) <= 80),
  seats              int  not null default 1 check (seats = 1),
  session_nonce      text,                          -- 1 seat = 1 live session; rotated on login
  last_verified_at   timestamptz,
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);

create table if not exists public.petdesk_passports (
  id          bigserial primary key,
  account_id  uuid not null references public.petdesk_accounts(id) on delete cascade,
  period      text not null,                        -- 'YYYY-MM' (UTC) for the 15 / month quota
  ref         text not null unique,                 -- e.g. PD-202611-AB12-03
  route       jsonb not null,                       -- {from,to,state,airline,pet,date,ret,retdate}
  langs       text[] not null check (array_length(langs,1) = 2),
  client_ref  text check (char_length(client_ref) <= 60),
  created_at  timestamptz not null default now()
);
create index if not exists petdesk_passports_acc_period on public.petdesk_passports(account_id, period);

create table if not exists public.petdesk_watch (
  account_id uuid not null references public.petdesk_accounts(id) on delete cascade,
  slug       text not null check (slug ~ '^[a-z0-9-]{2,40}$'),
  created_at timestamptz not null default now(),
  primary key (account_id, slug)
);

-- Gumroad pings / resource subscriptions (optional, phase 2). Deduplicated on
-- resource_name + sale_id/subscription_id as Gumroad recommends (https://gumroad.com/ping).
create table if not exists public.petdesk_gumroad_events (
  id            bigserial primary key,
  resource_name text not null,
  dedupe_key    text not null,
  payload       jsonb not null,
  received_at   timestamptz not null default now(),
  unique (resource_name, dedupe_key)
);

alter table public.petdesk_accounts       enable row level security;
alter table public.petdesk_passports      enable row level security;
alter table public.petdesk_watch          enable row level security;
alter table public.petdesk_gumroad_events enable row level security;
-- (deliberately no policies: deny-all for anon and authenticated)
revoke all on public.petdesk_accounts, public.petdesk_passports, public.petdesk_watch,
              public.petdesk_gumroad_events from anon, authenticated;

-- Max 5 watched airlines per account (also checked in the Edge Function).
create or replace function public.petdesk_watch_limit() returns trigger
language plpgsql security invoker set search_path = '' as $$
begin
  if (select count(*) from public.petdesk_watch where account_id = new.account_id) >= 5 then
    raise exception 'watch_limit' using errcode = 'P0001';
  end if;
  return new;
end $$;
drop trigger if exists petdesk_watch_limit on public.petdesk_watch;
create trigger petdesk_watch_limit before insert on public.petdesk_watch
  for each row execute function public.petdesk_watch_limit();
revoke all on function public.petdesk_watch_limit() from public, anon, authenticated;

-- Atomic 15-passports-per-month quota. Called only by the Edge Function (service role).
-- SECURITY INVOKER on purpose: no privileged function in the exposed public schema.
create or replace function public.petdesk_issue_passport(
  p_account uuid, p_route jsonb, p_langs text[], p_client_ref text, p_limit int default 15)
returns table(ref text, used int, quota int)
language plpgsql security invoker set search_path = public as $$
declare v_period text := to_char(now() at time zone 'utc', 'YYYY-MM');
        v_used int; v_ref text;
begin
  perform pg_advisory_xact_lock(hashtext(p_account::text));
  select count(*) into v_used from petdesk_passports
   where account_id = p_account and period = v_period;
  if v_used >= p_limit then
    raise exception 'quota_reached' using errcode = 'P0001';
  end if;
  v_ref := 'PD-' || replace(v_period,'-','') || '-' ||
           upper(substr(replace(p_account::text,'-',''),1,4)) || '-' || lpad((v_used+1)::text, 2, '0');
  insert into petdesk_passports(account_id, period, ref, route, langs, client_ref)
  values (p_account, v_period, v_ref, p_route, p_langs, nullif(p_client_ref,''));
  return query select v_ref, v_used + 1, p_limit;
end $$;
revoke all on function public.petdesk_issue_passport(uuid,jsonb,text[],text,int) from public, anon, authenticated;

-- Only the Edge Function (service_role) may use these objects. Explicit, so it does not depend on default privileges.
grant usage on schema public to service_role;
grant select, insert, update, delete on public.petdesk_accounts, public.petdesk_passports, public.petdesk_watch, public.petdesk_gumroad_events to service_role;
grant execute on function public.petdesk_issue_passport(uuid,jsonb,text[],text,int) to service_role;
grant execute on function public.petdesk_watch_limit() to service_role;
grant usage, select on sequence public.petdesk_passports_id_seq, public.petdesk_gumroad_events_id_seq to service_role;
