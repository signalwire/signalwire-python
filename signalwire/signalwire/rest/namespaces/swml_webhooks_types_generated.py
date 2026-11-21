# AUTO-GENERATED from porting-sdk/rest-apis/swml-webhooks/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``swml-webhooks`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Any, TypedDict


class SwaigRequestData(TypedDict, total=False):
    """Body POSTed to a SWAIG function's web_hook_url when the AI invokes it.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        call_id: Unique identifier for the call.
        ai_session_id: Identifier for the AI session.
        app_name: Application name (e.g. "swml").
        project_id: Your SignalWire project UUID.
        space_id: Your SignalWire space UUID.
        action: The function name being invoked.
        function: The function name (same as action).
        meta_data: Custom metadata from SWAIG.defaults.meta_data.
        conversation_id: Identifier for the conversation thread.
        content_type: Content type identifier (e.g. "text/swaig").
        version: SWAIG protocol version (e.g. "2.0").
    """

    call_id: str
    ai_session_id: str
    app_name: str
    project_id: str
    space_id: str
    action: str
    function: str
    argument: SwaigArgument
    meta_data: dict[str, Any]
    conversation_id: str
    content_type: str
    version: str


class SwaigArgument(TypedDict, total=False):
    """The arguments the AI extracted for a SWAIG function call.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        parsed: Structured argument data as JSON objects.
        raw: Raw argument string from the AI.
        substituted: Argument with variable substitutions applied.
    """

    parsed: list[dict[str, Any]]
    raw: str
    substituted: str


class PostPromptData(TypedDict, total=False):
    """Body POSTed to post_prompt_url at the end of an AI call — the calling.call.ai.complete event envelope.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    event_type: str
    event_channel: str
    timestamp: float
    project_id: str
    space_id: str
    params: PostPromptParams


class PostPromptParams(TypedDict, total=False):
    """The AI-completion payload carried by a post-prompt webhook.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        summary: The model's conversation summary.
        post_prompt_result: Structured summary requested via post_prompt.
    """

    call_id: str
    ai_session_id: str
    summary: str
    post_prompt_result: dict[str, Any] | str
    end_reason: str
    conversation: list[PostPromptConversationTurn]
    function_calls: list[PostPromptFunctionCall]


class PostPromptConversationTurn(TypedDict, total=False):
    """A single turn in a post-prompt conversation transcript.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    role: str
    content: str


class PostPromptFunctionCall(TypedDict, total=False):
    """A function the AI called during the conversation, as reported post-prompt.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    function: str
    params: dict[str, Any]
    result: dict[str, Any]


class SwmlRequestData(TypedDict, total=False):
    """Body POSTed to a dynamic-SWML request handler.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        vars: SWML variables.
        envs: Environment values.
        params: Request params (query/body merge).
    """

    call: SwmlRequestCall
    vars: dict[str, Any]
    envs: dict[str, Any]
    params: dict[str, Any]


class SwmlRequestCall(TypedDict, total=False):
    """The call object embedded in a dynamic-SWML request.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``)
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
    """Error body returned by the Compatibility REST API (single-error form).

    Source: signalwire/docs specs/compatibility-api/_shared/errors.tsp
    (CompatibilityErrorResponse).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        code: Numeric error code.
        message: Human-readable error message.
        more_info: URL with more information about the error.
        status: HTTP status code.
    """

    code: int
    message: str
    more_info: str
    status: int
