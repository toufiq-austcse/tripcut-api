"""Clip order in the reels (plan rev 6, section 9).

time   = capture time of each clip (UTC), so every reel follows the day.
upload = the order the user gave the files (CLI: natural file-name order).
mood   = the director orders cinematic/fast by mood; story keeps filming order.
"""

from datetime import datetime, timezone

ORDER_TIME = "time"
ORDER_UPLOAD = "upload"
ORDER_MOOD = "mood"
ORDER_MODES = (ORDER_TIME, ORDER_UPLOAD, ORDER_MOOD)
DEFAULT_ORDER = ORDER_TIME
NO_TIME_SORT_VALUE = datetime.min.replace(tzinfo=timezone.utc)
