"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
LiveWire plugin stubs.

These classes mirror popular livekit-agents plugin constructors so that
existing code compiles unchanged.  On SignalWire the platform handles all
STT/TTS/LLM/VAD infrastructure -- these are no-ops that log once.
"""

import logging
import threading
from typing import Any, Dict

_logger = logging.getLogger("LiveWire")

# Reuse a simple once-tracker scoped to this module
_lock = threading.Lock()
_logged: Dict[str, bool] = {}


def _log_once(key: str, message: str):
    global _logged
    with _lock:
        if _logged.get(key):
            return
        _logged[key] = True
        _logger.info("[LiveWire] %s", message)


def _reset_logged():
    """Reset the per-module noop tracker (for testing)."""
    global _logged
    with _lock:
        _logged.clear()


# ---------------------------------------------------------------------------
# STT plugins
# ---------------------------------------------------------------------------

class DeepgramSTT:
    """Stub for livekit Deepgram STT plugin."""

    def __init__(self, **kwargs: Any):
        self._kwargs = kwargs
        _log_once(
            "deepgram_stt",
            "DeepgramSTT(): SignalWire's control plane handles speech "
            "recognition at scale -- Deepgram plugin is a no-op",
        )


# ---------------------------------------------------------------------------
# LLM plugins
# ---------------------------------------------------------------------------

class OpenAILLM:
    """Stub for livekit OpenAI LLM plugin."""

    def __init__(self, **kwargs: Any):
        self._kwargs = kwargs
        self.model = kwargs.get("model", "")
        _log_once(
            "openai_llm",
            "OpenAILLM(): model selection is mapped to SignalWire AI "
            "params -- OpenAI plugin wrapper is a no-op",
        )


# ---------------------------------------------------------------------------
# TTS plugins
# ---------------------------------------------------------------------------

class CartesiaTTS:
    """Stub for livekit Cartesia TTS plugin."""

    def __init__(self, **kwargs: Any):
        self._kwargs = kwargs
        _log_once(
            "cartesia_tts",
            "CartesiaTTS(): SignalWire's control plane handles "
            "text-to-speech at scale -- Cartesia plugin is a no-op",
        )


class ElevenLabsTTS:
    """Stub for livekit ElevenLabs TTS plugin."""

    def __init__(self, **kwargs: Any):
        self._kwargs = kwargs
        _log_once(
            "elevenlabs_tts",
            "ElevenLabsTTS(): SignalWire's control plane handles "
            "text-to-speech at scale -- ElevenLabs plugin is a no-op",
        )


# ---------------------------------------------------------------------------
# VAD plugins
# ---------------------------------------------------------------------------

class SileroVAD:
    """Stub for livekit Silero VAD plugin."""

    def __init__(self, **kwargs: Any):
        self._kwargs = kwargs
        _log_once(
            "silero_vad",
            "SileroVAD(): SignalWire's control plane handles voice "
            "activity detection at scale automatically -- Silero VAD is a no-op",
        )

    @classmethod
    def load(cls):
        """Mirrors the SileroVAD.load() factory."""
        return cls()
