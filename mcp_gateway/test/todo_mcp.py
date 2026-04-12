#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Simple Todo List MCP Server for Testing

A stateful MCP server that maintains a todo list in memory.
Perfect for testing the MCP-SWAIG gateway functionality.
"""

import sys
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

# Set up logging to stderr to avoid polluting stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger('todo_mcp')


class TodoMCPServer:
    """Simple todo list MCP server"""
    
    def __init__(self):
        self.todos: List[Dict[str, Any]] = []
        self.next_id = 1
        logger.info("Todo MCP Server initialized")
    
    def send_message(self, msg: Dict[str, Any]):
        """Send a JSON-RPC message to stdout"""
        json_str = json.dumps(msg)
        sys.stdout.write(json_str + '\n')
        sys.stdout.flush()
        logger.debug(f"Sent: {json_str}")
    
    def read_message(self) -> Dict[str, Any]:
        """Read a JSON-RPC message from stdin"""
        line = sys.stdin.readline()
        if not line:
            return None
        
        msg = json.loads(line.strip())
        logger.debug(f"Received: {msg}")
        return msg
    
    def handle_initialize(self, msg_id: int, params: Dict[str, Any]):
        """Handle initialize request"""
        self.send_message({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "todo-mcp",
                    "version": "1.0.0"
                }
            }
        })
    
    def handle_tools_list(self, msg_id: int):
        """Handle tools/list request"""
        tools = [
            {
                "name": "add_todo",
                "description": "Add a new todo item",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The todo item text"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Priority level (low, medium, high)",
                            "enum": ["low", "medium", "high"],
                            "default": "medium"
                        }
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "list_todos",
                "description": "List all todo items",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Filter by status (all, pending, completed)",
                            "enum": ["all", "pending", "completed"],
                            "default": "all"
                        }
                    }
                }
            },
            {
                "name": "complete_todo",
                "description": "Mark a todo item as completed",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "The todo item ID"
                        }
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "delete_todo",
                "description": "Delete a todo item",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "The todo item ID"
                        }
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "clear_todos",
                "description": "Clear all todo items",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
        
        self.send_message({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": tools
            }
        })
    
    def handle_tools_call(self, msg_id: int, params: Dict[str, Any]):
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        try:
            if tool_name == "add_todo":
                result = self.add_todo(arguments)
            elif tool_name == "list_todos":
                result = self.list_todos(arguments)
            elif tool_name == "complete_todo":
                result = self.complete_todo(arguments)
            elif tool_name == "delete_todo":
                result = self.delete_todo(arguments)
            elif tool_name == "clear_todos":
                result = self.clear_todos(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            self.send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            })
            
        except Exception as e:
            logger.error(f"Error in tool {tool_name}: {e}")
            self.send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            })
    
    def add_todo(self, args: Dict[str, Any]) -> str:
        """Add a new todo item"""
        text = args.get("text")
        if not text:
            raise ValueError("Text is required")
        
        priority = args.get("priority", "medium")
        
        todo = {
            "id": self.next_id,
            "text": text,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self.todos.append(todo)
        self.next_id += 1
        
        return f"Added todo #{todo['id']}: {text} (priority: {priority})"
    
    def list_todos(self, args: Dict[str, Any]) -> str:
        """List todo items"""
        status_filter = args.get("status", "all")
        
        filtered_todos = self.todos
        if status_filter != "all":
            filtered_todos = [t for t in self.todos if t["status"] == status_filter]
        
        if not filtered_todos:
            return f"No {status_filter} todos found"
        
        lines = [f"Todo List ({status_filter}):"]
        for todo in filtered_todos:
            status_icon = "✓" if todo["status"] == "completed" else "○"
            lines.append(f"{status_icon} #{todo['id']} [{todo['priority']}] {todo['text']}")
        
        return "\n".join(lines)
    
    def complete_todo(self, args: Dict[str, Any]) -> str:
        """Mark a todo as completed"""
        todo_id = args.get("id")
        if not todo_id:
            raise ValueError("ID is required")
        
        for todo in self.todos:
            if todo["id"] == todo_id:
                if todo["status"] == "completed":
                    return f"Todo #{todo_id} is already completed"
                
                todo["status"] = "completed"
                todo["completed_at"] = datetime.now().isoformat()
                return f"Completed todo #{todo_id}: {todo['text']}"
        
        raise ValueError(f"Todo #{todo_id} not found")
    
    def delete_todo(self, args: Dict[str, Any]) -> str:
        """Delete a todo item"""
        todo_id = args.get("id")
        if not todo_id:
            raise ValueError("ID is required")
        
        for i, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                deleted = self.todos.pop(i)
                return f"Deleted todo #{todo_id}: {deleted['text']}"
        
        raise ValueError(f"Todo #{todo_id} not found")
    
    def clear_todos(self, args: Dict[str, Any]) -> str:
        """Clear all todos"""
        count = len(self.todos)
        self.todos.clear()
        self.next_id = 1
        return f"Cleared {count} todo(s)"
    
    def handle_shutdown(self, msg_id: int):
        """Handle shutdown request"""
        self.send_message({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {}
        })
        logger.info("Shutdown requested")
        sys.exit(0)
    
    def run(self):
        """Main server loop"""
        logger.info("Todo MCP Server starting...")
        
        while True:
            try:
                msg = self.read_message()
                if not msg:
                    break
                
                method = msg.get("method")
                msg_id = msg.get("id")
                params = msg.get("params", {})
                
                if method == "initialize":
                    self.handle_initialize(msg_id, params)
                elif method == "tools/list":
                    self.handle_tools_list(msg_id)
                elif method == "tools/call":
                    self.handle_tools_call(msg_id, params)
                elif method == "shutdown":
                    self.handle_shutdown(msg_id)
                else:
                    # Unknown method
                    self.send_message({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                if msg_id:
                    self.send_message({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    })
        
        logger.info("Todo MCP Server stopped")


if __name__ == "__main__":
    server = TodoMCPServer()
    server.run()