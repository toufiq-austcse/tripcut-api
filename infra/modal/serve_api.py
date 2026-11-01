"""Deploy: from tripcut-api/, run `pip install -e .` then `modal deploy infra/modal/serve_api.py`."""
import modal

from modal_app import APP
from modal_app_constants import APP_LABEL, MAX_CONCURRENT_INPUTS


@APP.function(min_containers=0, timeout=120)
@modal.concurrent(max_inputs=MAX_CONCURRENT_INPUTS)
@modal.asgi_app(label=APP_LABEL)
def serve_api():
    from tripcut_api.app.create_app import create_app

    return create_app()
