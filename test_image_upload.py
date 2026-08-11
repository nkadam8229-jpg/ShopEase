from io import BytesIO

from flask import Flask
from werkzeug.datastructures import FileStorage
from PIL import Image

from app import create_app
from app.services.upload_service import upload_image


app = create_app()


with app.app_context():

    image = Image.new(
        "RGB",
        (800, 600),
        "white"
    )

    image_data = BytesIO()

    image.save(
        image_data,
        format="JPEG"
    )

    image_data.seek(0)

    uploaded_file = FileStorage(
        stream=image_data,
        filename="test.jpg",
        content_type="image/jpeg"
    )

    image_key = upload_image(
        uploaded_file,
        "categories"
    )

    print("Image uploaded successfully!")
    print("Image key:", image_key)