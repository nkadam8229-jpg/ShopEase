from pathlib import Path
from io import BytesIO
import os

import boto3
from botocore.exceptions import ClientError


class LocalStorage:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parents[2] / "uploads"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file_stream: BytesIO, filename: str, folder: str = "") -> str:
        folder_path = self.base_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = folder_path / filename

        file_stream.seek(0)
        with open(file_path, "wb") as f:
            f.write(file_stream.read())

        return f"{folder}/{filename}" if folder else filename

    def delete(self, key: str) -> bool:
        file_path = self.base_dir / key

        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except OSError:
            return False

    def exists(self, key: str) -> bool:
        return (self.base_dir / key).exists()

    def get_path(self, key: str) -> Path:
        return self.base_dir / key

    def get_file(self, key: str):
        return open(
            self.base_dir / key,
            "rb"
        )

class S3Storage:
    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET")
        self.region = os.getenv("AWS_REGION", "ap-south-1")

        if not self.bucket:
            raise RuntimeError("S3_BUCKET is not configured")

        self.client = boto3.client(
            "s3",
            region_name=self.region
        )

    def save(self, file_stream: BytesIO, filename: str, folder: str = "") -> str:
        key = f"{folder}/{filename}" if folder else filename

        file_stream.seek(0)

        self.client.upload_fileobj(
            file_stream,
            self.bucket,
            key,
            ExtraArgs={
                "ContentType": "image/webp"
            }
        )

        return key

    def delete(self, key: str) -> bool:
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            return True
        except ClientError:
            return False

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=key
            )
            return True
        except ClientError:
            return False

    def get_path(self, key: str):
        """
        S3 objects do not have a local filesystem path.

        This method intentionally returns None.
        S3 retrieval will be handled separately by the routes.
        """
        return None

    def get_file(self, key: str):
        response = self.client.get_object(
            Bucket=self.bucket,
            Key=key
        )

        file_stream = BytesIO(
            response["Body"].read()
        )

        file_stream.seek(0)

        return file_stream

class StorageFactory:
    @staticmethod
    def create():
        storage_type = os.getenv("STORAGE_TYPE", "local").lower()

        if storage_type == "local":
            return LocalStorage()

        if storage_type == "s3":
            return S3Storage()

        raise ValueError(f"Unsupported storage type: {storage_type}")
