import io

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app import main
from app.image_ops import color_histogram_png, swap_halves

# "виртуальный браузер": вызывает приложение напрямую, сервер запускать не нужно
client = TestClient(main.app)


# тестовая картинка: height строк, width столбцов, столбец x залит числом x * 10
# для width=4 значения по столбцам: [0, 10, 20, 30]
def make_image(width, height=2):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    for x in range(width):
        img[:, x] = x * 10
    return img


# превращает массив в байты PNG, как будто это загруженный файл
def png_bytes(arr):
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


# отправляет форму на /process эндпоинт, как это делает браузер
# direction - "lr" или "tb", data - байты файла,
# captcha_ok - подменяет проверку капчи на заглушку (True - прошла, False - не прошла)
def post(direction, data, monkeypatch, captcha_ok=True):
    monkeypatch.setattr(main, "verify_captcha", lambda token: captcha_ok)
    return client.post(
        "/process",
        data={"direction": direction, "g-recaptcha-response": "token"},
        files={"image": ("test.png", data, "image/png")},
    )


# левая и правая половины меняются местами: [0, 10, 20, 30] -> [20, 30, 0, 10]
def test_swap_left_right():
    result = swap_halves(make_image(4), "lr")
    assert result[0, :, 0].tolist() == [20, 30, 0, 10]


# нечётная ширина: средний столбец (20) остаётся на месте
def test_swap_left_right_odd():
    result = swap_halves(make_image(5), "lr")
    assert result[0, :, 0].tolist() == [30, 40, 20, 0, 10]


# верхняя и нижняя половины: строки 0, 1, 2, 3 -> 2, 3, 0, 1
def test_swap_top_bottom():
    img = np.zeros((4, 3, 3), dtype=np.uint8)
    for y in range(4):
        img[y] = y
    result = swap_halves(img, "tb")
    assert result[:, 0, 0].tolist() == [2, 3, 0, 1]


# график возвращается как PNG (любой PNG начинается с байтов \x89PNG)
def test_histogram_is_png():
    assert color_histogram_png(make_image(4)).startswith(b"\x89PNG")


# GET / : главная страница открывается (200) и на ней есть капча
def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "g-recaptcha" in response.text


# POST /process с картинкой и пройденной капчей: 200 и в ответе 3 картинки
# (исходная, результат, график)
def test_process(monkeypatch):
    response = post("lr", png_bytes(make_image(4)), monkeypatch)
    assert response.status_code == 200
    assert response.text.count("data:image/png;base64") == 3


# после обработки имя и размер файла попадают в список и в таблицу на странице
def test_processed_files_summary(monkeypatch):
    main.processed_files.clear()
    data = png_bytes(make_image(4))
    response = post("lr", data, monkeypatch)
    assert main.processed_files == [{"name": "test.png", "size": len(data)}]
    assert "Обработанные файлы" in response.text
    assert "test.png" in response.text


# файл, который не удалось обработать, в список не попадает
def test_failed_file_not_in_summary(monkeypatch):
    main.processed_files.clear()
    post("lr", b"not an image", monkeypatch)
    assert main.processed_files == []


# капча не пройдена (captcha_ok=False): ответ 400
def test_captcha_failed(monkeypatch):
    response = post("lr", png_bytes(make_image(4)), monkeypatch, captcha_ok=False)
    assert response.status_code == 400


# вместо картинки прислали текст: ответ 400, сервер не падает
def test_not_an_image(monkeypatch):
    response = post("lr", b"not an image", monkeypatch)
    assert response.status_code == 400
