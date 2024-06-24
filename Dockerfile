FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /my_code
COPY . /my_code/

EXPOSE 8000

RUN pip install -r requirements.txt

# RUN python manage.py collectstatic --noinput

CMD python manage.py migrate && \
    gunicorn core.wsgi:application --bind 0.0.0.0:8000
