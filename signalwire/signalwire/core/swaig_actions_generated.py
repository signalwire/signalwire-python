# AUTO-GENERATED from porting-sdk/swaig-specs/swaig-response.yaml — DO NOT EDIT.
# (which is vendored from mod_openai; regenerate via
#  python3 porting-sdk/scripts/generate_python_rest_types.py)
#
# The SWAIG response-action surface: one <Action> value TypedDict per object-shaped
# action + a _SwaigActions base with one typed method per wire action (keyed by the wire
# key). The SDK's ergonomic FunctionResult methods (say(text), hold(timeout=300), ...) are
# hand-written on top and call these typed builders. STATIC-ONLY: the action list is a
# plain list of dicts at runtime; this layer just types the shapes.
from __future__ import annotations
from typing import Any, Literal, TypedDict
from typing import TypeVar

_Self = TypeVar("_Self", bound="_SwaigActions")


class ContextSwitchAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    system_prompt: Any
    user_prompt: Any
    system_pom: Any
    user_pom: Any
    consolidate: bool
    full_reset: bool


class HoldAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    timeout: int


class PlaybackBgAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    file: Any
    wait: bool


class TransferAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    dest: Any
    summarize: bool


class _SwaigActions:
    """Typed SWAIG response-action builders (one per wire action). The host class
    provides ``self.action`` (the list serialized to the wire)."""

    def add_dynamic_hints(self: _Self, value: list[Any]) -> _Self:
        """Add ASR hints. Strings go to `dynamic_hints`; `{hint, ...}` objects go to `dynamic_hearing_hints` (and the `hint` value is also added to `dynamic_hints`). Restarts speech detection"""  # actions.c:547
        self.action.append({"add_dynamic_hints": value})  # type: ignore[attr-defined]
        return self

    def back_to_back_functions(self: _Self, value: bool | Literal["forever"]) -> _Self:
        """Allow consecutive function calls without a user turn. `true` = `1`, `"forever"` = `2`"""  # actions.c:359
        self.action.append({"back_to_back_functions": value})  # type: ignore[attr-defined]
        return self

    def change_context(self: _Self, value: str) -> _Self:
        """Switch to a named **context** (same machinery as the `change_context` function)"""  # actions.c:238
        self.action.append({"change_context": value})  # type: ignore[attr-defined]
        return self

    def change_step(self: _Self, value: str) -> _Self:
        """Switch to a named **step** (or `"next"`)"""  # actions.c:248
        self.action.append({"change_step": value})  # type: ignore[attr-defined]
        return self

    def clear_dynamic_hints(self: _Self, value: dict[str, Any]) -> _Self:
        """Clear both dynamic hint lists and restart speech detection"""  # actions.c:579
        self.action.append({"clear_dynamic_hints": value})  # type: ignore[attr-defined]
        return self

    def context_switch(self: _Self, value: str | ContextSwitchAction) -> _Self:
        """Replace the system prompt / start a new conversation context. Object form: `{system_prompt, user_prompt, system_pom, user_pom, consolidate, full_reset}`. `system_pom`/`user_pom` render to prompt text; prompts are expanded against prompt vars + post_data; `consolidate:true` summarizes first"""  # actions.c:594
        self.action.append({"context_switch": value})  # type: ignore[attr-defined]
        return self

    def end_of_speech_timeout(self: _Self, value: int) -> _Self:
        """Set end-of-speech detection timeout (must be >0)"""  # actions.c:312
        self.action.append({"end_of_speech_timeout": value})  # type: ignore[attr-defined]
        return self

    def extensive_data(self: _Self, value: bool) -> _Self:
        """Enable extensive data in the function/conversation log"""  # actions.c:373
        self.action.append({"extensive_data": value})  # type: ignore[attr-defined]
        return self

    def functions_on_speaker_timeout(self: _Self, value: bool) -> _Self:
        """Set whether functions may fire on speaker timeout"""  # actions.c:369
        self.action.append({"functions_on_speaker_timeout": value})  # type: ignore[attr-defined]
        return self

    def hangup(self: _Self, value: dict[str, Any]) -> _Self:
        """Set `offhook = 0` (hang up). Note: a graceful "say goodbye" hangup is the **built-in `hangup` function**, not this action"""  # actions.c:294
        self.action.append({"hangup": value})  # type: ignore[attr-defined]
        return self

    def hold(self: _Self, value: int | str | HoldAction) -> _Self:
        """Put the call on hold for N seconds. Accepts a number, a time string (`"5m"`, `"1:30"` via `parse_time`), or `{timeout}`. Default 300s; values <0 or >900 clamp to 300"""  # actions.c:258
        self.action.append({"hold": value})  # type: ignore[attr-defined]
        return self

    def playback_bg(self: _Self, value: str | PlaybackBgAction) -> _Self:
        """Play an audio file in the background. `{wait:true}` makes the agent wait for it. Replaces any currently-open background file"""  # actions.c:695
        self.action.append({"playback_bg": value})  # type: ignore[attr-defined]
        return self

    def replace_in_history(self: _Self, value: str | Literal[True]) -> _Self:
        """Replace the function call's text in conversation history. A string is stored prefixed with `~LN(<language>)-; `; `true` stores an empty string"""  # actions.c:379
        self.action.append({"replace_in_history": value})  # type: ignore[attr-defined]
        return self

    def say(self: _Self, value: str) -> _Self:
        """Speak text immediately via TTS, then wait for speaking to finish. Also logs `tl_manual_say`"""  # actions.c:434
        self.action.append({"say": value})  # type: ignore[attr-defined]
        return self

    def set_global_data(self: _Self, value: dict[str, Any]) -> _Self:
        """Merge keys into global data, then refresh prompt vars. Gated by `swaig_set_global_data`"""  # actions.c:498
        self.action.append({"set_global_data": value})  # type: ignore[attr-defined]
        return self

    def set_meta_data(self: _Self, value: dict[str, Any]) -> _Self:
        """Merge keys into the calling function's metadata store (keyed by its `meta_data_token`)"""  # actions.c:459
        self.action.append({"set_meta_data": value})  # type: ignore[attr-defined]
        return self

    def settings(self: _Self, value: dict[str, Any]) -> _Self:
        """Modify LLM settings at runtime (`parse_json_settings`). Gated by `swaig_allow_settings`"""  # actions.c:442
        self.action.append({"settings": value})  # type: ignore[attr-defined]
        return self

    def speech_event_timeout(self: _Self, value: int) -> _Self:
        """Set speech event timeout (must be >0)"""  # actions.c:326
        self.action.append({"speech_event_timeout": value})  # type: ignore[attr-defined]
        return self

    def stop(self: _Self, value: dict[str, Any]) -> _Self:
        """Stop the AI agent immediately (interrupt + `running = 0`)"""  # actions.c:452
        self.action.append({"stop": value})  # type: ignore[attr-defined]
        return self

    def stop_playback_bg(self: _Self, value: dict[str, Any]) -> _Self:
        """Stop/close the background audio file"""  # actions.c:685
        self.action.append({"stop_playback_bg": value})  # type: ignore[attr-defined]
        return self

    def toggle_functions(self: _Self, value: list[dict[str, Any]]) -> _Self:
        """Enable/disable functions. `active` via `check_active`: `-1` default/toggle, `0` off, `1+` use-count. **Only affects functions sharing the calling function's `meta_data_token`** (`actions.c:419-420`)"""  # actions.c:389
        self.action.append({"toggle_functions": value})  # type: ignore[attr-defined]
        return self

    def transfer(self: _Self, value: str | TransferAction) -> _Self:
        """Transfer the call to `dest`. `summarize:true` sets `transfer_summary`. Sets `openai_transfer_check` var, interrupts, stops the loop. Ignored if already interrupted"""  # actions.c:136
        self.action.append({"transfer": value})  # type: ignore[attr-defined]
        return self

    def unset_global_data(self: _Self, value: str | list[Any]) -> _Self:
        """Remove key(s) from global data, then refresh prompt vars. Gated by `swaig_set_global_data`"""  # actions.c:515
        self.action.append({"unset_global_data": value})  # type: ignore[attr-defined]
        return self

    def unset_meta_data(self: _Self, value: str | list[Any]) -> _Self:
        """Remove key(s) from the calling function's metadata store"""  # actions.c:477
        self.action.append({"unset_meta_data": value})  # type: ignore[attr-defined]
        return self

    def user_event(self: _Self, value: dict[str, Any]) -> _Self:
        """Fire relay event `calling.user_event` with the object as payload"""  # actions.c:231
        self.action.append({"user_event": value})  # type: ignore[attr-defined]
        return self

    def user_input(self: _Self, value: str) -> _Self:
        """Push text onto the input queue as if the user spoke it"""  # actions.c:541
        self.action.append({"user_input": value})  # type: ignore[attr-defined]
        return self

    def wait_for_user(
        self: _Self, value: bool | int | Literal["answer_first"]
    ) -> _Self:
        """`true` = `1`, a number sets a count, `"answer_first"` = `2` (require caller answer)"""  # actions.c:300
        self.action.append({"wait_for_user": value})  # type: ignore[attr-defined]
        return self
