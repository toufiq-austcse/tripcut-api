# Clip columns plus the parent trip's status, shared by every clip read.
CLIP_SELECT_SQL = """
select c.id, c.trip_id, c.user_id, c.filename, c.content_type, c.size_bytes, c.fingerprint,
       c.r2_key, c.r2_upload_id, c.part_size_bytes, c.part_count, c.status::text as status,
       c.uploaded_at, c.created_at, t.status::text as trip_status
from public.clips c
join public.trips t on t.id = c.trip_id
"""
