-- SAN-51: TripCut initial schema (users, trips, clips, jobs, edit_lists, reels).
-- The API writes with the database owner connection; browsers may only read their own rows (RLS).
-- Rollback: supabase/rollback/20261101000000_init_schema_down.sql

-- ---------- enums ----------
create type public.trip_status as enum ('open', 'processing', 'ready', 'failed');
create type public.clip_status as enum ('uploading', 'uploaded');
create type public.job_kind as enum ('analyze', 'rerender');
create type public.job_status as enum ('queued', 'running', 'succeeded', 'failed');
create type public.job_step as enum ('ingest', 'score', 'direct', 'music', 'render', 'notify');
create type public.reel_style as enum ('cinematic', 'fast_cut', 'story');
create type public.edit_list_source as enum ('llm', 'fallback', 'user_edit');
create type public.reel_status as enum ('rendering', 'ready', 'failed');

-- ---------- shared trigger function ----------
create function public.set_updated_at() returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ---------- users (one row per auth.users row) ----------
create table public.users (
  id uuid primary key references auth.users (id) on delete cascade,
  email text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create function public.handle_new_auth_user() returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.users (id, email) values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_auth_user();

-- Users who signed up before this migration.
insert into public.users (id, email)
select id, email from auth.users
on conflict (id) do nothing;

-- ---------- trips ----------
create table public.trips (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users (id) on delete cascade,
  title text not null check (char_length(title) between 1 and 200),
  status public.trip_status not null default 'open',
  notify_email boolean not null default true,
  submitted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index trips_user_created_idx on public.trips (user_id, created_at desc, id desc);

-- ---------- clips ----------
create table public.clips (
  id uuid primary key default gen_random_uuid(),
  trip_id uuid not null references public.trips (id) on delete cascade,
  user_id uuid not null references public.users (id) on delete cascade,
  filename text not null,
  content_type text not null,
  size_bytes bigint not null check (size_bytes > 0),
  fingerprint text not null,
  r2_key text not null,
  r2_upload_id text,
  part_size_bytes integer not null check (part_size_bytes > 0),
  part_count integer not null check (part_count between 1 and 10000),
  status public.clip_status not null default 'uploading',
  uploaded_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint clips_trip_fingerprint_key unique (trip_id, fingerprint),
  constraint clips_r2_key_key unique (r2_key),
  constraint clips_upload_id_check check (status = 'uploaded' or r2_upload_id is not null)
);
-- Lookups by trip_id use the (trip_id, fingerprint) unique index.

-- ---------- jobs ----------
create table public.jobs (
  id uuid primary key default gen_random_uuid(),
  trip_id uuid not null references public.trips (id) on delete cascade,
  user_id uuid not null references public.users (id) on delete cascade,
  kind public.job_kind not null,
  status public.job_status not null default 'queued',
  step public.job_step,
  attempt integer not null default 0,
  error text,
  modal_call_id text,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index jobs_trip_created_idx on public.jobs (trip_id, created_at desc);
create index jobs_active_status_idx on public.jobs (status) where status in ('queued', 'running');

-- ---------- edit_lists (TDD-001 §8.4 body) ----------
create table public.edit_lists (
  id uuid primary key default gen_random_uuid(),
  trip_id uuid not null references public.trips (id) on delete cascade,
  user_id uuid not null references public.users (id) on delete cascade,
  job_id uuid references public.jobs (id) on delete set null,
  style public.reel_style not null,
  version integer not null check (version > 0),
  source public.edit_list_source not null,
  body jsonb not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint edit_lists_trip_style_version_key unique (trip_id, style, version)
);

-- ---------- reels ----------
create table public.reels (
  id uuid primary key default gen_random_uuid(),
  trip_id uuid not null references public.trips (id) on delete cascade,
  user_id uuid not null references public.users (id) on delete cascade,
  edit_list_id uuid not null references public.edit_lists (id) on delete cascade,
  style public.reel_style not null,
  status public.reel_status not null default 'rendering',
  track_id text,
  video_key text,
  poster_key text,
  duration_sec numeric,
  size_bytes bigint,
  expires_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index reels_trip_style_idx on public.reels (trip_id, style);

-- ---------- updated_at triggers ----------
create trigger users_set_updated_at before update on public.users
  for each row execute function public.set_updated_at();
create trigger trips_set_updated_at before update on public.trips
  for each row execute function public.set_updated_at();
create trigger clips_set_updated_at before update on public.clips
  for each row execute function public.set_updated_at();
create trigger jobs_set_updated_at before update on public.jobs
  for each row execute function public.set_updated_at();
create trigger edit_lists_set_updated_at before update on public.edit_lists
  for each row execute function public.set_updated_at();
create trigger reels_set_updated_at before update on public.reels
  for each row execute function public.set_updated_at();

-- ---------- row level security: read own rows only, no client writes ----------
alter table public.users enable row level security;
alter table public.trips enable row level security;
alter table public.clips enable row level security;
alter table public.jobs enable row level security;
alter table public.edit_lists enable row level security;
alter table public.reels enable row level security;

create policy users_select_own on public.users for select to authenticated using (id = (select auth.uid()));
create policy trips_select_own on public.trips for select to authenticated using (user_id = (select auth.uid()));
create policy clips_select_own on public.clips for select to authenticated using (user_id = (select auth.uid()));
create policy jobs_select_own on public.jobs for select to authenticated using (user_id = (select auth.uid()));
create policy edit_lists_select_own on public.edit_lists for select to authenticated using (user_id = (select auth.uid()));
create policy reels_select_own on public.reels for select to authenticated using (user_id = (select auth.uid()));
