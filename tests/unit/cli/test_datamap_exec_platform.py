"""
swaig-test's DataMap simulator runs a data_map as the platform does.

These follow mod_openai's actions.c (process_data_map, parse_webhook,
get_input_from_webhooks, parse_expression, process_foreach):

- A webhook's url and params read the call data, where the arguments are
  ${args.x}. Its foreach, expressions and output read the response, with the
  call data under input, so the arguments are ${input.args.x} there.
- Header values are sent as written.
- Only the first webhook requested runs. When it fails, the top-level output
  runs, not the next webhook; without one, the platform's generic error.
- error_keys fail a webhook by presence; a status outside 200-299 isn't a
  failure by itself, and an empty body is a parse error.
- GET and POST only, and params make a POST.
- require_args is any-of; input_args_as_params and form_param shape the body.
- Expression patterns match anywhere, without regard to case unless written
  /.../, and nomatch-output is used.
"""

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import Mock, patch
from urllib.parse import unquote

import pytest
import requests

from signalwire.cli.execution.datamap_exec import PLATFORM_ERROR_RESPONSE, execute_datamap_function

pytestmark = pytest.mark.usefixtures("route_public_session_to_requests")


def _response(payload: Any, status: int = 200) -> Mock:
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return Mock(status_code=status, text=text)


def _method(result: Any) -> Mock:
    """A requests.get or requests.post stand-in returning a response, or raising."""
    if isinstance(result, Exception):
        return Mock(side_effect=result)
    return Mock(return_value=result)


@contextmanager
def _http(get: Any = None, post: Any = None) -> Iterator[tuple[Mock, Mock]]:
    """Patch the SSRF check and both request methods."""
    get_mock = _method(get)
    post_mock = _method(post)
    with patch("signalwire.utils.url_validator.validate_url", return_value=True), \
         patch("requests.get", get_mock), \
         patch("requests.post", post_mock):
        yield get_mock, post_mock


