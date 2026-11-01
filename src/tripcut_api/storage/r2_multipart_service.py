from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from tripcut_api.errors import error_codes_constants as codes
from tripcut_api.errors.api_error import ApiError


class R2MultipartService:
    """Every R2 control call the API makes. The client only PUTs part bytes to presigned URLs."""

    def __init__(self, client: BaseClient, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def create(self, key: str, content_type: str) -> str:
        try:
            result = self._client.create_multipart_upload(Bucket=self._bucket, Key=key, ContentType=content_type)
        except (ClientError, BotoCoreError) as error:
            raise self._storage_error("create upload", error) from error
        return result["UploadId"]

    def sign_part(self, key: str, upload_id: str, part_number: int, expires_in: int) -> str:
        try:
            return self._client.generate_presigned_url(
                "upload_part",
                Params={"Bucket": self._bucket, "Key": key, "UploadId": upload_id, "PartNumber": part_number},
                ExpiresIn=expires_in,
                HttpMethod="PUT",
            )
        except (ClientError, BotoCoreError) as error:
            raise self._storage_error("sign part", error) from error

    def list_parts(self, key: str, upload_id: str) -> list[dict]:
        """All uploaded parts as {part_number, size_bytes, etag}, across every ListParts page."""
        parts = []
        marker = 0
        while True:
            try:
                page = self._client.list_parts(
                    Bucket=self._bucket, Key=key, UploadId=upload_id, PartNumberMarker=marker, MaxParts=1000
                )
            except (ClientError, BotoCoreError) as error:
                raise self._storage_error("list parts", error) from error
            page_parts = []
            if "Parts" in page:
                page_parts = page["Parts"]
            for part in page_parts:
                parts.append({"part_number": part["PartNumber"], "size_bytes": part["Size"], "etag": part["ETag"]})
            is_truncated = False
            if "IsTruncated" in page:
                is_truncated = page["IsTruncated"]
            if not is_truncated:
                break
            marker = page["NextPartNumberMarker"]
        parts.sort(key=lambda item: item["part_number"])
        return parts

    def complete(self, key: str, upload_id: str, parts: list[dict]) -> None:
        upload_parts = [{"PartNumber": part["part_number"], "ETag": part["etag"]} for part in parts]
        try:
            self._client.complete_multipart_upload(
                Bucket=self._bucket, Key=key, UploadId=upload_id, MultipartUpload={"Parts": upload_parts}
            )
        except (ClientError, BotoCoreError) as error:
            raise self._storage_error("complete upload", error) from error

    def abort(self, key: str, upload_id: str) -> None:
        """Abort an upload. An upload that is already gone counts as aborted."""
        try:
            self._client.abort_multipart_upload(Bucket=self._bucket, Key=key, UploadId=upload_id)
        except ClientError as error:
            if self._error_code(error) == "NoSuchUpload":
                return
            raise self._storage_error("abort upload", error) from error
        except BotoCoreError as error:
            raise self._storage_error("abort upload", error) from error

    def delete_object(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
        except (ClientError, BotoCoreError) as error:
            raise self._storage_error("delete object", error) from error

    def head_size(self, key: str) -> int | None:
        """Size of a finished object, or None when the object does not exist."""
        try:
            result = self._client.head_object(Bucket=self._bucket, Key=key)
        except ClientError as error:
            if self._error_code(error) in ("404", "NoSuchKey", "NotFound"):
                return None
            raise self._storage_error("head object", error) from error
        except BotoCoreError as error:
            raise self._storage_error("head object", error) from error
        return result["ContentLength"]

    def _error_code(self, error: ClientError) -> str:
        if "Error" in error.response:
            details = error.response["Error"]
            if "Code" in details:
                return str(details["Code"])
        return ""

    def _storage_error(self, action: str, error: Exception) -> ApiError:
        return ApiError(502, codes.STORAGE_ERROR, f"Storage failed to {action}: {error}")
