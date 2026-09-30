# AUTO-GENERATED from porting-sdk/rest-apis/calling/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

import uuid as _uuid
from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import BaseResource, _required_via_extras

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .calling_types_generated import (
        CallResponse,
        RelayCallCollectDigitsInner,
        RelayCallCollectSpeechInner,
        RelayCallDetectInner,
        RelayCallPlayInner,
        RelayCallRecordAudio,
        RelayCallRecordInner,
        RelayCallReferDevice,
        RelayCallTapDevice,
        RelayIsReset,
        RelayTap,
        SWMLObject,
        uuid,
    )


class Calling(BaseResource):
    """Typed resource for ``/calls`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/calling/calls")

    @_required_via_extras("to", from_="from")
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
        to_script: str | dict[str, Any] | None = None,
        timeout: int | None = None,
        max_price_per_minute: float | None = None,
        send_digits: str | None = None,
        region: str | list[str] | None = None,
        username: str | None = None,
        password: str | None = None,
        headers: list[dict[str, Any]] | None = None,
        custom_variables: dict[str, str] | None = None,
        url: str | None = None,
        codecs: list[str] | str | None = None,
        swml: str | dict[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
                "to_script": to_script,
                "timeout": timeout,
                "max_price_per_minute": max_price_per_minute,
                "send_digits": send_digits,
                "region": region,
                "username": username,
                "password": password,
                "headers": headers,
                "custom_variables": custom_variables,
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

    @_required_via_extras("id")
    def update(
        self,
        *,
        id: uuid,
        fallback_url: str | None = None,
        status: Literal["canceled", "completed"] | None = None,
        status_url: str | None = None,
        url: str | None = None,
        swml: str | dict[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        reason: Literal["hangup", "cancel", "busy", "noAnswer", "decline", "error"]
        | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        prompt: str | None = None,
        timeout: str | float | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v
            for k, v in {"prompt": prompt, "timeout": timeout}.items()
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
        global_data: dict[str, Any] | None = None,
        message_text: str | None = None,
        reset: RelayIsReset | None = None,
        role: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "global_data": global_data,
                "message_text": message_text,
                "reset": reset,
                "role": role,
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

    @_required_via_extras("action")
    def live_transcribe(
        self,
        call_id: str,
        *,
        action: Literal["start", "stop", "summarize"] | dict[str, Any],
        hints: list[Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v for k, v in {"action": action, "hints": hints}.items() if v is not None
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

    @_required_via_extras("action")
    def live_translate(
        self,
        call_id: str,
        *,
        action: Literal["start", "stop", "summarize", "inject"] | dict[str, Any],
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("dest")
    def transfer(
        self,
        call_id: str,
        *,
        dest: str | SWMLObject,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("event")
    def user_event(
        self,
        call_id: str,
        *,
        event: dict[str, Any],
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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

    @_required_via_extras("play")
    def play(
        self,
        call_id: str,
        *,
        play: list[RelayCallPlayInner],
        control_id: str | None = None,
        direction: Literal["listen", "speak", "both"] | None = None,
        gender: Literal["male", "female"] | None = None,
        language: str | None = None,
        loop: int | None = None,
        status_url: str | None = None,
        voice: str | None = None,
        volume: float | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "control_id": control_id,
                "direction": direction,
                "gender": gender,
                "language": language,
                "loop": loop,
                "play": play,
                "status_url": status_url,
                "voice": voice,
                "volume": volume,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        params.setdefault("control_id", str(_uuid.uuid4()))
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

    @_required_via_extras("control_id")
    def play_pause(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("control_id")
    def play_resume(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("control_id")
    def play_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("control_id", "volume")
    def play_volume(
        self,
        call_id: str,
        *,
        control_id: str,
        volume: float,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        record: RelayCallRecordInner | None = None,
        status_url: str | None = None,
        audio: RelayCallRecordAudio | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "control_id": control_id,
                "record": record,
                "status_url": status_url,
            }.items()
            if v is not None
        }
        if audio is not None:
            params["record"] = {**params.get("record", {}), "audio": audio}
        if extras:
            params.update(extras)
        params.setdefault("control_id", str(_uuid.uuid4()))
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

    @_required_via_extras("control_id")
    def record_pause(
        self,
        call_id: str,
        *,
        control_id: str,
        behavior: Literal["skip", "silence"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v
            for k, v in {"behavior": behavior, "control_id": control_id}.items()
            if v is not None
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

    @_required_via_extras("control_id")
    def record_resume(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("control_id")
    def record_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        continue_: bool | None = None,
        continuous: bool | None = None,
        control_id: str | None = None,
        digits: RelayCallCollectDigitsInner | None = None,
        initial_timeout: float | None = None,
        partial_results: bool | None = None,
        send_start_of_input: bool | None = None,
        speech: RelayCallCollectSpeechInner | None = None,
        start_input_timers: bool | None = None,
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "continue": continue_,
                "continuous": continuous,
                "control_id": control_id,
                "digits": digits,
                "initial_timeout": initial_timeout,
                "partial_results": partial_results,
                "send_start_of_input": send_start_of_input,
                "speech": speech,
                "start_input_timers": start_input_timers,
                "status_url": status_url,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        params.setdefault("control_id", str(_uuid.uuid4()))
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

    @_required_via_extras("control_id")
    def collect_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("control_id")
    def collect_start_input_timers(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("detect")
    def detect(
        self,
        call_id: str,
        *,
        detect: RelayCallDetectInner,
        control_id: str | None = None,
        status_url: str | None = None,
        timeout: float | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "control_id": control_id,
                "detect": detect,
                "status_url": status_url,
                "timeout": timeout,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        params.setdefault("control_id", str(_uuid.uuid4()))
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

    @_required_via_extras("control_id")
    def detect_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("device", "tap")
    def tap(
        self,
        call_id: str,
        *,
        device: RelayCallTapDevice,
        tap: RelayTap,
        control_id: str | None = None,
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "control_id": control_id,
                "device": device,
                "status_url": status_url,
                "tap": tap,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        params.setdefault("control_id", str(_uuid.uuid4()))
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

    @_required_via_extras("control_id")
    def tap_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("url")
    def stream(
        self,
        call_id: str,
        *,
        url: str,
        authorization_bearer_token: str | None = None,
        codec: str | None = None,
        control_id: str | None = None,
        custom_parameters: dict[str, Any] | None = None,
        name: str | None = None,
        status_url: str | None = None,
        status_url_method: Literal["GET", "POST"] | None = None,
        track: Literal["inbound_track", "outbound_track", "both_tracks"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v
            for k, v in {
                "authorization_bearer_token": authorization_bearer_token,
                "codec": codec,
                "control_id": control_id,
                "custom_parameters": custom_parameters,
                "name": name,
                "status_url": status_url,
                "status_url_method": status_url_method,
                "track": track,
                "url": url,
            }.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        params.setdefault("control_id", str(_uuid.uuid4()))
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

    @_required_via_extras("control_id")
    def stream_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        params: dict[str, Any] = {
            k: v
            for k, v in {"control_id": control_id, "status_url": status_url}.items()
            if v is not None
        }
        if extras:
            params.update(extras)
        params.setdefault("control_id", str(_uuid.uuid4()))
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

    @_required_via_extras("control_id")
    def transcribe_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        control_id: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("lang")
    def ai_sidecar(
        self,
        call_id: str,
        *,
        lang: str,
        SWAIG: dict[str, Any] | None = None,
        action: dict[str, Any] | None = None,
        customer_role: Literal["remote-caller", "local-caller"] | None = None,
        direction: list[Literal["remote-caller", "local-caller"]] | None = None,
        global_data: dict[str, Any] | None = None,
        hints: list[str] | None = None,
        model: str | None = None,
        params: dict[str, Any] | None = None,
        permissions: dict[str, Any] | None = None,
        prompt: dict[str, Any] | str | None = None,
        url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        command_params: dict[str, Any] = {
            k: v
            for k, v in {
                "SWAIG": SWAIG,
                "action": action,
                "customer_role": customer_role,
                "direction": direction,
                "global_data": global_data,
                "hints": hints,
                "lang": lang,
                "model": model,
                "params": params,
                "permissions": permissions,
                "prompt": prompt,
                "url": url,
            }.items()
            if v is not None
        }
        if extras:
            command_params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.ai_sidecar",
            "params": command_params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("text")
    def ai_sidecar_ask(
        self,
        call_id: str,
        *,
        text: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v for k, v in {"text": text}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.ai_sidecar.ask",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("text")
    def ai_sidecar_poke(
        self,
        call_id: str,
        *,
        text: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {
            k: v for k, v in {"text": text}.items() if v is not None
        }
        if extras:
            params.update(extras)
        body: dict[str, Any] = {
            "command": "calling.ai_sidecar.poke",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def ai_sidecar_stop(
        self,
        call_id: str,
        *,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {}
        body: dict[str, Any] = {
            "command": "calling.ai_sidecar.stop",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def ai_sidecar_status(
        self,
        call_id: str,
        *,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> CallResponse:
        params: dict[str, Any] = {}
        body: dict[str, Any] = {
            "command": "calling.ai_sidecar.status",
            "params": params,
            "id": call_id,
        }
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("control_id")
    def send_fax_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("control_id")
    def receive_fax_stop(
        self,
        call_id: str,
        *,
        control_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    @_required_via_extras("device")
    def refer(
        self,
        call_id: str,
        *,
        device: RelayCallReferDevice,
        status_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
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
        return cast(
            "CallResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )
