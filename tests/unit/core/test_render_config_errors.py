"""
A configuration error that stops the AI verb from being built must surface.

The render caught the error, logged it, and carried on with an empty AI
config, which then failed the schema check as "Missing required field
'prompt'". With logs suppressed, as swaig-test does by default, the real
reason (here, a step listing a tool the agent doesn't have) was lost.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from signalwire import AgentBase, FunctionResult

AGENT = '''
from signalwire import AgentBase, FunctionResult


class Agent(AgentBase):
    def __init__(self):
        super().__init__(name="ctx", route="/ctx")
        self.prompt_add_section("Role", body="You help callers.")
        ctx = self.define_contexts().add_context("default")
        ctx.add_step("identify").set_text("Ask for the account.").set_functions(["verify_account"])
        ctx.add_step("help").set_text("Help.").set_functions(["get_balance"])

    @AgentBase.tool()
    def verify_account(self, account: str) -> FunctionResult:
        """Verify the account."""
        return FunctionResult("ok")
'''


class _Agent(AgentBase):
    def __init__(self) -> None:
        super().__init__(name="ctx", route="/ctx", suppress_logs=True)
        self.prompt_add_section("Role", body="You help callers.")
        ctx = self.define_contexts().add_context("default")
        ctx.add_step("identify").set_text("Ask for the account.").set_functions(
            ["verify_account"]
        )
        # get_balance isn't registered anywhere
        ctx.add_step("help").set_text("Help.").set_functions(["get_balance"])

    @AgentBase.tool()
    def verify_account(self, account: str) -> FunctionResult:
        """Verify the account."""
        return FunctionResult("ok")


def test_render_raises_the_real_reason() -> None:
    with pytest.raises(ValueError, match="whitelists function 'get_balance'"):
        _Agent()._render_swml()


def test_swaig_test_dump_shows_the_real_reason(tmp_path: Path) -> None:
    agent_file = tmp_path / "ctx_agent.py"
    agent_file.write_text(AGENT, encoding="utf-8")
    completed = subprocess.run(  # noqa: S603  # fixed arguments: this interpreter and the CLI module
        [
            sys.executable,
            "-m",
            "signalwire.cli.swaig_test_wrapper",
            str(agent_file),
            "--dump-swml",
            "--raw",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    output = completed.stdout + completed.stderr
    assert "whitelists function 'get_balance'" in output
    assert "Missing required field 'prompt'" not in output
