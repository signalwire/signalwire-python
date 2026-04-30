"""Compat miscellaneous tests for resources with single-method gaps.

Covers:

  - CompatApplications.update
  - CompatLamlBins.update
"""

from __future__ import annotations


class TestCompatApplicationsUpdate:
    def test_returns_application_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.applications.update(
            "AP_U", FriendlyName="updated"
        )
        assert isinstance(result, dict)
        # Application resources carry friendly_name + sid + voice_url.
        assert "friendly_name" in result or "sid" in result

    def test_journal_records_post_with_friendly_name(self, signalwire_client, mock):
        signalwire_client.compat.applications.update(
            "AP_UU", FriendlyName="renamed", VoiceUrl="https://a.b/v"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Applications/AP_UU"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("FriendlyName") == "renamed"
        assert j.body.get("VoiceUrl") == "https://a.b/v"


class TestCompatLamlBinsUpdate:
    def test_returns_laml_bin_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.laml_bins.update(
            "LB_U", FriendlyName="updated"
        )
        assert isinstance(result, dict)
        # LAML bin resources carry friendly_name + sid + contents.
        assert "friendly_name" in result or "sid" in result or "contents" in result

    def test_journal_records_post_with_friendly_name(self, signalwire_client, mock):
        signalwire_client.compat.laml_bins.update(
            "LB_UU", FriendlyName="renamed", Contents="<Response/>"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/LamlBins/LB_UU"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("FriendlyName") == "renamed"
        assert j.body.get("Contents") == "<Response/>"
