import os

from tripcut_pipeline.errors.bad_input_error import BadInputError


def resolve_volume(flag_value: float | None, flag_name: str, env_name: str, default: float) -> float:
    """Volume from the flag, else the env var, else the default; must be between 0 and 1."""
    volume = default
    if flag_value is not None:
        volume = flag_value
    else:
        env_value = os.environ.get(env_name)
        if env_value is not None and env_value != "":
            try:
                volume = float(env_value)
            except ValueError as error:
                raise BadInputError(f"{env_name} must be a number, got {env_value!r}") from error
    if volume < 0.0 or volume > 1.0:
        raise BadInputError(f"{flag_name} must be between 0 and 1, got {volume}")
    return volume
