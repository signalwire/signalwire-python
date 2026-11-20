"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase  # type: ignore[attr-defined]  # cycle: agent_base imports the mixins; the name resolves at type-check time but mypy flags the back-reference


from signalwire.core.mixins._mixin_host import _HostTyped


class SkillMixin(_HostTyped):  # type: ignore[misc]  # _HostTyped is object at runtime; AgentBase under TYPE_CHECKING — intentional split
    """
    Mixin class containing all skill management methods for AgentBase
    """

    def add_skill(
        self, skill_name: str, params: dict[str, Any] | None = None
    ) -> "AgentBase":
        """Add a skill to this agent.

        Skills are pluggable capability modules that register their own tools,
        prompts, and configuration. The SDK ships with built-in skills for common
        tasks such as `datetime`, `web_search`, and `math`.

        Args:
            skill_name: Registered skill name, for example `"datetime"`,
                `"web_search"`, or `"math"`.
            params: Skill-specific configuration parameters. Each skill documents
                its own supported parameters. Defaults to None.

        Returns:
            This agent, for chaining.

        Raises:
            ValueError: If the skill is not found or fails to load. The message
                includes the loader's error. Call `list_skills()` to see the
                skills that are currently loaded.

        Example:
            ```python
            agent.add_skill("datetime")
            agent.add_skill("math")
            agent.add_skill("web_search", params={
                "api_key": "your-google-api-key",
                "search_engine_id": "your-search-engine-id",
                "num_results": 5,
            })
            ```
        """
        # Debug logging
        self.log.debug(
            "add_skill_called",
            skill_name=skill_name,
            agent_id=id(self),
            registry_id=id(self._tool_registry)
            if hasattr(self, "_tool_registry")
            else None,
            is_ephemeral=getattr(self, "_is_ephemeral", False),
        )

        success, error_message = self.skill_manager.load_skill(
            skill_name, params=params
        )
        if not success:
            raise ValueError(f"Failed to load skill '{skill_name}': {error_message}")
        return self

    def remove_skill(self, skill_name: str) -> "AgentBase":
        """Remove a skill from this agent.

        The skill's tools and configuration are unloaded.

        Args:
            skill_name: Name of the skill to remove.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.add_skill("datetime")
            agent.add_skill("math")
            agent.remove_skill("math")
            agent.list_skills()  # ["datetime"]
            ```
        """
        self.skill_manager.unload_skill(skill_name)
        return self

    def list_skills(self) -> list[str]:
        """List the names of the skills currently loaded on this agent.

        Returns:
            The loaded skill names.

        Example:
            ```python
            agent.add_skill("datetime")
            agent.add_skill("math")
            agent.list_skills()  # ["datetime", "math"]
            ```
        """
        # `skill_manager` is host-Any (mixin pattern); SkillManager
        # .list_loaded_skills() is declared -> list[str].
        return cast(list[str], self.skill_manager.list_loaded_skills())

    def has_skill(self, skill_name: str) -> bool:
        """Check whether a skill is currently loaded on this agent.

        Args:
            skill_name: Skill name to check.

        Returns:
            True if the skill is loaded, False otherwise.

        Example:
            ```python
            agent.add_skill("datetime")
            agent.has_skill("datetime")  # True
            agent.has_skill("web_search")  # False
            ```
        """
        # `skill_manager` is host-Any; SkillManager.has_skill() -> bool.
        return cast(bool, self.skill_manager.has_skill(skill_name))
