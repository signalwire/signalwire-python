"""REST wire-level regression PINS (Layer D / Tier-0) — hand-authored, DO NOT auto-generate.

These pin two cross-port bug classes surfaced by the 2026-07-06 DX review that the
auto-generated ``*_generated_test.py`` coverage suite does NOT catch (that suite only
asserts method / matched_route / success+error, not the exact wire encoding of the URL
or the request headers). Each pin drives a REAL ``RestClient`` request through the real
``requests`` transport into the shared ``mock_signalwire`` server and asserts on the
recorded journal — the same journal the REST-COVERAGE gate reads.

Pinned bug classes (see ~/src/_analysis/SDK_BUG_LEDGER_2026-07-06.md):

1. PERCENT-ENCODING — query params containing space / ``&`` / ``+`` / unicode must be
   correctly percent-encoded on the wire, so the server's ``parse_qs`` recovers the exact
   original values. A port that does NOT encode (rust shipped no percent-encoding) sends a
   raw ``&``/``=``/space in the query string; the server then mis-parses it into split
   values and phantom keys, so ``query_params`` no longer equals the input → this pin fails.

2. USER-AGENT — the recorded ``User-Agent`` header must be ``<name>/<package-version>`` with
   the version segment equal to the INSTALLED package version. Stale hardcoded UA strings
   (python ``signalwire-agents-python-rest/1.0``, ts ``…/2.0.0`` vs 2.0.5, perl ``…/1.0`` vs
   2.0.2) fail this because the version segment no longer tracks the package version.

The pins are language-neutral in intent: every port's equivalent wire suite should carry
the same two assertions against its journal.
"""

from __future__ import annotations

import re
from importlib.metadata import version as _pkg_version
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from signalwire.rest.client import RestClient

    from .conftest import _MockHarness

# The distribution name for this SDK (pyproject ``[project].name``). The UA's version
# segment must match ``importlib.metadata.version(_DIST_NAME)`` so it can never go stale.
_DIST_NAME = "signalwire-sdk"


class TestWirePercentEncodingPin:
    """A request whose query params contain space/&/+/unicode round-trips exactly."""

    # The adversarial value set: a space, an ``&`` (query separator), a ``+`` (space in
    # form-encoding), a raw ``=``, and a non-ASCII unicode char — every character a naive
    # (no-encoding) client would let leak into the query string and corrupt the parse.
    HOSTILE = {
        "q": "a b&c+dé",
        "tag": "x=y",
        "emoji": "smile\N{SNOWMAN}",
    }

    def test_query_params_are_percent_encoded_on_the_wire(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.addresses.list(**self.HOSTILE)
        last = mock.last_request()
        assert last.method == "GET"
        # The server journals ``parse_qs``-DECODED query params. If (and only if) the
        # client percent-encoded correctly, the decoded params equal the exact input.
        # A no-encoding client mangles them (splits on the raw ``&``/``=``, drops the
        # ``+``/space, corrupts the unicode) → this equality fails, naming the bug.
        expected = {k: [v] for k, v in self.HOSTILE.items()}
        assert last.query_params == expected, (
            "query params were not correctly percent-encoded on the wire; "
            f"server decoded {last.query_params!r}, expected {expected!r}"
        )


class TestWireUserAgentPin:
    """The recorded User-Agent is ``<name>/<installed-package-version>``, not a stale literal."""

    # KNOWN-FAILING against the current python reference: ``rest/_base.py`` hardcodes
    # ``User-Agent: signalwire-agents-python-rest/1.0`` (SDK_BUG_LEDGER P1 — "wrong name
    # and version; derive from package version"). This is a strict xfail so:
    #   * the pin does NOT redden the suite while the P1 is open, but
    #   * the moment the UA is fixed to derive from the package version, the xfail
    #     "unexpectedly passes" → strict-xfail turns that into a FAILURE, forcing this
    #     marker to be removed. That self-policing is the regression-pin contract:
    #     remove the xfail when you fix the UA, and the pin then guards against re-drift.
    @pytest.mark.xfail(
        strict=True,
        reason="SDK_BUG_LEDGER P1: python UA is hardcoded 'signalwire-agents-python-rest/1.0' "
        "instead of deriving from the package version. Remove this marker when the UA is fixed.",
    )
    def test_user_agent_version_tracks_the_package_version(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        # Any journaled request carries the client's default headers; drive one.
        signalwire_client.addresses.list()
        last = mock.last_request()
        ua = last.headers.get("user-agent")
        assert ua, "no User-Agent header was recorded for the request"

        # Shape: ``<name>/<version>`` — a name token then a slash then a version.
        m = re.fullmatch(r"(?P<name>[^/\s]+)/(?P<version>[^/\s]+)", ua)
        assert m, f"User-Agent {ua!r} is not of the form <name>/<version>"

        # The load-bearing assertion: the version segment MUST equal the installed
        # package version. This is what catches a stale hardcoded UA (``/1.0`` etc.).
        assert m.group("version") == _pkg_version(_DIST_NAME), (
            f"User-Agent version segment {m.group('version')!r} does not match the "
            f"installed package version {_pkg_version(_DIST_NAME)!r} — stale UA literal"
        )
