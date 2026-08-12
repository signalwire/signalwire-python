# AUTO-GENERATED from porting-sdk/swaig-specs/swaig-request.yaml — DO NOT EDIT.
# (vendored from mod_openai; regenerate via
#  python3 porting-sdk/scripts/generate_python_rest_types.py)
#
# The SWAIG function-webhook REQUEST payload — the body a SWAIG function handler
# RECEIVES (swaig_function.execute(raw_data), tool_mixin.on_function_call). STATIC-ONLY:
# it's a plain dict at runtime; this TypedDict types its known shape (conditional fields
# are optional; extra keys are tolerated).
from __future__ import annotations
from typing import Any, Literal, TypedDict


class SwaigArgument(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    parsed: list[Any]
    raw: str
    substituted: str


class SwaigRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai_session_id: str
    app_name: str
    args: str
    argument: SwaigArgument
    argument_desc: dict[str, Any]
    call_id: str
    call_log: list[Any]
    caller_id_name: str
    caller_id_num: str
    channel_active: bool
    channel_offhook: bool
    channel_ready: bool
    content_disposition: Literal["SWAIG Function"]
    content_type: Literal["text/swaig"]
    conversation_id: str
    description: str
    error_reason: str
    fatal_error: bool
    function: str
    global_data: dict[str, Any]
    input: str
    meta_data: dict[str, Any]
    meta_data_token: str
    project_id: str
    raw_call_log: list[Any]
    space_id: str
    version: Literal["2.0"]
