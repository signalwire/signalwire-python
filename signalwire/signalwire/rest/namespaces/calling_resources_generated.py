# AUTO-GENERATED from porting-sdk/rest-apis/calling/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``calling`` REST resources, generated from the OpenAPI spec.

One resource class per spec collection: closed, typed ``create`` / ``update``
parameters (the explicit spec fields) and typed sub-operation methods, plus an
``extras`` escape hatch and a ``**_reserved_kw`` tail for unknown or reserved-word
wire fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import BaseResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .calling_types_generated import (
        CallAIMessageResetParams,
        CallResponse,
        HangupReason,
        LiveTranscribeStartAction,
        LiveTranscribeStopAction,
        LiveTranscribeSummarizeAction,
        LiveTranslateInjectAction,
        LiveTranslateStartAction,
        LiveTranslateStopAction,
        LiveTranslateSummarizeAction,
        SWMLObject,
        uuid,
    )


class Calling(BaseResource):
    """Typed resource for ``/calls`` (generated).

    Bound to ``/api/calling/calls``; construct it as ``Calling(http)`` with the client's
    HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/calling/calls")

    def dial(
        self,
        *,
        from_: str,
        to: str,
        caller_id: str | None = None,
        fallback_url: str | None = None,
        status_url: str | None = None,
        status_events: list[
            Literal["answered", "queued", "initiated", "ringing", "ending", "ended"]
        ]
        | None = None,
        url_method: str | None = None,
        url: str | None = None,
        codecs: list[str] | str | None = None,
        swml: SWMLObject | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``dial`` command.

        Args:
            from_: The address that initiated the call. Can be either a E.164 formatted
                number (`+xxxxxxxxxxx`), or a SIP endpoint (`sip:xxx@yyy.zzz`). Sent as
                the wire key ``from``.
            to: The address that received the call. Can be either a E.164 formatted
                number (`+xxxxxxxxxxx`), or a SIP endpoint (`sip:xxx@yyy.zzz`).
            caller_id: The number, in E.164 format, or identifier of the caller.
            fallback_url: The Fallback URL to handle the call. This parameter allows you
                to specify a backup webhook or different route in your code containing
                SWML instructions for handling the call.
            status_url: A URL that will recieve status updates of the current call. Any
                call events defined in `status_events` will be delivered to the defined
                URL.
            status_events: The call events that will be monitored and sent to the
                `status_url` when active.
            url_method: The HTTP method to use when requesting the URL.
            url: The URL to handle the call. This parameter allows you to specify a
                webhook or different route in your code containing SWML instructions for
                handling the call. Either `url` or `swml` must be included for a new
                call.
            codecs: A list of codecs to use for the call. Can be an array of codec
                strings or a comma-separated string. Valid codecs are: `PCMU`, `PCMA`,
                `G722`, `G729`, `OPUS`, `VP8`, `H264`. For PSTN calls, `PCMA` and `PCMU`
                are recommended as many other codecs are not supported by PSTN gateways.
                If a SIP URI with included codecs is passed in the `to` field along with
                this parameter, the SIP URI codecs will be prioritized.
            swml: Inline SWML object containing SWML instructions for handling the call.
                Either `url` or `swml` must be included for a new call.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "from": from_,
                "to": to,
                "caller_id": caller_id,
                "fallback_url": fallback_url,
                "status_url": status_url,
                "status_events": status_events,
                "url_method": url_method,
                "url": url,
                "codecs": codecs,
                "swml": swml,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {"command": "dial", "params": params}
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        *,
        id: uuid,
        fallback_url: str | None = None,
        status: Literal["canceled", "completed"] | None = None,
        status_url: str | None = None,
        url: str | None = None,
        swml: SWMLObject | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``update`` command.

        Args:
            id: The unique identifying ID of a existing call.
            fallback_url: The Fallback URL to handle the call. This parameter allows you
                to specify a backup webhook or different route in your code containing
                SWML instructions for handling the call.
            status: Either `canceled` (to cancel a not yet connected call) or
                `completed` (to end a call that is in progress).
            status_url: A URL to receive call status update callbacks.
            url: The URL to handle the call. This parameter allows you to specify a
                webhook or different route in your code containing SWML instructions for
                handling the call. Either `url` or `swml` must be included for a new
                call.
            swml: Inline SWML object containing SWML instructions for handling the call.
                Either `url` or `swml` must be included for a new call.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "id": id,
                "fallback_url": fallback_url,
                "status": status,
                "status_url": status_url,
                "url": url,
                "swml": swml,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {"command": "update", "params": params}
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def end(
        self,
        call_id: str,
        *,
        reason: HangupReason | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.end`` command.

        Args:
            call_id: The unique identifying ID of a existing call.
            reason: Set the reason why the call was hung up.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"reason": reason}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.end",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def ai_hold(
        self,
        call_id: str,
        *,
        timeout: int | None = None,
        prompt: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.ai_hold`` command.

        Args:
            call_id: The unique identifying ID of a existing call.
            timeout: The duration to hold the caller in seconds.
            prompt: A system message added to the AI conversation before placing the
                caller on hold. The AI will speak this message to the caller before hold
                music begins.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {"timeout": timeout, "prompt": prompt}.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.ai_hold",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def ai_unhold(
        self,
        call_id: str,
        *,
        prompt: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.ai_unhold`` command.

        Args:
            call_id: The unique identifying ID of a existing call.
            prompt: A system message added to the AI conversation when taking the caller
                off hold. The AI will use this context when resuming the conversation.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"prompt": prompt}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.ai_unhold",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def ai_message(
        self,
        call_id: str,
        *,
        role: Literal["system", "user", "assistant"] | None = None,
        message_text: str | None = None,
        reset: CallAIMessageResetParams | None = None,
        global_data: dict[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.ai_message`` command.

        Args:
            call_id: The unique identifying ID of a existing call.
            role: The role that the message is from. Required when `reset` is not
                provided. Each role type has a different purpose and will influence how
                the AI will interpret the message.
                - `system`: Inject instructions or context that modify the AI's behavior
                  mid-conversation without the caller hearing it. This could change the
                  AI's personality, add new constraints, provide context about the
                  conversation, or give the AI information it should know going forward.
                - `user`: Inject a message as if the caller said it. This would appear
                  in the conversation history as coming from the caller, and the AI
                  would respond to it as if the caller just spoke it.
                - `assistant`: Inject a message as if the AI said it. This would appear
                  as an AI response in the conversation history. The AI would treat this
                  as its own previous response when generating future replies.
            message_text: The text content that will be sent to the AI. Required when
                `reset` is not provided.
            reset: Parameters for resetting the AI conversation state. When provided,
                `role` and `message_text` are optional.
            global_data: Arbitrary JSON data to merge into the AI session's global data
                store.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "role": role,
                "message_text": message_text,
                "reset": reset,
                "global_data": global_data,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.ai_message",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def live_transcribe(
        self,
        call_id: str,
        *,
        action: LiveTranscribeStartAction
        | LiveTranscribeSummarizeAction
        | LiveTranscribeStopAction,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.live_transcribe`` command.

        Args:
            call_id: The unique identifying ID of a existing call.
            action: The transcription action to perform: start, stop, or summarize.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"action": action}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.live_transcribe",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def live_translate(
        self,
        call_id: str,
        *,
        action: LiveTranslateStartAction
        | LiveTranslateSummarizeAction
        | LiveTranslateInjectAction
        | LiveTranslateStopAction,
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.live_translate`` command.

        Args:
            call_id: The unique identifying ID of a existing call.
            action: The translation action to perform: start, stop, summarize, or
                inject.
            status_url: A URL to receive status update callbacks for the translation
                session.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {"action": action, "status_url": status_url}.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.live_translate",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def transfer(
        self,
        call_id: str,
        *,
        dest: str | SWMLObject,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.transfer`` command.

        Args:
            call_id: The unique identifying ID of a existing call.
            dest: The destination to transfer the call to. Can be a SIP URI, phone
                number, or an inline SWML object.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"dest": dest}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.transfer",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def user_event(
        self,
        call_id: str,
        *,
        event: dict[str, Any],
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.user_event`` command.

        Args:
            call_id: The unique identifying ID of a existing call.
            event: Arbitrary JSON event data to fire on the call.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"event": event}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.user_event",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def disconnect(
        self,
        call_id: str,
        *,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.disconnect`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {}
        body: dict[str, Any] = {
            "command": "calling.disconnect",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def play(
        self,
        call_id: str,
        *,
        play: list[dict[str, Any]],
        control_id: str | None = None,
        volume: float | None = None,
        direction: Literal["listen", "speak", "both"] | None = None,
        loop: int | None = None,
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.play`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            play: Array of media objects to play.
            control_id: Unique identifier for this play operation. Auto-generated if not
                provided.
            volume: Volume adjustment in dB. 0 is default.
            direction: Which leg of the call to play to.
            loop: Number of times to loop. 0 means infinite.
            status_url: Webhook URL for play state events.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "control_id": control_id,
                "play": play,
                "volume": volume,
                "direction": direction,
                "loop": loop,
                "status_url": status_url,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.play",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def play_pause(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.play.pause`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the play operation to pause.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.play.pause",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def play_resume(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.play.resume`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the play operation to resume.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.play.resume",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def play_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.play.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the play operation to stop.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.play.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def play_volume(
        self,
        call_id: str,
        *,
        control_id: str,
        volume: float,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.play.volume`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the play operation.
            volume: Volume adjustment in dB.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {"control_id": control_id, "volume": volume}.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.play.volume",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def record(
        self,
        call_id: str,
        *,
        control_id: str | None = None,
        audio: dict[str, Any] | None = None,
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.record`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: Unique identifier for this recording. Auto-generated if not
                provided.
            audio: Audio recording parameters.
            status_url: Webhook URL for recording state events.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "control_id": control_id,
                "audio": audio,
                "status_url": status_url,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.record",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def record_pause(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.record.pause`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the recording to pause.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.record.pause",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def record_resume(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.record.resume`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the recording to resume.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.record.resume",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def record_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.record.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the recording to stop.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.record.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def collect(
        self,
        call_id: str,
        *,
        control_id: str | None = None,
        initial_timeout: float | None = None,
        digits: dict[str, Any] | None = None,
        speech: dict[str, Any] | None = None,
        continuous: bool | None = None,
        partial_results: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.collect`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: Unique identifier for this collect operation.
            initial_timeout: Seconds to wait for first input before timeout.
            digits: DTMF digit collection parameters.
            speech: Speech recognition parameters.
            continuous: Keep collecting after each result.
            partial_results: Deliver partial recognition results.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "control_id": control_id,
                "initial_timeout": initial_timeout,
                "digits": digits,
                "speech": speech,
                "continuous": continuous,
                "partial_results": partial_results,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.collect",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def collect_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.collect.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the collect operation to stop.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.collect.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def collect_start_input_timers(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.collect.start_input_timers`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the collect operation.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.collect.start_input_timers",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def detect(
        self,
        call_id: str,
        *,
        detect: dict[str, Any],
        control_id: str | None = None,
        timeout: float | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.detect`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            detect: Detection configuration.
            control_id: Unique identifier for this detect operation.
            timeout: Overall timeout in seconds for the detect operation.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "control_id": control_id,
                "detect": detect,
                "timeout": timeout,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.detect",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def detect_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.detect.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the detect operation to stop.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.detect.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def tap(
        self,
        call_id: str,
        *,
        tap: dict[str, Any],
        device: dict[str, Any],
        control_id: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.tap`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            tap: What to tap.
            device: Target device to send tapped audio to.
            control_id: Unique identifier for this tap operation.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {"control_id": control_id, "tap": tap, "device": device}.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.tap",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def tap_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.tap.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the tap operation to stop.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.tap.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def stream(
        self,
        call_id: str,
        *,
        url: str,
        control_id: str | None = None,
        codec: str | None = None,
        track: Literal["inbound_track", "outbound_track", "both_tracks"] | None = None,
        authorization_bearer_token: str | None = None,
        custom_parameters: dict[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.stream`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            url: WebSocket URL (wss://) to stream audio to.
            control_id: Unique identifier for this stream operation.
            codec: Audio codec for the stream.
            track: Which audio track(s) to stream.
            authorization_bearer_token: Bearer token sent in the WebSocket handshake.
            custom_parameters: Custom key-value pairs sent with the stream.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "control_id": control_id,
                "url": url,
                "codec": codec,
                "track": track,
                "authorization_bearer_token": authorization_bearer_token,
                "custom_parameters": custom_parameters,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.stream",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def stream_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.stream.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the stream to stop.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.stream.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def denoise(
        self,
        call_id: str,
        *,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.denoise`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {}
        body: dict[str, Any] = {
            "command": "calling.denoise",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def denoise_stop(
        self,
        call_id: str,
        *,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.denoise.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {}
        body: dict[str, Any] = {
            "command": "calling.denoise.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def transcribe(
        self,
        call_id: str,
        *,
        control_id: str | None = None,
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.transcribe`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: Unique identifier for this transcription.
            status_url: Webhook URL for transcription results.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {"control_id": control_id, "status_url": status_url}.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.transcribe",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def transcribe_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.transcribe.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the transcription to stop.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.transcribe.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def ai_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.ai.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the AI session to stop.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.ai.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def send_fax_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.send_fax.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the fax send to stop.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.send_fax.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def receive_fax_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.receive_fax.stop`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            control_id: The control_id of the fax receive to stop.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v for k, v in {"control_id": control_id}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.receive_fax.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def refer(
        self,
        call_id: str,
        *,
        device: dict[str, Any],
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        """Send the ``calling.refer`` command.

        Args:
            call_id: The unique identifying ID of an existing call.
            device: Target device for the REFER.
            status_url: Webhook URL for REFER state events.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The call state after the command.
        """
        params: dict[str, Any] = {
            k: v
            for k, v in {"device": device, "status_url": status_url}.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.refer",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )
