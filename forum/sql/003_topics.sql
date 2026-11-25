-- Phase 1: topic column for the five forum sections.
-- Applied on uouccgyeujtmbeeneuwq as migration forum_phase1_posts_topic (20261125015223).
-- Adds a topic column to public.posts (the five rosace-aligned sections).
-- Existing RLS policies on posts already cover the new column (no new POLICY).
-- forum.js sends `topic` on insert and filters by topic.

alter table public.posts
  add column if not exists topic text;

alter table public.posts
  drop constraint if exists posts_topic_check;

alter table public.posts
  add constraint posts_topic_check
  check (topic is null or topic in (
    'flights',
    'road_trip_camping',
    'adoption',
    'health_seniors',
    'life_with_pet'
  ));

create index if not exists posts_topic_status_created
  on public.posts (topic, status, created_at desc);

-- Let members include topic on insert (column-level, same pattern as transport).
grant insert (topic) on public.posts to authenticated;

comment on column public.posts.topic is
  'Forum section: flights | road_trip_camping | adoption | health_seniors | life_with_pet';
