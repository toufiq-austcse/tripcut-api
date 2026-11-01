# Per-user and per-trip limits (TDD-002 §3). Served to clients by GET /v1/me.
MAX_OPEN_TRIPS = 3
MIN_CLIPS_PER_TRIP = 10
MAX_CLIPS_PER_TRIP = 100
MAX_TRIP_BYTES = 3 * 1024 * 1024 * 1024
ALLOWED_CONTENT_TYPE_PREFIX = "video/"
ACTIVE_TRIP_STATUSES = ("open", "processing")
