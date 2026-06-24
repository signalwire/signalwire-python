"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

MFA (Multi-Factor Authentication) namespace.
"""

from typing import TYPE_CHECKING, Any

from .._base import BaseResource

if TYPE_CHECKING:
    from .relay_rest_types_generated import (
        MfaResponse,
        MfaVerifyResponse,
    )


class MfaResource(BaseResource):
    """Multi-factor authentication via SMS or phone call."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/mfa")

    def sms(self, **kwargs: Any) -> "MfaResponse":
        return self._http.post(self._path("sms"), body=kwargs)

    def call(self, **kwargs: Any) -> "MfaResponse":
        return self._http.post(self._path("call"), body=kwargs)

    def verify(self, request_id: str, **kwargs: Any) -> "MfaVerifyResponse":
        return self._http.post(self._path(request_id, "verify"), body=kwargs)
