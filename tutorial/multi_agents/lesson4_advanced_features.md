# Lesson 4: Advanced Features and Best Practices

This lesson covers advanced features of the SignalWire Agents SDK and production deployment practices: custom SWAIG functions, error handling, debugging techniques, and deployment strategies.

## Table of Contents

1. [Custom SWAIG Functions](#custom-swaig-functions)
2. [Error Handling and Results](#error-handling-and-results)
3. [Logging and Debugging](#logging-and-debugging)
4. [Production Deployment](#production-deployment)
5. [Testing Strategies](#testing-strategies)
6. [Performance Optimization](#performance-optimization)
7. [Security Best Practices](#security-best-practices)
8. [Summary](#summary)

---

## Custom SWAIG Functions

SWAIG (SignalWire AI Gateway) functions allow your agent to perform actions beyond conversation. These can integrate with APIs, databases, or perform calculations.

### Basic Function Structure

A SWAIG function is a Python function registered with the `@self.tool()` decorator inside the agent's `__init__`:

```python
from signalwire import AgentBase
from signalwire.core.function_result import SwaigFunctionResult

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="My Agent", route="/")
        
        # Define a function using the decorator
        @self.tool(
            "calculate_price",
            description="Calculate total price with tax",
            parameters={
                "amount": {"type": "number", "description": "Base price"},
                "tax_rate": {"type": "number", "description": "Tax rate (default 8%)"}
            }
        )
        def calculate_price(args, raw_data):
            """Calculate total price including tax"""
            amount = args.get("amount", 0)
            tax_rate = args.get("tax_rate", 0.08)
            tax = amount * tax_rate
            total = amount + tax

            return SwaigFunctionResult(
                f"The total price is ${total:.2f} "
                f"(${amount:.2f} + ${tax:.2f} tax)"
            )
```

### Function Parameters

**Required Parameters:**

```python
@self.tool(
    "create_order",
    description="Create a new order",
    parameters={
        "customer_name": {"type": "string", "description": "Customer's full name"},
        "items": {"type": "string", "description": "Items to order"},
        "priority": {"type": "string", "description": "Order priority level"}
    },
    required=["customer_name", "items"]  # These params are required
)
def create_order(args, raw_data):
    customer_name = args.get("customer_name")
    items = args.get("items")
    priority = args.get("priority", "normal")
    # Implementation
```

**Parameter Types:**

```python
# Supported parameter types in the parameters dict
parameters={
    "text": {"type": "string", "description": "A text value"},
    "number": {"type": "integer", "description": "An integer value"},
    "decimal": {"type": "number", "description": "A decimal value"},
    "flag": {"type": "boolean", "description": "A true/false value"}
}
```

### Advanced Function Results

The `SwaigFunctionResult` class provides rich responses:

```python
@self.tool(
    "check_inventory",
    description="Check product availability",
    parameters={
        "product_id": {"type": "string", "description": "The product ID to check"}
    }
)
def check_inventory(args, raw_data):
    product_id = args.get("product_id")
    # Simulate inventory check
    in_stock = 5

    if in_stock > 0:
        result = SwaigFunctionResult(f"Product {product_id} is in stock ({in_stock} units)")

        # Add data the agent can reference later in the call
        result.add_action("set_global_data", {
            "last_checked_product": product_id,
            "stock_level": in_stock
        })

        return result
    else:
        # Return error state
        return SwaigFunctionResult(
            f"Product {product_id} is out of stock"
        )
```

### Async vs Sync Functions

Both patterns are supported:

```python
# Async function (recommended for I/O operations)
@self.tool(
    "fetch_data",
    description="Fetch data from API",
    parameters={
        "query": {"type": "string", "description": "Search query"}
    }
)
async def fetch_data(args, raw_data):
    query = args.get("query")
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/{query}") as resp:
            data = await resp.json()
            return SwaigFunctionResult(f"Found {len(data)} results")

# Sync function (for quick calculations)
@self.tool(
    "calculate",
    description="Perform calculation",
    parameters={
        "x": {"type": "integer", "description": "First number"},
        "y": {"type": "integer", "description": "Second number"}
    }
)
def calculate(args, raw_data):
    x = args.get("x", 0)
    y = args.get("y", 0)
    return SwaigFunctionResult(f"Result: {x + y}")
```

---

## Error Handling and Results

Proper error handling ensures your agent gracefully handles failures.

### Function Error Handling

Wrap the function body in a `try`/`except` block and describe the problem in the response text:

```python
@self.tool(
    "process_order",
    description="Process customer order",
    parameters={
        "order_id": {"type": "string", "description": "The order ID to process"}
    }
)
def process_order(args, raw_data):
    order_id = args.get("order_id")
    try:
        # Validate input
        if not order_id or len(order_id) < 5:
            return SwaigFunctionResult(
                "Invalid order ID format"
            )

        # Simulate processing
        if order_id.startswith("TEST"):
            raise ValueError("Test orders cannot be processed")

        # Success case
        return SwaigFunctionResult(f"Order {order_id} processed successfully")

    except ValueError as e:
        return SwaigFunctionResult(
            f"Order processing failed: {str(e)}"
        )
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error processing order: {e}")
        return SwaigFunctionResult(
            "An unexpected error occurred. Please try again."
        )
```

### Agent-Level Error Handling

The prompt can also tell the model how to talk about a failed function call:

```python
class RobustAgent(AgentBase):
    def __init__(self):
        super().__init__(name="Robust Agent", route="/")
        
        # Add error handling instructions to prompt
        self.prompt_add_section(
            "Error Handling",
            body="How to handle errors gracefully:",
            bullets=[
                "If a function returns an error, acknowledge it politely",
                "Offer alternative solutions when possible",
                "Never expose technical error details to customers",
                "Always maintain a helpful, professional tone"
            ]
        )
```

### Validation Patterns

Collect validation problems into a list, then report all of them at once instead of stopping at the first one:

```python
@self.tool(
    "update_customer",
    description="Update customer information",
    parameters={
        "customer_id": {"type": "string", "description": "The customer's ID"},
        "email": {"type": "string", "description": "Customer's email address"},
        "phone": {"type": "string", "description": "Customer's phone number"}
    }
)
def update_customer(args, raw_data):
    customer_id = args.get("customer_id")
    email = args.get("email")
    phone = args.get("phone")
    # Input validation
    errors = []

    if not customer_id:
        errors.append("Customer ID is required")

    if email and "@" not in email:
        errors.append("Invalid email format")

    if phone and len(phone) < 10:
        errors.append("Phone number must be at least 10 digits")

    if errors:
        return SwaigFunctionResult(
            f"Validation failed: {', '.join(errors)}"
        )

    # Process valid input
    return SwaigFunctionResult("Customer updated successfully")
```

---

## Logging and Debugging

Effective logging is crucial for troubleshooting and monitoring.

### Using the Logger

Get a logger from the SDK's logging module and call it from inside a tool function:

```python
from signalwire.core.logging_config import get_logger

logger = get_logger(__name__)

class DebugAgent(AgentBase):
    def __init__(self):
        super().__init__(name="Debug Agent", route="/")
        logger.info("Initializing Debug Agent")

        @self.tool(
            "debug_function",
            description="Test function with logging",
            parameters={
                "param": {"type": "string", "description": "Parameter to process"}
            }
        )
        def debug_function(args, raw_data):
            param = args.get("param", "")
            logger.debug(f"Function called with param: {param}")

            try:
                # Some operation
                result = param.upper()
                logger.info(f"Operation successful: {result}")
                return SwaigFunctionResult(result)

            except Exception as e:
                logger.error(f"Operation failed: {e}", exc_info=True)
                return SwaigFunctionResult("Operation failed")
```

### Log Levels

Set the level when you create the server:

```python
server = AgentServer(log_level="debug")
```

You can set the same level through the environment instead:

```bash
export SIGNALWIRE_LOG_LEVEL=debug
```

The accepted levels are `debug` (detailed information for debugging), `info` (general information, the default), `warning`, `error`, and `critical`.

### Debugging Techniques

**1. Request Logging:**

```python
def configure_dynamic(self, query_params, body_params, headers, agent):
    logger.debug(f"Query params: {query_params}")
    logger.debug(f"Body params: {body_params}")
    logger.debug(f"Headers: {headers}")
```

**2. SWML Inspection:**

```bash
# Dump SWML without running
swaig-test agent.py --dump-swml

# Test specific functions
swaig-test agent.py --exec function_name --param value
```

**3. Interactive Debugging:**

```python
@self.tool(
    "debug_state",
    description="Debug agent state",
    parameters={}
)
def debug_state(args, raw_data):
    import json
    state = {
        "agent_name": self.get_name(),
        "functions": list(self._tool_registry._swaig_functions.keys()),
        "languages": self._languages
    }
    logger.info(f"Agent state: {json.dumps(state, indent=2)}")
    return SwaigFunctionResult("State logged to console")
```

---

## Production Deployment

### Environment Variables

Set authentication, logging, and SSL through environment variables rather than hardcoding them:

```bash
# Core configuration
export SWML_BASIC_AUTH_USER=produser
export SWML_BASIC_AUTH_PASSWORD=strongpassword
export SIGNALWIRE_LOG_LEVEL=info

# SSL configuration
export SWML_SSL_ENABLED=true
export SWML_SSL_CERT_PATH=/etc/ssl/certs/agent.crt
export SWML_SSL_KEY_PATH=/etc/ssl/private/agent.key
export SWML_DOMAIN=agents.example.com
```

### Docker Deployment

This `Dockerfile` installs the SDK, runs the agent as a non-root user, and checks `/health`:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Run agent
CMD ["python", "agent.py"]
```

### Systemd Service

On a plain Linux host without Docker, a systemd unit keeps the agent running and restarts it on failure:

```ini
# /etc/systemd/system/signalwire-agent.service
[Unit]
Description=SignalWire AI Agent
After=network.target

[Service]
Type=simple
User=agent
WorkingDirectory=/opt/signalwire-agent
Environment="SIGNALWIRE_LOG_LEVEL=info"
Environment="SWML_SSL_ENABLED=true"
ExecStart=/usr/bin/python3 /opt/signalwire-agent/agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Health Monitoring

`AgentServer` already exposes `/health`. Add a route directly to its FastAPI app for a more detailed check:

<!-- snippet: no-run illustrative fragment (references `server` established in the surrounding prose) -->
```python
# Add custom health checks
@server.app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "triage": "active",
            "sales": "active",
            "support": "active"
        },
        "checks": {
            "database": check_database_connection(),
            "search_index": check_search_index(),
            "memory_usage": get_memory_usage()
        }
    }
```

---

## Testing Strategies

### Unit Testing Functions

Call `on_function_call()` the same way the SWAIG endpoint does, with the function name, its arguments, and the raw request data:

```python
from signalwire.core.function_result import SwaigFunctionResult

def test_calculate_price():
    agent = MyAgent()

    # Test the normal case
    result = agent.on_function_call("calculate_price", {"amount": 100.0, "tax_rate": 0.08}, {})
    assert isinstance(result, SwaigFunctionResult)
    assert "108.00" in result.response

    # Test the edge case
    result = agent.on_function_call("calculate_price", {"amount": 0, "tax_rate": 0}, {})
    assert "0.00" in result.response
```

### Integration Testing

Run the agent, then test it as a client would, over HTTP and through `swaig-test`:

```python
# test_integration.py
import requests

def test_agent_swml_generation():
    """Test that the agent generates valid SWML"""
    response = requests.get("http://localhost:3000/")
    assert response.status_code == 200

    swml = response.json()
    ai_section = swml["sections"]["main"][-1]["ai"]
    assert "prompt" in ai_section
    assert "languages" in ai_section

def test_function_execution():
    """Test function execution via swaig-test"""
    import subprocess
    result = subprocess.run(
        ["swaig-test", "agent.py", "--exec", "calculate_price", "--amount", "100"],
        capture_output=True,
        text=True
    )
    assert "108.00" in result.stdout
```

### Load Testing

Send concurrent requests to the SWML endpoint to see how the agent behaves under load:

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:3000/

# Using curl in a loop
for i in {1..100}; do
    curl -s http://localhost:3000/ > /dev/null &
done
wait
```

---

## Performance Optimization

### Caching Strategies

Cache an expensive lookup on the agent instance, and expire it after a few minutes:

```python
from functools import lru_cache
import asyncio

class OptimizedAgent(AgentBase):
    def __init__(self):
        super().__init__(name="Optimized Agent", route="/")
        self._cache = {}

        @self.tool(
            "get_product_info",
            description="Get product information",
            parameters={
                "product_id": {"type": "string", "description": "The product ID to look up"}
            }
        )
        async def get_product_info(args, raw_data):
            product_id = args.get("product_id")
            # Check cache first
            if product_id in self._cache:
                logger.debug(f"Cache hit for {product_id}")
                return SwaigFunctionResult(self._cache[product_id])

            # Expensive operation
            info = await fetch_from_database(product_id)

            # Cache for 5 minutes
            self._cache[product_id] = info
            asyncio.create_task(self._expire_cache(product_id, 300))

            return SwaigFunctionResult(info)

    async def _expire_cache(self, key: str, seconds: int):
        await asyncio.sleep(seconds)
        self._cache.pop(key, None)
```

### Async Best Practices

Run independent queries concurrently with `asyncio.gather()` instead of awaiting them one at a time:

```python
# Good: Concurrent operations
@self.tool(
    "get_full_info",
    description="Get complete information",
    parameters={
        "customer_id": {"type": "string", "description": "The customer ID"}
    }
)
async def get_full_info(args, raw_data):
    customer_id = args.get("customer_id")
    # Run multiple queries concurrently
    orders, profile, preferences = await asyncio.gather(
        get_orders(customer_id),
        get_profile(customer_id),
        get_preferences(customer_id)
    )

    return SwaigFunctionResult(f"Found {len(orders)} orders")

# Bad: Sequential operations (don't do this)
async def get_full_info_slow(customer_id):
    orders = await get_orders(customer_id)  # Waits
    profile = await get_profile(customer_id)  # Then waits
    preferences = await get_preferences(customer_id)  # Then waits
```

### Memory Management

Keep the search skill's result count small, and delete large objects once a function no longer needs them:

```python
# Limit search results
self.add_skill("native_vector_search", {
    "tool_name": "search_knowledge",
    "index_file": "knowledge.swsearch",
    "count": 3  # Limit results to reduce memory
})

# Clean up large objects
@self.tool(
    "process_large_data",
    description="Process large dataset",
    parameters={
        "dataset_id": {"type": "string", "description": "The dataset ID to process"}
    }
)
async def process_large_data(args, raw_data):
    dataset_id = args.get("dataset_id")
    data = await load_large_dataset(dataset_id)
    result = process_data(data)

    # Explicitly clean up
    del data

    return SwaigFunctionResult(f"Processed {result['count']} items")
```

---

## Security Best Practices

### Input Sanitization

Strip characters a downstream query does not expect, and cap the length, before using caller-supplied text:

```python
import re

@self.tool(
    "safe_search",
    description="Search with sanitized input",
    parameters={
        "query": {"type": "string", "description": "Search query to sanitize and execute"}
    }
)
def safe_search(args, raw_data):
    query = args.get("query", "")
    # Sanitize input
    safe_query = re.sub(r'[^\w\s-]', '', query)
    safe_query = safe_query.strip()[:100]  # Limit length

    if not safe_query:
        return SwaigFunctionResult("Invalid search query")

    # Safe to use
    results = search_database(safe_query)
    return SwaigFunctionResult(f"Found {len(results)} results")
```

### Secrets Management

Read credentials from the environment, and never write them to the logs:

```python
import os
from typing import Optional

class SecureAgent(AgentBase):
    def __init__(self):
        super().__init__(name="Secure Agent", route="/")

        # Load secrets from environment
        self._api_key = os.environ.get("API_KEY")
        if not self._api_key:
            logger.warning("API_KEY not set")

        @self.tool(
            "secure_api_call",
            description="Make secure API call",
            parameters={
                "endpoint": {"type": "string", "description": "API endpoint to call"}
            }
        )
        def secure_api_call(args, raw_data):
            endpoint = args.get("endpoint")
            if not self._api_key:
                return SwaigFunctionResult("API not configured")

            # Never log secrets
            logger.info(f"Calling API endpoint: {endpoint}")
            # logger.info(f"Using key: {self._api_key}")  # NEVER DO THIS

            headers = {"Authorization": f"Bearer {self._api_key}"}
            # Make API call...
```

### Rate Limiting

Track call timestamps per user, and reject a request once it exceeds the limit for the current window:

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimitedAgent(AgentBase):
    def __init__(self):
        super().__init__(name="Rate Limited Agent", route="/")
        self._call_counts = defaultdict(list)

        @self.tool(
            "limited_function",
            description="Rate limited function",
            parameters={
                "user_id": {"type": "string", "description": "User ID for rate limiting"}
            }
        )
        def limited_function(args, raw_data):
            user_id = args.get("user_id")
            # Check rate limit (10 calls per minute)
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)

            # Clean old entries
            self._call_counts[user_id] = [
                t for t in self._call_counts[user_id]
                if t > minute_ago
            ]

            # Check limit
            if len(self._call_counts[user_id]) >= 10:
                return SwaigFunctionResult(
                    "Rate limit exceeded. Please try again later."
                )
            
            # Record call
            self._call_counts[user_id].append(now)
            
            # Process normally
            return SwaigFunctionResult("Function executed successfully")
```

---

## Summary

This lesson covered advanced SignalWire Agents features:

**Technical Skills:**
- Creating custom SWAIG functions with parameters and validation
- Proper error handling with SwaigFunctionResult
- Logging and debugging techniques
- Production deployment patterns
- Testing strategies for reliability

**Best Practices:**
- Performance optimization techniques
- Security considerations
- Monitoring and health checks
- Scalable architecture patterns

**What's Next?**

In the final lesson, you'll learn how to extend agents with custom skills, create complex conversation flows, and integrate with external services.

### Practice Exercises

Before moving on, try these exercises:

1. **Create a Calculator Agent**: Build an agent with math functions (add, subtract, multiply, divide) with proper error handling
2. **Add Caching**: Implement a caching layer for expensive operations
3. **Build Health Checks**: Create comprehensive health monitoring
4. **Security Audit**: Review an agent for security vulnerabilities

### Production Checklist

Before deploying to production:

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Authentication enabled
- [ ] Logging configured appropriately
- [ ] Error handling comprehensive
- [ ] Health checks implemented
- [ ] Monitoring set up
- [ ] Load tested
- [ ] Security reviewed
- [ ] Documentation complete

---

[Previous: Lesson 3 - Building Multi-Agent Systems](lesson3_multi_agent_systems.md) | [Tutorial Overview](README.md) | [Next: Lesson 5 - Extending Your Agents](lesson5_extending_agents.md)
