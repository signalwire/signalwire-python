"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The verb methods SWMLService and SWMLBuilder install from the schema, one per
SWML verb. A method takes the verb's body positionally: an object, or the
string, number or array some verbs take (``label("start")``,
``unset(["a", "b"])``, ``cond([...])``). It also takes an object body's
options as keywords. A verb whose name is a Python keyword is also reachable
with a trailing underscore: ``return_(...)`` adds ``return``.
"""

from __future__ import annotations

import keyword
from collections.abc import Callable, Mapping
from typing import Any

# The keyword names the generated declarations give a verb's body
_BODY_KEYWORDS = ("config", "value")

#: ``add(instance, verb, body)`` adds the verb and returns add_verb's result
_VerbAdder = Callable[[Any, str, Any], bool]


def _attribute_names(verb: str) -> list[str]:
    """The attribute names a verb's method goes under: the verb's own, and
    with a trailing underscore for a Python keyword such as ``return``."""
    return [verb, f"{verb}_"] if keyword.iskeyword(verb) else [verb]


def _verb_for_attribute(name: str) -> str:
    """The verb an attribute name stands for: ``return_`` is ``return``."""
    if name.endswith("_") and keyword.iskeyword(name[:-1]):
        return name[:-1]
    return name


def _verb_body(
    verb: str, body: Any, options: dict[str, Any], properties: Mapping[str, Any]
) -> Any:
    """
    The body a verb method was given.

    Args:
        verb: The verb's name.
        body: The positional body, or None.
        options: The keyword options. A None value is left out.
        properties: The verb body's schema properties.

    Returns:
        The positional body, with the options merged in when it's an object;
        the body given as ``config=`` or ``value=``, as the generated
        declarations name it, unless the verb has an option of that name;
        or else the options as an object.

    Raises:
        TypeError: For a body that isn't an object together with options.
    """
    options = {key: value for key, value in options.items() if value is not None}
    if body is None and len(options) == 1:
        ((name, value),) = options.items()
        if name in _BODY_KEYWORDS and name not in properties:
            return dict(value) if isinstance(value, Mapping) else value
    if body is None:
        return options
    if isinstance(body, Mapping):
        return {**body, **options}
    if options:
        raise TypeError(
            f"{verb}() takes a {type(body).__name__} body or keyword options, not both"
        )
    return body


def _make_verb_method(
    verb: str,
    description: str | None,
    properties: Mapping[str, Any],
    add: _VerbAdder,
    *,
    returns_self: bool,
) -> Callable[..., Any]:
    """
    The method for one verb.

    Args:
        verb: The verb's name.
        description: The schema's description of the verb, for the docstring.
        properties: The verb body's schema properties.
        add: Adds the verb to the instance's document.
        returns_self: True for a builder's method, which returns the builder
            for chaining; False for a service's, which returns add_verb's
            result.
    """
    if verb == "sleep":

        def sleep(instance: Any, duration: Any = None, **kwargs: Any) -> Any:
            # sleep takes its duration as the body: sleep(5000), or
            # sleep(duration=5000)
            if duration is not None:
                body = duration
            elif kwargs:
                body = next(iter(kwargs.values()))
            else:
                raise TypeError("sleep() missing required argument: 'duration'")
            added = add(instance, "sleep", body)
            return instance if returns_self else added

        sleep.__doc__ = (
            "Add the sleep verb to the document.\n\n"
            "Args:\n"
            "    duration: The time to sleep in milliseconds, or -1 to sleep "
            "until the call ends"
        )
        return sleep

    def verb_method(instance: Any, body: Any = None, /, **kwargs: Any) -> Any:
        added = add(instance, verb, _verb_body(verb, body, kwargs, properties))
        return instance if returns_self else added

    doc = f"Add the {verb} verb to the document."
    if description:
        doc += f"\n\n{description}"
    if returns_self:
        doc += "\n\nReturns: Self for method chaining"
    verb_method.__doc__ = doc
    verb_method.__name__ = verb_method.__qualname__ = _attribute_names(verb)[-1]
    return verb_method
