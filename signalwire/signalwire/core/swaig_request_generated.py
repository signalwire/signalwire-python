# AUTO-GENERATED from porting-sdk/swaig-specs/swaig-request.yaml — DO NOT EDIT.
# (vendored from mod_openai; regenerate via
#  python3 porting-sdk/scripts/generate_python_rest_types.py)
"""TypedDicts for the SWAIG function-webhook request payload.

The body a SWAIG function handler receives (``swaig_function.execute(raw_data)``,
``tool_mixin.on_function_call``). Static-only: a plain ``dict`` at runtime; this
``TypedDict`` types its known shape (conditional fields are optional; extra keys are
tolerated).
"""

from __future__ import annotations
from typing import Any, Literal, TypedDict


class SwaigArgument(TypedDict, total=False):
    """Always present.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        parsed: JSON objects parsed from the model's argument string (always an array,
            possibly empty).
        raw: The original argument string.
        substituted: The argument string with JSON blocks replaced.
    """

    parsed: list[Any]
    raw: str
    substituted: str


class SwaigRequest(TypedDict, total=False):
    """The SWAIG function-webhook request payload.

    Open shape: conditional fields appear only when their precondition holds.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        ai_session_id: Always present.
        app_name: Always present.
        args: added **only on the data_map path**. `args` is `argument.parsed[0]`
            promoted to the top level; `input` is a shallow self-duplicate of the
            post_data. The webhook-URL path does not add these.
        argument: Always present.
        argument_desc: Always present.
        call_id: Always present.
        call_log: only if `swaig_post_conversation` is set. `call_log` is redacted when
            `redact_prompt` is enabled; `raw_call_log` is the full transcript.
        caller_id_name: only if the caller-ID channel vars are set. The source channel
            var for `caller_id_num` is `caller_id_number` — the JSON key is renamed to
            `caller_id_num`.
        caller_id_num: only if the caller-ID channel vars are set. The source channel
            var for `caller_id_num` is `caller_id_number` — the JSON key is renamed to
            `caller_id_num`.
        channel_active: Always present.
        channel_offhook: Always present.
        channel_ready: Always present.
        content_disposition: Always present.
        content_type: Always present.
        conversation_id: only if configured.
        description: Always present.
        error_reason: only on a hangup-hook/error invocation when `fatal_error_reason`
            is set.
        fatal_error: only on a hangup-hook/error invocation when `fatal_error_reason` is
            set.
        function: Always present.
        global_data: only if global data exists.
        input: added **only on the data_map path**. `args` is `argument.parsed[0]`
            promoted to the top level; `input` is a shallow self-duplicate of the
            post_data. The webhook-URL path does not add these.
        meta_data: only if the function has a `meta_data_token`. `meta_data` is that
            token's metadata store (empty object if none).
        meta_data_token: only if the function has a `meta_data_token`. `meta_data` is
            that token's metadata store (empty object if none).
        project_id: only if the `signalwire_project_id` / `signalwire_space_id` channel
            vars are set.
        raw_call_log: only if `swaig_post_conversation` is set. `call_log` is redacted
            when `redact_prompt` is enabled; `raw_call_log` is the full transcript.
        space_id: only if the `signalwire_project_id` / `signalwire_space_id` channel
            vars are set.
        version: Always present.
    """

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
