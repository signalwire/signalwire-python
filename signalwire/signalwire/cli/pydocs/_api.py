"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

``sw-pydocs api``: signatures, docstrings and members, read from the installed code.
"""

from __future__ import annotations

import difflib
import importlib
import inspect
import re
from dataclasses import dataclass
from types import ModuleType
from typing import Any

# Where a bare name such as ``AgentBase`` or ``hangup`` is looked up. The
# search package isn't here: importing it loads the model stack, so its names
# need their module, as in ``signalwire.search.SearchEngine``.
_MODULES = (
    "signalwire",
    "signalwire.relay",
    "signalwire.rest",
    "signalwire.prefabs",
    "signalwire.livewire",
)
_CLASSES = (
    "signalwire.AgentBase",
    "signalwire.FunctionResult",
    "signalwire.DataMap",
    "signalwire.SWMLService",
    "signalwire.ContextBuilder",
    "signalwire.Context",
    "signalwire.Step",
    "signalwire.AgentServer",
    "signalwire.relay.RelayClient",
    "signalwire.relay.Call",
    "signalwire.rest.RestClient",
    "signalwire.core.skill_base.SkillBase",
)

# Noise removed from rendered signatures
_ANNOTATION_NOISE = re.compile(
    r"\b(?:typing|collections\.abc|signalwire(?:\.\w+)*)\.(?=[A-Za-z_])"
)


@dataclass(frozen=True)
class Found:
    """A resolved name and the object it refers to."""

    name: str
    obj: Any


def _import(name: str) -> ModuleType | None:
    """Import module ``name``, or return ``None`` if it cannot be imported."""
    try:
        return importlib.import_module(name)
    except ImportError:
        return None


def _lookup_dotted(name: str) -> Found | None:
    """Resolve a dotted name: the longest importable module, then attributes."""
    parts = name.split(".")
    for split in range(len(parts), 0, -1):
        module = _import(".".join(parts[:split]))
        if module is None:
            continue
        obj: Any = module
        try:
            for attr in parts[split:]:
                obj = getattr(obj, attr)
        except AttributeError:
            return None
        return Found(name, obj)
    return None


def _public(names: list[str]) -> list[str]:
    """Return the names that do not start with an underscore."""
    return [n for n in names if not n.startswith("_")]


def _module_names(module: ModuleType) -> list[str]:
    """Return a module's ``__all__``, or its public names when it has none."""
    exported = getattr(module, "__all__", None)
    return list(exported) if exported else _public(dir(module))


def resolve(name: str) -> list[Found]:
    """Everything ``name`` could refer to, most specific first."""
    wanted = name.strip()
    if not wanted:
        return []
    if "." in wanted:
        candidates = (
            [wanted]
            if wanted.startswith("signalwire")
            else [f"signalwire.{wanted}", wanted]
        )
        for candidate in candidates:
            found = _lookup_dotted(candidate)
            if found is not None:
                return [found]
        return []
    results: list[Found] = []
    seen: set[int] = set()
    for module_name in _MODULES:
        module = _import(module_name)
        if module is None or wanted not in _module_names(module):
            continue
        obj = getattr(module, wanted, None)
        if obj is not None and id(obj) not in seen:
            seen.add(id(obj))
            results.append(Found(f"{module_name}.{wanted}", obj))
    for class_name in _CLASSES:
        found = _lookup_dotted(class_name)
        if found is None:
            continue
        member = inspect.getattr_static(found.obj, wanted, None)
        if member is not None and not wanted.startswith("_"):
            results.append(Found(f"{class_name}.{wanted}", getattr(found.obj, wanted)))
    return results


def suggestions(name: str) -> list[str]:
    """Known names that look like ``name``."""
    pool: set[str] = set()
    for module_name in _MODULES:
        module = _import(module_name)
        if module is not None:
            pool.update(_module_names(module))
    for class_name in _CLASSES:
        found = _lookup_dotted(class_name)
        if found is not None:
            pool.update(_public(dir(found.obj)))
    last = name.rsplit(".", 1)[-1]
    return difflib.get_close_matches(last, sorted(pool), n=8, cutoff=0.6)


