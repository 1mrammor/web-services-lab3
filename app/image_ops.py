import base64
import io

import numpy as np
from matplotlib.figure import Figure
from PIL import Image


def load_image(data):
    return np.array(Image.open(io.BytesIO(data)).convert("RGB"))


def swap_halves(img, direction):
    result = img.copy()
    if direction == "lr":
        w = img.shape[1]
        half = w // 2
        result[:, :half] = img[:, w - half:]
        result[:, w - half:] = img[:, :half]
    else:
        h = img.shape[0]
        half = h // 2
        result[:half] = img[h - half:]
        result[h - half:] = img[:half]
    return result


def color_histogram_png(img):
    fig = Figure(figsize=(6, 3.5))
    ax = fig.subplots()
    for i, color in enumerate(("red", "green", "blue")):
        counts = np.bincount(img[:, :, i].ravel(), minlength=256)
        ax.plot(counts, color=color, label=color)
    ax.set_xlabel("Значение канала")
    ax.set_ylabel("Количество пикселей")
    ax.set_title("Распределение цветов исходной картинки")
    ax.legend()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    return buf.getvalue()


def png_to_data_uri(png_bytes):
    return "data:image/png;base64," + base64.b64encode(png_bytes).decode()


def array_to_data_uri(arr):
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return png_to_data_uri(buf.getvalue())
