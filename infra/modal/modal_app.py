import modal

from modal_app_constants import APP_NAME, SECRET_NAME
from modal_image import API_IMAGE

# The Modal App object. Modal needs it at module level, so it lives alone in this file.
APP = modal.App(APP_NAME, image=API_IMAGE, secrets=[modal.Secret.from_name(SECRET_NAME)])
