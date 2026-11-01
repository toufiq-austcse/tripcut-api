from tripcut_api.schemas.clips.clip_response import ClipResponse
from tripcut_api.schemas.jobs.job_response import JobResponse
from tripcut_api.schemas.trips.trip_response import TripResponse


class TripDetailResponse(TripResponse):
    clips: list[ClipResponse]
    latest_job: JobResponse | None
