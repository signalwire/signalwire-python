FROM python:3.12-slim

# Install build-essential and any other necessary system dependencies
RUN apt-get update && apt-get install -y build-essential

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip && pip install pipenv && pipenv install --dev

CMD ["pipenv", "run", "pytest"]
