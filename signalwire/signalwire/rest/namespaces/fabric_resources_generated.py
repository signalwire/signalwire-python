# AUTO-GENERATED from porting-sdk/rest-apis/fabric/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``fabric`` REST resources, generated from the OpenAPI spec.

One resource class per spec collection: closed, typed ``create`` / ``update``
parameters (the explicit spec fields) and typed sub-operation methods, plus an
``extras`` escape hatch and a ``**_reserved_kw`` tail for unknown or reserved-word
wire fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import BaseResource, FabricResource, ReadResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .fabric_types_generated import (
        AIAgentCreateRequest,
        AIAgentListResponse,
        AIAgentResponse,
        AIAgentUpdateRequest,
        AIParams,
        AIPostPrompt,
        AIPostPromptUpdate,
        AIPrompt,
        AIPromptUpdate,
        CXMLScriptCreateRequest,
        CXMLScriptListResponse,
        CXMLScriptResponse,
        CXMLScriptUpdateRequest,
        CXMLWebhookCreateRequest,
        CXMLWebhookListResponse,
        CXMLWebhookResponse,
        CXMLWebhookUpdateRequest,
        CallFlowAddressListResponse,
        CallFlowCreateRequest,
        CallFlowListResponse,
        CallFlowResponse,
        CallFlowUpdateRequest,
        CallFlowVersionDeployRequest,
        CallFlowVersionDeployResponse,
        CallFlowVersionListResponse,
        CallHandlerType,
        Ciphers,
        Codecs,
        ConferenceRoomAddressListResponse,
        ConferenceRoomCreateRequest,
        ConferenceRoomListResponse,
        ConferenceRoomResponse,
        ConferenceRoomUpdateRequest,
        CxmlApplicationAddressListResponse,
        CxmlApplicationListResponse,
        CxmlApplicationResponse,
        DomainApplicationResponse,
        EmbedsTokensResponse,
        Encryption,
        FabricAddress,
        FabricAddressesResponse,
        FreeswitchConnectorCreateRequest,
        FreeswitchConnectorListResponse,
        FreeswitchConnectorResponse,
        FreeswitchConnectorUpdateRequest,
        Hint,
        Languages,
        Layout,
        PhoneRouteResponse,
        Pronounce,
        RelayApplicationCreateRequest,
        RelayApplicationListResponse,
        RelayApplicationResponse,
        RelayApplicationUpdateRequest,
        ResourceAddressListResponse,
        ResourceListResponse,
        ResourceResponse,
        SWAIG,
        SWAIGUpdate,
        SWMLWebhookCreateRequest,
        SWMLWebhookListResponse,
        SWMLWebhookResponse,
        SWMLWebhookUpdateRequest,
        SipEndpointCreateRequest,
        SipEndpointListResponse,
        SipEndpointResponse,
        SipEndpointUpdateRequest,
        SipGatewayListResponse,
        SipGatewayRequest,
        SipGatewayRequestUpdate,
        SipGatewayResponse,
        SubscriberGuestTokenCreateResponse,
        SubscriberInviteTokenCreateResponse,
        SubscriberListResponse,
        SubscriberRefreshTokenResponse,
        SubscriberRequest,
        SubscriberResponse,
        SubscriberSIPEndpoint,
        SubscriberSipEndpointListResponse,
        SubscriberTokenResponse,
        SwmlScriptCreateRequest,
        SwmlScriptListResponse,
        SwmlScriptResponse,
        SwmlScriptUpdateRequest,
        UsedForType,
        jwt,
        uuid,
    )


