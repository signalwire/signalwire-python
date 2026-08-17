"""Tests for client.py — RestClient instantiation and namespace wiring."""

import os
import pytest
from unittest.mock import patch

from signalwire.rest.client import RestClient
from signalwire.rest.namespaces._client_tree_generated import (
    FabricNamespace,
    VideoNamespace,
)
from signalwire.rest.namespaces.calling_resources_generated import Calling
from unittest.mock import MagicMock


class TestRestClient:
    def test_requires_credentials(self) -> None:
        with pytest.raises(ValueError, match="project, token, and host"):
            RestClient()

    def test_env_var_fallback(self, mock_session: MagicMock) -> None:
        env = {
            "SIGNALWIRE_PROJECT_ID": "env-project",
            "SIGNALWIRE_API_TOKEN": "env-token",
            "SIGNALWIRE_SPACE": "env.signalwire.com",
        }
        with patch.dict(os.environ, env):
            c = RestClient()
            assert c._project == "env-project"

    def test_explicit_overrides_env(self, mock_session: MagicMock) -> None:
        env = {
            "SIGNALWIRE_PROJECT_ID": "env-project",
            "SIGNALWIRE_API_TOKEN": "env-token",
            "SIGNALWIRE_SPACE": "env.signalwire.com",
        }
        with patch.dict(os.environ, env):
            c = RestClient(project="explicit", token="tok", host="h.com")
            assert c._project == "explicit"

    def test_namespaces_exist(self, client: RestClient) -> None:
        assert isinstance(client.fabric, FabricNamespace)
        assert isinstance(client.calling, Calling)
        assert isinstance(client.video, VideoNamespace)
        assert hasattr(client, "phone_numbers")
        assert hasattr(client, "addresses")
        assert hasattr(client, "queues")
        assert hasattr(client, "recordings")
        assert hasattr(client, "number_groups")
        assert hasattr(client, "verified_callers")
        assert hasattr(client, "sip_profile")
        assert hasattr(client, "lookup")
        assert hasattr(client, "short_codes")
        assert hasattr(client, "imported_numbers")
        assert hasattr(client, "mfa")
        assert hasattr(client, "registry")
        assert hasattr(client, "datasphere")
        assert hasattr(client, "logs")
        assert hasattr(client, "project")
        assert hasattr(client, "pubsub")
        assert hasattr(client, "chat")


class TestRestCaFile:
    """A5 fleet CA-var contract (hard-cut, no aliases): SIGNALWIRE_REST_CA_FILE
    supplies a custom CA bundle for the REST transport."""

    def test_ca_file_env_var_sets_session_verify(self) -> None:
        env = {
            "SIGNALWIRE_PROJECT_ID": "p",
            "SIGNALWIRE_API_TOKEN": "t",
            "SIGNALWIRE_SPACE": "x.signalwire.com",
            "SIGNALWIRE_REST_CA_FILE": "/etc/ssl/custom-ca.pem",
        }
        with patch.dict(os.environ, env):
            c = RestClient()
            assert c._http._session.verify == "/etc/ssl/custom-ca.pem"

    def test_no_ca_file_uses_default_verify(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SIGNALWIRE_PROJECT_ID", "p")
        monkeypatch.setenv("SIGNALWIRE_API_TOKEN", "t")
        monkeypatch.setenv("SIGNALWIRE_SPACE", "x.signalwire.com")
        monkeypatch.delenv("SIGNALWIRE_REST_CA_FILE", raising=False)
        c = RestClient()
        # requests' default verify is True (use the system trust store).
        assert c._http._session.verify is True
