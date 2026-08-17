#!/usr/bin/env python3
"""doc_wire_runner.py — the DOC-WIRE fixture runner for signalwire-python.

The DOC-WIRE gate (porting-sdk `scripts/doc_wire.py`) spawns `mock_signalwire`
in flag mode, exports `MOCK_SIGNALWIRE_PORT`, then runs THIS command; it then
reads the mock journal and fails on any `wire_violations`. Our job is only to
DRIVE the documented REST calls against the mock so the mock journals what the
documented fixtures actually put on the wire.

We replay the REST calls shown in the README/rest quickstart + rest-docs +
rest-examples (the wire-bearing doc fixtures) — the exact kwargs the docs teach
— so a doc lie like `area_code=` (spec `areacode`) or a flat `{type:tts,text}`
play item shows up as a journaled violation and fails the gate. The blocking
agent/relay quickstarts are covered by EXAMPLES-RUN, not here.

The RestClient always prepends `https://`; we overwrite `_base_url` to the mock
after construction, exactly as the REST test conftest does.
"""

from __future__ import annotations

import os
import sys

from signalwire.rest import RequestOptions, RestClient
from signalwire.rest._base import HttpClient


def _client(base_url: str) -> RestClient:
    original_init = HttpClient.__init__

    def _patched_init(
        self: HttpClient,
        project: str,
        token: str,
        host: str,
        request_options: RequestOptions | None = None,
    ) -> None:
        original_init(self, project, token, host, request_options=request_options)
        self._base_url = base_url

    HttpClient.__init__ = _patched_init  # type: ignore[method-assign]
    return RestClient(project="test_proj", token="test_tok", host="127.0.0.1")  # noqa: S106


def main() -> int:
    port = os.environ.get("MOCK_SIGNALWIRE_PORT")
    if not port:
        print("doc_wire_runner: MOCK_SIGNALWIRE_PORT not set", file=sys.stderr)
        return 2
    base_url = os.environ.get("SIGNALWIRE_MOCK_URL", f"http://127.0.0.1:{port}")
    client = _client(base_url)

    call_id = "call-doc-wire"

    # --- README + examples/quickstart_rest.py (region: rest) -----------------
    client.fabric.ai_agents.create(
        name="Support Bot", prompt={"text": "You are helpful."}
    )
    client.calling.play(call_id, play=[{"type": "tts", "params": {"text": "Hello!"}}])
    client.phone_numbers.search(areacode="512")
    client.datasphere.documents.search(query_string="billing policy")

    # --- rest/README.md + rest/docs/namespaces.md phone-number search --------
    client.phone_numbers.search(areacode="512", number_type="local")

    # --- rest/docs/calling.md play (nested params:{text}) --------------------
    client.calling.play(call_id, play=[{"type": "tts", "params": {"text": "Hello!"}}])

    # --- rest/examples/rest_calling_play_and_record.py + ivr_and_ai.py -------
    client.calling.play(
        call_id, play=[{"type": "tts", "params": {"text": "Welcome to SignalWire."}}]
    )
    client.calling.play(
        call_id,
        play=[{"type": "tts", "params": {"text": "Enter your PIN followed by pound."}}],
    )

    print("doc_wire_runner: replayed documented REST fixtures against the mock")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
