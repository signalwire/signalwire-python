FROM python:3.13-slim

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

RUN pip install --upgrade pip && pip install pipenv && pipenv install --dev

CMD ["pipenv", "run", "pytest"]
