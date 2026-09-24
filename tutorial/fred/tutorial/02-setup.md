# Lesson 2: Setting Up Your Environment

Fred needs Python and the SignalWire SDK. This lesson installs the SDK in a virtual environment, checks that it works, and sets up the project directory the rest of the tutorial uses.

## Table of Contents

1. [Prerequisites Check](#prerequisites-check)
2. [Installing the SDK](#installing-the-sdk)
3. [Verifying Installation](#verifying-installation)
4. [Understanding Dependencies](#understanding-dependencies)
5. [Project Structure](#project-structure)
6. [Environment Variables](#environment-variables)
7. [Testing Your Setup](#testing-your-setup)
8. [Common Installation Issues](#common-installation-issues)

---

## Prerequisites Check

The SDK needs Python 3.10 or later, and pip to install it.

### Required Software

Check your Python version:

```bash
python3 --version
```

The output should show version 3.10 or later:

```
Python 3.11.5
```

Check that pip is installed:

```bash
pip3 --version
```

### Virtual Environment

A virtual environment keeps Fred's packages separate from the rest of your system. Create one and activate it:

```bash
# Create a virtual environment
python3 -m venv fred-env

# Activate it
# On Linux/Mac:
source fred-env/bin/activate

# On Windows:
fred-env\Scripts\activate
```

## Installing the SDK

With the virtual environment active, install the SDK from PyPI.

### Basic Installation

One command installs the SDK:

```bash
pip install signalwire-sdk
```

This installs the core SDK and everything it requires.

### What Gets Installed

The core installation includes:

- `signalwire-sdk`: the SDK itself
- `fastapi`: the web framework behind the agent's HTTP endpoints
- `uvicorn`: the server that runs the agent
- `pydantic`: data validation
- `requests`: an HTTP client
- `structlog`: structured logging
- Other supporting libraries

## Verifying Installation

Two short scripts confirm the SDK imports and can create an agent.

### Test Import

Create a test file called `test_install.py`:

```python
#!/usr/bin/env python3
"""Test SignalWire SDK installation"""

try:
    from signalwire import AgentBase
    print("SignalWire SDK imported.")
    
    # Check version
    import signalwire
    print(f"   Version: {signalwire.__version__}")
    
except ImportError as e:
    print(f"Import failed: {e}")
    print("   Run: pip install signalwire-sdk")
```

Run the script to import the SDK and print its version:

```bash
python test_install.py
```

The output shows the installed version:

```
SignalWire SDK imported.
   Version: 3.4.3
```

### Test Basic Agent

This script creates a minimal agent without starting a server:

```python
#!/usr/bin/env python3
"""Minimal test agent"""

from signalwire import AgentBase

# Create a minimal agent
agent = AgentBase("Test Agent", route="/test")

# If this runs without errors, the installation works
print("Agent created.")
print(f"   Agent name: {agent.get_name()}")
print(f"   Agent route: /test")
```

## Understanding Dependencies

The SDK splits its dependencies into a core set and optional extras.

### Core Dependencies

These are always installed:

- `fastapi`: web framework
- `uvicorn`: ASGI server
- `pydantic`: data validation
- `PyYAML`: YAML support
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing, used by the web search skill

### Optional Dependencies

The search extras add local vector search. Fred doesn't need them:

```bash
# Only if you want the SDK's search features:
pip install "signalwire-sdk[search]"
```

## Project Structure

Fred's files live in one directory. Create it:

```bash
mkdir fred-bot
cd fred-bot
```

### Project Files

By the end of the tutorial, the directory holds these files:

```
fred-bot/
├── fred.py           # The agent
├── fred.sh           # Management script (Lesson 6)
└── requirements.txt  # Dependencies
```

### Create requirements.txt

A requirements file lets you reinstall the same dependencies later. Create a minimal one:

```txt
signalwire-sdk>=3.4.3
```

Or record everything installed in the virtual environment:

```bash
pip freeze > requirements.txt
```

## Environment Variables

The SDK reads a few optional environment variables.

### Authentication

Without these, the SDK generates a random username and password each time the agent starts:

```bash
export SWML_BASIC_AUTH_USER="fred"
export SWML_BASIC_AUTH_PASSWORD="a-long-random-password"
```

### Port

Fred listens on port 3000 by default. If something else uses that port, choose another:

```bash
export PORT=3001
```

### Proxy Configuration

When Fred runs behind a proxy or a tunnel such as ngrok, tell the SDK its public address:

```bash
export SWML_PROXY_URL_BASE="https://your-domain.com"
```

## Testing Your Setup

This script checks the Python version and the main packages in one run:

```python
#!/usr/bin/env python3
"""Setup verification script"""

import sys

def check_setup():
    """Verify environment is ready for Fred"""
    
    print("Checking Fred's environment...\n")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 10):
        print(f"OK       Python {python_version.major}.{python_version.minor}")
    else:
        print(f"MISSING  Python {python_version.major}.{python_version.minor} (need 3.10 or later)")
        return False
    
    # Check imports
    try:
        import signalwire
        print("OK       SignalWire SDK")
    except ImportError:
        print("MISSING  SignalWire SDK")
        return False
    
    try:
        import fastapi
        print("OK       FastAPI")
    except ImportError:
        print("MISSING  FastAPI")
        return False
    
    try:
        import uvicorn
        print("OK       Uvicorn")
    except ImportError:
        print("MISSING  Uvicorn")
        return False
    
    print("\nThe environment is ready to build Fred.")
    return True

if __name__ == "__main__":
    if not check_setup():
        print("\nInstall the missing dependencies:")
        print("   pip install signalwire-sdk")
        sys.exit(1)
```

## Common Installation Issues

Most installation problems have one of three causes.

### Issue: Permission Denied

Installing into the system Python needs administrator rights. Use a virtual environment, as in [Virtual Environment](#virtual-environment), or install for your user only:

```bash
pip install --user signalwire-sdk
```

Avoid `sudo pip install`, which can conflict with packages your operating system manages.

### Issue: pip Not Found

Install pip for your Python:

```bash
python3 -m ensurepip

# Or on Ubuntu/Debian
sudo apt-get install python3-pip
```

### Issue: SSL Certificate Errors

Update the certificate bundle pip uses:

```bash
pip install --upgrade certifi
```

If your network inspects TLS traffic, point pip at your organization's CA certificate with `pip install --cert /path/to/ca.pem signalwire-sdk`.

## Next Steps

Before you continue, check that:

- Python 3.10 or later is installed
- The SignalWire SDK is installed
- The import test passes
- The project directory exists

Next, create Fred's agent class. Continue with [Lesson 3: Creating Fred's Basic Structure](03-basic-agent.md).

---

[Previous: Introduction](01-introduction.md) | [Overview](README.md) | [Next: Basic Agent](03-basic-agent.md)
