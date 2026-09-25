"""
Constructor arguments take precedence over an agent's config file (B17).

The documented order is constructor parameters, then the config file,
then environment variables, then defaults. AgentBase let the config file's
service.name replace the name passed to it, and let its route and host
replace a route or host passed with the default value ("/" or "0.0.0.0").
"""

import json
from pathlib import Path

import pytest

from signalwire import AgentBase


@pytest.fixture
def config_file(tmp_path: Path) -> str:
    path = tmp_path / "agent.json"
    path.write_text(
        json.dumps(
            {
                "service": {
                    "name": "from-config",
                    "route": "/from-config",
                    "host": "127.0.0.1",
                }
            }
        )
    )
    return str(path)


def test_explicit_arguments_win_even_at_their_default_values(config_file: str) -> None:
    agent = AgentBase(
        name="explicit", route="/", host="0.0.0.0", config_file=config_file
    )
    assert agent.name == "explicit"
    assert agent.route in ("", "/")
    assert agent.host == "0.0.0.0"


def test_config_fills_in_omitted_arguments(config_file: str) -> None:
    agent = AgentBase(name="explicit", config_file=config_file)
    assert agent.name == "explicit"
    assert agent.route == "/from-config"
    assert agent.host == "127.0.0.1"


def test_mixed(config_file: str) -> None:
    agent = AgentBase(name="explicit", route="/mine", config_file=config_file)
    assert agent.route == "/mine"
    assert agent.host == "127.0.0.1"


def test_subclass_passing_arguments_positionally(config_file: str) -> None:
    class MyAgent(AgentBase):
        def __init__(self) -> None:
            super().__init__("positional", "/", config_file=config_file)

    agent = MyAgent()
    assert agent.name == "positional"
    assert agent.route in ("", "/")
    assert agent.host == "127.0.0.1"


def test_signature_is_unchanged() -> None:
    import inspect

    params = inspect.signature(AgentBase.__init__).parameters
    assert params["route"].default == "/"
    assert params["host"].default == "0.0.0.0"
