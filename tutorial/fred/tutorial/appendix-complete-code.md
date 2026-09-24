# Appendix A: Complete Code and Management Script

This appendix has the complete `fred.py`, the complete management script, and a quick start that puts them together. The code here is the same as the files in `tutorial/fred/`.

## Table of Contents

1. [Complete fred.py](#complete-fredpy)
2. [Management Script (fred.sh)](#management-script-fredsh)
3. [Requirements File](#requirements-file)
4. [Quick Start Guide](#quick-start-guide)
5. [Directory Structure](#directory-structure)
6. [Deployment Tips](#deployment-tips)

---

## Complete fred.py

The agent, with the Wikipedia skill, the fun fact function, and the `main` function that runs it:

<!-- snippet: no-run starts a blocking server/client (covered by SNIPPET-COMPILE + EXAMPLES-RUN) -->
```python
#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Fred: a Wikipedia knowledge bot

An agent that searches Wikipedia and shares facts about Wikipedia itself,
with a friendly, curious persona.
"""

from signalwire import AgentBase
from signalwire.core.function_result import SwaigFunctionResult

class FredTheWikiBot(AgentBase):
    """Fred, a Wikipedia assistant with a friendly persona"""
    
    def __init__(self):
        super().__init__(
            name="Fred",
            route="/fred"
        )
        
        # Set up Fred's personality using POM
        self.prompt_add_section(
            "Personality", 
            "You are Fred, a friendly and knowledgeable assistant who loves learning and sharing information from Wikipedia. You're enthusiastic about facts and always eager to help people discover new things."
        )
        
        self.prompt_add_section(
            "Goal",
            "Help users find reliable factual information by searching Wikipedia. Make learning fun and engaging."
        )
        
        self.prompt_add_section(
            "Instructions",
            bullets=[
                "Introduce yourself as Fred when greeting users",
                "Use the search_wiki function whenever users ask about factual topics",
                "Be enthusiastic about sharing knowledge",
                "If Wikipedia doesn't have information, suggest alternative search terms",
                "Make learning conversational and enjoyable",
                "Add interesting context or follow-up questions to engage users"
            ]
        )
        
        # Add the Wikipedia search skill with custom configuration
        self.add_skill("wikipedia_search", {
            "num_results": 2,  # Get up to 2 articles for broader coverage
            "no_results_message": "Oh, I couldn't find anything about '{query}' on Wikipedia. Maybe try different keywords or let me know if you meant something else!",
            "swaig_fields": {
                "fillers": {
                    "en-US": [
                        "Let me look that up on Wikipedia for you...",
                        "Searching Wikipedia for that information...",
                        "One moment, checking Wikipedia...",
                        "Let me find that in the encyclopedia..."
                    ]
                }
            }
        })
        
        # Add a fun fact function
        @self.tool(
            name="share_fun_fact",
            description="Share an interesting fact about Wikipedia itself",
            parameters={
                "category": {
                    "type": "string",
                    "description": "Type of fact to share",
                    "enum": ["statistics", "history", "records", "random"]
                }
            }
        )
        def share_fun_fact(args, raw_data):
            import random

            # Get the requested category
            category = args.get("category", "random")

            # Define facts by category
            facts = {
                "statistics": [
                    "Wikipedia has over 6 million articles in English alone!",
                    "Wikipedia is available in more than 300 languages!",
                    "Wikipedia receives over 18 billion page views per month!",
                    "There are over 100,000 active Wikipedia contributors!"
                ],
                "history": [
                    "Wikipedia was launched on January 15, 2001!",
                    "The first Wikipedia article was about the letter 'U'!",
                    "Wikipedia's name comes from 'wiki' (Hawaiian for 'quick') and 'encyclopedia'!",
                    "Jimmy Wales and Larry Sanger founded Wikipedia!"
                ],
                "records": [
                    "The most edited Wikipedia page is about George W. Bush!",
                    "The longest Wikipedia article is about California Proposition 8!",
                    "Wikipedia is the 7th most visited website in the world!",
                    "The Wikipedia article on 'List of Pokemon' is one of the most viewed!"
                ],
                "random": []  # Will be filled with all facts
            }

            # Combine all facts for random selection
            all_facts = []
            for fact_list in facts.values():
                if fact_list:  # Skip empty random list
                    all_facts.extend(fact_list)
            facts["random"] = all_facts

            # Select appropriate fact
            fact_list = facts.get(category, facts["random"])
            if not fact_list:
                return SwaigFunctionResult("I don't have any facts in that category.")

            fact = random.choice(fact_list)

            # Add category context to response
            if category != "random":
                return SwaigFunctionResult(f"Here's a {category} fact about Wikipedia: {fact}")
            else:
                return SwaigFunctionResult(f"Here's a fun Wikipedia fact: {fact}")
        
        # Configure Fred's voice
        self.add_language(
            name="English",
            code="en-US",
            voice="rime.bolt",  # A friendly, energetic voice for Fred
            speech_fillers=[
                "Hmm, let me think...",
                "Oh, that's interesting...",
                "Great question!",
                "Let me see..."
            ]
        )
        
        # Add some hints for better speech recognition
        self.add_hints([
            "Wikipedia",
            "Fred",
            "tell me about",
            "what is",
            "who is",
            "search for",
            "look up"
        ])
        
        # Set conversation parameters
        self.set_params({
            "ai_model": "gpt-4.1-nano",
            "wait_for_user": True,
            "end_of_speech_timeout": 1000,
            "ai_volume": 7,
            "local_tz": "America/New_York"
        })
        
        # Add some context about Fred
        self.set_global_data({
            "assistant_name": "Fred",
            "specialty": "Wikipedia knowledge",
            "personality_traits": ["friendly", "curious", "enthusiastic", "helpful"]
        })


def main():
    """Run Fred"""
    print("=" * 60)
    print("Fred: a Wikipedia knowledge bot")
    print("=" * 60)
    print()
    print("Fred searches Wikipedia and shares facts about Wikipedia itself.")
    print()
    print("Questions to try:")
    print("  - Tell me about Albert Einstein")
    print("  - What is quantum physics?")
    print("  - Who was Marie Curie?")
    print("  - Search for information about the solar system")
    print("  - Can you share a fun fact?")
    print()
    
    # Create and run Fred
    fred = FredTheWikiBot()
    
    # Get auth credentials for display
    username, password = fred.get_basic_auth_credentials()
    
    print(f"Fred is available at: http://localhost:{fred.port}/fred")
    print(f"Basic Auth: {username}:{password}")
    print()
    print("Starting Fred. Press Ctrl+C to stop.")
    print("=" * 60)
    
    try:
        fred.run()
    except KeyboardInterrupt:
        print("\nFred stopped.")


if __name__ == "__main__":
    main()
```

## Management Script (fred.sh)

The complete script starts Fred in the background, stops it, reports its status, and follows its log:

```bash
#!/bin/bash
# Start, stop and check Fred, the Wikipedia bot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="fred.pid"
LOG_FILE="fred.log"
FRED_SCRIPT="$SCRIPT_DIR/fred.py"

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
        else
            # PID file exists but process is dead
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Start Fred
start_fred() {
    if is_running; then
        echo -e "${YELLOW}Fred is already running with PID: $(cat "$PID_FILE")${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Starting Fred...${NC}"
    
    # Check that fred.py exists
    if [ ! -f "$FRED_SCRIPT" ]; then
        echo -e "${RED}Error: $FRED_SCRIPT not found!${NC}"
        return 1
    fi
    
    # Start Fred in background and redirect output to log file
    nohup python3 "$FRED_SCRIPT" > "$LOG_FILE" 2>&1 &
    PID=$!
    
    # Save PID to file
    echo $PID > "$PID_FILE"
    
    # Wait a moment to check if it started successfully
    sleep 2
    
    if is_running; then
        echo -e "${GREEN}Fred started${NC}"
        echo -e "   PID: $PID"
        echo -e "   Log: $LOG_FILE"
        echo -e "   URL: http://localhost:${PORT:-3000}/fred"
        
        # Try to extract auth credentials from log
        if [ -f "$LOG_FILE" ]; then
            AUTH=$(grep "Basic Auth:" "$LOG_FILE" | head -1)
            if [ ! -z "$AUTH" ]; then
                echo -e "   $AUTH"
            fi
        fi
    else
        echo -e "${RED}Fred failed to start${NC}"
        echo -e "   Check $LOG_FILE for errors"
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
    echo -e "${GREEN}Stopping Fred (PID: $PID)...${NC}"
    
    # Send SIGTERM for graceful shutdown
    kill -TERM "$PID" 2>/dev/null
    
    # Wait up to 5 seconds for process to stop
    for i in {1..5}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    # If still running, force kill
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}Fred didn't stop gracefully, forcing shutdown...${NC}"
        kill -9 "$PID" 2>/dev/null
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    echo -e "${GREEN}Fred stopped${NC}"
}

# Check Fred's status
status_fred() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}Fred is running${NC}"
        echo -e "   PID: $PID"
        echo -e "   URL: http://localhost:${PORT:-3000}/fred"
        
        # Show process info
        ps -p "$PID" -o pid,vsz,rss,comm
        
        # Show last few log lines
        if [ -f "$LOG_FILE" ]; then
            echo -e "\n${YELLOW}Recent log entries:${NC}"
            tail -5 "$LOG_FILE"
        fi
    else
        echo -e "${RED}Fred is not running${NC}"
    fi
}

# Show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}Fred's logs (press Ctrl+C to exit):${NC}"
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}No log file found${NC}"
    fi
}

# Main script logic
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
        status_fred
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Fred manager"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start Fred in the background"
        echo "  stop     - Stop Fred gracefully"
        echo "  restart  - Restart Fred"
        echo "  status   - Check if Fred is running"
        echo "  logs     - Follow Fred's logs"
        echo ""
        echo "Example:"
        echo "  $0 start   # Start Fred"
        echo "  $0 status  # Check status"
        echo "  $0 stop    # Stop Fred"
        ;;
esac
```

## Requirements File

Fred needs only the SDK. Create `requirements.txt`:

```txt
signalwire-sdk>=3.4.3
```

Or record everything installed in your virtual environment:

```bash
pip freeze > requirements.txt
```

## Quick Start Guide

These steps take you from an empty directory to a running Fred.

### 1. Setup

Create the project and install the SDK:

```bash
# Create project directory
mkdir fred-bot
cd fred-bot

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install signalwire-sdk
```

### 2. Create Files

Save the code in this appendix as three files:

- `fred.py`: the agent
- `fred.sh`: the management script
- `requirements.txt`: the dependencies

Then make the script executable:

```bash
chmod +x fred.sh
```

### 3. Run Fred

Run Fred directly, or with the management script:

```bash
# Direct method
python fred.py

# Or using management script
./fred.sh start
./fred.sh status
./fred.sh stop
```

### 4. Test Fred

Take the credentials from Fred's output, then test it:

```bash
# Test SWML endpoint
curl -u username:password http://localhost:3000/fred

# Test Wikipedia search
swaig-test fred.py --exec search_wiki --query "Python programming"

# Test fun fact
swaig-test fred.py --exec share_fun_fact --category history
```

To call a function over HTTP instead, use the URL from Fred's SWML, which carries the function's token. [Lesson 6, Step 3](06-running-testing.md#step-3-test-wikipedia-search) shows how.

### 5. Environment Variables (Optional)

Fixed credentials stay the same across restarts:

```bash
# Set fixed credentials
export SWML_BASIC_AUTH_USER="fred"
export SWML_BASIC_AUTH_PASSWORD="a-long-random-password"

# Run Fred with fixed auth
python fred.py
```

## Directory Structure

A complete Fred project looks like this. `fred.pid` and `fred.log` appear when the management script runs Fred:

```
fred-bot/
├── fred.py           # The agent
├── fred.sh           # Management script
├── requirements.txt  # Python dependencies
├── fred.pid          # Process ID (created by fred.sh)
└── fred.log          # Log file (created by fred.sh)
```

## Deployment Tips

A production deployment needs more than a running process.

### For Production

Five practices cover most deployments:

1. **Set secrets in environment variables**: the credentials, `SIGNALWIRE_SIGNING_KEY` and `SIGNALWIRE_SWAIG_SECRET` ([Lesson 6](06-running-testing.md#production-considerations) explains each)
2. **Serve Fred over HTTPS**, behind a reverse proxy or with the SDK's TLS support
3. **Run Fred under a process manager**, such as systemd or Docker, so it restarts after a crash or a reboot
4. **Rotate the logs**
5. **Monitor health and uptime**, for example with the `/health` endpoint

### Example systemd Service

This unit runs Fred from a virtual environment in `/opt/fred-bot`, and restarts it if it stops:

```ini
[Unit]
Description=Fred Wikipedia Bot
After=network.target

[Service]
Type=simple
User=fredbot
WorkingDirectory=/opt/fred-bot
ExecStart=/opt/fred-bot/venv/bin/python /opt/fred-bot/fred.py
Restart=always
EnvironmentFile=/opt/fred-bot/fred.env

[Install]
WantedBy=multi-user.target
```

Keep the secrets in `/opt/fred-bot/fred.env`, readable only by the `fredbot` user, rather than in the unit file:

```bash
SWML_BASIC_AUTH_USER=fred
SWML_BASIC_AUTH_PASSWORD=a-long-random-password
SIGNALWIRE_SIGNING_KEY=your-signing-key
SIGNALWIRE_SWAIG_SECRET=another-long-random-string
```

## Next Steps

To run Fred in a container, continue with [Appendix B: Docker Deployment](appendix-docker-deployment.md).

---

[Previous: Running and Testing](06-running-testing.md) | [Overview](README.md) | [Next: Docker Deployment](appendix-docker-deployment.md)
