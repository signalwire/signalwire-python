# Lesson 6: Running and Testing Fred

Fred is complete. This lesson runs it, tests its functions with `swaig-test` and `curl`, adds a script to manage it, and covers the problems you're most likely to hit.

## Table of Contents

1. [Running Fred](#running-fred)
2. [Understanding the Endpoints](#understanding-the-endpoints)
3. [Testing with swaig-test](#testing-with-swaig-test)
4. [Testing with curl](#testing-with-curl)
5. [Managing Fred with Scripts](#managing-fred-with-scripts)
6. [Troubleshooting](#troubleshooting)
7. [Production Considerations](#production-considerations)

---

## Running Fred

Running `fred.py` starts a web server that SignalWire can call.

### Step 1: Run Fred Directly

Start Fred from the project directory:

```bash
python fred.py
```

The output looks like this. Your password will differ:

```
============================================================
Fred: a Wikipedia knowledge bot
============================================================

Fred searches Wikipedia and shares facts about Wikipedia itself.

Questions to try:
  - Tell me about Albert Einstein
  - What is quantum physics?
  - Who was Marie Curie?
  - Search for information about the solar system
  - Can you share a fun fact?

Fred is available at: http://localhost:3000/fred
Basic Auth: signalwire:Xk2vQ9mR7tLp4WzN8bJc5HdF3sGy6AeU1oKi0nY

Starting Fred. Press Ctrl+C to stop.
============================================================
... [warning  ] webhook_signature_validation_disabled ...
... [info     ] agent_starting ...
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:3000 (Press CTRL+C to quit)
```

### Important Information

Note three details from the output:

- **URL**: `http://localhost:3000/fred`
- **Credentials**: the username and password for basic authentication. Without `SWML_BASIC_AUTH_USER` and `SWML_BASIC_AUTH_PASSWORD` set, the SDK generates new ones each time Fred starts.
- **The signature warning**: webhook signature validation is off until you set `SIGNALWIRE_SIGNING_KEY`. That's fine on your own machine. [Production Considerations](#production-considerations) covers when to set it.

## Understanding the Endpoints

Fred answers on three HTTP endpoints.

### 1. SWML Endpoint (/fred)

Returns Fred's configuration as a SWML document:

- **Purpose**: tells SignalWire how Fred behaves
- **Method**: SignalWire requests it with a `POST`. You can fetch it with `GET` to inspect it.
- **Auth**: required

### 2. SWAIG Endpoint (POST /fred/swaig/)

Runs Fred's functions:

- **Purpose**: executes a function the model called
- **Method**: `POST`
- **Auth**: required
- **Token**: required. Each function's URL in the SWML carries a token that's valid for one call.
- **Content-Type**: `application/json`

### 3. Health Endpoint (GET /health)

Reports whether Fred is running. It needs no credentials, so load balancers and container health checks can use it.

## Testing with swaig-test

The SDK includes a command-line tool, `swaig-test`, that loads an agent from its file and runs its functions without starting a server.

### List Fred's Functions

List the functions Fred registers:

```bash
swaig-test fred.py --list-tools
```

`fred.py` creates the agent in `main()`, so `swaig-test` runs `main()` to find it, and Fred's banner prints first. The function list follows it:

```
Available SWAIG functions:
  search_wiki - Search Wikipedia for information about a topic and get article summaries (LOCAL webhook)
    Parameters:
      query (string): The search term or topic to look up on Wikipedia
  share_fun_fact - Share an interesting fact about Wikipedia itself (LOCAL webhook)
    Parameters:
      category (string [options: statistics, history, records, random]): Type of fact to share
```

### Test Functions Without Running the Server

Run a function with `--exec`, followed by its arguments:

```bash
# Test Wikipedia search
swaig-test fred.py --exec search_wiki --query "Python programming language"

# Test fun fact with category
swaig-test fred.py --exec share_fun_fact --category history

# Test fun fact without parameters (uses default)
swaig-test fred.py --exec share_fun_fact
```

Everything after `--exec` and the function name is passed to the function as an argument. Put `swaig-test`'s own options, such as `--verbose` or `--call-id`, before `--exec`.

### Generate and Inspect SWML

`--dump-swml` prints the SWML document SignalWire would receive:

```bash
# Generate SWML document
swaig-test fred.py --dump-swml

# Get raw JSON for processing
swaig-test fred.py --dump-swml --raw | jq '.sections.main[] | select(.ai) | .ai.SWAIG.functions'
```

The `ai` verb isn't the first entry in `main`. An `answer` verb comes before it, so the `jq` filter selects the entry that has `ai`.

### Test Different Call Scenarios

Options that describe the call change the request `swaig-test` simulates:

```bash
# Simulate an inbound SIP call
swaig-test fred.py --dump-swml --call-type sip --call-direction inbound

# Custom caller info
swaig-test fred.py --dump-swml --from-number "+15551234567" --to-extension "+15559876543"
```

### Test Serverless Deployment

`--simulate-serverless` renders the agent as it would run on a serverless platform:

```bash
# Test Lambda deployment
swaig-test fred.py --simulate-serverless lambda --dump-swml

# Test with Lambda function execution
swaig-test fred.py --simulate-serverless lambda --exec search_wiki --query "SignalWire"

# Test CGI deployment
swaig-test fred.py --simulate-serverless cgi --cgi-host example.com --dump-swml
```

### Debug Mode

`--verbose` shows the SDK's logs while a function runs. Like every `swaig-test` option, it goes before `--exec`:

```bash
# See the SDK's logs during the call
swaig-test fred.py --verbose --exec search_wiki --query "Albert Einstein"

# Run a function as part of a specific call
swaig-test fred.py --call-id custom-123 --exec share_fun_fact
```

### Benefits of swaig-test

`swaig-test` is the fastest way to check an agent:

1. **No server required**: functions run without starting Fred
2. **Quick validation**: check a function before you deploy
3. **SWML inspection**: see exactly what SignalWire receives
4. **Serverless testing**: check Lambda and CGI configurations
5. **Debugging**: see the SDK's logs for one function call

## Testing with curl

With Fred running, you can also test it over HTTP. Replace `username:password` with the credentials from Fred's output.

### Step 2: Fetch Fred's SWML Configuration

Fetch the SWML document, and format it:

```bash
# Get Fred's SWML document
curl -u username:password http://localhost:3000/fred | python -m json.tool
```

The response is Fred's SWML document. This excerpt is shortened:

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "answer": {}
      },
      {
        "ai": {
          "prompt": {
            "pom": [
              {
                "title": "Personality",
                "body": "You are Fred, a friendly and knowledgeable assistant..."
              }
            ]
          },
          "SWAIG": {
            "functions": [
              {
                "function": "search_wiki",
                "description": "Search Wikipedia for information about a topic and get article summaries"
              },
              {
                "function": "share_fun_fact",
                "description": "Share an interesting fact about Wikipedia itself"
              }
            ]
          }
        }
      }
    ]
  }
}
```

### Step 3: Test Wikipedia Search

SignalWire calls a function at the URL Fred's SWML gives it, and that URL carries a security token that's valid for one call only. A test does the same. It fetches the SWML for a test call, takes the function's URL from it, and posts to that URL with the same call ID.

```bash
# Fetch the SWML for a test call, and take search_wiki's URL from it
URL=$(curl -s -u username:password "http://localhost:3000/fred?call_id=test-call-123" | python -c '
import json, sys
ai = next(v["ai"] for v in json.load(sys.stdin)["sections"]["main"] if "ai" in v)
print(next(f["web_hook_url"] for f in ai["SWAIG"]["functions"] if f["function"] == "search_wiki"))')

# Call search_wiki the way SignalWire does, with the same call ID
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "function": "search_wiki",
    "argument": {
      "parsed": [
        {
          "query": "FreeSWITCH"
        }
      ]
    },
    "call_id": "test-call-123"
  }' \
  "$URL"
```

The URL already includes Fred's credentials, so the second `curl` doesn't need `-u`.

The response holds up to two article summaries, separated by a line of `=` characters. This one is shortened:

```json
{
  "response": "**FreeSWITCH**\n\nFreeSWITCH is a free and open-source application server for real-time communication...\n\n==================================================\n\n**...**\n\n..."
}
```

### Step 4: Test Fun Fact Function

Each function has its own token, so take `share_fun_fact`'s URL the same way:

```bash
# Fetch the SWML for a test call, and take share_fun_fact's URL from it
URL=$(curl -s -u username:password "http://localhost:3000/fred?call_id=test-call-456" | python -c '
import json, sys
ai = next(v["ai"] for v in json.load(sys.stdin)["sections"]["main"] if "ai" in v)
print(next(f["web_hook_url"] for f in ai["SWAIG"]["functions"] if f["function"] == "share_fun_fact"))')

# Get a history fact
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "function": "share_fun_fact",
    "argument": {
      "parsed": [
        {
          "category": "history"
        }
      ]
    },
    "call_id": "test-call-456"
  }' \
  "$URL"
```

The response is one fact from the category:

```json
{
  "response": "Here's a history fact about Wikipedia: Wikipedia was launched on January 15, 2001!"
}
```

## Managing Fred with Scripts

A small shell script can start Fred in the background, stop it, and report its status.

### Step 5: Create Management Script

Create `fred.sh` with this minimal version. [Appendix A](appendix-complete-code.md) has the complete script, which adds a `logs` command:

```bash
#!/bin/bash
# Start, stop and check Fred

PID_FILE="fred.pid"
LOG_FILE="fred.log"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if Fred is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Start Fred
start_fred() {
    if is_running; then
        echo -e "${YELLOW}Fred is already running${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Starting Fred...${NC}"
    nohup python fred.py > "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    sleep 2
    
    if is_running; then
        echo -e "${GREEN}Fred started${NC}"
        echo "   PID: $PID"
        echo "   Logs: $LOG_FILE"
        
        # Extract auth from log
        AUTH=$(grep "Basic Auth:" "$LOG_FILE" | head -1)
        if [ ! -z "$AUTH" ]; then
            echo "   $AUTH"
        fi
    else
        echo -e "${RED}Fred failed to start${NC}"
        return 1
    fi
}

# Stop Fred
stop_fred() {
    if ! is_running; then
        echo -e "${YELLOW}Fred is not running${NC}"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    echo -e "${GREEN}Stopping Fred...${NC}"
    kill $PID
    rm -f "$PID_FILE"
    echo -e "${GREEN}Fred stopped${NC}"
}

# Main script
case "$1" in
    start)
        start_fred
        ;;
    stop)
        stop_fred
        ;;
    restart)
        stop_fred
        sleep 1
        start_fred
        ;;
    status)
        if is_running; then
            echo -e "${GREEN}Fred is running${NC}"
            PID=$(cat "$PID_FILE")
            echo "   PID: $PID"
        else
            echo -e "${RED}Fred is not running${NC}"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
