"""
swaig-test's DataMap simulator with a webhook that returns a JSON array.

Both error checks called .get() on the response, so a top-level array, the
shape ${array[0].field} templates expect, raised AttributeError, and the
simulator fell back to the error output even without error_keys (B15).
"""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from signalwire.cli.execution.datamap_exec import execute_datamap_function


def _config(error_keys: Any = None) -> dict[str, Any]:
    webhook: dict[str, Any] = {
        "url": "https://jokes.example.com/api?type=${args.type}",
        "method": "GET",
        "output": {"response": "Joke: ${array[0].joke}"},
    }
    if error_keys is not None:
        webhook["error_keys"] = error_keys
    return {
        "function": "get_joke",
        "data_map": {
            "webhooks": [webhook],
            "output": {"response": "The joke service failed."},
        },
    }


def _response(payload: Any) -> Mock:
    response = Mock(status_code=200, text="[]")
    response.json.return_value = payload
    return response


@pytest.mark.parametrize("error_keys", [None, ["error"], "error"])
def test_array_response_reaches_the_output_template(error_keys: Any) -> None:
    payload = [{"joke": "Why did the webhook cross the road?"}]
    with patch("signalwire.utils.url_validator.validate_url", return_value=True), \
         patch("requests.get", return_value=_response(payload)):
        result = execute_datamap_function(_config(error_keys), {"type": "dad"})
    assert "Why did the webhook cross the road?" in str(result)
    assert "failed" not in str(result)


def test_error_key_in_an_object_response_still_fails_the_webhook() -> None:
    with patch("signalwire.utils.url_validator.validate_url", return_value=True), \
         patch("requests.get", return_value=_response({"error": "rate limited"})):
        result = execute_datamap_function(_config(["error"]), {"type": "dad"})
    assert "The joke service failed." in str(result)
