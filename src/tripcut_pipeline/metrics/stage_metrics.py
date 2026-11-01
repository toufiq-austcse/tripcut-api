from dataclasses import dataclass, field


@dataclass
class StageMetrics:
    """Cost of one stage. core_s = user+sys CPU seconds of this process and its ffmpeg children."""

    wall_s: float = 0.0
    core_s: float = 0.0
    peak_rss_mb: float = 0.0
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = {
            "wall_s": round(self.wall_s, 3),
            "core_s": round(self.core_s, 3),
            "peak_rss_mb": round(self.peak_rss_mb, 1),
        }
        data.update(self.extra)
        return data
