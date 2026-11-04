from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.captcha import site_key, verify_captcha
from app.image_ops import (array_to_data_uri, color_histogram_png, load_image,
                           png_to_data_uri, swap_halves)

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def show_form(request, error=None, status_code=200):
    context = {"site_key": site_key(), "error": error}
    return templates.TemplateResponse(request, "index.html", context, status_code=status_code)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return show_form(request)


@app.post("/process", response_class=HTMLResponse)
def process(
    request: Request,
    direction: Literal["lr", "tb"] = Form(),
    image: UploadFile = File(),
    captcha: str = Form("", alias="g-recaptcha-response"),
):
    if not verify_captcha(captcha):
        return show_form(request, "Капча не пройдена", 400)

    try:
        original = load_image(image.file.read())
    except OSError:
        return show_form(request, "Файл не является изображением", 400)

    context = {
        "original": array_to_data_uri(original),
        "result": array_to_data_uri(swap_halves(original, direction)),
        "histogram": png_to_data_uri(color_histogram_png(original)),
    }
    return templates.TemplateResponse(request, "result.html", context)
