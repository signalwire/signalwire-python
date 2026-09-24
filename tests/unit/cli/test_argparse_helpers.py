"""
swaig-test's warnings for function arguments the function doesn't declare.

Everything after --exec <function> goes to the function, so a misplaced or
mistyped swaig-test option reached it silently (B20). The arguments still
go to the function, since a parameter can share an option's name, but
swaig-test now says so.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

from signalwire.cli.core.argparse_helpers import (
    parse_function_arguments,
    undeclared_argument_warnings,
)

SCHEMA = {"parameters": {"type": "object", "properties": {"location": {"type": "string"}, "verbose": {"type": "boolean"}}}}
CLI = {"--verbose", "--custom-data", "--raw"}


def test_declared_arguments_do_not_warn() -> None:
    args = parse_function_arguments(["--location", "Paris", "--verbose"], SCHEMA)
    assert undeclared_argument_warnings(args, SCHEMA, CLI) == []


def test_misplaced_swaig_test_option_is_named() -> None:
    args = parse_function_arguments(["--location", "Paris", "--custom-data", "{}"], SCHEMA)
    [warning] = undeclared_argument_warnings(args, SCHEMA, CLI)
    assert "--custom-data" in warning
    assert "before --exec" in warning
    assert args["custom_data"] == "{}"  # still passed to the function


def test_unknown_argument_warns() -> None:
    args = parse_function_arguments(["--units", "metric"], SCHEMA)
    [warning] = undeclared_argument_warnings(args, SCHEMA, CLI)
    assert "--units" in warning
    assert "before --exec" not in warning


def test_swaig_test_prints_the_warning(tmp_path: Path) -> None:
    agent_file = tmp_path / "agent.py"
    agent_file.write_text(textwrap.dedent('''
        from signalwire import AgentBase
        from signalwire.core.function_result import FunctionResult

        agent = AgentBase(name="warn", route="/")
        agent.define_tool(
            name="lookup",
            description="Lookup",
            parameters={"city": {"type": "string", "description": "City"}},
            handler=lambda args, raw: FunctionResult("ok " + args.get("city", "")),
        )
    '''))
    completed = subprocess.run(
        [sys.executable, "-m", "signalwire.cli.swaig_test_wrapper", str(agent_file),
         "--exec", "lookup", "--city", "Oslo", "--custom-data", "{}"],
        capture_output=True, text=True, timeout=120,
    )
    assert "--custom-data isn't a parameter of this function" in completed.stderr
    assert "ok Oslo" in completed.stdout
