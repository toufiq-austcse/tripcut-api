import resource
import time
from collections.abc import Iterator
from contextlib import contextmanager

from tripcut_pipeline.metrics.rss_to_mb import rss_to_mb
from tripcut_pipeline.metrics.stage_metrics import StageMetrics


class StageTimerService:
    """Wraps each stage and records wall time, core-seconds (getrusage SELF + CHILDREN) and peak RSS.

    Peak RSS is the high-water mark so far (process or largest ffmpeg child), not a per-stage peak.
    """

    def __init__(self) -> None:
        self._stages: dict[str, StageMetrics] = {}

    @contextmanager
    def stage(self, name: str) -> Iterator[StageMetrics]:
        metrics = StageMetrics()
        self._stages[name] = metrics
        wall_start = time.perf_counter()
        self_start = resource.getrusage(resource.RUSAGE_SELF)
        children_start = resource.getrusage(resource.RUSAGE_CHILDREN)
        try:
            yield metrics
        finally:
            self_end = resource.getrusage(resource.RUSAGE_SELF)
            children_end = resource.getrusage(resource.RUSAGE_CHILDREN)
            metrics.wall_s = time.perf_counter() - wall_start
            metrics.core_s = (
                (self_end.ru_utime - self_start.ru_utime)
                + (self_end.ru_stime - self_start.ru_stime)
                + (children_end.ru_utime - children_start.ru_utime)
                + (children_end.ru_stime - children_start.ru_stime)
            )
            metrics.peak_rss_mb = rss_to_mb(max(self_end.ru_maxrss, children_end.ru_maxrss))

    def to_dict(self) -> dict[str, dict]:
        return {name: metrics.to_dict() for name, metrics in self._stages.items()}
