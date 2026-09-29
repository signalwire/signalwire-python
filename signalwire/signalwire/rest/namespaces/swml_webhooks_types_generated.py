# AUTO-GENERATED from porting-sdk/combined-specs/swml.yaml (webhook_request) — DO NOT EDIT.
# (vendored from mod_infrastructure specs/swml.yaml; regenerate via
#  python3 porting-sdk/scripts/generate_python_rest_types.py)
#
# The SWML webhook REQUEST body — what the engine POSTs to a SWML webhook to fetch
# the next document (a dynamic-SWML handler RECEIVES it). Derived by mod_infrastructure
# from the C functions that build it, read through
# porting-sdk/scripts/swml_webhook_request_shapes.py. STATIC-ONLY: a plain dict at
# runtime. ``Required`` marks a key the engine writes on every request; every other
# key is conditional. The objects are CLOSED: the engine writes no other keys.
from __future__ import annotations

import sys
from typing import Any, Literal, TypeAlias, TypedDict

if sys.version_info >= (3, 11):
    from typing import Required
else:
    from typing_extensions import Required


class SwmlRequestData(TypedDict, total=False):
    """The JSON body the engine POSTs to a SWML webhook to fetch the next document.

    Closed shape: the engine writes no other keys. Not validated at runtime
    (a TypedDict is a plain ``dict``).
    """

    call: SwmlRequestCall
    vars: Required[dict[str, Any]]
    envs: Any
    params: Any


SwmlRequestCall: TypeAlias = "SwmlRequestCallPhone | SwmlRequestCallSip | SwmlRequestCallWebrtc | SwmlRequestCallOther"
"""The `call` object of a SWML webhook request: one of its per-device-type variants."""


class SwmlRequestCallParent(TypedDict, total=False):
    """The `call.parent` object of a SWML webhook request.

    Closed shape: the engine writes no other keys. Not validated at runtime
    (a TypedDict is a plain ``dict``).
    """

    device_type: str
    call_id: Required[str]
    node_id: Required[str]


class SwmlRequestCallPeer(TypedDict, total=False):
    """The `call.peer` object of a SWML webhook request.

    Closed shape: the engine writes no other keys. Not validated at runtime
    (a TypedDict is a plain ``dict``).
    """

    call_id: Required[str]
    node_id: Required[str]


SwmlRequestCallPhone = TypedDict(
    "SwmlRequestCallPhone",
    {
        "project_id": "str",
        "space_id": "str",
        "call_id": "Required[str]",
        "node_id": "Required[str]",
        "segment_id": "str",
        "tag": "str",
        "call_state": "Required[Literal['answered', 'created', 'ended', 'ending', 'ringing']]",
        "parent": "SwmlRequestCallParent",
        "peer": "SwmlRequestCallPeer",
        "direction": "Required[Literal['inbound', 'outbound']]",
        "end_reason": "Literal['abandoned', 'busy', 'cancel', 'decline', 'error', 'hangup', 'maxDuration', 'noAnswer', 'notFound']",
        "end_source": "Literal['inbound', 'none', 'outbound']",
        "dial_winner": "Literal['true']",
        "address_id": "str",
        "subscriber_id": "str",
        "subscriber_name": "str",
        "type": "Required[Literal['phone']]",
        "from": "Required[str]",
        "to": "Required[str]",
        "from_number": "Required[str]",
        "to_number": "Required[str]",
        "headers": "list[SwmlRequestCallPhoneHeadersItem]",
    },
    total=False,
)
SwmlRequestCallPhone.__doc__ = """The `call` object of a SWML webhook request, `phone` device variant (engine: call -> device . type == RELAY_DEVICE_PHONE).

Closed shape: the engine writes no other keys. Not validated at runtime
(a TypedDict is a plain ``dict``).
"""


class SwmlRequestCallPhoneHeadersItem(TypedDict, total=False):
    """The `call.phone.headers.items` object of a SWML webhook request.

    Closed shape: the engine writes no other keys. Not validated at runtime
    (a TypedDict is a plain ``dict``).
    """

    name: Required[Literal["Diversion"]]
    value: Required[str]


SwmlRequestCallSip = TypedDict(
    "SwmlRequestCallSip",
    {
        "project_id": "str",
        "space_id": "str",
        "call_id": "Required[str]",
        "node_id": "Required[str]",
        "segment_id": "str",
        "tag": "str",
        "call_state": "Required[Literal['answered', 'created', 'ended', 'ending', 'ringing']]",
        "parent": "SwmlRequestCallParent",
        "peer": "SwmlRequestCallPeer",
        "direction": "Required[Literal['inbound', 'outbound']]",
        "end_reason": "Literal['abandoned', 'busy', 'cancel', 'decline', 'error', 'hangup', 'maxDuration', 'noAnswer', 'notFound']",
        "end_source": "Literal['inbound', 'none', 'outbound']",
        "dial_winner": "Literal['true']",
        "address_id": "str",
        "subscriber_id": "str",
        "subscriber_name": "str",
        "type": "Required[Literal['sip']]",
        "from": "Required[str]",
        "to": "Required[str]",
        "headers": "list[SwmlRequestCallSipHeadersItem]",
        "sip_data": "SwmlRequestCallSipSipData",
    },
    total=False,
)
SwmlRequestCallSip.__doc__ = """The `call` object of a SWML webhook request, `sip` device variant (engine: call -> device . type == RELAY_DEVICE_SIP).

Closed shape: the engine writes no other keys. Not validated at runtime
(a TypedDict is a plain ``dict``).
"""