```

Make it executable:

```bash
chmod +x fred.sh
```

### Using the Management Script

The script's commands start, check and stop Fred:

```bash
# Start Fred in background
./fred.sh start

# Check status
./fred.sh status

# View logs
tail -f fred.log

# Stop Fred
./fred.sh stop
```

## Troubleshooting

Most problems when running Fred fall into a few groups.

### Common Issues and Solutions

#### Port Already in Use

Another program is using port 3000. The error is `[Errno 98]` on Linux and `[Errno 48]` on macOS:

```
ERROR: [Errno 98] Address already in use
```

Find the program that holds the port, and stop it:

```bash
# Find process using port 3000
lsof -i :3000
```

Or run Fred on another port:

```bash
PORT=3001 python fred.py
```

#### Authentication Failed

A request with missing or wrong credentials gets `401` and this body:

```json
{"error": "Unauthorized"}
```

To fix it, check three things:

- The username and password match the ones in Fred's output
- The credentials are current. Generated credentials change each time Fred restarts.
- The `curl` command includes `-u username:password`

#### Module Not Found

The SDK isn't installed in the Python that runs Fred:

```
ModuleNotFoundError: No module named 'signalwire'
```

Activate the virtual environment, then install the SDK:

```bash
source fred-env/bin/activate
pip install signalwire-sdk
```

#### Invalid or Expired Token

A function call through `/fred/swaig/` can answer "the security token for this function is invalid or expired". The request either lacks the token from Fred's SWML, or carries a token from another call. [Step 3](#step-3-test-wikipedia-search) shows how to call a function with its token.

#### No Response from Functions

If a function call returns nothing useful, check three things:

1. The function name matches exactly (`search_wiki`, not `search_wikipedia`)
2. The JSON has the right structure, including the `parsed` array
3. The `Content-Type: application/json` header is set

### Debug Tips

These checks narrow down most problems.

#### Enable Debug Logging

`SIGNALWIRE_LOG_LEVEL` sets how much the SDK logs. Run Fred with debug logging:

```bash
SIGNALWIRE_LOG_LEVEL=debug python fred.py
```

#### Test a Function Without the Server

`swaig-test` runs a function without a server, credentials or a token:

```bash
# Simplest possible function call: no server, no credentials, no token
swaig-test fred.py --exec share_fun_fact
```

If this works but a call over HTTP doesn't, the problem is in the request, not in Fred's code.

#### Check Fred's Health

The health endpoint needs no credentials:

```bash
curl http://localhost:3000/health
```

A running Fred answers:

```json
{"status":"healthy","agent":"Fred"}
```

## Production Considerations

Running Fred for real callers needs fixed secrets, HTTPS, and a process manager.

### Security

Set these environment variables before Fred takes real calls:

1. **Fixed credentials**, so they don't change on restart:

   ```bash
   export SWML_BASIC_AUTH_USER="fred"
   export SWML_BASIC_AUTH_PASSWORD="a-long-random-password"
   ```

2. **Your project's signing key**, from the SignalWire dashboard. With it set, the SDK rejects requests that SignalWire didn't sign.

   ```bash
   export SIGNALWIRE_SIGNING_KEY="your-signing-key"
   ```

3. **A fixed secret for tool tokens.** Without one, the SDK generates a new secret each time Fred starts, so calls in progress during a restart lose their tokens. Every copy of Fred must use the same secret.

   ```bash
   export SIGNALWIRE_SWAIG_SECRET="another-long-random-string"
   ```

Serve Fred over HTTPS, either behind a reverse proxy such as nginx, or with the SDK's own TLS support (`SWML_SSL_ENABLED`, `SWML_SSL_CERT_PATH` and `SWML_SSL_KEY_PATH`).

### Deployment Options

Three common ways to keep Fred running:

1. **Direct**, choosing the port with `PORT`:

   ```bash
   PORT=8080 python fred.py
   ```

2. **Docker**: [Appendix B](appendix-docker-deployment.md) has a Dockerfile and a Compose file.

3. **systemd**: [Appendix A](appendix-complete-code.md) has a service file.

## Summary

In this tutorial you:

- Built Fred from scratch
- Ran Fred locally
- Tested Wikipedia search and fun facts with `swaig-test` and `curl`
- Created a management script
- Learned how to troubleshoot common problems

## Next Steps

To take real phone calls with Fred:

1. Sign up for a SignalWire account
2. Make Fred reachable at a public HTTPS address, with a deployment or a tunnel such as ngrok
3. Set `SWML_PROXY_URL_BASE` to that address
4. Buy or configure a phone number, and point it at `https://username:password@your-address/fred`

The appendices have the complete code and deployment files. Continue with [Appendix A: Complete Code and Management Script](appendix-complete-code.md).

---

The commands from this lesson, for quick reference:

```bash
# Start Fred
python fred.py

# Test SWML
curl -u user:pass http://localhost:3000/fred

# Test Wikipedia search
swaig-test fred.py --exec search_wiki --query "Python"

# Test fun fact
swaig-test fred.py --exec share_fun_fact
```

---

[Previous: Custom Functions](05-custom-functions.md) | [Overview](README.md) | [Next: Complete Code](appendix-complete-code.md)
