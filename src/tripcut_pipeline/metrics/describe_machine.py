import os
import platform
import subprocess


def describe_machine() -> str:
    """CPU model and core count, e.g. 'Apple M3 Pro, 12 cores (macOS-15...-arm64)'."""
    cpu = platform.processor()
    if platform.system() == "Darwin":
        completed = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, check=False
        )
        if completed.returncode == 0:
            cpu = completed.stdout.strip()
    cores = os.cpu_count()
    return f"{cpu}, {cores} cores ({platform.platform()})"
