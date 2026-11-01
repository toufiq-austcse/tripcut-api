import boto3
from botocore.client import BaseClient
from botocore.config import Config

from tripcut_api.config.settings import Settings


def create_r2_client(settings: Settings) -> BaseClient:
    endpoint_url = f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
    config = Config(
        signature_version="s3v4",
        # SAN-49 fix: R2 rejects the newer default checksum headers on presigned part PUTs.
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required",
        retries={"max_attempts": 3, "mode": "standard"},
    )
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
        config=config,
    )
