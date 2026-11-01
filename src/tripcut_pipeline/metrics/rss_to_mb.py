import sys


def rss_to_mb(max_rss: int) -> float:
    """ru_maxrss is bytes on macOS and kilobytes on Linux."""
    if sys.platform == "darwin":
        return max_rss / (1024 * 1024)
    return max_rss / 1024
