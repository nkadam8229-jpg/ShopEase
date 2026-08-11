from flask import current_app

from app.services.storage import LocalStorage


class StorageService:

    def __init__(self):

        storage_type = current_app.config.get(
            "STORAGE_TYPE",
            "local"
        )

        if storage_type == "local":

            self.storage = LocalStorage()

        else:

            raise ValueError(
                f"Unsupported storage type: {storage_type}"
            )

    def save(
        self,
        file,
        folder,
        filename=None
    ):

        return self.storage.save(
            file,
            folder,
            filename
        )

    def delete(self, key):

        return self.storage.delete(key)

    def exists(self, key):

        return self.storage.exists(key)

    def get_path(self, key):

        return self.storage.get_path(key)