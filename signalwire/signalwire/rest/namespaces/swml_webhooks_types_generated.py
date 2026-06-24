# AUTO-GENERATED from porting-sdk/rest-apis/swml-webhooks/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Any, TypedDict


class SwaigRequestData(TypedDict, total=False):
    """Body POSTed to a SWAIG function's web_hook_url when the AI invokes it.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    parsed: list[dict[str, Any]]
    raw: str
    substituted: str


class PostPromptData(TypedDict, total=False):
    """Body POSTed to post_prompt_url at the end of an AI call — the calling.call.ai.complete event envelope.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    event_type: str
    event_channel: str
    timestamp: float
    project_id: str
    space_id: str
    params: PostPromptParams


class PostPromptParams(TypedDict, total=False):
    """The AI-completion payload carried by a post-prompt webhook.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
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

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    role: str
    content: str


class PostPromptFunctionCall(TypedDict, total=False):
    """A function the AI called during the conversation, as reported post-prompt.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    function: str
    params: dict[str, Any]
    result: dict[str, Any]


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
