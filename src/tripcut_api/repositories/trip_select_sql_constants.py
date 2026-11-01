# Trip columns plus clip totals, shared by every trip read.
TRIP_SELECT_SQL = """
select t.id, t.title, t.status::text as status, t.notify_email, t.submitted_at, t.created_at, t.updated_at,
       c.clip_count, c.total_bytes, c.uploaded_clip_count
from public.trips t
cross join lateral (
    select count(*)::int as clip_count,
           coalesce(sum(size_bytes), 0)::bigint as total_bytes,
           (count(*) filter (where status = 'uploaded'))::int as uploaded_clip_count
    from public.clips
    where trip_id = t.id
) c
"""
