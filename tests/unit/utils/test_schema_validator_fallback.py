"""
The SDK loads and validates without jsonschema-rs.

jsonschema-rs has no WebAssembly build, so on Pyodide (Cloudflare Workers)
it can't be installed, and schema_utils imported it unconditionally: the SDK
didn't load at all. It now falls back to jsonschema when that's installed,
and to the lightweight checks (verb names and required fields) when neither
is. Each case runs in its own interpreter with the missing libraries
blocked, so this test's imports don't change the module other tests use.
"""

import json
import subprocess
import sys
import textwrap

import pytest


def _run(blocked: list[str]) -> dict[str, object]:
    script = textwrap.dedent(f"""
        import json, sys
        for name in {blocked!r}:
            sys.modules[name] = None  # import raises ImportError
        from signalwire import AgentBase
        from signalwire.utils import schema_utils
        from signalwire.utils.schema_utils import SchemaUtils

        agent = AgentBase(name="w", route="/", basic_auth=("u", "p"), suppress_logs=True)
        agent.prompt_add_section("Role", body="Help the caller.")
        document = json.loads(agent._render_swml())
        utils = SchemaUtils()
        valid = utils.validate_document(document)[0] if utils.full_validation_available else None
        bad = {{"version": "1.0.0", "sections": {{"main": [{{"play": {{"url": 5}}}}]}}}}
        invalid = utils.validate_document(bad)[0] if utils.full_validation_available else None
        print(json.dumps({{
            "rs": schema_utils.jsonschema_rs is not None,
            "full": utils.full_validation_available,
            "rendered": any("ai" in verb for verb in document["sections"]["main"]),
            "valid": valid,
            "invalid": invalid,
            "unknown_verb": utils.validate_verb("no_such_verb", {{}})[0],
        }}))
    """)
    completed = subprocess.run(  # noqa: S603  # fixed arguments: this interpreter and a fixed script
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=120, check=False)
    assert completed.returncode == 0, completed.stderr[-2000:]
    result: dict[str, object] = json.loads(completed.stdout.strip().splitlines()[-1])
    return result


def test_without_jsonschema_rs_it_validates_with_jsonschema() -> None:
    pytest.importorskip("jsonschema")
    result = _run(["jsonschema_rs"])
    assert result == {"rs": False, "full": True, "rendered": True, "valid": True,
                      "invalid": False, "unknown_verb": False}


def test_without_either_it_loads_and_checks_verb_names() -> None:
    result = _run(["jsonschema_rs", "jsonschema"])
    assert result == {"rs": False, "full": False, "rendered": True, "valid": None,
                      "invalid": None, "unknown_verb": False}


def test_with_jsonschema_rs_nothing_changes() -> None:
    result = _run([])
    assert result == {"rs": True, "full": True, "rendered": True, "valid": True,
                      "invalid": False, "unknown_verb": False}
