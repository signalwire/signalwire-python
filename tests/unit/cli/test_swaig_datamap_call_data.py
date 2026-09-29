"""
swaig-test passes --custom-data to a DataMap tool as the call's data.

The DataMap simulator takes the call data the platform would add, such as
global_data, but swaig-test didn't pass it, so a DataMap tool that read
${global_data.x} always got an empty value.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

AGENT = textwrap.dedent('''
    from signalwire import AgentBase
    from signalwire.core.data_map import DataMap
    from signalwire.core.function_result import FunctionResult

    agent = AgentBase(name="tenant", route="/agent")
    agent.register_swaig_function(
        DataMap("which_tenant")
        .description("Say which tenant this is")
        .parameter("topic", "string", "Anything")
        .expression("${args.topic}", r".*", FunctionResult("Tenant ${global_data.tenant}"))
        .to_swaig_function()
    )
''')


def _run(tmp_path: Path, *extra: str, agent: str = AGENT) -> str:
    agent_file = tmp_path / "tenant_agent.py"
    agent_file.write_text(agent, encoding="utf-8")
    completed = subprocess.run(  # noqa: S603  # fixed arguments: this interpreter and the CLI module
        [sys.executable, "-m", "signalwire.cli.swaig_test_wrapper", str(agent_file), *extra,
         "--exec", "which_tenant", "--topic", "hours"],
        capture_output=True, text=True, timeout=120, check=False,
    )
    return completed.stdout + completed.stderr


def test_custom_data_reaches_the_datamap_tool(tmp_path: Path) -> None:
    output = _run(tmp_path, "--custom-data", '{"global_data": {"tenant": "acme"}}')
    assert "Tenant acme" in output


def test_without_custom_data_the_value_is_empty(tmp_path: Path) -> None:
    output = _run(tmp_path)
    assert "Tenant acme" not in output
    assert "Tenant " in output


def test_without_custom_data_the_agents_global_data_applies(tmp_path: Path) -> None:
    # On a call, global_data starts as the agent's
    agent = AGENT + 'agent.set_global_data({"tenant": "house"})\n'
    assert "Tenant house" in _run(tmp_path, agent=agent)
    assert "Tenant acme" in _run(
        tmp_path, "--custom-data", '{"global_data": {"tenant": "acme"}}', agent=agent)
