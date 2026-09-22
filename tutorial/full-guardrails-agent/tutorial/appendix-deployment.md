# Appendix B: Deployment

In production, Penny needs four things: her secrets, a public HTTPS address, somewhere safe to keep the reservation book, and a process manager to keep her running.

## Table of Contents

1. [Settings](#settings)
2. [Secrets](#secrets)
3. [Running in Docker](#running-in-docker)
4. [The Management Script](#the-management-script)
5. [One Reservation Book](#one-reservation-book)
6. [Before You Go Live](#before-you-go-live)

---

## Settings

Penny reads everything from environment variables. `penny.sh` loads them from `.env`, and Docker takes them with `--env-file`.

| Variable | Required | Default | What it does |
|---|---|---|---|
| `SWML_BASIC_AUTH_USER` | Yes | | The user SignalWire presents to fetch SWML and call tools |
| `SWML_BASIC_AUTH_PASSWORD` | Yes | | Its password |
| `SIGNALWIRE_SIGNING_KEY` | In production | | Your project's signing key. When it's set, the SDK checks that SignalWire sent each request. |
| `SIGNALWIRE_SWAIG_SECRET` | Yes | | The secret behind the per-call tool tokens |
| `PENNY_DB_PATH` | No | `penny.sqlite3` | Where the reservation book lives. The Docker image sets `/data/penny.sqlite3`. |
| `PENNY_DEMO_DATA` | No | off | `1` adds the demo reservation to an empty book. Never in production. |
| `PENNY_HOST_NUMBER` | No | empty | Where "talk to a person" goes. Empty means Penny always takes a message. |
| `PENNY_SMS_FROM` | No | empty | Your SignalWire number for confirmation texts. Empty turns texting off. |
| `PORT` | No | `3000` | The port Penny listens on |
| `SWML_PROXY_URL_BASE` | Behind a proxy | | The public URL SignalWire reaches Penny at |
| `PENNY_AI_MODEL` | No | `gpt-4.1-mini` | The model |
| `PENNY_VOICE` | No | `inworld.Sarah` | The voice |
| `PENNY_DEBUG_EVENTS` | No | off | `1` logs the platform's debug events for each call |

`SWML_PROXY_URL_BASE` matters more than it looks. The SWML Penny serves includes the address SignalWire calls back for every tool. Behind a proxy or a tunnel, that address must be the public one, or the model's tool calls go nowhere.

## Secrets

Generate the password and the tool-token secret, rather than inventing them:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

- `SIGNALWIRE_SIGNING_KEY` isn't something you generate. It's your project's signing key from the SignalWire dashboard.
- Use the same `SIGNALWIRE_SWAIG_SECRET` on every server, so a tool call is accepted by whichever server receives it
- Keep `.env` out of version control. The tutorial's `.gitignore` already does.

## Running in Docker

<!-- source: Dockerfile -->
```dockerfile
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
```

The image runs Penny as an unprivileged user, keeps the reservation book on a volume at `/data`, and checks her health every 30 seconds. Build and run it:

```bash
docker build -t penny .
docker run -d --name penny --env-file .env -p 3000:3000 -v penny-data:/data penny
```

If you change `PORT`, change the `-p` mapping to match.

## The Management Script

<!-- source: penny.sh -->
```bash
#!/usr/bin/env bash
# Start, stop and check Penny. Reads settings from .env next to this script.
#
#   ./penny.sh start | stop | restart | status | logs | test
set -euo pipefail
cd "$(dirname "$0")"

PID_FILE=penny.pid
LOG_FILE=penny.log

load_env() {
    if [[ -f .env ]]; then
        set -a
        # shellcheck disable=SC1091
        source .env
        set +a
    fi
}

running() {
    [[ -f $PID_FILE ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

case "${1:-}" in
    start)
        if running; then echo "Penny is already running (pid $(cat "$PID_FILE"))."; exit 0; fi
        load_env
        nohup python3 penny.py >"$LOG_FILE" 2>&1 &
        echo $! >"$PID_FILE"
        sleep 2
        if running; then
            echo "Penny started (pid $(cat "$PID_FILE")). Logs: ./penny.sh logs"
        else
            echo "Penny failed to start:"; tail -n 20 "$LOG_FILE"; rm -f "$PID_FILE"; exit 1
        fi
        ;;
    stop)
        if ! running; then echo "Penny is not running."; rm -f "$PID_FILE"; exit 0; fi
        kill "$(cat "$PID_FILE")"
        for _ in 1 2 3 4 5; do running || break; sleep 1; done
        running && kill -9 "$(cat "$PID_FILE")"
        rm -f "$PID_FILE"
        echo "Penny stopped."
        ;;
    restart)
        "$0" stop
        "$0" start
        ;;
    status)
        if running; then echo "Penny is running (pid $(cat "$PID_FILE"))."; else echo "Penny is not running."; fi
        ;;
    logs)
        tail -f "$LOG_FILE"
        ;;
    test)
        python3 -m unittest -v test_penny
        ;;
    *)
        echo "usage: $0 start|stop|restart|status|logs|test"; exit 2
        ;;
esac
```

`penny.sh` is for your own machine. It doesn't restart Penny if she crashes or the server reboots, so in production use Docker, systemd, or your platform's process manager instead.

## One Reservation Book

Penny keeps all her state in one SQLite file:

- Every write is a short transaction that starts with `BEGIN IMMEDIATE`, so requests arriving together are handled one at a time. `test_parallel_confirms_book_once` checks that four confirms racing on threads book one table.
- The state is keyed by call, not held in memory, so restarting Penny between two turns of a call loses nothing.
- Back up the file while Penny runs with `sqlite3 penny.sqlite3 ".backup penny-backup.sqlite3"`.
- The restaurant's time zone is set in `reservations.py`, not taken from the server, so "tonight" means the restaurant's tonight wherever Penny runs.

One SQLite file suits one restaurant on one server. Don't put it on a network file system, where SQLite's locking can't be trusted. To run Penny on more than one server, move `ReservationStore` to a shared database such as PostgreSQL. Every rule lives in that one class, so nothing outside `reservations.py` needs to change.

## Before You Go Live

- [ ] The three required secrets are real values, `SIGNALWIRE_SIGNING_KEY` is set, and `PENNY_DEMO_DATA` is `0`
- [ ] `SWML_PROXY_URL_BASE` is Penny's public HTTPS address
- [ ] A SignalWire phone number points at `https://USER:PASSWORD@your-address/penny`
- [ ] The reservation book is on persistent storage, and backed up
- [ ] `PENNY_HOST_NUMBER` reaches a real person during the host stand's hours (`HOST_STAND_HOURS` in `reservations.py`)
- [ ] `PENNY_SMS_FROM` is a SignalWire number that can send texts
- [ ] The tables, seatings, policy and house facts in `reservations.py` are your restaurant's, not The Copper Pot's
- [ ] `python -m unittest test_penny` passes
- [ ] You called Penny yourself and tried the attacks from Lesson 10

---

[← Previous: Complete Code](appendix-complete-code.md) | [Back to Overview](README.md) | [Next: Technique Map →](appendix-technique-map.md)
