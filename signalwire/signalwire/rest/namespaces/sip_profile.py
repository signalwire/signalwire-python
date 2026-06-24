"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

SIP Profile namespace — get and update project SIP profile.
"""

from typing import TYPE_CHECKING, Any

from .._base import BaseResource

if TYPE_CHECKING:
    from .relay_rest_types_generated import SipProfileResponse


class SipProfileResource(BaseResource):
    """Project SIP profile (singleton resource)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/sip_profile")

    def get(self) -> "SipProfileResponse":
        return self._http.get(self._base_path)

    def update(self, **kwargs: Any) -> "SipProfileResponse":
        return self._http.put(self._base_path, body=kwargs)
