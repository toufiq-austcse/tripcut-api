import logging
import shutil

from tripcut_pipeline.config.exit_codes_constants import EXIT_BAD_INPUT, EXIT_OK, EXIT_RENDER_FAILED
from tripcut_pipeline.direct.direct_trip import direct_trip
from tripcut_pipeline.direct.director_request import DirectorRequest
from tripcut_pipeline.errors.bad_input_error import BadInputError
from tripcut_pipeline.errors.render_error import RenderError
from tripcut_pipeline.ingest.ingest_trip import ingest_trip
from tripcut_pipeline.metrics.describe_machine import describe_machine
from tripcut_pipeline.metrics.stage_timer_service import StageTimerService
from tripcut_pipeline.music.load_beat_grid import load_beat_grid
from tripcut_pipeline.music.resolve_music_track import resolve_music_track
from tripcut_pipeline.pipeline_options import PipelineOptions
from tripcut_pipeline.render.render_trip import render_trip
from tripcut_pipeline.score.score_trip import score_trip
from tripcut_pipeline.tools.write_json import write_json


def run_pipeline(options: PipelineOptions) -> int:
    """ingest -> score -> direct -> music -> render, each wrapped by StageTimerService. Returns the exit code."""
    log = logging.getLogger(__name__)
    work_dir = options.out_dir / "work"
    work_dir.mkdir(parents=True, exist_ok=True)
    timer = StageTimerService()
    metrics: dict = {"trip": options.trip_dir.name, "machine": describe_machine(), "director": options.director}
    exit_code = EXIT_OK
    try:
        with timer.stage("ingest") as stage:
            proxies = ingest_trip(options.trip_dir, work_dir / "proxies")
            clips = {proxy.meta.clip_id: proxy.meta for proxy in proxies}
            largest = max(clips.values(), key=lambda clip: clip.width * clip.height)
            metrics["clips"] = len(clips)
            metrics["footage_s"] = round(sum(clip.duration_s for clip in clips.values()), 3)
            metrics["max_res"] = f"{largest.width}x{largest.height}"
            metrics["codec"] = sorted({clip.codec for clip in clips.values()})
            stage.extra["clips"] = len(clips)

        with timer.stage("score") as stage:
            scored = score_trip(proxies)
            if len(scored.kept) == 0:
                raise BadInputError("no usable segments (every clip is shorter than 1 s or has no frames)")
            stage.extra["segments"] = scored.segment_count
            stage.extra["kept"] = len(scored.kept)

        with timer.stage("music") as stage:
            track = resolve_music_track(options.music)
            beat_grid = None
            music_id = None
            if track is not None:
                beat_grid = load_beat_grid(track)
                music_id = beat_grid.music_id
                stage.extra["music_id"] = music_id
                stage.extra["tempo_bpm"] = beat_grid.tempo_bpm

        with timer.stage("direct") as stage:
            request = DirectorRequest(
                trip_name=options.trip_dir.name,
                duration_s=options.duration_s,
                music_id=music_id,
                segments=scored.kept,
                clips=clips,
            )
            result = direct_trip(request, options.director, options.model)
            stage.extra["model"] = result.model
            stage.extra["tokens_in"] = result.tokens_in
            stage.extra["tokens_out"] = result.tokens_out
            stage.extra["attempts"] = result.attempts
            stage.extra["fallback"] = result.fallback
            if result.fallback_reason is not None:
                stage.extra["fallback_reason"] = result.fallback_reason[:500]
            for edit_list in result.edit_lists:
                write_json(options.out_dir / "edit_lists" / f"{edit_list['version']}.director.json", edit_list)

        with timer.stage("render") as stage:
            rendered = render_trip(
                result.edit_lists, clips, scored.face_tracks, beat_grid, work_dir, options.out_dir
            )
            for edit_list in rendered:
                write_json(options.out_dir / "edit_lists" / f"{edit_list['version']}.json", edit_list)
            stage.extra["reels"] = len(rendered)
    except BadInputError as error:
        log.error("bad input: %s", error)
        metrics["error"] = str(error)
        exit_code = EXIT_BAD_INPUT
    except RenderError as error:
        log.error("render failed: %s", error)
        metrics["error"] = str(error)[:2000]
        exit_code = EXIT_RENDER_FAILED
    finally:
        metrics["stages"] = timer.to_dict()
        write_json(options.out_dir / "metrics.json", metrics)

    if not options.keep_proxies and exit_code == EXIT_OK:
        shutil.rmtree(work_dir, ignore_errors=True)
    return exit_code
