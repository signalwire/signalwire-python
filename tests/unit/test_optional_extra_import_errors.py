"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Optional-extra import guards.

Modules that are only usable when an optional extra is installed must fail with
a message naming the ``pip install signalwire-sdk[<extra>]`` command that
supplies them -- never with a bare ``ModuleNotFoundError: No module named
'flask'``, which tells the user nothing about how to fix it.

These tests simulate the third-party package being absent (they do NOT require
it to actually be uninstalled), so they are meaningful on a developer box whose
venv happens to have every extra installed.
"""

import builtins
import importlib
import sys
from collections.abc import Iterator
from contextlib import contextmanager

import pytest


@contextmanager
def hidden_modules(*prefixes: str) -> Iterator[None]:
    """Make ``import <prefix>`` (and any submodule) raise ModuleNotFoundError.

    Both the already-imported entries in ``sys.modules`` and any fresh import
    attempt are blocked, so a module re-imported inside the block sees the
    packages as genuinely absent.
    """

    def blocked(name: str) -> bool:
        return any(name == p or name.startswith(p + ".") for p in prefixes)

    saved = {k: v for k, v in sys.modules.items() if blocked(k)}
    for k in saved:
        del sys.modules[k]

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # type: ignore[no-untyped-def]
        if blocked(name):
            raise ModuleNotFoundError(f"No module named {name.split('.')[0]!r}")
        return real_import(name, globals, locals, fromlist, level)

    builtins.__import__ = fake_import
    try:
        yield
    finally:
        builtins.__import__ = real_import
        sys.modules.update(saved)


def reimport(module_name: str) -> None:
    """Force a fresh top-level execution of ``module_name``."""
    sys.modules.pop(module_name, None)
    importlib.import_module(module_name)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("module_name", "hidden", "extra"),
    [
        (
            "signalwire.mcp_gateway.gateway_service",
            ("flask", "flask_limiter", "werkzeug"),
            "mcp-gateway",
        ),
        ("signalwire.search.query_processor", ("nltk",), "search"),
    ],
)
def test_missing_extra_names_the_pip_install_command(
    module_name: str, hidden: tuple[str, ...], extra: str
) -> None:
    """The raised error must tell the user which extra to install."""
    original = sys.modules.get(module_name)
    try:
        with hidden_modules(*hidden), pytest.raises(ImportError) as excinfo:
            reimport(module_name)
        message = str(excinfo.value)
        assert f"signalwire-sdk[{extra}]" in message, (
            f"{module_name} raised {message!r}, which does not name the "
            f"'{extra}' extra -- the user is left with a bare "
            f"ModuleNotFoundError and no way to know the fix."
        )
        assert "pip install" in message
    finally:
        sys.modules.pop(module_name, None)
        if original is not None:
            sys.modules[module_name] = original


@pytest.mark.unit
def test_guard_is_transparent_when_the_extra_is_installed() -> None:
    """With the extra present the module imports normally (no false failure)."""
    pytest.importorskip("flask")
    pytest.importorskip("flask_limiter")
    reimport("signalwire.mcp_gateway.gateway_service")
