"""
swaig-test and an agent's per-call configuration callback.

--dump-swml renders as the server does, which applies the callback to a copy
of the agent for the request. swaig-test also applied it to the agent first,
so everything the callback added appeared twice in the dump.
"""

import json
import subprocess
import sys
from pathlib import Path

AGENT = """
from signalwire import AgentBase, FunctionResult


class DynAgent(AgentBase):
    def __init__(self):
        super().__init__(name="dyn", route="/dyn")
        self.prompt_add_section("Role", body="You help callers.")
        self.set_dynamic_config_callback(self.per_call)

    def per_call(self, query_params, body_params, headers, agent):
        agent.prompt_add_section("Today", body="Per-call section.")
        agent.define_tool(
            name="per_call_tool",
            description="A tool added for the call",
            parameters={"type": "object", "properties": {}},
            handler=lambda args, raw_data: FunctionResult("ok"),
        )
"""


def _swaig_test(agent_file: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603  # fixed arguments: this interpreter and the CLI module
        [
            sys.executable,
            "-m",
            "signalwire.cli.swaig_test_wrapper",
            str(agent_file),
            *args,
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_dump_swml_applies_the_callback_once(tmp_path: Path) -> None:
    agent_file = tmp_path / "dyn_agent.py"
    agent_file.write_text(AGENT, encoding="utf-8")
    completed = _swaig_test(agent_file, "--dump-swml", "--raw")
    document = json.loads(completed.stdout)
    ai = next(verb["ai"] for verb in document["sections"]["main"] if "ai" in verb)
    assert [section["title"] for section in ai["prompt"]["pom"]] == ["Role", "Today"]
    functions = [f["function"] for f in ai["SWAIG"]["functions"]]
    assert functions.count("per_call_tool") == 1


def test_list_tools_still_shows_tools_the_callback_adds(tmp_path: Path) -> None:
    agent_file = tmp_path / "dyn_agent.py"
    agent_file.write_text(AGENT, encoding="utf-8")
    completed = _swaig_test(agent_file, "--list-tools")
    assert "per_call_tool" in completed.stdout


def test_exec_runs_a_tool_the_callback_adds(tmp_path: Path) -> None:
    agent_file = tmp_path / "dyn_agent.py"
    agent_file.write_text(AGENT, encoding="utf-8")
    completed = _swaig_test(agent_file, "--exec", "per_call_tool")
    assert "ok" in completed.stdout


def test_dump_swml_of_a_static_agent(tmp_path: Path) -> None:
    agent_file = tmp_path / "static_agent.py"
    agent_file.write_text(
        "from signalwire import AgentBase\n\n\n"
        "class StaticAgent(AgentBase):\n"
        "    def __init__(self):\n"
        "        super().__init__(name='static', route='/static')\n"
        "        self.prompt_add_section('Role', body='You help callers.')\n",
        encoding="utf-8",
    )
    document = json.loads(_swaig_test(agent_file, "--dump-swml", "--raw").stdout)
    ai = next(verb["ai"] for verb in document["sections"]["main"] if "ai" in verb)
    assert [section["title"] for section in ai["prompt"]["pom"]] == ["Role"]


def test_dump_swml_of_a_plain_swml_service(tmp_path: Path) -> None:
    # An SWMLService, which has no AI verb; the dump failed with an AttributeError
    service_file = tmp_path / "svc.py"
    service_file.write_text(
        "from signalwire import SWMLService\n\n"
        "service = SWMLService(name='svc', route='/svc')\n"
        "service.add_verb('answer', {})\n"
        "service.add_verb('hangup', {})\n",
        encoding="utf-8",
    )
    document = json.loads(_swaig_test(service_file, "--dump-swml", "--raw").stdout)
    assert document["sections"]["main"] == [{"answer": {}}, {"hangup": {}}]
