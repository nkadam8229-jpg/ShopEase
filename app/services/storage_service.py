import os

from app.services.storage import LocalStorage, S3Storage


class StorageService:
    _s3_client = None  # Class-level cache for S3 client

    def __init__(self):
        storage_type = os.getenv("STORAGE_TYPE", "local").lower()

        if storage_type == "local":
            self.storage = LocalStorage()

        elif storage_type == "s3":
            if StorageService._s3_client is None:
                StorageService._s3_client = S3Storage()
            self.storage = StorageService._s3_client

        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

    def save(self, file_stream, filename, folder=""):
        return self.storage.save(
            file_stream,
            filename,
            folder
        )

    def delete(self, key):
        return self.storage.delete(key)

    def exists(self, key):
        return self.storage.exists(key)

    def get_path(self, key):
        return self.storage.get_path(key)

    def get_file(self, key):
        return self.storage.get_file(key)

    def get_object(self, key):
        if hasattr(self.storage, "get_object"):
            return self.storage.get_object(key)

        raise NotImplementedError(
            "get_object() is only supported for S3 storage"
        )