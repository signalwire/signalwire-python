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