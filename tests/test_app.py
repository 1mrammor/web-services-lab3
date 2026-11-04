import io

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app import main
from app.image_ops import color_histogram_png, swap_halves

client = TestClient(main.app)


def make_image(width, height=2):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    for x in range(width):
        img[:, x] = x * 10
    return img


def png_bytes(arr):
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


def post(direction, data, monkeypatch, captcha_ok=True):
    monkeypatch.setattr(main, "verify_captcha", lambda token: captcha_ok)
    return client.post(
        "/process",
        data={"direction": direction, "g-recaptcha-response": "token"},
        files={"image": ("test.png", data, "image/png")},
    )


def test_swap_left_right():
    result = swap_halves(make_image(4), "lr")
    assert result[0, :, 0].tolist() == [20, 30, 0, 10]


def test_swap_left_right_odd():
    result = swap_halves(make_image(5), "lr")
    assert result[0, :, 0].tolist() == [30, 40, 20, 0, 10]


def test_swap_top_bottom():
    img = np.zeros((4, 3, 3), dtype=np.uint8)
    for y in range(4):
        img[y] = y
    result = swap_halves(img, "tb")
    assert result[:, 0, 0].tolist() == [2, 3, 0, 1]


def test_histogram_is_png():
    assert color_histogram_png(make_image(4)).startswith(b"\x89PNG")


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "g-recaptcha" in response.text


def test_process(monkeypatch):
    response = post("lr", png_bytes(make_image(4)), monkeypatch)
    assert response.status_code == 200
    assert response.text.count("data:image/png;base64") == 3


def test_captcha_failed(monkeypatch):
    response = post("lr", png_bytes(make_image(4)), monkeypatch, captcha_ok=False)
    assert response.status_code == 400


def test_not_an_image(monkeypatch):
    response = post("lr", b"not an image", monkeypatch)
    assert response.status_code == 400
