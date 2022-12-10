FROM python:3.8
WORKDIR /app

RUN pip install --no-cache-dir --upgrade poetry==1.1.6

COPY . /app
RUN poetry install -n --no-root