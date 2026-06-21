"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Static-typing support for the AgentBase mixins.

Each mixin (StateMixin, ToolMixin, WebMixin, ...) is a fragment of AgentBase:
its methods reference attributes and methods (``self.log``, ``self._tool_registry``,
``self.pom``, ``self._render_swml``, ...) that are only provided once the mixin
is composed into the concrete ``AgentBase``. A type checker analysing a mixin in
isolation cannot see those, producing a large ``attr-defined`` cluster.

``_AgentHost`` is a typing-only Protocol that declares the surface the mixins
assume their host exposes. Mixins inherit it ONLY under ``typing.TYPE_CHECKING``
(via the ``_HostTyped`` alias), so it is purely a static-analysis aid — it adds
nothing to the runtime MRO, defines no behaviour, and does not appear on the
public surface (the audit oracle enumerates ``AgentBase``, not this Protocol).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol


if TYPE_CHECKING:
    import structlog

    class _AgentHost(Protocol):
        """The AgentBase surface that mixins rely on at type-check time.

        Only members actually referenced as ``self.<x>`` from inside a mixin
        body need to appear here. Keep this in sync with AgentBase; it is a
        typing aid, never imported at runtime.
        """

        # --- core attributes provided by AgentBase.__init__ ---
        log: structlog.stdlib.BoundLogger
        name: str
        route: str
        pom: Any
        _global_data: Dict[str, Any]
        _hints: List[Any]
        _params: Dict[str, Any]
        _use_pom: bool
        _session_manager: Any
        _tool_registry: Any
        _prompt_manager: Any
        skill_manager: Any
        _basic_auth: Any
        _mcp_servers: Any
        _prompt_llm_params: Dict[str, Any]
        _post_prompt_llm_params: Dict[str, Any]
        # Mutable host state the web/prompt mixins read AND write — declared with
        # their true Optional types so a mixin's assignment doesn't infer a
        # narrower (non-Optional) type that then clashes with AgentBase's init.
        _app: Optional[Any]
        _router: Optional[Any]
        _proxy_url_base: Optional[str]
        _dynamic_config_callback: Optional[Any]
        _contexts_builder: Optional[Any]
        ssl_cert_path: Optional[str]
        ssl_key_path: Optional[str]
        host: str
        port: int
        path: str

        # --- methods provided by sibling mixins / AgentBase ---
        def _render_swml(self, *args: Any, **kwargs: Any) -> Any: ...
        def _handle_swaig_request(self, *args: Any, **kwargs: Any) -> Any: ...
        def _handle_mcp_request(self, *args: Any, **kwargs: Any) -> Any: ...
        def _check_basic_auth(self, *args: Any, **kwargs: Any) -> Any: ...
        def _check_content_type(self, *args: Any, **kwargs: Any) -> Any: ...
        def _read_body_with_limit(self, *args: Any, **kwargs: Any) -> Any: ...
        def _find_summary_in_post_data(self, *args: Any, **kwargs: Any) -> Any: ...
        def _create_ephemeral_copy(self, *args: Any, **kwargs: Any) -> Any: ...
        def get_basic_auth_credentials(self, *args: Any, **kwargs: Any) -> Any: ...
        def get_full_url(self, *args: Any, **kwargs: Any) -> Any: ...
        def handle_serverless_request(self, *args: Any, **kwargs: Any) -> Any: ...
        def on_summary(self, *args: Any, **kwargs: Any) -> Any: ...
        def on_function_call(self, *args: Any, **kwargs: Any) -> Any: ...

    # Mixins inherit this alias. At runtime it is `object` (see else branch),
    # so it contributes nothing to the MRO; under TYPE_CHECKING it is the
    # Protocol, so mypy resolves `self.<host attr>` against it.
    _HostTyped = _AgentHost
else:
    _HostTyped = object
