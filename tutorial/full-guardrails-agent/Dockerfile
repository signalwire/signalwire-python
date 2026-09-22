FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY reservations.py workflow.py handlers.py penny.py ./

# Run as an unprivileged user, and keep the reservation book on a volume.
RUN useradd --create-home penny && mkdir -p /data && chown penny /data
USER penny
ENV PENNY_DB_PATH=/data/penny.sqlite3
VOLUME /data

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://localhost:' + os.environ.get('PORT', '3000') + '/health')" || exit 1
CMD ["python", "penny.py"]
