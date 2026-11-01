import modal

from modal_app_constants import IMAGE_PIP_PACKAGES, LOCAL_MODULES, PYTHON_VERSION

# Container image: the API's pip packages plus the local tripcut_api package and these deploy modules.
API_IMAGE = (
    modal.Image.debian_slim(python_version=PYTHON_VERSION)
    .pip_install(*IMAGE_PIP_PACKAGES)
    .add_local_python_source(*LOCAL_MODULES)
)
