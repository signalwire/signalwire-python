# Migrating to SignalWire SDK 2.0

## Package Rename

```bash
# Before
pip install signalwire-sdk

# After
pip install signalwire-sdk
```

## Import Changes

```python
# Before
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult
from signalwire_agents.rest import SignalWireClient

# After
from signalwire import AgentBase
from signalwire.core.function_result import FunctionResult
from signalwire.rest import RestClient
```

## Class Renames

| Before | After |
|--------|-------|
| `SwaigFunctionResult` | `FunctionResult` |
| `SignalWireClient` | `RestClient` |

## Quick Migration

Find and replace in your project:
```bash
# In all .py files:
sed -i 's/signalwire_agents/signalwire/g' **/*.py
sed -i 's/SwaigFunctionResult/FunctionResult/g' **/*.py
sed -i 's/SignalWireClient/RestClient/g' **/*.py
```

## What Didn't Change

- All method names (set_prompt_text, define_tool, add_skill, etc.)
- All parameter shapes
- SWML output format
- RELAY protocol
- REST API paths
- Skills, prefabs, contexts, DataMap -- all the same