def _function(data_map: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {"function": "lookup", "data_map": data_map, **extra}


# Template data by stage


def test_webhook_output_reads_arguments_under_input(capsys: pytest.CaptureFixture[str]) -> None:
    config = _function({
        "webhooks": [{
            "url": "https://api.example.com/w?q=${enc:args.city}",
            "method": "GET",
            "output": {"response": "${input.args.city}: ${temp}. [${args.city}]"},
        }],
    })
    with _http(get=_response({"temp": 72})) as (get, _):
        result = execute_datamap_function(config, {"city": "New York"})
    assert result == {"response": "New York: 72. []"}
    assert get.call_args.args[0] == "https://api.example.com/w?q=New%20York"
    assert "write ${input.args.city}" in capsys.readouterr().err


def test_webhook_output_reads_global_data_and_prompt_vars_from_the_root() -> None:
    config = _function({
        "webhooks": [{
            "url": "https://api.example.com/${global_data.tenant}/w",
            "method": "GET",
            "output": {"response": "${global_data.tenant} ${prompt_vars.time_of_day} ${input.caller_id_num}"},
        }],
    })
    call_data = {
        "global_data": {"tenant": "acme"},
        "caller_id_num": "+12025550143",
        "prompt_vars": {"time_of_day": "morning"},
    }
    with _http(get=_response({})) as (get, _):
        result = execute_datamap_function(config, {}, call_data=call_data)
    assert get.call_args.args[0] == "https://api.example.com/acme/w"
    assert result == {"response": "acme morning +12025550143"}


def test_prompt_vars_are_merged_into_the_call_data() -> None:
    config = _function({"output": {"response": "${time_of_day}|${prompt_vars.time_of_day}|${input.args.x}"}})
    result = execute_datamap_function(config, {"x": "1"}, call_data={"prompt_vars": {"time_of_day": "evening"}})
    assert result == {"response": "evening|evening|"}


def test_top_level_output_reads_arguments_at_the_root(capsys: pytest.CaptureFixture[str]) -> None:
    config = _function({"output": {"response": "Sorry about ${args.city}.${input.args.city}"}})
    result = execute_datamap_function(config, {"city": "Paris"})
    assert result == {"response": "Sorry about Paris."}
    assert "input is empty until a webhook responds" in capsys.readouterr().err


def test_meta_data_comes_from_the_function_definition() -> None:
    config = _function(
        {"expressions": [{"string": "${meta_data.contacts.${lc:args.dept}}", "pattern": r"\d", "output": {"response": "Call ${meta_data.contacts.${lc:args.dept}}"}}]},
        meta_data={"contacts": {"sales": "+12025550143"}},
    )
    assert execute_datamap_function(config, {"dept": "Sales"}) == {"response": "Call +12025550143"}


def test_meta_data_is_merged_over_the_global_data() -> None:
    # The platform merges a function's meta_data over the AI's global_data,
    # key by key, when it loads the function
    config = _function(
        {"output": {"response": "${meta_data.tenant}|${meta_data.region}|${global_data.region}"}},
        meta_data={"region": "eu"},
    )
    result = execute_datamap_function(
        config, {}, call_data={"global_data": {"tenant": "acme", "region": "us"}})
    assert result == {"response": "acme|eu|us"}


def test_headers_are_sent_unexpanded() -> None:
    config = _function({
        "webhooks": [{
            "url": "https://api.example.com/w",
            "method": "GET",
            "headers": {"Authorization": "Bearer ${global_data.token}", "X-Count": 3},
            "output": {"response": "ok"},
        }],
    })
    with _http(get=_response({})) as (get, _):
        execute_datamap_function(config, {}, call_data={"global_data": {"token": "secret"}})
    headers = get.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer ${global_data.token}"
    assert "X-Count" not in headers
    assert headers["Content-Type"] == "application/json"


def test_response_numbers_print_as_the_platform_prints_them() -> None:
    config = _function({"webhooks": [{"url": "https://api.example.com/w", "method": "GET", "output": {"response": "${temp} ${count}"}}]})
    with _http(get=_response({"temp": 72.5, "count": 3})):
        assert execute_datamap_function(config, {}) == {"response": "72.500000 3"}


def test_an_object_inserted_into_a_string_breaks_the_output() -> None:
    config = _function({"webhooks": [{"url": "https://api.example.com/w", "method": "GET", "output": {"response": "Data: ${data}"}}]})
    with _http(get=_response({"data": {"a": 1}})):
        result = execute_datamap_function(config, {})
    assert "isn't valid JSON" in result["error"]


# Which webhook runs


def test_a_failed_webhook_falls_back_to_the_top_level_output_not_the_next_webhook() -> None:
    config = _function({
        "webhooks": [
            {"url": "https://primary.example.com/", "method": "GET", "error_keys": ["error"], "output": {"response": "primary"}},
            {"url": "https://backup.example.com/", "method": "GET", "output": {"response": "backup"}},
        ],
        "output": {"response": "fallback for ${args.q}"},
    })
    with _http(get=_response({"error": "down"})) as (get, _):
        result = execute_datamap_function(config, {"q": "x"})
    assert result == {"response": "fallback for x"}
    assert [call.args[0] for call in get.call_args_list] == ["https://primary.example.com/"]


def test_without_a_top_level_output_the_platform_returns_its_generic_error() -> None:
    config = _function({"webhooks": [{"url": "https://api.example.com/", "method": "GET", "error_keys": "error", "output": {"response": "ok"}}]})
    with _http(get=_response({"error": "down"})):
        assert execute_datamap_function(config, {}) == {"response": PLATFORM_ERROR_RESPONSE}


def test_require_args_is_any_of_and_skips_without_a_request() -> None:
    config = _function({
        "webhooks": [
            {"url": "https://by-zip.example.com/", "method": "GET", "require_args": ["zip"], "output": {"response": "zip"}},
            {"url": "https://by-city.example.com/", "method": "GET", "require_args": ["zip", "city"], "output": {"response": "city"}},
        ],
    })
    with _http(get=_response({})) as (get, _):
        result = execute_datamap_function(config, {"city": "Paris"})
    assert result == {"response": "city"}
    assert [call.args[0] for call in get.call_args_list] == ["https://by-city.example.com/"]


def test_a_webhook_without_output_or_expressions_is_skipped() -> None:
    config = _function({
        "webhooks": [
            {"url": "https://skipped.example.com/", "method": "GET"},
            {"url": "https://used.example.com/", "method": "GET", "output": {"response": "used"}},
        ],
    })
    with _http(get=_response({})) as (get, _):
        assert execute_datamap_function(config, {}) == {"response": "used"}
    assert get.call_count == 1


def test_a_single_webhook_object_is_not_checked_for_errors() -> None:
    config = _function({
        "webhooks": {"url": "https://api.example.com/", "method": "GET", "error_keys": ["error"], "output": {"response": "got ${error}"}},
        "output": {"response": "fallback"},
    })
    with _http(get=_response({"error": "down"})):
        assert execute_datamap_function(config, {}) == {"response": "got down"}


# Failure detection


@pytest.mark.parametrize("value", [None, False, "", 0])
def test_error_keys_fail_by_presence(value: Any) -> None:
    config = _function({
        "webhooks": [{"url": "https://api.example.com/", "method": "GET", "error_keys": ["error"], "output": {"response": "ok"}}],
        "output": {"response": "failed"},
    })
    with _http(get=_response({"error": value, "data": 1})):
        assert execute_datamap_function(config, {}) == {"response": "failed"}


def test_a_status_outside_2xx_with_a_body_is_not_a_failure() -> None:
    config = _function({
        "webhooks": [{"url": "https://api.example.com/", "method": "GET", "output": {"response": "${message} (${http_code})"}}],
        "output": {"response": "failed"},
    })
    with _http(get=_response({"message": "Not found"}, status=404)):
        assert execute_datamap_function(config, {}) == {"response": "Not found (404)"}


def test_http_code_as_an_error_key_fails_a_status_outside_2xx() -> None:
    config = _function({
        "webhooks": [{"url": "https://api.example.com/", "method": "GET", "error_keys": ["http_code"], "output": {"response": "ok"}}],
        "output": {"response": "failed"},
    })
    with _http(get=_response({"message": "Not found"}, status=404)):
        assert execute_datamap_function(config, {}) == {"response": "failed"}
    with _http(get=_response({"message": "fine"})):
        assert execute_datamap_function(config, {}) == {"response": "ok"}


@pytest.mark.parametrize("body", ["", "not json"])
def test_an_empty_or_unparseable_body_is_a_parse_error(body: str) -> None:
    config = _function({
        "webhooks": [{"url": "https://api.example.com/", "method": "GET", "output": {"response": "ok"}}],
        "output": {"response": "failed"},
    })
    with _http(get=_response(body)):
        assert execute_datamap_function(config, {}) == {"response": "failed"}


def test_a_request_error_is_a_protocol_error() -> None:
    config = _function({
        "webhooks": [{"url": "https://api.example.com/", "method": "GET", "output": {"response": "ok"}}],
        "output": {"response": "failed"},
    })
    with _http(get=requests.ConnectionError("refused")):
        assert execute_datamap_function(config, {}) == {"response": "failed"}


# The request


@pytest.mark.parametrize("method", ["PUT", "DELETE", "PATCH", "get", None])
def test_only_post_is_sent_as_a_post(method: str | None) -> None:
    webhook: dict[str, Any] = {"url": "https://api.example.com/", "output": {"response": "ok"}}
    if method is not None:
        webhook["method"] = method
    with _http(get=_response({}), post=_response({})) as (get, post):
        execute_datamap_function(_function({"webhooks": [webhook]}), {})
    assert get.call_count == 1
    assert post.call_count == 0


def test_params_are_the_json_body_and_make_a_post() -> None:
    config = _function({
        "webhooks": [{
            "url": "https://api.example.com/",
            "method": "GET",
            "params": {"q": "${args.query}", "limit": 3, "note": 'say "hi"'},
            "output": {"response": "ok"},
        }],
    })
    with _http(get=_response({}), post=_response({})) as (get, post):
        execute_datamap_function(config, {"query": 'the "best" pizza'})
    assert get.call_count == 0
    assert json.loads(post.call_args.kwargs["data"]) == {"q": 'the "best" pizza', "limit": 3, "note": 'say "hi"'}


def test_input_args_as_params_sends_the_arguments() -> None:
    config = _function({
        "webhooks": [{
            "url": "https://api.example.com/",
            "method": "GET",
            "input_args_as_params": True,
            "params": {"source": "agent", "city": "overridden"},
            "output": {"response": "ok"},
        }],
    })
    with _http(post=_response({})) as (_, post):
        execute_datamap_function(config, {"city": "Paris", "units": "metric"})
    assert json.loads(post.call_args.kwargs["data"]) == {"source": "agent", "city": "Paris", "units": "metric"}


def test_form_param_sends_the_json_as_one_form_field() -> None:
    config = _function({
        "webhooks": [{
            "url": "https://api.example.com/",
            "method": "POST",
            "form_param": "payload",
            "params": {"name": "${args.name}"},
            "output": {"response": "ok"},
        }],
    })
    with _http(post=_response({})) as (_, post):
        execute_datamap_function(config, {"name": "Ann Lee"})
    body = post.call_args.kwargs["data"]
    assert body.startswith("payload=")
    assert json.loads(unquote(body[len("payload="):])) == {"name": "Ann Lee"}
    assert post.call_args.kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"


def test_url_credentials_become_basic_auth() -> None:
    config = _function({"webhooks": [{"url": "https://user:pa%40ss@api.example.com/w", "method": "GET", "output": {"response": "ok"}}]})
    with _http(get=_response({})) as (get, _):
        execute_datamap_function(config, {})
    assert get.call_args.args[0] == "https://api.example.com/w"
    assert get.call_args.kwargs["auth"] == ("user", "pa@ss")


# Expressions


def test_top_level_expressions_match_anywhere_without_regard_to_case() -> None:
    config = _function({
        "expressions": [
            {"string": "${args.command}", "pattern": "start", "output": {"response": "Starting ${args.target}"}},
        ],
        "output": {"response": "no match"},
    })
    assert execute_datamap_function(config, {"command": "Please START it", "target": "pump"}) == {"response": "Starting pump"}


def test_a_slash_pattern_sets_its_own_flags_and_nomatch_output_is_used() -> None:
    config = _function({
        "expressions": [
            {"string": "${args.command}", "pattern": "/^start/", "output": {"response": "start"}, "nomatch-output": {"response": "unknown: ${args.command}"}},
            {"string": "${args.command}", "pattern": "Start", "output": {"response": "never reached"}},
        ],
    })
    assert execute_datamap_function(config, {"command": "Start"}) == {"response": "unknown: Start"}


def test_an_expression_without_string_never_matches() -> None:
    config = _function({
        "expressions": [{"pattern": ".*", "output": {"response": "matched"}}],
        "output": {"response": "top-level output"},
    })
    assert execute_datamap_function(config, {}) == {"response": "top-level output"}


def test_a_single_expression_object_works() -> None:
    config = _function({"expressions": {"string": "${args.x}", "pattern": "yes", "output": {"response": "matched"}}})
    assert execute_datamap_function(config, {"x": "yes"}) == {"response": "matched"}


def test_webhook_expressions_read_the_response_and_replace_its_output() -> None:
    webhook = {
        "url": "https://api.example.com/",
        "method": "GET",
        "expressions": [
            {"string": "${status}", "pattern": "^done$", "output": {"response": "Order ${input.args.order} is done"}},
        ],
        "output": {"response": "Order ${input.args.order} is ${status}"},
    }
    with _http(get=_response({"status": "done"})):
        assert execute_datamap_function(_function({"webhooks": [webhook]}), {"order": "7"}) == {"response": "Order 7 is done"}
    with _http(get=_response({"status": "pending"})):
        assert execute_datamap_function(_function({"webhooks": [webhook]}), {"order": "7"}) == {"response": "Order 7 is pending"}


# foreach


def test_foreach_walks_a_path_with_the_whole_response_readable() -> None:
    config = _function({
        "webhooks": [{
            "url": "https://api.example.com/",
            "method": "GET",
            "foreach": {"input_key": "data.items", "output_key": "found", "max": "2", "append": "${this} (${unit}, ${input.args.q});"},
            "output": {"response": "${found}"},
        }],
    })
    with _http(get=_response({"data": {"items": ["a", "b", "c"]}, "unit": "kg"})):
        assert execute_datamap_function(config, {"q": "x"}) == {"response": "a (kg, x);b (kg, x);"}


def test_foreach_over_objects_with_no_max() -> None:
    config = _function({
        "webhooks": [{
            "url": "https://api.example.com/",
            "method": "GET",
            "foreach": {"input_key": "results", "output_key": "found", "max": 0, "append": "${this.title}\n"},
            "output": {"response": "${found}"},
        }],
    })
    with _http(get=_response({"results": [{"title": "A"}, {"title": "B"}, {"title": "C"}]})):
        assert execute_datamap_function(config, {}) == {"response": "A\nB\nC\n"}


def test_verbose_output_says_why_the_webhook_failed(capsys: pytest.CaptureFixture[str]) -> None:
    config = _function({
        "webhooks": [{"url": "https://api.example.com/", "method": "GET", "error_keys": ["fault"], "output": {"response": "ok"}}],
        "output": {"response": "failed"},
    })
    with _http(get=_response({"fault": None})):
        execute_datamap_function(config, {}, verbose=True)
    out = capsys.readouterr().out
    assert "Webhook 1 failed: the response has the error key 'fault'." in out
    assert "--- Using the Top-Level Output ---" in out
