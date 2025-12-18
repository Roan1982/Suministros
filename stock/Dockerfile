# Dockerfile para Django + Postgres
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --upgrade pip && \
	apt-get update -y && apt-get install -y --no-install-recommends netcat-openbsd && rm -rf /var/lib/apt/lists/* && \
	pip install -r requirements.txt

COPY . /code/

COPY docker-entrypoint.sh /code/docker-entrypoint.sh
RUN chmod +x /code/docker-entrypoint.sh

ENTRYPOINT ["/code/docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
