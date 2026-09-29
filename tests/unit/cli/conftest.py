"""
Shared fixtures for the CLI tests.
"""

from collections.abc import Iterator
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests


@pytest.fixture
def route_public_session_to_requests() -> Iterator[None]:
    """Send the DataMap simulator's requests to ``requests.get`` and ``requests.post``.

    The simulator sends through the SDK's ``_PublicSession``. Tests that stub
    ``requests.get`` and ``requests.post`` use this to have the session call
    those stubs, with the same arguments they'd get when called directly.
    """

    def request(self: Any, method: str, url: str, **kwargs: Any) -> Any:
        kwargs.pop("allow_redirects", None)
        if method == "POST":
            response = requests.post(url, **kwargs)
        else:
            kwargs.pop("data", None)
            response = requests.get(url, **kwargs)
        if isinstance(response, Mock) and not isinstance(response.is_redirect, bool):
            response.is_redirect = False
        return response

    with patch("signalwire.utils.url_validator._PublicSession.request", request):
        yield
