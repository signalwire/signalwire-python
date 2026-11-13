"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Testing helpers: a simulated call, and recorded tool requests to replay.

``CallSimulator`` runs an agent's tools through a call without the platform
or a model, checking each call as the platform would: the step's function
list, the semantic gates (from a callback), and the result's actions.
``RequestRecorder`` records real tool requests for ``CallSimulator.replay``.
"""

from signalwire.testing.call_simulator import (
    CallSimulator,
    RequestRecorder,
    SimulatedCall,
)

__all__ = ["CallSimulator", "RequestRecorder", "SimulatedCall"]
