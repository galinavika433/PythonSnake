#база докер файла
FROM python:3.11-slim

#рабочая директория
WORKDIR / app

#установка зависимостей
RUN pip install property

COPY pyproject.