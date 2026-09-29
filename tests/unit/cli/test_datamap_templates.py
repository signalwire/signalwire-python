"""
swaig-test's DataMap simulator expands templates as the platform does.

The platform's expander (mod_openai's swaig.c) works like this, and the
simulator now matches it:

- A path uses dots and one [n] per name; names match without regard to case,
  and a negative index counts from the end.
- The prefix helpers are lc, enc and fmt_ph, matched without regard to case,
  and they apply in a fixed order, fmt_ph, then lc, then enc, whatever order
  they're written in. There's no enc:url: ${enc:url:x} reads the path url:x
  and expands to nothing.
- enc is FreeSWITCH's switch_url_encode(), which leaves / , $ ! ' ( ) * and
  an already-encoded %XX alone.
- A nested template expands first, one level deep, and its value becomes part
  of the path.
- A value that isn't a string is inserted as cJSON prints it, and a path that
  doesn't resolve expands to an empty string.
"""

import json
from typing import Any
from unittest.mock import Mock, patch

import pytest

from signalwire.cli.execution.datamap_exec import execute_datamap_function, simple_template_expand

DATA: dict[str, Any] = {
    "args": {
        "city": "New York",
        "target": "Sales",
        "phone": "2025550143",
        "path": "/a b,c$!'()*~?&=#%2F%2fé",
    },
    "meta_data": {"table": {"sales": "+15551234567"}},
    "array": [{"joke": "ha"}],
    "items": ["a", "b", "c"],
    "grid": [[1, 2]],
    "count": 3,
    "ratio": 72.5,
    "flag": True,
    "nothing": None,
    "obj": {"a": 1},
}


@pytest.mark.parametrize(
    ("template", "expected"),
    [
        ("${args.city}", "New York"),
        ("%{args.city}", "New York"),
        ("${ARGS.City}", "New York"),
        ("${lc:args.city}", "new york"),
        ("${LC:args.city}", "new york"),
        ("${enc:args.city}", "New%20York"),
        ("${Enc:args.city}", "New%20York"),
        ("${enc:url:args.city}", ""),
        ("${lc:enc:args.city}", "new%20york"),
        ("${enc:lc:args.city}", "new%20york"),
        ("${enc:enc:args.city}", "New%20York"),
        ("${fmt_ph:args.phone}", "(202) 555-0143"),
        ("${enc:fmt_ph:args.phone}", "(202)%20555-0143"),
        ("${enc:args.path}", "/a%20b,c$!'()*~%3F%26%3D%23%2F%252f%C3%A9"),
        ("${meta_data.table.${lc:args.target}}", "+15551234567"),
        ("${lc:${args.target}}", ""),
        ("${array[0].joke}", "ha"),
        ("${items[-1]}", "c"),
        ("${items[3]}", ""),
        ("${grid[0][1]}", ""),
        ("${count}", "3"),
        ("${ratio}", "72.500000"),
        ("${flag}", "true"),
        ("${nothing}", "null"),
        ("${obj}", '{\n\t"a":\t1\n}'),
        ("${items}", '["a", "b", "c"]'),
        ("${args.missing}", ""),
        ("${args.}", ""),
        ("x${}y", "xy"),
        ("${unclosed", "${unclosed"),
        ("@{expr 1 + 2}", "@{expr 1 + 2}"),
    ],
)
def test_template_expansion(template: str, expected: str) -> None:
    assert simple_template_expand(template, DATA) == expected


def test_unresolved_templates_are_collected() -> None:
    unresolved: list[tuple[str, str]] = []
    text = simple_template_expand("${args.city} ${enc:url:args.city} ${response.x}", DATA, unresolved)
    assert text == "New York  "
    assert unresolved == [("${enc:url:args.city}", "url:args.city"), ("${response.x}", "response.x")]


def _run(output: str, payload: Any, url: str = "https://api.example.com/w?q=${lc:enc:args.city}") -> tuple[Any, Mock]:
    response = Mock(status_code=200, text=json.dumps(payload))
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
    assert result == {"response": "It's  degrees"}
    assert "not ${response.<field>}" in capsys.readouterr().err


def test_enc_url_leaves_the_query_empty(capsys: pytest.CaptureFixture[str]) -> None:
    _, get = _run("ok", {}, url="https://api.example.com/w?q=${enc:url:args.city}")
    assert get.call_args.args[0] == "https://api.example.com/w?q="
    assert "${enc:url:args.city} in the webhook url" in capsys.readouterr().err
