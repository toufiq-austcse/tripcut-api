class CommandError(Exception):
    """An external command (ffmpeg / ffprobe) exited with a non-zero code."""

    def __init__(self, args: list[str], returncode: int, stderr: str) -> None:
        tail = stderr[-2000:]
        super().__init__(f"{args[0]} exited with {returncode}: {tail}")
        self.args_list = args
        self.returncode = returncode
        self.stderr = stderr
