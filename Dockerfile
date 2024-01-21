FROM python:3.11.7-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY notes_project /app/notes_project
WORKDIR /app/notes_project

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
