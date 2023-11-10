FROM python:3.10-bookworm

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip && pip install pipenv && pipenv install --dev

CMD ["pipenv", "run", "pytest"]
