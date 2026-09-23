#!/bin/bash

# MCP Gateway Docker Manager
# Convenient wrapper for docker-compose commands

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "MCP Gateway Docker Manager"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  start       Start the container (builds if needed)"
    echo "  stop        Stop the container"
    echo "  restart     Restart the container"
    echo "  status      Show container status"
    echo "  logs        Show container logs (use -f to follow)"
    echo "  shell       Open a shell in the running container"
    echo "  clean       Stop and remove container and volumes"
    echo "  config      Validate docker-compose.yml"
    echo ""
    echo "Options:"
    echo "  -f, --follow    Follow logs (with 'logs' command)"
    echo "  -d, --detach    Run in background (with 'start' command)"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start              # Start in foreground"
    echo "  $0 start -d           # Start in background"
    echo "  $0 logs -f            # Follow logs"
    echo "  $0 restart            # Restart the container"
}

# Function to check if container is running
is_running() {
    docker-compose ps --services --filter "status=running" | grep -q "mcp-gateway"
}

# Function to ensure config exists
ensure_config() {
    if [ ! -f "config.json" ]; then
        if [ -f "sample_config.json" ]; then
            echo -e "${YELLOW}No config.json found. Docker will use sample_config.json${NC}"
            echo -e "${YELLOW}To customize, create config.json from sample:${NC}"
            echo -e "${BLUE}  cp sample_config.json config.json${NC}"
            echo -e "${BLUE}  # Then edit config.json${NC}"
        else
            echo -e "${RED}Error: No config.json or sample_config.json found${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ Using existing config.json${NC}"
    fi
}


# Parse command
COMMAND=${1:-help}
shift || true

case "$COMMAND" in
    build)
        echo -e "${BLUE}Building MCP Gateway Docker image...${NC}"
        docker-compose build
        echo -e "${GREEN}✓ Build complete${NC}"
        ;;
        
    start)
        ensure_config
        DETACH=""
        for arg in "$@"; do
            case $arg in
                -d|--detach)
                    DETACH="-d"
                    ;;
            esac
        done
        
        echo -e "${BLUE}Starting MCP Gateway...${NC}"
        if [ -n "$DETACH" ]; then
            docker-compose up -d
            echo -e "${GREEN}✓ MCP Gateway started in background${NC}"
            echo -e "${BLUE}View logs with: $0 logs -f${NC}"
            echo -e "${BLUE}Access at: http://localhost:${MCP_PORT:-8080}${NC}"
        else
            docker-compose up
        fi
        ;;
        
    stop)
        if is_running; then
            echo -e "${BLUE}Stopping MCP Gateway...${NC}"
            docker-compose stop
            echo -e "${GREEN}✓ MCP Gateway stopped${NC}"
        else
            echo -e "${YELLOW}MCP Gateway is not running${NC}"
        fi
        ;;
        
    restart)
        echo -e "${BLUE}Restarting MCP Gateway...${NC}"
        docker-compose restart
        echo -e "${GREEN}✓ MCP Gateway restarted${NC}"
        ;;
        
    status)
        echo -e "${BLUE}MCP Gateway Status:${NC}"
        docker-compose ps
        
        if is_running; then
            echo ""
            echo -e "${GREEN}✓ MCP Gateway is running${NC}"
            
            # Try to get health status
            echo -e "${BLUE}Checking health at http://localhost:${MCP_PORT:-8080}/health...${NC}"
            if curl -s -f "http://localhost:${MCP_PORT:-8080}/health" > /dev/null 2>&1; then
                echo -e "${GREEN}✓ Health check passed${NC}"
            else
                echo -e "${YELLOW}⚠ Health check failed${NC}"
            fi
        else
            echo -e "${YELLOW}MCP Gateway is not running${NC}"
        fi
        ;;
        
    logs)
        FOLLOW=""
        for arg in "$@"; do
            case $arg in
                -f|--follow)
                    FOLLOW="-f"
                    ;;
            esac
        done
        
        if [ -n "$FOLLOW" ]; then
            echo -e "${BLUE}Following MCP Gateway logs (Ctrl+C to stop)...${NC}"
        else
            echo -e "${BLUE}MCP Gateway logs:${NC}"
        fi
        docker-compose logs $FOLLOW mcp-gateway
        ;;
        
    shell)
        if is_running; then
            echo -e "${BLUE}Opening shell in MCP Gateway container...${NC}"
            docker-compose exec mcp-gateway /bin/sh
        else
            echo -e "${RED}Error: MCP Gateway is not running${NC}"
            echo -e "${YELLOW}Start it with: $0 start${NC}"
            exit 1
        fi
        ;;
        
    clean)
        echo -e "${YELLOW}This will stop and remove the MCP Gateway container and volumes${NC}"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Cleaning up MCP Gateway...${NC}"
            docker-compose down -v
            echo -e "${GREEN}✓ Cleanup complete${NC}"
        else
            echo -e "${YELLOW}Cancelled${NC}"
        fi
        ;;
        
    config)
        echo -e "${BLUE}Validating docker-compose.yml...${NC}"
        if docker-compose config > /dev/null; then
            echo -e "${GREEN}✓ Configuration is valid${NC}"
            echo ""
            echo -e "${BLUE}Services:${NC}"
            docker-compose config --services
        else
            echo -e "${RED}✗ Configuration is invalid${NC}"
            exit 1
        fi
        ;;
        
    help|-h|--help)
        show_usage
        ;;
        
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac