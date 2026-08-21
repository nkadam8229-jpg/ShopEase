from app.services.image_service import process_image
from app.services.storage_service import StorageService


def upload_image(file, folder):

    processed_image, filename = process_image(file)

    storage = StorageService()

    image_key = storage.save(
        processed_image,
        filename,
        folder
    )

    return image_key
