# AUTO-GENERATED from porting-sdk/rest-apis/calling/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import BaseResource

if TYPE_CHECKING:
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
    """Typed resource for ``/calls`` (generated)."""

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
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

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
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def end(
        self,
        call_id: str,
        *,
        reason: HangupReason | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def ai_hold(
        self,
        call_id: str,
        *,
        timeout: int | None = None,
        prompt: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def ai_unhold(
        self,
        call_id: str,
        *,
        prompt: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def ai_message(
        self,
        call_id: str,
        *,
        role: Literal["system", "user", "assistant"] | None = None,
        message_text: str | None = None,
        reset: CallAIMessageResetParams | None = None,
        global_data: dict[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def live_transcribe(
        self,
        call_id: str,
        *,
        action: LiveTranscribeStartAction
        | LiveTranscribeSummarizeAction
        | LiveTranscribeStopAction,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

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
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def transfer(
        self,
        call_id: str,
        *,
        dest: str | SWMLObject,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def user_event(
        self,
        call_id: str,
        *,
        event: dict[str, Any],
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def disconnect(
        self, call_id: str, *, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
        params: dict[str, Any] = {}
        body: dict[str, Any] = {
            "command": "calling.disconnect",
            "params": params,
            "id": call_id,
        }
        return cast("CallResponse", self._http.post(self._base_path, body=body))

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
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def play_pause(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def play_resume(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def play_stop(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def play_volume(
        self,
        call_id: str,
        *,
        control_id: str,
        volume: float,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def record(
        self,
        call_id: str,
        *,
        control_id: str | None = None,
        audio: dict[str, Any] | None = None,
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def record_pause(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def record_resume(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def record_stop(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

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
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def collect_stop(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def collect_start_input_timers(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def detect(
        self,
        call_id: str,
        *,
        detect: dict[str, Any],
        control_id: str | None = None,
        timeout: float | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def detect_stop(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def tap(
        self,
        call_id: str,
        *,
        tap: dict[str, Any],
        device: dict[str, Any],
        control_id: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def tap_stop(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

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
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def stream_stop(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def denoise(
        self, call_id: str, *, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
        params: dict[str, Any] = {}
        body: dict[str, Any] = {
            "command": "calling.denoise",
            "params": params,
            "id": call_id,
        }
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def denoise_stop(
        self, call_id: str, *, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
        params: dict[str, Any] = {}
        body: dict[str, Any] = {
            "command": "calling.denoise.stop",
            "params": params,
            "id": call_id,
        }
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def transcribe(
        self,
        call_id: str,
        *,
        control_id: str | None = None,
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def transcribe_stop(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def ai_stop(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def send_fax_stop(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def receive_fax_stop(
        self, call_id: str, *, control_id: str, extras: Mapping[str, Any] | None = None
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))

    def refer(
        self,
        call_id: str,
        *,
        device: dict[str, Any],
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> CallResponse:
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
        return cast("CallResponse", self._http.post(self._base_path, body=body))
