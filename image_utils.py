import base64
import mimetypes


def encode_image_to_base64(image_path: str) -> str:
    """Reads a local image file and returns its base64 encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def image_to_data_uri(image_path: str) -> str:
    """Reads a local image file and returns a data URI (e.g. data:image/png;base64,...)."""
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"
    b64_str = encode_image_to_base64(image_path)
    return f"data:{mime_type};base64,{b64_str}"
