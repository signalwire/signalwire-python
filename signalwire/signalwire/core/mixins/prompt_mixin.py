"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from typing import Union, Any, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase  # type: ignore[attr-defined]  # cycle: agent_base imports the mixins; the name resolves at type-check time but mypy flags the back-reference
    from signalwire.core.contexts import ContextBuilder
else:
    from signalwire.core.contexts import ContextBuilder


from signalwire.core.mixins._mixin_host import _HostTyped


class PromptMixin(_HostTyped):  # type: ignore[misc]  # _HostTyped is object at runtime; AgentBase under TYPE_CHECKING — intentional split
    """
    Mixin class containing all prompt-related methods for AgentBase
    """

    # Host attribute PromptMixin reads/writes; owned by AgentBase. Declared here
    # (Optional) so the checker resolves it without a cross-class has-type gap.
    _contexts_builder: Any | None

    def _process_prompt_sections(self) -> None:
        """
        Process declarative PROMPT_SECTIONS attribute from a subclass

        This auto-vivifies section methods and bootstraps the prompt
        from class declaration, allowing for declarative agents.
        """
        # Skip if no PROMPT_SECTIONS defined or not using POM
        cls = self.__class__
        if (
            not hasattr(cls, "PROMPT_SECTIONS")
            or cls.PROMPT_SECTIONS is None
            or not self._use_pom
        ):
            return

        sections = cls.PROMPT_SECTIONS

        # If sections is a dictionary mapping section names to content
        if isinstance(sections, dict):
            for title, content in sections.items():
                # Handle different content types
                if isinstance(content, str):
                    # Plain text - add as body
                    self.prompt_add_section(title, body=content)
                elif isinstance(content, list) and content:  # Only add if non-empty
                    # List of strings - add as bullets
                    self.prompt_add_section(title, bullets=content)
                elif isinstance(content, dict):
                    # Dictionary with body/bullets/subsections
                    body = content.get("body", "")
                    bullets = content.get("bullets", [])
                    numbered = content.get("numbered", False)
                    numbered_bullets = content.get("numberedBullets", False)

                    # Only create section if it has content
                    if body or bullets or "subsections" in content:
                        # Create the section
                        self.prompt_add_section(
                            title,
                            body=body,
                            bullets=bullets if bullets else None,
                            numbered=numbered,
                            numbered_bullets=numbered_bullets,
                        )

                        # Process subsections if any
                        subsections = content.get("subsections", [])
                        for subsection in subsections:
                            if "title" in subsection:
                                sub_title = subsection["title"]
                                sub_body = subsection.get("body", "")
                                sub_bullets = subsection.get("bullets", [])

                                # Only add subsection if it has content
                                if sub_body or sub_bullets:
                                    self.prompt_add_subsection(
                                        title,
                                        sub_title,
                                        body=sub_body,
                                        bullets=sub_bullets if sub_bullets else None,
                                    )
        # If sections is a list of section objects, use the POM format directly
        elif isinstance(sections, list) and self.pom:
            # Process each section using auto-vivifying methods
            for section in sections:
                if "title" in section:
                    title = section["title"]
                    body = section.get("body", "")
                    bullets = section.get("bullets", [])
                    numbered = section.get("numbered", False)
                    numbered_bullets = section.get("numberedBullets", False)

                    # Only create section if it has content
                    if body or bullets or "subsections" in section:
                        self.prompt_add_section(
                            title,
                            body=body,
                            bullets=bullets if bullets else None,
                            numbered=numbered,
                            numbered_bullets=numbered_bullets,
                        )

                        # Process subsections if any
                        subsections = section.get("subsections", [])
                        for subsection in subsections:
                            if "title" in subsection:
                                sub_title = subsection["title"]
                                sub_body = subsection.get("body", "")
                                sub_bullets = subsection.get("bullets", [])

                                # Only add subsection if it has content
                                if sub_body or sub_bullets:
                                    self.prompt_add_subsection(
                                        title,
                                        sub_title,
                                        body=sub_body,
                                        bullets=sub_bullets if sub_bullets else None,
                                    )

    def define_contexts(
        self, contexts: "dict[str, Any] | ContextBuilder | None" = None
    ) -> Union["AgentBase", "ContextBuilder"]:
        """
        Define contexts and steps for multi-step conversation workflows.

        Contexts let an agent guide the caller through a structured sequence of
        interactions, such as gathering information, verifying identity, and then
        performing an action. This is an alternative to a single prompt.

        When called with an argument, it sets the context configuration directly and
        returns the agent. When called without arguments, it returns the
        `ContextBuilder` for fluent context definition.

        Note:
            Contexts can coexist with traditional prompts. The only restriction is
            that POM sections and raw text cannot be mixed in the main prompt.

        Args:
            contexts: Context configuration, as a dictionary or a `ContextBuilder`,
                to set contexts directly. Omit it to receive a `ContextBuilder`.

        Returns:
            This agent, for chaining, when `contexts` is provided. The
            `ContextBuilder` when called with no arguments.

        Example:
            ```python
            # Fluent ContextBuilder
            ctx = agent.define_contexts()
            default = ctx.add_context("default")
            (
                default.add_step("greeting")
                .set_text("Greet the caller and ask for their name.")
                .set_step_criteria("The caller has provided their name.")
                .set_valid_steps(["verify"])
            )
            (
                default.add_step("verify")
                .set_text("Verify the caller's identity.")
                .set_step_criteria("Identity verified.")
                .set_valid_steps(["assist"])
            )
            default.add_step("assist").set_text("Help the caller with their request.")
            ```

            ```python
            # Direct dictionary configuration
            agent.define_contexts({
                "default": {
                    "steps": {
                        "greeting": {
                            "text": "Greet the caller.",
                            "valid_steps": ["verify"],
                        },
                        "verify": {"text": "Verify identity.", "valid_steps": []},
                    }
                }
            })
            ```
        """
        if contexts is not None:
            # New behavior - set contexts
            self._prompt_manager.define_contexts(contexts)
            return self
        # Legacy behavior - return ContextBuilder
        if self._contexts_builder is None:
            # ContextBuilder.__init__ is untyped (cross-file: core/contexts.py).
            self._contexts_builder = ContextBuilder(self)
            self._contexts_defined = True

        return self._contexts_builder

    @property
    def contexts(self) -> "ContextBuilder":
        """
        Get the ContextBuilder for this agent

        Returns:
            ContextBuilder instance for defining contexts
        """
        return self.define_contexts()

    def reset_contexts(self) -> "AgentBase":
        """
        Remove all contexts, returning the agent to a no-contexts state.

        This is a convenience wrapper around `define_contexts().reset()`. Use it in
        a dynamic config callback when you need to rebuild contexts from scratch for
        a specific request.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            def on_dynamic_config(query, body, headers, agent):
                if query.get("transfer"):
                    agent.reset_contexts()
                    ctx = agent.define_contexts().add_context("default")
                    ctx.add_step("route").set_text("Route the caller.")

            agent.set_dynamic_config_callback(on_dynamic_config)
            ```
        """
        if self._contexts_builder is not None:
            self._contexts_builder.reset()
        return self

    def _validate_prompt_mode_exclusivity(self) -> None:
        """
        Validate that POM sections and raw text are not mixed in the main prompt

        Note: This does NOT prevent contexts from being used alongside traditional prompts
        """
        # Delegate to prompt manager
        self._prompt_manager._validate_prompt_mode_exclusivity()

    def set_prompt_text(self, text: str) -> "AgentBase":
        """
        Set the agent's system prompt as raw text instead of using POM.

        This is the simplest way to configure what the AI knows and how it behaves.
        It sets the `prompt` of the SWML AI verb.

        Warning:
            Cannot be mixed with POM-based prompt sections (`prompt_add_section()`)
            in the same agent. Use one approach or the other for the main prompt.
            Contexts can still be used alongside either approach.

        Args:
            text: The complete system prompt text. Multi-line strings are fine.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_prompt_text(
                "You are a customer support agent for Acme Corp. "
                "You help customers with billing, order tracking and returns. "
                "Always be polite and professional."
            )
            ```
        """
        self._prompt_manager.set_prompt_text(text)
        return self

    def set_post_prompt(self, text: str) -> "AgentBase":
        """
        Set the post-prompt text for summary generation.

        After a conversation ends, the AI uses this prompt to analyze the
        conversation and generate a structured summary. The summary is delivered to
        your `on_summary()` callback or to the endpoint set with
        `set_post_prompt_url()`.

        Args:
            text: Instructions for summary generation. Tell the AI what to extract
                from the conversation, for example caller intent, resolution
                status, or action items.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_post_prompt(
                "Summarize this conversation as JSON with these fields: "
                "caller_intent (what the caller wanted), resolution "
                "(yes, no or partial), action_items (follow-ups needed) "
                "and sentiment (positive, neutral or negative)."
            )
            ```
        """
        self._prompt_manager.set_post_prompt(text)
        return self

    def set_prompt_pom(self, pom: list[dict[str, Any]]) -> "AgentBase":
        """
        Set the prompt directly as a POM (Prompt Object Model) structure.

        This is a low-level method that accepts the POM data format directly. For
        most cases, use `prompt_add_section()` to build POM prompts incrementally.

        The POM format structures a prompt into titled sections with body text,
        bullet points, and nested subsections. This structure helps the AI model
        parse complex instructions more reliably than flat text.

        Args:
            pom: POM structure, a list of section dictionaries. Each section has
                `title` (the heading), `body` (the text), optional `bullets` (a
                list of strings), optional `numbered` (whether the section is
                numbered), and optional `subsections` (nested sections with the
                same keys).

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_prompt_pom([
                {
                    "title": "Role",
                    "body": "You are a customer support agent for Acme Corp.",
                },
                {
                    "title": "Guidelines",
                    "body": "",
                    "bullets": [
                        "Always greet the caller by name if available",
                        "Never share internal pricing details",
                    ],
                },
                {
                    "title": "Capabilities",
                    "body": "You can help with the following:",
                    "subsections": [
                        {"title": "Orders", "body": "Look up order status"},
                        {"title": "Billing", "body": "Check balances"},
                    ],
                },
            ])
            ```
        """
        self._prompt_manager.set_prompt_pom(pom)
        return self

    def prompt_add_section(
        self,
        title: str,
        body: str = "",
        bullets: list[str] | None = None,
        numbered: bool = False,
        numbered_bullets: bool = False,
        subsections: list[dict[str, Any]] | None = None,
    ) -> "AgentBase":
        """
        Add a section to the prompt.

        Sections give the AI structured instructions that are easier to follow than
        a single block of text. Each section has a title and optional body text,
        bullet points, and subsections.

        Warning:
            POM sections cannot be mixed with `set_prompt_text()` in the same
            agent. Use one approach or the other.

        Args:
            title: Section heading shown to the AI.
            body: Section body text. Default empty.
            bullets: List of bullet point strings.
            numbered: Whether the section itself should be numbered. Default False.
            numbered_bullets: Whether the bullet points should be numbered instead
                of bulleted. Default False.
            subsections: List of subsection dictionaries, each with `title`,
                `body`, and optional `bullets`.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.prompt_add_section(
                "Role", body="You are a customer support agent for Acme Corp."
            )
            agent.prompt_add_section("Guidelines", bullets=[
                "Always greet the caller by name if available",
                "Never share internal pricing details",
                "Escalate to a human if the caller asks",
            ])
            ```
        """
        self._prompt_manager.prompt_add_section(
            title=title,
            body=body,
            bullets=bullets,
            numbered=numbered,
            numbered_bullets=numbered_bullets,
            subsections=subsections,
        )
        return self

    def prompt_add_to_section(
        self,
        title: str,
        body: str | None = None,
        bullet: str | None = None,
        bullets: list[str] | None = None,
    ) -> "AgentBase":
        """
        Add content to an existing section, creating the section if needed.

        Args:
            title: Title of the section to update (or create).
            body: Text to append to the section body.
            bullet: A single bullet point to add.
            bullets: Multiple bullet points to add.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.prompt_add_section("Rules", bullets=["Be polite"])
            agent.prompt_add_to_section("Rules", bullet="Never lie")
            agent.prompt_add_to_section("Rules", bullets=[
                "Keep responses concise",
                "Ask clarifying questions when needed",
            ])
            ```
        """
        self._prompt_manager.prompt_add_to_section(
            title=title, body=body, bullet=bullet, bullets=bullets
        )
        return self

    def prompt_add_subsection(
        self,
        parent_title: str,
        title: str,
        body: str = "",
        bullets: list[str] | None = None,
    ) -> "AgentBase":
        """
        Add a subsection to an existing section, creating the parent if needed.

        Args:
            parent_title: Title of the parent section. If no such section exists,
                it is created.
            title: Subsection heading.
            body: Subsection body text. Default empty.
            bullets: Subsection bullet points.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.prompt_add_section(
                "Capabilities", body="You can help with the following:"
            )
            agent.prompt_add_subsection(
                "Capabilities", "Orders",
                body="Look up order status, process returns and exchanges.",
            )
            agent.prompt_add_subsection(
                "Capabilities", "Billing",
                body="Check account balances and explain recent charges.",
            )
            ```
        """
        self._prompt_manager.prompt_add_subsection(
            parent_title=parent_title, title=title, body=body, bullets=bullets
        )
        return self

    def prompt_has_section(self, title: str) -> bool:
        """
        Check whether a named section exists in the agent's POM prompt.

        Useful for conditionally adding content to avoid duplicate sections.

        Args:
            title: The section title to look up. It must match the title passed to
                `prompt_add_section()`.

        Returns:
            True if a section with the given title exists, False otherwise.

        Example:
            ```python
            agent.prompt_add_section("Greeting", body="Greet the caller by name.")
            if not agent.prompt_has_section("Policies"):
                agent.prompt_add_section("Policies", body="Follow company guidelines.")
            ```
        """
        # `_prompt_manager` is host-Any (mixin pattern); PromptManager
        # .prompt_has_section() is declared -> bool.
        return cast(bool, self._prompt_manager.prompt_has_section(title))

    def get_prompt(self) -> str | list[dict[str, Any]]:
        """
        Get the agent's current prompt.

        Returns a string if `set_prompt_text()` was used, or the POM structure (a
        list of dictionaries) if prompt sections were used. If neither was set, it
        returns the default prompt, "You are {name}, a helpful AI assistant.".

        Returns:
            The current prompt, either a string or a POM list of section
            dictionaries, in whatever format was configured.

        Example:
            ```python
            agent.set_prompt_text("You are a customer support agent for Acme Corp.")
            prompt = agent.get_prompt()
            ```
        """
        # First check if prompt manager has a prompt. `_prompt_manager` is
        # host-Any (mixin pattern); PromptManager.get_prompt() is declared
        # -> str | list[dict[str, Any]] | None, so narrow the non-None branch.
        prompt_result = self._prompt_manager.get_prompt()
        if prompt_result is not None:
            return cast("str | list[dict[str, Any]]", prompt_result)

        # If using POM, return the POM structure. `self.pom` is host-Any and the
        # POM implementation is duck-typed (whichever render method it exposes);
        # narrow each branch back to this method's declared return contract.
        if self._use_pom and self.pom:
            try:
                # Try different methods that might be available on the POM implementation
                if hasattr(self.pom, "render_dict"):
                    return cast("list[dict[str, Any]]", self.pom.render_dict())
                if hasattr(self.pom, "to_dict"):
                    return cast("list[dict[str, Any]]", self.pom.to_dict())
                if hasattr(self.pom, "to_list"):
                    return cast("list[dict[str, Any]]", self.pom.to_list())
                if hasattr(self.pom, "render"):
                    render_result = self.pom.render()
                    # If render returns a string, we need to convert it to JSON
                    if isinstance(render_result, str):
                        try:
                            import json

                            return cast(
                                "list[dict[str, Any]]", json.loads(render_result)
                            )
                        except (ValueError, json.JSONDecodeError):
                            # If we can't parse as JSON, fall back to raw text
                            pass
                    return cast("str | list[dict[str, Any]]", render_result)
                # Last resort: attempt to convert the POM object directly to a list/dict
                # This assumes the POM object has a reasonable __str__ or __repr__ method
                pom_data = self.pom.__dict__
                if "_sections" in pom_data and isinstance(pom_data["_sections"], list):
                    return pom_data["_sections"]
                    # Fall through to default if nothing worked
            except Exception as e:
                self.log.error("pom_rendering_failed", error=str(e))
                # Fall back to raw text if POM fails

        # Return default text
        return f"You are {self.name}, a helpful AI assistant."

    def get_post_prompt(self) -> str | None:
        """
        Get the current post-prompt text.

        Returns:
            The post-prompt text, or None if it is not set.

        Example:
            ```python
            agent.set_post_prompt("Summarize this call as JSON.")
            post_prompt = agent.get_post_prompt()
            ```
        """
        # `_prompt_manager` is host-Any; PromptManager.get_post_prompt() -> str | None.
        return cast("str | None", self._prompt_manager.get_post_prompt())
