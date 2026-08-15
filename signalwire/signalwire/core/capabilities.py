#!/usr/bin/env python3
"""
Copyright (c) 2026 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Reading what a client says it can do.

A browser client -- the SignalWire address widget, or anything speaking the
same convention -- declares its rendering capabilities in the user variables it
sends at dial time::

    {
      "vars": {
        "userVariables": {
          "capabilities": {
            "display_content": true,
            "transcript": true,
            "chat_handoff": false,
            ...
          },
          "metadata": {"page": {...}, "client": {...}, "widget": {...}}
        }
      }
    }

Both ends of that wire are SignalWire's, which is the only reason it belongs in
the SDK: no single application can standardize a convention between two
products it does not own.

**These are declarations of what the client can RENDER, not grants of
authority.** Treat them as hints for deciding what to offer -- whether to push
code to a screen, whether to advertise a text-handoff tool -- never as
permission to do anything privileged. A caller controls its own user variables.

**Absence means no.** Every function here resolves errors and missing data to
"not declared", because offering a caller something they cannot reach is worse
than never mentioning it: a PSTN caller has no browser, and an agent that
offers to "put that on your screen" to someone on a phone has simply lied.

Deliberately NOT provided:

* An enum of known capability names. The producer side evolves by adding
  booleans, and an SDK release per new capability would invert that -- a client
  must be able to declare something this SDK has never heard of and have an
  application act on it today.
* Any wiring of capabilities to tools. Deciding what a capability *implies*
  behaviourally is application policy, and applications write it in a few lines.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "declared_capabilities",
    "has_capability",
    "user_variables",
]


def user_variables(body_params: Any) -> dict[str, Any]:
    """Return the user variables from a SWML request body.

    They are nested two levels down (``vars.userVariables``), which is easy to
    get subtly wrong and easy to get wrong silently -- a missing level yields
    an empty dict and every downstream check quietly reports "not declared".

    Args:
        body_params: The SWML request body.

    Returns:
        The user variables, or ``{}``.
    """
    try:
        variables = (body_params or {}).get("vars", {}).get("userVariables", {})
    except (AttributeError, TypeError):
        return {}
    return variables if isinstance(variables, dict) else {}


def declared_capabilities(body_params: Any) -> frozenset[str]:
    """Return the capability names the client declared as truthy.

    Accepts either a full SWML request body or an already-extracted user
    variables dict, so it is usable from a dynamic-config callback and from a
    SWAIG handler without the caller having to remember which one it holds.

    Args:
        body_params: SWML request body, or a user variables dict.

    Returns:
        Names whose declared value is truthy. Empty when nothing was declared,
        the payload was malformed, or the client is not a browser at all.

    Example:
        caps = declared_capabilities(body_params)
        if "display_content" in caps:
            agent.prompt_add_section("Screen", body=...)
    """
    variables = user_variables(body_params)
    if not variables and isinstance(body_params, dict):
        # Already-extracted user variables were passed directly.
        variables = body_params

    capabilities = variables.get("capabilities")
    if not isinstance(capabilities, dict):
        return frozenset()
    return frozenset(
        name for name, value in capabilities.items() if value and isinstance(name, str)
    )


def has_capability(body_params: Any, name: str) -> bool:
    """Whether the client declared ``name``.

    Args:
        body_params: SWML request body, or a user variables dict.
        name: Capability name, e.g. ``"display_content"``.

    Returns:
        True only when explicitly declared truthy.
    """
    return name in declared_capabilities(body_params)
