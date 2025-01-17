# Use an official Python runtime as a parent image
FROM python:3.11.7

WORKDIR /app


COPY requirements.txt ./


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


EXPOSE 8080


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]