def _clean(text: str) -> str:
    """Drop the typing, collections.abc and signalwire prefixes from ``text``."""
    return _ANNOTATION_NOISE.sub("", text)


def signature(obj: Any, drop_self: bool = False) -> str:
    """``obj``'s call signature, with long module prefixes removed, or ``""``."""
    try:
        sig = inspect.signature(obj)
    except (TypeError, ValueError):
        return ""
    params = list(sig.parameters.values())
    if drop_self and params and params[0].name in ("self", "cls"):
        sig = sig.replace(parameters=params[1:])
    return _clean(str(sig))


def summary(obj: Any) -> str:
    """The first line of ``obj``'s docstring."""
    doc = inspect.getdoc(obj) or ""
    for line in doc.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _source(obj: Any) -> str:
    """Return ``obj``'s source ``path:line``, or ``""`` if it has no source file."""
    target: Any = obj.fget if isinstance(obj, property) else obj
    if target is None:
        return ""
    try:
        path = inspect.getsourcefile(target)
        _, line = inspect.getsourcelines(target)
    except (TypeError, OSError):
        return ""
    return f"{path}:{line}" if path else ""


def _kind(obj: Any) -> str:
    """Name ``obj``'s kind: module, class, property, function or its type."""
    if inspect.ismodule(obj):
        return "module"
    if inspect.isclass(obj):
        return "class"
    if isinstance(obj, property):
        return "property"
    if inspect.isroutine(obj):
        return "function"
    return type(obj).__name__


def _class_members(cls: type) -> list[tuple[str, list[tuple[str, Any]]]]:
    """Public methods and properties, grouped by the class that defines them."""
    groups: dict[str, list[tuple[str, Any]]] = {}
    order: list[str] = []
    for name in sorted(_public(dir(cls))):
        for klass in inspect.getmro(cls):
            if klass is object or name not in vars(klass):
                continue
            member = vars(klass)[name]
            if isinstance(member, (staticmethod, classmethod)):
                member = member.__func__
            if not (inspect.isroutine(member) or isinstance(member, property)):
                break
            if klass.__name__ not in groups:
                groups[klass.__name__] = []
                order.append(klass.__name__)
            groups[klass.__name__].append((name, member))
            break
    return [(owner, groups[owner]) for owner in order]


def render(found: Found) -> str:
    """Markdown for one resolved name."""
    obj = found.obj
    kind = _kind(obj)
    out = [f"# {kind} {found.name}", ""]
    source = _source(obj)
    if source:
        out += [f"Source: {source}", ""]
    if kind in ("class", "function"):
        sig = signature(obj, drop_self=True)
        if sig:
            label = found.name.rsplit(".", 1)[-1]
            out += ["```python", f"{label}{sig}", "```", ""]
    doc = inspect.getdoc(obj)
    if doc:
        out += [doc, ""]
    if kind == "class":
        members = _class_members(obj)
        count = sum(len(group) for _, group in members)
        if count:
            out += [
                f"## Members ({count})",
                "",
                f"Grouped by the class that defines them. `sw-pydocs api {found.name}.<name>` shows one.",
                "",
            ]
            for owner, group in members:
                out += [f"### {owner}", ""]
                for name, member in group:
                    if isinstance(member, property):
                        line = f"- `{name}` (property)"
                    else:
                        line = f"- `{name}{signature(member, drop_self=True)}`"
                    text = summary(member)
                    out.append(f"{line}: {text}" if text else line)
                out.append("")
    elif kind == "module":
        names = _module_names(obj)
        if names:
            out += ["## Contents", ""]
            for name in names:
                member = getattr(obj, name, None)
                if member is None:
                    continue
                text = (
                    summary(member)
                    if inspect.isclass(member) or inspect.isroutine(member)
                    else ""
                )
                label = f"- `{name}` ({_kind(member)})"
                out.append(f"{label}: {text}" if text else label)
            out.append("")
    elif kind not in ("function", "property"):
        out += ["```python", _clean(repr(obj))[:400], "```", ""]
    return "\n".join(out).rstrip() + "\n"
