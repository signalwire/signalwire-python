FROM python:3.12-slim

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip && pip install pipenv && pipenv install --dev

CMD ["pipenv", "run", "pytest"]