class FabricAddresses(ReadResource["FabricAddressesResponse", "FabricAddress"]):
    """Typed resource for ``/addresses`` (generated).

    Bound to ``/api/fabric/addresses``; construct it as ``FabricAddresses(http)`` with
    the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/addresses")


class GenericResources(BaseResource):
    """Typed resource for ``/resources`` (generated).

    Bound to ``/api/fabric/resources``; construct it as ``GenericResources(http)`` with
    the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ResourceListResponse:
        """A list of Fabric Resources.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: The number of items per page (1-1000).
                - ``page_token``: Token for cursor-based pagination. Required when
                  page_number > 0.
                - ``type``: Filter resources by type.

        Returns:
            The request has succeeded.
        """
        return cast(
            "ResourceListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ResourceResponse:
        """Returns a Resource by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a Resource.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            The request has succeeded.
        """
        return cast(
            "ResourceResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        """Deletes a Resource by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a Resource.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )

    def list_addresses(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ResourceAddressListResponse:
        """This endpoint is used to retrieve addresses associated with a specific Resource.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: The unique identifier of the Resource.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: The number of items per page (1-1000).
                - ``page_token``: Token for cursor-based pagination. Required when
                  page_number > 0.

        Returns:
            The request has succeeded.
        """
        return cast(
            "ResourceAddressListResponse",
            self._http.get(
                self._path(id, "addresses"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def assign_phone_route(
        self,
        id: str,
        *,
        phone_route_id: uuid,
        handler: UsedForType,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneRouteResponse:
        """This endpoint assigns a specific resource to a phone route, allowing inbound calls & messages to be handled by the resource.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: The unique identifier of the Resource.
            phone_route_id: The id of the phone route.
            handler: Indicates if the resource should be assigned to a `calling` or
                `messaging` handler.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"phone_route_id": phone_route_id, "handler": handler}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneRouteResponse",
            self._http.post(
                self._path(id, "phone_routes"),
                body=body,
                request_options=request_options,
            ),
        )

    def assign_domain_application(
        self,
        id: str,
        *,
        domain_application_id: uuid,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> DomainApplicationResponse:
        """This endpoint assigns a specific resource to a Domain Application, allowing inbound calls to be handled by the resource.

        **Note:** Currently only supports `calling` as a handler and automatically
        defaults to it.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: The unique identifier of the Resource.
            domain_application_id: The id of the domain application you wish to assign a
                resource to.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"domain_application_id": domain_application_id}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "DomainApplicationResponse",
            self._http.post(
                self._path(id, "domain_applications"),
                body=body,
                request_options=request_options,
            ),
        )


class AiAgents(
    FabricResource[
        "AIAgentListResponse",
        "AIAgentResponse",
        "AIAgentCreateRequest",
        "AIAgentUpdateRequest",
    ]
):
    """Typed resource for ``/resources/ai_agents`` (generated).

    Bound to ``/api/fabric/resources/ai_agents``; construct it as ``AiAgents(http)``
    with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/ai_agents")

    def create(  # type: ignore[override]
        self,
        *,
        prompt: AIPrompt,
        name: str,
        global_data: dict[str, Any] | None = None,
        hints: list[str | Hint] | None = None,
        languages: list[Languages] | None = None,
        params: AIParams | None = None,
        post_prompt: AIPostPrompt | None = None,
        post_prompt_url: str | None = None,
        pronounce: list[Pronounce] | None = None,
        SWAIG: SWAIG | None = None,
        agent_id: uuid | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> AIAgentResponse:
        """Creates an AI Agent.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            prompt: Defines the AI agent's personality, goals, behaviors, and
                instructions for handling conversations. The prompt establishes how the
                agent should interact with callers, what information it should gather,
                and how it should respond to various scenarios. It is recommended to
                write prompts using markdown formatting.
            name: Name of the AI Agent.
            global_data: A key-value object for storing data that persists throughout
                the AI session. Can be set initially in the SWML script or modified
                during the conversation using the set_global_data action. The
                global_data object is accessible everywhere in the AI session: prompts,
                AI parameters, and SWML returned from SWAIG functions. Access properties
                using template strings (e.g. ${global_data.property_name}).
            hints: Hints help the AI agent understand certain words or phrases better.
                Words that can commonly be misinterpreted can be added to the hints to
                help the AI speak more accurately.
            languages: An array of JSON objects defining supported languages in the
                conversation.
            params: A JSON object containing parameters as key-value pairs.
            post_prompt: The final set of instructions and configuration settings to
                send to the agent.
            post_prompt_url: The URL to which to send status callbacks and reports.
                Authentication can also be set in the url in the format of
                `username:password@url`.
            pronounce: An array of JSON objects to clarify the AI's pronunciation of
                words or expressions.
            SWAIG: An array of JSON objects to create user-defined functions/endpoints
                that can be executed during the dialogue.
            agent_id: Unique ID of an AI Agent.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "global_data": global_data,
                "hints": hints,
                "languages": languages,
                "params": params,
                "post_prompt": post_prompt,
                "post_prompt_url": post_prompt_url,
                "pronounce": pronounce,
                "prompt": prompt,
                "SWAIG": SWAIG,
                "agent_id": agent_id,
                "name": name,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AIAgentResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        global_data: dict[str, Any] | None = None,
        hints: list[str | Hint] | None = None,
        languages: list[Languages] | None = None,
        params: AIParams | None = None,
        post_prompt: AIPostPromptUpdate | None = None,
        post_prompt_url: str | None = None,
        pronounce: list[Pronounce] | None = None,
        prompt: AIPromptUpdate | None = None,
        SWAIG: SWAIGUpdate | None = None,
        agent_id: uuid | None = None,
        name: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> AIAgentResponse:
        """Updates an AI Agent by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of an AI Agent.
            global_data: A key-value object for storing data that persists throughout
                the AI session. Can be set initially in the SWML script or modified
                during the conversation using the set_global_data action. The
                global_data object is accessible everywhere in the AI session: prompts,
                AI parameters, and SWML returned from SWAIG functions. Access properties
                using template strings (e.g. ${global_data.property_name}).
            hints: Hints help the AI agent understand certain words or phrases better.
                Words that can commonly be misinterpreted can be added to the hints to
                help the AI speak more accurately.
            languages: An array of JSON objects defining supported languages in the
                conversation.
            params: A JSON object containing parameters as key-value pairs.
            post_prompt: The final set of instructions and configuration settings to
                send to the agent.
            post_prompt_url: The URL to which to send status callbacks and reports.
                Authentication can also be set in the url in the format of
                `username:password@url`.
            pronounce: An array of JSON objects to clarify the AI's pronunciation of
                words or expressions.
            prompt: Defines the AI agent's personality, goals, behaviors, and
                instructions for handling conversations. The prompt establishes how the
                agent should interact with callers, what information it should gather,
                and how it should respond to various scenarios. It is recommended to
                write prompts using markdown formatting.
            SWAIG: An array of JSON objects to create user-defined functions/endpoints
                that can be executed during the dialogue.
            agent_id: Unique ID of an AI Agent.
            name: Name of the AI Agent.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "global_data": global_data,
                "hints": hints,
                "languages": languages,
                "params": params,
                "post_prompt": post_prompt,
                "post_prompt_url": post_prompt_url,
                "pronounce": pronounce,
                "prompt": prompt,
                "SWAIG": SWAIG,
                "agent_id": agent_id,
                "name": name,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AIAgentResponse",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class CallFlows(
    FabricResource[
        "CallFlowListResponse",
        "CallFlowResponse",
        "CallFlowCreateRequest",
        "CallFlowUpdateRequest",
    ]
):
    """Typed resource for ``/resources/call_flows`` (generated).

    Bound to ``/api/fabric/resources/call_flows``; construct it as ``CallFlows(http)``
    with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/call_flows")

    def create(  # type: ignore[override]
        self,
        *,
        title: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CallFlowResponse:
        """Creates a Call Flow.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            title: The name of the Call Flow
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v for k, v in {"title": title}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CallFlowResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        title: str | None = None,
        document_version: int | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CallFlowResponse:
        """Updates a Call Flow by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a Call Flow.
            title: The name of the Call Flow
            document_version: The current revision of the call flow. Every update must
                increase this number.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"title": title, "document_version": document_version}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CallFlowResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_addresses(  # type: ignore[override]
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CallFlowAddressListResponse:
        """This endpoint returns a list of addresses associated with a specific Call Flow.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: The unique identifier of the Call Flow.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: The number of items per page (1-1000).
                - ``page_token``: Token for cursor-based pagination. Required when
                  page_number > 0.

        Returns:
            The request has succeeded.
        """
        return cast(
            "CallFlowAddressListResponse",
            self._http.get(
                f"/api/fabric/resources/call_flow/{id}/addresses",
                params=params or None,
                request_options=request_options,
            ),
        )

    def list_versions(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CallFlowVersionListResponse:
        """Returns a list of versions of a Call Flow.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: The unique identifier of the Call Flow.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: The number of items per page (1-1000).
                - ``page_token``: Token for cursor-based pagination. Required when
                  page_number > 0.

        Returns:
            The request has succeeded.
        """
        return cast(
            "CallFlowVersionListResponse",
            self._http.get(
                f"/api/fabric/resources/call_flow/{id}/versions",
                params=params or None,
                request_options=request_options,
            ),
        )

    def deploy_version(
        self,
        id: str,
        body: CallFlowVersionDeployRequest,
        *,
        request_options: RequestOptions | None = None,
    ) -> CallFlowVersionDeployResponse:
        """Deploys a specific version of a Call Flow.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: The unique identifier of the Call Flow.
            body: The request body (a ``CallFlowVersionDeployRequest``).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        return cast(
            "CallFlowVersionDeployResponse",
            self._http.post(
                f"/api/fabric/resources/call_flow/{id}/versions",
                body=body,
                request_options=request_options,
            ),
        )


class ConferenceRooms(
    FabricResource[
        "ConferenceRoomListResponse",
        "ConferenceRoomResponse",
        "ConferenceRoomCreateRequest",
        "ConferenceRoomUpdateRequest",
    ]
):
    """Typed resource for ``/resources/conference_rooms`` (generated).

    Bound to ``/api/fabric/resources/conference_rooms``; construct it as
    ``ConferenceRooms(http)`` with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/conference_rooms")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        enable_room_previews: bool,
        display_name: str | None = None,
        description: str | None = None,
        join_from: str | None = None,
        join_until: str | None = None,
        max_members: int | None = None,
        quality: Literal["1080p", "720p"] | None = None,
        remove_at: str | None = None,
        remove_after_seconds_elapsed: int | None = None,
        layout: Layout | None = None,
        record_on_start: bool | None = None,
        meta: dict[str, Any] | None = None,
        sync_audio_video: bool | None = None,
        tone_on_entry_and_exit: bool | None = None,
        room_join_video_off: bool | None = None,
        user_join_video_off: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> ConferenceRoomResponse:
        """Creates a Conference Room.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            name: The name of the Conference Room
            enable_room_previews: Enables live video room previews for the conference.
            display_name: Display name of the Conference Room
            description: The descrption of the Conference Room
            join_from: The time users are allowed to start joining the conference.
                Joining before this time will result in failure to join the conference.
            join_until: The time users are allowed to until the conference is locked.
                Attempting to join the conference after the set time will result in
                failure to join the conference.
            max_members: Maximum number of members allowed in the conference room
            quality: The viudeo quality of the Conference Room.
            remove_at: The time to remove all participants from the conference.
            remove_after_seconds_elapsed: The amount of time in seconds to remove a
                particpant from a conference after they join.
            layout: The video layout of the conference.
            record_on_start: Starts recording when the conference starts.
            meta: Metadata of the conference.
            sync_audio_video: Syncs the participants audio and video.
            tone_on_entry_and_exit: Plays a tone when a participant joins or leaves the
                conference.
            room_join_video_off: Turns the conference video off when the participant
                joins the room if `true`.
            user_join_video_off: Turns the participants video off when the participant
                joins the room if `true`.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "display_name": display_name,
                "description": description,
                "join_from": join_from,
                "join_until": join_until,
                "max_members": max_members,
                "quality": quality,
                "remove_at": remove_at,
                "remove_after_seconds_elapsed": remove_after_seconds_elapsed,
                "layout": layout,
                "record_on_start": record_on_start,
                "enable_room_previews": enable_room_previews,
                "meta": meta,
                "sync_audio_video": sync_audio_video,
                "tone_on_entry_and_exit": tone_on_entry_and_exit,
                "room_join_video_off": room_join_video_off,
                "user_join_video_off": user_join_video_off,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "ConferenceRoomResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        display_name: str | None = None,
        description: str | None = None,
        join_from: str | None = None,
        join_until: str | None = None,
        max_members: int | None = None,
        quality: Literal["1080p", "720p"] | None = None,
        remove_at: str | None = None,
        remove_after_seconds_elapsed: int | None = None,
        layout: Layout | None = None,
        record_on_start: bool | None = None,
        enable_room_previews: bool | None = None,
        meta: dict[str, Any] | None = None,
        sync_audio_video: bool | None = None,
        tone_on_entry_and_exit: bool | None = None,
        room_join_video_off: bool | None = None,
        user_join_video_off: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> ConferenceRoomResponse:
        """Updates a Conference Room by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a Conference Room.
            name: The name of the Conference Room
            display_name: Display name of the Conference Room
            description: The descrption of the Conference Room
            join_from: The time users are allowed to start joining the conference.
                Joining before this time will result in failure to join the conference.
            join_until: The time users are allowed to until the conference is locked.
                Attempting to join the conference after the set time will result in
                failure to join the conference.
            max_members: Maximum number of members allowed in the conference room
            quality: The viudeo quality of the Conference Room.
            remove_at: The time to remove all participants from the conference.
            remove_after_seconds_elapsed: The amount of time in seconds to remove a
                particpant from a conference after they join.
            layout: The video layout of the conference.
            record_on_start: Starts recording when the conference starts.
            enable_room_previews: Enables live video room previews for the conference.
            meta: Metadata of the conference.
            sync_audio_video: Syncs the participants audio and video.
            tone_on_entry_and_exit: Plays a tone when a participant joins or leaves the
                conference.
            room_join_video_off: Turns the conference video off when the participant
                joins the room if `true`.
            user_join_video_off: Turns the participants video off when the participant
                joins the room if `true`.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "display_name": display_name,
                "description": description,
                "join_from": join_from,
                "join_until": join_until,
                "max_members": max_members,
                "quality": quality,
                "remove_at": remove_at,
                "remove_after_seconds_elapsed": remove_after_seconds_elapsed,
                "layout": layout,
                "record_on_start": record_on_start,
                "enable_room_previews": enable_room_previews,
                "meta": meta,
                "sync_audio_video": sync_audio_video,
                "tone_on_entry_and_exit": tone_on_entry_and_exit,
                "room_join_video_off": room_join_video_off,
                "user_join_video_off": user_join_video_off,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "ConferenceRoomResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_addresses(  # type: ignore[override]
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ConferenceRoomAddressListResponse:
        """This endpoint returns a list of addresses associated with a specific Conference Room.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: The unique identifier of the Conference Room.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: The number of items per page (1-1000).
                - ``page_token``: Token for cursor-based pagination. Required when
                  page_number > 0.

        Returns:
            The request has succeeded.
        """
        return cast(
            "ConferenceRoomAddressListResponse",
            self._http.get(
                f"/api/fabric/resources/conference_room/{id}/addresses",
                params=params or None,
                request_options=request_options,
            ),
        )


class CxmlApplications(BaseResource):
    """Typed resource for ``/resources/cxml_applications`` (generated).

    Bound to ``/api/fabric/resources/cxml_applications``; construct it as
    ``CxmlApplications(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/cxml_applications")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CxmlApplicationListResponse:
        """A list of cXML Applications.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: The number of items per page (1-1000).
                - ``page_token``: Token for cursor-based pagination. Required when
                  page_number > 0.

        Returns:
            The request has succeeded.
        """
        return cast(
            "CxmlApplicationListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CxmlApplicationResponse:
        """Returns a cXML Application by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a cXML Application.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            The request has succeeded.
        """
        return cast(
            "CxmlApplicationResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        *,
        display_name: str | None = None,
        account_sid: uuid | None = None,
        voice_url: str | None = None,
        voice_method: Literal["GET"] | Literal["POST"] | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        sms_url: str | None = None,
        sms_method: Literal["GET"] | Literal["POST"] | None = None,
        sms_fallback_url: str | None = None,
        sms_fallback_method: Literal["GET"] | Literal["POST"] | None = None,
        sms_status_callback: str | None = None,
        sms_status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CxmlApplicationResponse:
        """Updates a cXML Application by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a cXML Application.
            display_name: Display name of the cXML Application
            account_sid: Project ID for the cXML Application
            voice_url: URL to handle incoming calls
            voice_method: HTTP method for voice URL
            voice_fallback_url: Fallback URL for voice errors
            voice_fallback_method: HTTP method for voice fallback URL
            status_callback: URL to receive status callbacks
            status_callback_method: HTTP method for status callbacks
            sms_url: URL to handle incoming messages
            sms_method: HTTP method for SMS URL
            sms_fallback_url: Fallback URL for SMS errors
            sms_fallback_method: HTTP method for SMS fallback URL
            sms_status_callback: URL to receive SMS status callbacks
            sms_status_callback_method: HTTP method for SMS status callbacks
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "account_sid": account_sid,
                "voice_url": voice_url,
                "voice_method": voice_method,
                "voice_fallback_url": voice_fallback_url,
                "voice_fallback_method": voice_fallback_method,
                "status_callback": status_callback,
                "status_callback_method": status_callback_method,
                "sms_url": sms_url,
                "sms_method": sms_method,
                "sms_fallback_url": sms_fallback_url,
                "sms_fallback_method": sms_fallback_method,
                "sms_status_callback": sms_status_callback,
                "sms_status_callback_method": sms_status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CxmlApplicationResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        """Deletes a LAML Application by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a cXML Application.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )

    def list_addresses(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CxmlApplicationAddressListResponse:
        """This endpoint returns a list of addresses associated with a specific LaML Application.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: The unique identifier of the cXML Application.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: The number of items per page (1-1000).
                - ``page_token``: Token for cursor-based pagination. Required when
                  page_number > 0.

        Returns:
            The request has succeeded.
        """
        return cast(
            "CxmlApplicationAddressListResponse",
            self._http.get(
                self._path(id, "addresses"),
                params=params or None,
                request_options=request_options,
            ),
        )


class CxmlScripts(
    FabricResource[
        "CXMLScriptListResponse",
        "CXMLScriptResponse",
        "CXMLScriptCreateRequest",
        "CXMLScriptUpdateRequest",
    ]
):
    """Typed resource for ``/resources/cxml_scripts`` (generated).

    Bound to ``/api/fabric/resources/cxml_scripts``; construct it as
    ``CxmlScripts(http)`` with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/cxml_scripts")

    def create(  # type: ignore[override]
        self,
        *,
        display_name: str,
        contents: str,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CXMLScriptResponse:
        """Creates a cXML Script.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            display_name: Display name of the cXML Script
            contents: The cXML script contents
            status_callback_url: URL to send status callbacks to
            status_callback_method: HTTP method to use for status callbacks
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "contents": contents,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CXMLScriptResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        display_name: str | None = None,
        contents: str | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CXMLScriptResponse:
        """Updates a cXML Script by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a cXML Script.
            display_name: Display name of the cXML Script
            contents: The cXML script contents
            status_callback_url: URL to send status callbacks to
            status_callback_method: HTTP method to use for status callbacks
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "contents": contents,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CXMLScriptResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class CxmlWebhooks(
    FabricResource[
        "CXMLWebhookListResponse",
        "CXMLWebhookResponse",
        "CXMLWebhookCreateRequest",
        "CXMLWebhookUpdateRequest",
    ]
):
    """Typed resource for ``/resources/cxml_webhooks`` (generated).

    Bound to ``/api/fabric/resources/cxml_webhooks``; construct it as
    ``CxmlWebhooks(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/cxml_webhooks")

    def create(  # type: ignore[override]
        self,
        *,
        primary_request_url: str,
        name: str | None = None,
        used_for: UsedForType | None = None,
        primary_request_method: Literal["GET"] | Literal["POST"] | None = None,
        fallback_request_url: str | None = None,
        fallback_request_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CXMLWebhookResponse:
        """Creates an cXML Webhook.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            primary_request_url: Primary request url of the CXML Webhook.
            name: Name of the CXML Webhook.
            used_for: Used for of the CXML Webhook.
            primary_request_method: Primary request method of the CXML Webhook.
            fallback_request_url: Fallback request url of the CXML Webhook.
            fallback_request_method: Fallback request method of the CXML Webhook.
            status_callback_url: Status callback url of the CXML Webhook.
            status_callback_method: Status callback method of the CXML Webhook.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "used_for": used_for,
                "primary_request_url": primary_request_url,
                "primary_request_method": primary_request_method,
                "fallback_request_url": fallback_request_url,
                "fallback_request_method": fallback_request_method,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CXMLWebhookResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        used_for: UsedForType | None = None,
        primary_request_url: str | None = None,
        primary_request_method: Literal["GET"] | Literal["POST"] | None = None,
        fallback_request_url: str | None = None,
        fallback_request_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CXMLWebhookResponse:
        """Updates an cXML Webhook by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a CXML Webhook.
            name: Name of the CXML Webhook.
            used_for: Used for of the CXML Webhook.
            primary_request_url: Primary request url of the CXML Webhook.
            primary_request_method: Primary request method of the CXML Webhook.
            fallback_request_url: Fallback request url of the CXML Webhook.
            fallback_request_method: Fallback request method of the CXML Webhook.
            status_callback_url: Status callback url of the CXML Webhook.
            status_callback_method: Status callback method of the CXML Webhook.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "used_for": used_for,
                "primary_request_url": primary_request_url,
                "primary_request_method": primary_request_method,
                "fallback_request_url": fallback_request_url,
                "fallback_request_method": fallback_request_method,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CXMLWebhookResponse",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class FreeswitchConnectors(
    FabricResource[
        "FreeswitchConnectorListResponse",
        "FreeswitchConnectorResponse",
        "FreeswitchConnectorCreateRequest",
        "FreeswitchConnectorUpdateRequest",
    ]
):
    """Typed resource for ``/resources/freeswitch_connectors`` (generated).

    Bound to ``/api/fabric/resources/freeswitch_connectors``; construct it as
    ``FreeswitchConnectors(http)`` with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/freeswitch_connectors")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        token: uuid,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> FreeswitchConnectorResponse:
        """Creates a FreeSWITCH Connector.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            name: Name of the FreeSWITCH Connector
            token: FreeSWITCH token
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v for k, v in {"name": name, "token": token}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "FreeswitchConnectorResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        caller_id: str | None = None,
        send_as: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> FreeswitchConnectorResponse:
        """Updates a FreeSWITCH Connector by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a FreeSWITCH Connector.
            name: Name of the FreeSWITCH Connector
            caller_id: Caller ID for the connector
            send_as: Send as identifier
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "caller_id": caller_id,
                "send_as": send_as,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "FreeswitchConnectorResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class RelayApplications(
    FabricResource[
        "RelayApplicationListResponse",
        "RelayApplicationResponse",
        "RelayApplicationCreateRequest",
        "RelayApplicationUpdateRequest",
    ]
):
    """Typed resource for ``/resources/relay_applications`` (generated).

    Bound to ``/api/fabric/resources/relay_applications``; construct it as
    ``RelayApplications(http)`` with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/relay_applications")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        topic: str,
        call_status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> RelayApplicationResponse:
        """Creates a Relay Application.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            name: Name of the Relay Application
            topic: Topic of the Relay Application
            call_status_callback_url: Call status callback URL
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "topic": topic,
                "call_status_callback_url": call_status_callback_url,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "RelayApplicationResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        topic: str | None = None,
        call_status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> RelayApplicationResponse:
        """Updates a Relay Application by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a Relay Application.
            name: Name of the Relay Application
            topic: Topic of the Relay Application
            call_status_callback_url: Call status callback URL
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "topic": topic,
                "call_status_callback_url": call_status_callback_url,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "RelayApplicationResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class SipEndpoints(
    FabricResource[
        "SipEndpointListResponse",
        "SipEndpointResponse",
        "SipEndpointCreateRequest",
        "SipEndpointUpdateRequest",
    ]
):
    """Typed resource for ``/resources/sip_endpoints`` (generated).

    Bound to ``/api/fabric/resources/sip_endpoints``; construct it as
    ``SipEndpoints(http)`` with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/sip_endpoints")

    def create(  # type: ignore[override]
        self,
        *,
        username: str,
        caller_id: str,
        send_as: str,
        ciphers: list[Ciphers],
        codecs: list[Codecs],
        encryption: Encryption,
        call_handler: CallHandlerType,
        calling_handler_resource_id: uuid | None,
        id: uuid | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipEndpointResponse:
        """Creates a SIP Endpoint.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            username: The username of the Sip Endpoint
            caller_id: The caller ID that will showup when dialing from this Sip
                Endpoint
            send_as: The Sip username that will show up on the calle's side. Overrides
                the username.
            ciphers: Ciphers that can be enabled for calls on this Sip Endpoint.
            codecs: Codecs that can be enabled for calls on this Sip Endpoint.
            encryption: The set encryption type on the Sip Endpoint.
            call_handler: Specify how the SIP endpoint will handle outbound calls.
                - **default**: The SIP endpoint will pull the outbound policy setting
                  from the [SIP Profile
                  Settings](https://my.signalwire.com?page=sip_profile/edit). This
                  allows centralized management of outbound call behavior across
                  multiple endpoints from a single configuration.
                - **passthrough**: The SIP endpoint will be allowed to dial PSTN
                  numbers. This permits outbound calling to traditional phone numbers
                  without restrictions.
                - **block-pstn**: The SIP endpoint will be blocked from dialing PSTN
                  numbers. Use this to restrict the endpoint from initiating calls to
                  the public telephone network.
                - **resource**: Outbound calls from this SIP endpoint will dial the
                  specified resource and execute its instructions. Requires setting
                  `calling_handler_resource_id` to a valid resource. This enables custom
                  call handling workflows for outbound calls. See the [Fabric REST
                  API](https://signalwire.com/docs/rest/signalwire-rest/endpoints/fabric)
                  for valid resource types.
            calling_handler_resource_id: If `call_handler` is set to `resource`, this
                field expects the id of the set resouce. Will be `null` otherwise.
            id: The id of the Sip Endpoint
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "id": id,
                "username": username,
                "caller_id": caller_id,
                "send_as": send_as,
                "ciphers": ciphers,
                "codecs": codecs,
                "encryption": encryption,
                "call_handler": call_handler,
                "calling_handler_resource_id": calling_handler_resource_id,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipEndpointResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        username: str | None = None,
        caller_id: str | None = None,
        send_as: str | None = None,
        ciphers: list[Ciphers] | None = None,
        codecs: list[Codecs] | None = None,
        encryption: Encryption | None = None,
        call_handler: CallHandlerType | None = None,
        calling_handler_resource_id: uuid | None | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipEndpointResponse:
        """Updates a SIP Endpoint by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a SIP Endpoint.
            username: The username of the Sip Endpoint
            caller_id: The caller ID that will showup when dialing from this Sip
                Endpoint
            send_as: The Sip username that will show up on the calle's side. Overrides
                the username.
            ciphers: Ciphers that can be enabled for calls on this Sip Endpoint.
            codecs: Codecs that can be enabled for calls on this Sip Endpoint.
            encryption: The set encryption type on the Sip Endpoint.
            call_handler: Specify how the SIP endpoint will handle outbound calls.
                - **default**: The SIP endpoint will pull the outbound policy setting
                  from the [SIP Profile
                  Settings](https://my.signalwire.com?page=sip_profile/edit). This
                  allows centralized management of outbound call behavior across
                  multiple endpoints from a single configuration.
                - **passthrough**: The SIP endpoint will be allowed to dial PSTN
                  numbers. This permits outbound calling to traditional phone numbers
                  without restrictions.
                - **block-pstn**: The SIP endpoint will be blocked from dialing PSTN
                  numbers. Use this to restrict the endpoint from initiating calls to
                  the public telephone network.
                - **resource**: Outbound calls from this SIP endpoint will dial the
                  specified resource and execute its instructions. Requires setting
                  `calling_handler_resource_id` to a valid resource. This enables custom
                  call handling workflows for outbound calls. See the [Fabric REST
                  API](https://signalwire.com/docs/rest/signalwire-rest/endpoints/fabric)
                  for valid resource types.
            calling_handler_resource_id: If `call_handler` is set to `resource`, this
                field will contain the id of the set resouce. Will be `null` otherwise.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "username": username,
                "caller_id": caller_id,
                "send_as": send_as,
                "ciphers": ciphers,
                "codecs": codecs,
                "encryption": encryption,
                "call_handler": call_handler,
                "calling_handler_resource_id": calling_handler_resource_id,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipEndpointResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class SipGateways(
    FabricResource[
        "SipGatewayListResponse",
        "SipGatewayResponse",
        "SipGatewayRequest",
        "SipGatewayRequestUpdate",
    ]
):
    """Typed resource for ``/resources/sip_gateways`` (generated).

    Bound to ``/api/fabric/resources/sip_gateways``; construct it as
    ``SipGateways(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/sip_gateways")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        uri: str,
        encryption: Encryption,
        ciphers: list[Ciphers],
        codecs: list[Codecs],
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipGatewayResponse:
        """Creates a SIP Gateway that can be used to dial external SIP entities.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            name: Display name for the SIP Gateway.
            uri: External SIP URI.
            encryption: Specifies the encryption requirement for the SIP connection.
            ciphers: List of supported SIP ciphers.
            codecs: List of supported codecs for media transmission.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "uri": uri,
                "encryption": encryption,
                "ciphers": ciphers,
                "codecs": codecs,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipGatewayResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        uri: str | None = None,
        encryption: Encryption | None = None,
        ciphers: list[Ciphers] | None = None,
        codecs: list[Codecs] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipGatewayResponse:
        """Updates a SIP Gateway by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a SIP Gateway.
            name: Display name for the SIP Gateway.
            uri: External SIP URI.
            encryption: Specifies the encryption requirement for the SIP connection.
            ciphers: List of supported SIP ciphers.
            codecs: List of supported codecs for media transmission.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "uri": uri,
                "encryption": encryption,
                "ciphers": ciphers,
                "codecs": codecs,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipGatewayResponse",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class Subscribers(
    FabricResource[
        "SubscriberListResponse",
        "SubscriberResponse",
        "SubscriberRequest",
        "SubscriberRequest",
    ]
):
    """Typed resource for ``/resources/subscribers`` (generated).

    Bound to ``/api/fabric/resources/subscribers``; construct it as
    ``Subscribers(http)`` with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/subscribers")

    def create(  # type: ignore[override]
        self,
        *,
        email: str,
        password: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        display_name: str | None = None,
        job_title: str | None = None,
        timezone: str | None = None,
        country: str | None = None,
        region: str | None = None,
        company_name: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberResponse:
        """Create a new Subscriber.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            email: Email of the Subscriber.
            password: Password of the Subscriber. Defaults to a secure random password
                if not provided.
            first_name: First name of the Subscriber.
            last_name: Last name of the Subscriber.
            display_name: Display name of the Subscriber.
            job_title: Job title of the Subscriber.
            timezone: Timezone of the Subscriber.
            country: Country of the Subscriber.
            region: Region of the Subscriber.
            company_name: Company name of the Subscriber.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "password": password,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "display_name": display_name,
                "job_title": job_title,
                "timezone": timezone,
                "country": country,
                "region": region,
                "company_name": company_name,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        password: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        display_name: str | None = None,
        job_title: str | None = None,
        timezone: str | None = None,
        country: str | None = None,
        region: str | None = None,
        company_name: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberResponse:
        """Update an existing Subsriber.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a Subscriber.
            password: Password of the Subscriber. Defaults to a secure random password
                if not provided.
            email: Email of the Subscriber.
            first_name: First name of the Subscriber.
            last_name: Last name of the Subscriber.
            display_name: Display name of the Subscriber.
            job_title: Job title of the Subscriber.
            timezone: Timezone of the Subscriber.
            country: Country of the Subscriber.
            region: Region of the Subscriber.
            company_name: Company name of the Subscriber.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "password": password,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "display_name": display_name,
                "job_title": job_title,
                "timezone": timezone,
                "country": country,
                "region": region,
                "company_name": company_name,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_sip_endpoints(
        self,
        fabric_subscriber_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> SubscriberSipEndpointListResponse:
        """A list of Sip Endpoints of the Subscriber.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            fabric_subscriber_id: Unique ID of a Fabric Subscriber.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: The number of items per page (1-1000).
                - ``page_token``: Token for cursor-based pagination. Required when
                  page_number > 0.
                - ``username``: Filter subscriber SIP endpoints by username.

        Returns:
            The request has succeeded.
        """
        return cast(
            "SubscriberSipEndpointListResponse",
            self._http.get(
                self._path(fabric_subscriber_id, "sip_endpoints"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def create_sip_endpoint(
        self,
        fabric_subscriber_id: str,
        *,
        username: str,
        password: str,
        caller_id: str | None = None,
        send_as: str | None = None,
        ciphers: list[Ciphers] | None = None,
        codecs: list[Codecs] | None = None,
        encryption: Encryption | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberSIPEndpoint:
        """Creates a Subscriber Sip Endpoint.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            fabric_subscriber_id: Unique ID of a Fabric Subscriber.
            username: Username of the Sip Endpoint.
            password: Password of the Sip Endpoint.
            caller_id: Caller ID of the Sip Endpoint.
            send_as: The Number to send as.
            ciphers: Ciphers of the Sip Endpoint.
            codecs: Codecs of the Sip Endpoint.
            encryption: Encryption requirement of the Sip Endpoint.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "username": username,
                "password": password,
                "caller_id": caller_id,
                "send_as": send_as,
                "ciphers": ciphers,
                "codecs": codecs,
                "encryption": encryption,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberSIPEndpoint",
            self._http.post(
                self._path(fabric_subscriber_id, "sip_endpoints"),
                body=body,
                request_options=request_options,
            ),
        )

    def get_sip_endpoint(
        self,
        fabric_subscriber_id: str,
        id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> SubscriberSIPEndpoint:
        """Returns a Subscriber Sip Endpoint by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            fabric_subscriber_id: Unique ID of a Fabric Subscriber.
            id: Unique ID of a Sip Endpoint.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            The request has succeeded.
        """
        return cast(
            "SubscriberSIPEndpoint",
            self._http.get(
                self._path(fabric_subscriber_id, "sip_endpoints", id),
                params=params or None,
                request_options=request_options,
            ),
        )

    def update_sip_endpoint(
        self,
        fabric_subscriber_id: str,
        id: str,
        *,
        username: str | None = None,
        password: str | None = None,
        caller_id: str | None = None,
        send_as: str | None = None,
        ciphers: list[Ciphers] | None = None,
        codecs: list[Codecs] | None = None,
        encryption: Encryption | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberSIPEndpoint:
        """Updates a Subscriber Sip Endpoint by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            fabric_subscriber_id: Unique ID of a Fabric Subscriber.
            id: Unique ID of a Sip Endpoint.
            username: Username of the Sip Endpoint.
            password: Password of the Sip Endpoint.
            caller_id: Caller ID of the Sip Endpoint.
            send_as: The Number to send as.
            ciphers: Ciphers of the Sip Endpoint.
            codecs: Codecs of the Sip Endpoint.
            encryption: Encryption requirement of the Sip Endpoint.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "username": username,
                "password": password,
                "caller_id": caller_id,
                "send_as": send_as,
                "ciphers": ciphers,
                "codecs": codecs,
                "encryption": encryption,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberSIPEndpoint",
            self._http.patch(
                self._path(fabric_subscriber_id, "sip_endpoints", id),
                body=body,
                request_options=request_options,
            ),
        )

    def delete_sip_endpoint(
        self,
        fabric_subscriber_id: str,
        id: str,
        *,
        request_options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """Deletes a Subscriber Sip Endpoint by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            fabric_subscriber_id: Unique ID of a Fabric Subscriber.
            id: Unique ID of a Sip Endpoint.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(
                self._path(fabric_subscriber_id, "sip_endpoints", id),
                request_options=request_options,
            ),
        )


class SwmlScripts(
    FabricResource[
        "SwmlScriptListResponse",
        "SwmlScriptResponse",
        "SwmlScriptCreateRequest",
        "SwmlScriptUpdateRequest",
    ]
):
    """Typed resource for ``/resources/swml_scripts`` (generated).

    Bound to ``/api/fabric/resources/swml_scripts``; construct it as
    ``SwmlScripts(http)`` with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/swml_scripts")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        contents: str,
        status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SwmlScriptResponse:
        """Creates a SWML Script.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            name: Display name of the SWML Script
            contents: The contents of the SWML script.
            status_callback_url: URL to send status callbacks to
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "contents": contents,
                "status_callback_url": status_callback_url,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SwmlScriptResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        display_name: str | None = None,
        contents: str | None = None,
        status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SwmlScriptResponse:
        """Updates a SWML Script by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a SWML Script.
            display_name: Display name of the SWML Script
            contents: The contents of the SWML script.
            status_callback_url: URL to send status callbacks to
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "display_name": display_name,
                "contents": contents,
                "status_callback_url": status_callback_url,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SwmlScriptResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class SwmlWebhooks(
    FabricResource[
        "SWMLWebhookListResponse",
        "SWMLWebhookResponse",
        "SWMLWebhookCreateRequest",
        "SWMLWebhookUpdateRequest",
    ]
):
    """Typed resource for ``/resources/swml_webhooks`` (generated).

    Bound to ``/api/fabric/resources/swml_webhooks``; construct it as
    ``SwmlWebhooks(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/resources/swml_webhooks")

    def create(  # type: ignore[override]
        self,
        *,
        primary_request_url: str,
        name: str | None = None,
        used_for: Literal["calling"] | None = None,
        primary_request_method: Literal["GET"] | Literal["POST"] | None = None,
        fallback_request_url: str | None = None,
        fallback_request_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SWMLWebhookResponse:
        """Creates an SWML Webhook.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            primary_request_url: Primary request url of the SWML Webhook.
            name: Name of the SWML Webhook.
            used_for: Used for of the SWML Webhook.
            primary_request_method: Primary request method of the SWML Webhook.
            fallback_request_url: Fallback request url of the SWML Webhook.
            fallback_request_method: Fallback request method of the SWML Webhook.
            status_callback_url: Status callback url of the SWML Webhook.
            status_callback_method: Status callback method of the SWML Webhook.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "used_for": used_for,
                "primary_request_url": primary_request_url,
                "primary_request_method": primary_request_method,
                "fallback_request_url": fallback_request_url,
                "fallback_request_method": fallback_request_method,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SWMLWebhookResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        used_for: Literal["calling"] | None = None,
        primary_request_url: str | None = None,
        primary_request_method: Literal["GET"] | Literal["POST"] | None = None,
        fallback_request_url: str | None = None,
        fallback_request_method: Literal["GET"] | Literal["POST"] | None = None,
        status_callback_url: str | None = None,
        status_callback_method: Literal["GET"] | Literal["POST"] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SWMLWebhookResponse:
        """Updates an SWML Webhook by ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of a SWML Webhook.
            name: Name of the SWML Webhook.
            used_for: Used for of the SWML Webhook.
            primary_request_url: Primary request url of the SWML Webhook.
            primary_request_method: Primary request method of the SWML Webhook.
            fallback_request_url: Fallback request url of the SWML Webhook.
            fallback_request_method: Fallback request method of the SWML Webhook.
            status_callback_url: Status callback url of the SWML Webhook.
            status_callback_method: Status callback method of the SWML Webhook.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "used_for": used_for,
                "primary_request_url": primary_request_url,
                "primary_request_method": primary_request_method,
                "fallback_request_url": fallback_request_url,
                "fallback_request_method": fallback_request_method,
                "status_callback_url": status_callback_url,
                "status_callback_method": status_callback_method,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SWMLWebhookResponse",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class FabricTokens(BaseResource):
    """Typed resource for ```` (generated).

    Bound to ``/api/fabric``; construct it as ``FabricTokens(http)`` with the client's
    HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric")

    def create_subscriber_token(
        self,
        *,
        reference: str,
        expire_at: int | None = None,
        application_id: uuid | None = None,
        password: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        display_name: str | None = None,
        job_title: str | None = None,
        time_zone: str | None = None,
        country: str | None = None,
        region: str | None = None,
        company_name: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberTokenResponse:
        """Create a Subscriber Token.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            reference: A string that uniquely identifies the subscriber. Often it's an
                email, but can be any other string.
            expire_at: A unixtime (the number of seconds since 1970-01-01 00:00:00) at
                which the token should no longer be valid. Defaults to 'two hours from
                now'
            application_id: The ID of the application that the token is associated with.
            password: Set or update the subscriber's password. Omit this field or pass
                an empty string if you don't want to update the password.
            first_name: Set or update the first name of the subscriber.
            last_name: Set or update the last name of the subscriber.
            display_name: Set or update the display name of the subscriber.
            job_title: Set or update the job title of the subscriber.
            time_zone: Set or update the time zone of the subscriber.
            country: Set or update the country of the subscriber.
            region: Set or update the region of the subscriber.
            company_name: Set or update the company name of the subscriber.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "reference": reference,
                "expire_at": expire_at,
                "application_id": application_id,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "display_name": display_name,
                "job_title": job_title,
                "time_zone": time_zone,
                "country": country,
                "region": region,
                "company_name": company_name,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberTokenResponse",
            self._http.post(
                self._path("subscribers", "tokens"),
                body=body,
                request_options=request_options,
            ),
        )

    def refresh_subscriber_token(
        self,
        *,
        refresh_token: jwt,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberRefreshTokenResponse:
        """Exchanges a valid refresh token for a new subscriber access token and a new refresh token.

        The new access token is valid for 2 hours, and the new refresh token is valid
        for 2 hours and 5 minutes.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            refresh_token: The refresh token previously issued alongside a subscriber
                access token. This token is used to request a new access token.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v for k, v in {"refresh_token": refresh_token}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberRefreshTokenResponse",
            self._http.post(
                self._path("subscribers", "tokens", "refresh"),
                body=body,
                request_options=request_options,
            ),
        )

    def create_invite_token(
        self,
        *,
        address_id: uuid,
        expires_at: int | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberInviteTokenCreateResponse:
        """Creates a Subscriber Invite Token to be used for client-side API calls.

        The token is authorized using a subscriber's SAT (Subscriber Access Token)

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            address_id: Unique ID of a Subscriber Address
            expires_at: A unixtime (the number of seconds since 1970-01-01 00:00:00) at
                which the token should no longer be valid. Defaults to 'two hours from
                now'
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"address_id": address_id, "expires_at": expires_at}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberInviteTokenCreateResponse",
            self._http.post(
                self._path("subscriber", "invites"),
                body=body,
                request_options=request_options,
            ),
        )

    def create_guest_token(
        self,
        *,
        allowed_addresses: list[uuid],
        expire_at: int | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SubscriberGuestTokenCreateResponse:
        """Creates a Subscriber Guest Token.

        The token is authorized using an existing API token.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            allowed_addresses: List of up to 10 UUIDs representing the allowed Fabric
                addresses.
            expire_at: A unixtime (the number of seconds since 1970-01-01 00:00:00) at
                which the token should no longer be valid. Defaults to 'two hours from
                now'
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "allowed_addresses": allowed_addresses,
                "expire_at": expire_at,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SubscriberGuestTokenCreateResponse",
            self._http.post(
                self._path("guests", "tokens"),
                body=body,
                request_options=request_options,
            ),
        )

    def create_embed_token(
        self,
        *,
        token: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> EmbedsTokensResponse:
        """Exchanges a public Click-to-Call (C2C) token for a short-lived, private embed guest token used to authorize a call.

        This allows secure activation of the C2C widget without exposing sensitive
        credentials.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_, _Messaging_, _Fax_, or _Video_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            token: Click to Call Token
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            The request has succeeded and a new resource has been created as a result.
        """
        body: dict[str, Any] = {
            k: v for k, v in {"token": token}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "EmbedsTokensResponse",
            self._http.post(
                self._path("embeds", "tokens"),
                body=body,
                request_options=request_options,
            ),
        )
