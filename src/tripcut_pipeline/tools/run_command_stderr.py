import subprocess

from tripcut_pipeline.errors.command_error import CommandError


def run_command_stderr(args: list[str]) -> str:
    """Run a command, return its stderr (ffmpeg filters such as loudnorm print there), raise CommandError on a non-zero exit."""
    completed = subprocess.run(args, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise CommandError(args, completed.returncode, completed.stderr)
    return completed.stderr
