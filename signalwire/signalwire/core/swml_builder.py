"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

SWML Builder - Fluent API for building SWML documents

This module provides a fluent builder API for creating SWML documents.
It allows for chaining method calls to build up a document step by step.
"""

import types
from typing import TYPE_CHECKING, Any, TypeVar
from collections.abc import Callable

try:
    from typing import Self  # type: ignore[attr-defined]  # 3.11+; typing_extensions fallback below
except ImportError:
    from typing_extensions import Self  # For Python 3.9-3.10

from signalwire.core.swml_service import SWMLService
from signalwire.core._verb_methods import _make_verb_method, _verb_for_attribute

if TYPE_CHECKING:
    # The SWML verb methods are installed dynamically at runtime (_create_verb_methods,
    # from schema.json). Inheriting the generated _SwmlVerbs Protocol gives the type
    # checker the static signatures for those verbs (answer/play/ai/record/...). Generated
    # from schema.json — see swml_verbs_generated.py. TYPE_CHECKING-only: no runtime base.
    from signalwire.core.swml_verbs_generated import _SwmlVerbs

    _VerbsBase = _SwmlVerbs
else:
    _VerbsBase = object


T = TypeVar("T", bound="SWMLBuilder")


class SWMLBuilder(_VerbsBase):
    """
    Fluent builder for SWML documents

    This class provides a fluent interface for building SWML documents
    by chaining method calls. It delegates to an underlying SWMLService
    instance for the actual document creation.
    """

    def __init__(self, service: SWMLService):
        """
        Initialize with a SWMLService instance

        Args:
            service: The SWMLService to delegate to
        """
        self.service = service

        # Dictionary to cache dynamically created methods
        self._verb_methods_cache: dict[str, Any] = {}

        # Create auto-vivified methods for all verbs
        self._create_verb_methods()

    def answer(
        self,
        max_duration: int | None = None,
        codecs: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> Self:
        """
        Add an 'answer' verb to the main section

        Args:
            max_duration: Maximum duration in seconds
            codecs: Comma-separated list of codecs
            username: Username for SIP authentication
            password: Password for SIP authentication

        Returns:
            Self for method chaining
        """
        config: dict[str, Any] = {}
        if max_duration is not None:
            config["max_duration"] = max_duration
        if codecs is not None:
            config["codecs"] = codecs
        if username is not None:
            config["username"] = username
        if password is not None:
            config["password"] = password
        self.service.add_verb("answer", config)
        return self

    def hangup(self, reason: str | None = None) -> Self:
        """
        Add a 'hangup' verb to the main section

        Args:
            reason: Optional reason for hangup

        Returns:
            Self for method chaining
        """
        config: dict[str, Any] = {}
        if reason is not None:
            config["reason"] = reason
        self.service.add_verb("hangup", config)
        return self

    def ai(
        self,
        prompt_text: str | None = None,
        prompt_pom: list[dict[str, Any]] | None = None,
        post_prompt: str | None = None,
        post_prompt_url: str | None = None,
        swaig: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Add an 'ai' verb to the main section

        Args:
            prompt_text: Text prompt for the AI (mutually exclusive with prompt_pom)
            prompt_pom: POM structure for the AI prompt (mutually exclusive with prompt_text)
            post_prompt: Optional post-prompt text
            post_prompt_url: Optional URL for post-prompt processing
            swaig: Optional SWAIG configuration
            **kwargs: Additional AI parameters

        Returns:
            Self for method chaining
        """
        config: dict[str, Any] = {}

        # Handle prompt (either text or POM, but not both). The SWML `ai` verb requires
        # `prompt` to be an OBJECT — {"text": ...} or {"pom": [...]}; a bare string is a
        # fatal error in the AI engine (mod_openai app_config.c: `!cJSON_IsObject(prompt)`
        # fires calling.error and aborts the call), so wrap accordingly.
        if prompt_text is not None:
            config["prompt"] = {"text": prompt_text}
        elif prompt_pom is not None:
            config["prompt"] = {"pom": prompt_pom}

        # Add optional parameters. post_prompt is the same object contract as prompt.
        if post_prompt is not None:
            config["post_prompt"] = {"text": post_prompt}
        if post_prompt_url is not None:
            config["post_prompt_url"] = post_prompt_url
        if swaig is not None:
            config["SWAIG"] = swaig

        # Add any additional kwargs
        config.update(kwargs)

        self.service.add_verb("ai", config)
        return self

    def play(
        self,
        url: str | None = None,
        urls: list[str] | None = None,
        volume: float | None = None,
        say_voice: str | None = None,
        say_language: str | None = None,
        say_gender: str | None = None,
        auto_answer: bool | None = None,
        status_url: str | None = None,
    ) -> Self:
        """
        Add a 'play' verb to the main section

        Args:
            url: Single URL to play (mutually exclusive with urls)
            urls: List of URLs to play (mutually exclusive with url)
            volume: Volume level (-40 to 40)
            say_voice: Voice for text-to-speech
            say_language: Language for text-to-speech
            say_gender: Gender for text-to-speech
            auto_answer: Whether to auto-answer the call
            status_url: URL that receives the play's status events

        Returns:
            Self for method chaining
        """
        # Create base config
        config: dict[str, Any] = {}

        # Add play config (either single URL or list)
        if url is not None:
            config["url"] = url
        elif urls is not None:
            config["urls"] = urls
        else:
            raise ValueError("Either url or urls must be provided")

        # Add optional parameters
        if volume is not None:
            config["volume"] = volume
        if say_voice is not None:
            config["say_voice"] = say_voice
        if say_language is not None:
            config["say_language"] = say_language
        if say_gender is not None:
            config["say_gender"] = say_gender
        if auto_answer is not None:
            config["auto_answer"] = auto_answer
        if status_url is not None:
            config["status_url"] = status_url

        # Add the verb
        self.service.add_verb("play", config)
        return self

    def say(
        self,
        text: str,
        voice: str | None = None,
        language: str | None = None,
        gender: str | None = None,
        volume: float | None = None,
    ) -> Self:
        """
        Add a 'play' verb with say: prefix for text-to-speech

        Args:
            text: Text to speak
            voice: Voice for text-to-speech
            language: Language for text-to-speech
            gender: Gender for text-to-speech
            volume: Volume level (-40 to 40)

        Returns:
            Self for method chaining
        """
        # Create play config with say: prefix
        url = f"say:{text}"

        # Add the verb
        return self.play(
            url=url,
            say_voice=voice,
            say_language=language,
            say_gender=gender,
            volume=volume,
        )

    def add_section(self, section_name: str) -> Self:
        """
        Add a new section to the document

        Args:
            section_name: Name of the section to add

        Returns:
            Self for method chaining
        """
        self.service.add_section(section_name)
        return self

    def build(self) -> dict[str, Any]:
        """
        Build and return the SWML document

        Returns:
            The complete SWML document as a dictionary
        """
        return self.service.get_document()

    def render(self) -> str:
        """
        Build and render the SWML document as a JSON string

        Returns:
            The complete SWML document as a JSON string
        """
        return self.service.render_document()

    def reset(self) -> Self:
        """
        Reset the document to an empty state

        Returns:
            Self for method chaining
        """
        self.service.reset_document()
        return self

    def _create_verb_methods(self) -> None:
        """
        Make the method for each of the schema's verbs, ready for
        ``__getattr__`` to return, allowing for fluent chaining like
        builder.denoise().goto().play(). A method the class defines, such as
        ``answer`` or ``play``, wins: verbs are found through ``__getattr__``,
        which runs only when nothing else is.
        """
        if not getattr(self.service, "schema_utils", None):
            return
        for verb_name in self.service.schema_utils.get_all_verb_names():
            self._verb_method(verb_name)

    def _verb_method(self, verb_name: str) -> Callable[..., Any]:
        """The method for ``verb_name``, made once and cached."""
        method = self._verb_methods_cache.get(verb_name)
        if method is None:
            schema_utils = self.service.schema_utils
            method = _make_verb_method(
                verb_name,
                schema_utils.get_verb_properties(verb_name).get("description"),
                schema_utils.get_verb_parameters(verb_name),
                _add_to_builder,
                returns_self=True,
            )
            self._verb_methods_cache[verb_name] = method
        return method

    def __getattr__(self, name: str) -> Any:
        """
        Dynamically generate and return SWML verb methods when accessed

        This method is called when an attribute lookup fails through the normal
        mechanisms. It checks if the attribute name corresponds to a SWML verb
        defined in the schema, and if so, returns the method for that verb.
        ``return_`` is the method for ``return``, a Python keyword.

        Args:
            name: The name of the attribute being accessed

        Returns:
            The verb method if name is a valid SWML verb, otherwise raises
            AttributeError

        Raises:
            AttributeError: If name is not a valid SWML verb
        """
        if name.startswith("__") or name in ("service", "_verb_methods_cache"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )
        if not getattr(self.service, "schema_utils", None):
            msg = f"'{self.__class__.__name__}' object has no attribute '{name}' (no schema available)"
            raise AttributeError(msg)

        verb_name = _verb_for_attribute(name)
        if verb_name in self.service.schema_utils.get_all_verb_names():
            if "_verb_methods_cache" not in self.__dict__:
                self._verb_methods_cache = {}
            return types.MethodType(self._verb_method(verb_name), self)

        # Not a valid verb
        msg = f"'{self.__class__.__name__}' object has no attribute '{name}'"
        raise AttributeError(msg)


def _add_to_builder(builder: SWMLBuilder, verb: str, body: Any) -> bool:
    """A builder's verb method adds to its service's document."""
    return builder.service.add_verb(verb, body)
