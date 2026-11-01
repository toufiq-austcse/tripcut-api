from fastapi import APIRouter, FastAPI

from tripcut_api.routes.clips.abort_clip import abort_clip
from tripcut_api.routes.clips.complete_clip import complete_clip
from tripcut_api.routes.clips.create_clip import create_clip
from tripcut_api.routes.clips.list_clip_parts import list_clip_parts
from tripcut_api.routes.clips.sign_clip_parts import sign_clip_parts
from tripcut_api.routes.me.get_me import get_me
from tripcut_api.routes.trips.create_trip import create_trip
from tripcut_api.routes.trips.delete_trip import delete_trip
from tripcut_api.routes.trips.get_trip import get_trip
from tripcut_api.routes.trips.list_trips import list_trips
from tripcut_api.routes.trips.submit_trip import submit_trip
from tripcut_api.routes.trips.update_trip import update_trip
from tripcut_api.schemas.clips.clip_response import ClipResponse


def register_routes(app: FastAPI) -> None:
    """The 12 /v1 endpoints. See docs/api-contract.md."""
    router = APIRouter(prefix="/v1")
    router.add_api_route("/me", get_me, methods=["GET"], tags=["me"])

    router.add_api_route("/trips", create_trip, methods=["POST"], status_code=201, tags=["trips"])
    router.add_api_route("/trips", list_trips, methods=["GET"], tags=["trips"])
    router.add_api_route("/trips/{trip_id}", get_trip, methods=["GET"], tags=["trips"])
    router.add_api_route("/trips/{trip_id}", update_trip, methods=["PATCH"], tags=["trips"])
    router.add_api_route("/trips/{trip_id}", delete_trip, methods=["DELETE"], status_code=204, tags=["trips"])
    router.add_api_route("/trips/{trip_id}/submit", submit_trip, methods=["POST"], status_code=202, tags=["trips"])

    router.add_api_route(
        "/trips/{trip_id}/clips",
        create_clip,
        methods=["POST"],
        status_code=201,
        responses={200: {"model": ClipResponse, "description": "Clip already registered (resume)"}},
        tags=["clips"],
    )
    router.add_api_route("/clips/{clip_id}/parts:sign", sign_clip_parts, methods=["POST"], tags=["clips"])
    router.add_api_route("/clips/{clip_id}/parts", list_clip_parts, methods=["GET"], tags=["clips"])
    router.add_api_route("/clips/{clip_id}/complete", complete_clip, methods=["POST"], tags=["clips"])
    router.add_api_route("/clips/{clip_id}", abort_clip, methods=["DELETE"], status_code=204, tags=["clips"])

    app.include_router(router)
