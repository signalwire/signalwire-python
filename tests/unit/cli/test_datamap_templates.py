"""
swaig-test's DataMap simulator expands templates as the platform does.

- A webhook's JSON object response is read from the root of the template
  data: ${current.temp_f}, not ${response.current.temp_f}. The simulator
  filed it under response, so a template that works in production failed
  in simulation, and one that fails in production passed.
- Prefix helpers transform a value left to right: ${lc:enc:args.city}
  lowercases and then URL-encodes the city. The simulator didn't know them,
  so the weather skill's URL came out as <MISSING:lc:enc:args.location>.
- Nested templates expand from the inside out.
"""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from signalwire.cli.execution.datamap_exec import execute_datamap_function, simple_template_expand

DATA: dict[str, Any] = {
    "args": {"city": "New York", "target": "Sales"},
    "meta_data": {"table": {"sales": "+15551234567"}},
    "array": [{"joke": "ha"}],
}


@pytest.mark.parametrize(
    ("template", "expected"),
    [
        ("${args.city}", "New York"),
        ("%{args.city}", "New York"),
        ("${lc:args.city}", "new york"),
        ("${enc:args.city}", "New%20York"),
        ("${enc:url:args.city}", "New%20York"),
        ("${lc:enc:args.city}", "new%20york"),
        ("${meta_data.table.${lc:args.target}}", "+15551234567"),
        ("${array[0].joke}", "ha"),
        ("${args.missing}", "<MISSING:args.missing>"),
        ("@{expr 1 + 2}", "@{expr 1 + 2}"),
    ],
)
def test_template_expansion(template: str, expected: str) -> None:
    assert simple_template_expand(template, DATA) == expected


def _run(output: str, payload: Any, url: str = "https://api.example.com/w?q=${lc:enc:args.city}") -> tuple[Any, Mock]:
    response = Mock(status_code=200, text="{}")
    response.json.return_value = payload
    config = {
        "function": "get_weather",
        "data_map": {"webhooks": [{"url": url, "method": "GET", "output": {"response": output}}]},
    }
    with patch("signalwire.utils.url_validator.validate_url", return_value=True), \
         patch("requests.get", return_value=response) as get:
        return execute_datamap_function(config, {"city": "New York"}), get


def test_object_response_is_read_from_the_root() -> None:
    result, get = _run("It's ${current.temp_f} degrees", {"current": {"temp_f": 72}})
    assert result == {"response": "It's 72 degrees"}
    assert get.call_args.args[0] == "https://api.example.com/w?q=new%20york"


def test_response_prefix_gets_a_hint(capsys: pytest.CaptureFixture[str]) -> None:
    result, _ = _run("It's ${response.current.temp_f} degrees", {"current": {"temp_f": 72}})
    assert "<MISSING:response.current.temp_f>" in str(result)
    assert "not ${response.<field>}" in capsys.readouterr().err
