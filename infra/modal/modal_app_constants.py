# Names shared by the Modal deploy files.
APP_NAME = "tripcut-api"
SECRET_NAME = "tripcut-api"
APP_LABEL = "tripcut-api"
PYTHON_VERSION = "3.12"
MAX_CONCURRENT_INPUTS = 50
LOCAL_MODULES = ("tripcut_api", "modal_app", "modal_image", "modal_app_constants")
# Keep in step with [project].dependencies in pyproject.toml (modal itself is already in the image).
IMAGE_PIP_PACKAGES = (
    "fastapi>=0.115,<1.0",
    "pydantic>=2.9,<3.0",
    "pydantic-settings>=2.6,<3.0",
    "boto3>=1.36",
    "psycopg[binary,pool]>=3.2,<4.0",
    "pyjwt[crypto]>=2.10,<3.0",
)
