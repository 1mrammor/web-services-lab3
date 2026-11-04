# Лабораторная работа 3, вариант 8

Веб-приложение на FastAPI: меняет местами левую и правую (или верхнюю и нижнюю)
части картинки и рисует график распределения цветов исходной картинки.

## Запуск

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Тесты: `python -m pytest`

Ключи капчи задаются переменными окружения `RECAPTCHA_SITE_KEY` и `RECAPTCHA_SECRET_KEY`.
