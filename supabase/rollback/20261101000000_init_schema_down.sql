-- Rollback for 20261101000000_init_schema.sql. Deletes every TripCut row. Run by hand:
--   psql "$SUPABASE_DB_URL" -f supabase/rollback/20261101000000_init_schema_down.sql
-- then remove the row from supabase_migrations.schema_migrations:
--   delete from supabase_migrations.schema_migrations where version = '20261101000000';
begin;

drop trigger if exists on_auth_user_created on auth.users;

drop table if exists public.reels;
drop table if exists public.edit_lists;
drop table if exists public.jobs;
drop table if exists public.clips;
drop table if exists public.trips;
drop table if exists public.users;

drop function if exists public.handle_new_auth_user();
drop function if exists public.set_updated_at();

drop type if exists public.reel_status;
drop type if exists public.edit_list_source;
drop type if exists public.reel_style;
drop type if exists public.job_step;
drop type if exists public.job_status;
drop type if exists public.job_kind;
drop type if exists public.clip_status;
drop type if exists public.trip_status;

commit;
