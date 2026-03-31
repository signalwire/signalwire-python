"""Tests for client.py — RestClient instantiation and namespace wiring."""

import os
import pytest
from unittest.mock import patch

from signalwire.rest.client import RestClient
from signalwire.rest.namespaces.fabric import FabricNamespace
from signalwire.rest.namespaces.calling import CallingNamespace
from signalwire.rest.namespaces.video import VideoNamespace
from signalwire.rest.namespaces.compat import CompatNamespace


class TestRestClient:
    def test_requires_credentials(self):
        with pytest.raises(ValueError, match="project, token, and host"):
            RestClient()

    def test_env_var_fallback(self, mock_session):
        env = {
            "SIGNALWIRE_PROJECT_ID": "env-project",
            "SIGNALWIRE_API_TOKEN": "env-token",
            "SIGNALWIRE_SPACE": "env.signalwire.com",
        }
        with patch.dict(os.environ, env):
            c = RestClient()
            assert c._project == "env-project"

    def test_explicit_overrides_env(self, mock_session):
        env = {
            "SIGNALWIRE_PROJECT_ID": "env-project",
            "SIGNALWIRE_API_TOKEN": "env-token",
            "SIGNALWIRE_SPACE": "env.signalwire.com",
        }
        with patch.dict(os.environ, env):
            c = RestClient(project="explicit", token="tok", host="h.com")
            assert c._project == "explicit"

    def test_namespaces_exist(self, client):
        assert isinstance(client.fabric, FabricNamespace)
        assert isinstance(client.calling, CallingNamespace)
        assert isinstance(client.video, VideoNamespace)
        assert isinstance(client.compat, CompatNamespace)
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
