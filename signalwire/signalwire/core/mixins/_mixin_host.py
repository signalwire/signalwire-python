"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Static-typing support for the AgentBase mixins.

Each mixin (StateMixin, ToolMixin, WebMixin, ...) is a fragment of AgentBase:
its methods reference attributes/methods only provided once composed into the
concrete ``AgentBase`` (``self.log``, ``self._tool_registry``, ``self.pom``,
``self._render_swml``, ...) and many ``return self`` typed ``-> AgentBase``.
Analysed in isolation a mixin can't see those, producing a large cluster of
``attr-defined`` / ``return-value`` errors.

``_HostTyped`` is the alias each mixin inherits. Under ``TYPE_CHECKING`` it IS
``AgentBase`` (the real composed class), so the checker resolves every
``self.<host member>`` and every ``return self`` against the true class — no
hand-maintained surface list to keep in sync. At runtime it is plain ``object``,
so it contributes nothing to the MRO, adds no behaviour, and never appears on
the audit oracle's public surface. The forward reference avoids the import cycle
(agent_base imports the mixins, not vice-versa).
"""

from __future__ import annotations

from typing import TYPE_CHECKING


# Each mixin declares ``class XMixin(_HostTyped)``. At runtime ``_HostTyped`` is
# plain ``object`` — it adds nothing to the MRO and never reaches the audit
# oracle. Under TYPE_CHECKING it resolves to the concrete ``AgentBase`` (imported
# lazily inside each mixin's own ``if TYPE_CHECKING`` block — importing it HERE
# would create a cycle, since agent_base imports the mixins). So the checker sees
# every mixin as AgentBase: all ``self.<host attr>`` resolve and every fluent
# ``return self`` typed ``-> AgentBase`` checks out.
if TYPE_CHECKING:
    from signalwire.core._agent_host import AgentHost as _HostTyped
else:
    _HostTyped = object

# Explicit re-export: the mixins import _HostTyped from here. Under --strict
# (no_implicit_reexport) an aliased import isn't re-exported unless named in __all__.
__all__ = ["_HostTyped"]
