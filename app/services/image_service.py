import io
import uuid

from PIL import Image, UnidentifiedImageError


ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}


MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_image(file):

    if not file or not file.filename:
        raise ValueError("No image selected.")

    extension = (
        file.filename
        .rsplit(".", 1)[-1]
        .lower()
    )

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Invalid image format. "
            "Allowed formats: JPG, JPEG, PNG and WebP."
        )

    file.seek(0)

    data = file.read()

    if len(data) > MAX_FILE_SIZE:
        raise ValueError(
            "Image size must not exceed 5 MB."
        )

    file.seek(0)

    try:
        image = Image.open(file)

        image.verify()

    except UnidentifiedImageError:
        raise ValueError(
            "The uploaded file is not a valid image."
        )

    finally:
        file.seek(0)

    return True


def process_image(file):

    validate_image(file)

    file.seek(0)

    image = Image.open(file)

    if image.mode in ("RGBA", "LA"):
        background = Image.new(
            "RGB",
            image.size,
            "white"
        )

        background.paste(
            image,
            mask=image.getchannel("A")
        )

        image = background

    else:
        image = image.convert("RGB")

    image.thumbnail(
        (1600, 1600),
        Image.Resampling.LANCZOS
    )

    output = io.BytesIO()

    image.save(
        output,
        format="WEBP",
        quality=85,
        method=6
    )

    output.seek(0)

    filename = (
        f"{uuid.uuid4().hex}.webp"
    )

    return output, filename