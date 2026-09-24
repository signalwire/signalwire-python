#!/bin/bash
# Test script for MCP Gateway using curl

# Configuration
GATEWAY_URL="http://localhost:8080"
AUTH="admin:changeme"

echo "=== MCP Gateway Test Script ==="
echo "Gateway URL: $GATEWAY_URL"
echo ""

# Health check
echo "1. Health Check:"
curl -s "$GATEWAY_URL/health" | jq .
echo ""

# List services
echo "2. List Services:"
curl -s -u "$AUTH" "$GATEWAY_URL/services" | jq .
echo ""

# Get todo service tools
echo "3. Get Todo Service Tools:"
curl -s -u "$AUTH" "$GATEWAY_URL/services/todo/tools" | jq .
echo ""

# Add a todo
echo "4. Add a Todo:"
curl -s -u "$AUTH" -X POST "$GATEWAY_URL/services/todo/call" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "add_todo",
    "arguments": {"text": "Test todo from curl", "priority": "high"},
    "session_id": "test-session-123",
    "timeout": 300
  }' | jq .
echo ""

# List todos
echo "5. List Todos:"
curl -s -u "$AUTH" -X POST "$GATEWAY_URL/services/todo/call" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "list_todos",
    "arguments": {"status": "all"},
    "session_id": "test-session-123"
  }' | jq .
echo ""

# List sessions
echo "6. List Active Sessions:"
curl -s -u "$AUTH" "$GATEWAY_URL/sessions" | jq .
echo ""

# Complete a todo
echo "7. Complete Todo #1:"
curl -s -u "$AUTH" -X POST "$GATEWAY_URL/services/todo/call" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "complete_todo",
    "arguments": {"id": 1},
    "session_id": "test-session-123"
  }' | jq .
echo ""

# Close session
echo "8. Close Session:"
curl -s -u "$AUTH" -X DELETE "$GATEWAY_URL/sessions/test-session-123" | jq .
echo ""

echo "=== Test Complete ==="