class SwmlRequestCallSipHeadersItem(TypedDict, total=False):
    """The `call.sip.headers.items` object of a SWML webhook request.

    Closed shape: the engine writes no other keys. Not validated at runtime
    (a TypedDict is a plain ``dict``).
    """

    name: Required[str]
    value: Required[str]


class SwmlRequestCallSipSipData(TypedDict, total=False):
    """The `call.sip.sip_data` object of a SWML webhook request.

    Closed shape: the engine writes no other keys. Not validated at runtime
    (a TypedDict is a plain ``dict``).
    """

    sip_req_user: str
    sip_req_uri: str
    sip_req_host: str
    sip_from_user: str
    sip_from_uri: str
    sip_from_host: str
    sip_to_user: str
    sip_to_uri: str
    sip_to_host: str
    sip_contact_user: str
    sip_contact_port: str
    sip_contact_uri: str
    sip_contact_host: str
    sip_from_params: dict[str, str]
    sip_to_params: dict[str, str]
    sip_contact_params: dict[str, str]
    sip_req_params: dict[str, str]
    sip_p_asserted_identity: str


SwmlRequestCallWebrtc = TypedDict(
    "SwmlRequestCallWebrtc",
    {
        "project_id": "str",
        "space_id": "str",
        "call_id": "Required[str]",
        "node_id": "Required[str]",
        "segment_id": "str",
        "tag": "str",
        "call_state": "Required[Literal['answered', 'created', 'ended', 'ending', 'ringing']]",
        "parent": "SwmlRequestCallParent",
        "peer": "SwmlRequestCallPeer",
        "direction": "Required[Literal['inbound', 'outbound']]",
        "end_reason": "Literal['abandoned', 'busy', 'cancel', 'decline', 'error', 'hangup', 'maxDuration', 'noAnswer', 'notFound']",
        "end_source": "Literal['inbound', 'none', 'outbound']",
        "dial_winner": "Literal['true']",
        "address_id": "str",
        "subscriber_id": "str",
        "subscriber_name": "str",
        "type": "Required[Literal['webrtc']]",
        "from": "Required[str]",
        "to": "Required[str]",
    },
    total=False,
)
SwmlRequestCallWebrtc.__doc__ = """The `call` object of a SWML webhook request, `webrtc` device variant (engine: call -> device . type == RELAY_DEVICE_WEBRTC).

Closed shape: the engine writes no other keys. Not validated at runtime
(a TypedDict is a plain ``dict``).
"""


class SwmlRequestCallOther(TypedDict, total=False):
    """The `call` object of a SWML webhook request, `other` device variant (engine: call -> device . type is one of RELAY_DEVICE_NONE, RELAY_DEVICE_TYPE_MAX).

    Closed shape: the engine writes no other keys. Not validated at runtime
    (a TypedDict is a plain ``dict``).
    """

    project_id: str
    space_id: str
    call_id: Required[str]
    node_id: Required[str]
    segment_id: str
    tag: str
    call_state: Required[Literal["answered", "created", "ended", "ending", "ringing"]]
    parent: SwmlRequestCallParent
    peer: SwmlRequestCallPeer
    direction: Required[Literal["inbound", "outbound"]]
    end_reason: Literal[
        "abandoned",
        "busy",
        "cancel",
        "decline",
        "error",
        "hangup",
        "maxDuration",
        "noAnswer",
        "notFound",
    ]
    end_source: Literal["inbound", "none", "outbound"]
    dial_winner: Literal["true"]
    address_id: str
    subscriber_id: str
    subscriber_name: str


# Deprecated aliases: names this module exported before its types were re-derived
# (signalwire-python 3.x at f870cc15). Kept so existing imports keep working; use the
# new name. Names with no single replacement are listed in CHANGELOG.md instead.
import signalwire.core.post_prompt_generated as _dep_m0  # noqa: E402
import signalwire.core.swaig_request_generated as _dep_m1  # noqa: E402

# deprecated: use signalwire.core.post_prompt_generated.PostPrompt
PostPromptData = _dep_m0.PostPrompt
# deprecated: use signalwire.core.swaig_request_generated.SwaigArgument
SwaigArgument = _dep_m1.SwaigArgument
# deprecated: use signalwire.core.swaig_request_generated.SwaigRequest
SwaigRequestData = _dep_m1.SwaigRequest
