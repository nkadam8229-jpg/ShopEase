import uuid

from pathlib import Path

from flask import current_app


class LocalStorage:

    def __init__(self):

        self.base_path = (
            Path(current_app.root_path).parent
            / "uploads"
        )

    def save(
        self,
        file,
        folder,
        filename=None
    ):

        folder_path = self.base_path / folder

        folder_path.mkdir(
            parents=True,
            exist_ok=True
        )

        if filename is None:

            filename = (
                f"{uuid.uuid4().hex}.webp"
            )

        file_path = folder_path / filename

        # Support processed file streams such as BytesIO
        if hasattr(file, "read"):

            file.seek(0)

            with open(file_path, "wb") as output:

                output.write(
                    file.read()
                )

        # Support Flask FileStorage objects
        elif hasattr(file, "save"):

            file.save(file_path)

        else:

            raise ValueError(
                "Unsupported file object."
            )

        return f"{folder}/{filename}"

    def delete(self, key):

        if not key:
            return False

        file_path = self.base_path / key

        if file_path.exists():

            file_path.unlink()

            return True

        return False

    def exists(self, key):

        if not key:
            return False

        file_path = self.base_path / key

        return file_path.exists()

    def get_path(self, key):

        if not key:
            return None

        return self.base_path / key