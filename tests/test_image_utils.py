import base64
from image_utils import encode_image_to_base64, image_to_data_uri


def test_encode_image_to_base64(tmp_path):
    img_file = tmp_path / "test.png"
    img_bytes = b"fake_png_data"
    img_file.write_bytes(img_bytes)

    encoded = encode_image_to_base64(str(img_file))
    assert encoded == base64.b64encode(img_bytes).decode("utf-8")


def test_image_to_data_uri(tmp_path):
    img_file = tmp_path / "test.jpg"
    img_bytes = b"jpeg_data"
    img_file.write_bytes(img_bytes)

    data_uri = image_to_data_uri(str(img_file))
    expected_b64 = base64.b64encode(img_bytes).decode("utf-8")
    assert data_uri == f"data:image/jpeg;base64,{expected_b64}"
