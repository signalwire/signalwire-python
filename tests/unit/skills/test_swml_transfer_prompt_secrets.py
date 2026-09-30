"""
swml_transfer shows the model its destinations without their credentials.

A transfer to another agent's URL carries that agent's basic-auth
credentials (https://user:password@host/route), and the prompt listed each
destination in full, so the model could repeat the password to a caller. The
transfer itself still uses the full URL.
"""

import json
from typing import Any

import pytest

from signalwire import AgentBase


def _ai(agent: AgentBase) -> dict[str, Any]:
    main = json.loads(agent._render_swml())["sections"]["main"]
    return next(verb["ai"] for verb in main if "ai" in verb)


def _agent(url: str) -> AgentBase:
    agent = AgentBase(
        name="triage", route="/", basic_auth=("u", "p"), suppress_logs=True
    )
    # POM sections, so the skill's prompt section is rendered
    agent.prompt_add_section("Role", body="Route the caller.")
    agent.add_skill("swml_transfer", {"transfers": {"/sales/i": {"url": url}}})
    return agent


@pytest.mark.parametrize(
    "url",
    [
        "https://agent:s3cret-pass@pc.example.com/sales",
        "https://agent:s3cret@pass@pc.example.com/sales",  # an unencoded "@" in the password
        "HTTPS://agent:s3cret-pass@pc.example.com/sales",
    ],
)
def test_the_prompt_shows_the_destination_without_its_credentials(url: str) -> None:
    ai = _ai(_agent(url))
    model_facing = json.dumps(
        {
            "prompt": ai["prompt"],
            "functions": [
                {
                    "description": function["description"],
                    "parameters": function["parameters"],
                }
                for function in ai["SWAIG"]["functions"]
            ],
        }
    )
    assert "s3cret" not in model_facing
    assert "pc.example.com/sales" in model_facing


def test_the_transfer_still_uses_the_full_url() -> None:
    url = "https://agent:s3cret-pass@pc.example.com/sales"
    ai = _ai(_agent(url))
    transfer = next(
        f for f in ai["SWAIG"]["functions"] if f["function"] == "transfer_call"
    )
    assert url in json.dumps(transfer["data_map"])


def test_a_destination_without_credentials_is_shown_as_is() -> None:
    ai = _ai(_agent("https://pc.example.com/sales?team=a@b"))
    assert "pc.example.com/sales?team=a@b" in json.dumps(ai["prompt"])
