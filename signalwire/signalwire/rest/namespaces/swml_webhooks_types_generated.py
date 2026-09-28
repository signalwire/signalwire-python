# AUTO-GENERATED from porting-sdk/rest-apis/swml-webhooks/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Any, TypedDict


class SwmlRequestData(TypedDict, total=False):
    """Body POSTed to a dynamic-SWML request handler.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call: SwmlRequestCall
    vars: dict[str, Any]
    envs: dict[str, Any]
    params: dict[str, Any]


class SwmlRequestCall(TypedDict, total=False):
    """The call object embedded in a dynamic-SWML request.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str
    node_id: str
    segment_id: str
    project_id: str
    space_id: str
    call_state: str
    direction: str
    type: str
    # non-identifier field 'from': str
    to: str
    from_number: str
    to_number: str
    headers: list[dict[str, Any]]


class SignalWireErrorBody(TypedDict, total=False):
    """Error body returned by the Compatibility REST API (single-error form). Source: signalwire/docs specs/compatibility-api/_shared/errors.tsp (CompatibilityErrorResponse).

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: int
    message: str
    more_info: str
    status: int
