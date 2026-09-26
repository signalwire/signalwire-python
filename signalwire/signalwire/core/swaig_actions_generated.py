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


class ChangeVoiceAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    voice: Any


class ContextSwitchAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    consolidate: bool | str
    full_reset: bool | str
    system_pom: dict[str, Any]
    system_prompt: str
    user_pom: dict[str, Any]
    user_prompt: str


class HoldAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    step: str
    timeout: float | str
    timeout_step: str


class PlaybackBgAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    file: str
    wait: bool | str


class TransferAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    dest: str
    summarize: bool | str


class SwaigAction(TypedDict, total=False):
    """A response-action object. The keys below are the full vocabulary dispatched by actions.c::process_action; an action object sets one or more of them. Each key's source line is the engine dispatch site.

    Open shape: extra server keys permitted; not validated at runtime.
    """

    SWML: str | dict[str, Any]
    add_dynamic_hints: list[dict[str, Any] | str]
    back_to_back_functions: bool | Literal["forever"] | str
    change_context: str
    change_step: str
    change_voice: str | ChangeVoiceAction
    clear_dynamic_hints: bool | str
    context_switch: str | ContextSwitchAction
    end_of_speech_timeout: int
    extensive_data: bool | str
    functions_on_speaker_timeout: bool | str
    hangup: bool | str
    hold: int | str | HoldAction
    playback_bg: str | PlaybackBgAction
    replace_in_history: str | Literal[True]
    say: str
    set_global_data: dict[str, Any]
    set_meta_data: dict[str, Any]
    settings: dict[str, Any]
    speech_event_timeout: int
    stop: bool | str
    stop_playback_bg: bool | str | int | dict[str, Any] | list[Any] | None
    toggle_functions: list[dict[str, Any]]
    transfer: str | TransferAction
    unset_global_data: str | list[str]
    unset_meta_data: str | list[str]
    user_event: dict[str, Any]
    user_input: str
    wait_for_user: bool | int | Literal["answer_first"] | str


class SwaigResponse(TypedDict, total=False):
    """Parsed at actions.c:2479-2521.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    response: str | dict[str, Any]
    action: SwaigAction | list[SwaigAction]
    post_process: bool


class _SwaigActions:
    """Typed SWAIG response-action builders (one per wire action). The host class
    provides ``self.action`` (the list serialized to the wire)."""

    def SWML(self: _Self, value: str | dict[str, Any]) -> _Self:
        """Execute a SWML document inline, or with sibling `transfer:true` transfer the call into it. Gated by `swaig_allow_swml`. **Transfer additionally requires `from_relay`** (`actions.c:142-145`); inline execution captures an optional `ai_response` SWML var back into the conversation"""  # actions.c:129
        self.action.append({"SWML": value})  # type: ignore[attr-defined]
        return self

    def add_dynamic_hints(self: _Self, value: list[dict[str, Any] | str]) -> _Self:
        """Add ASR hints. Strings go to `dynamic_hints`; `{hint, ...}` objects go to `dynamic_hearing_hints` (and the `hint` value is also added to `dynamic_hints`). Restarts speech detection"""  # actions.c:611
        self.action.append({"add_dynamic_hints": value})  # type: ignore[attr-defined]
        return self

    def back_to_back_functions(
        self: _Self, value: bool | Literal["forever"] | str
    ) -> _Self:
        """Allow consecutive function calls without a user turn. `true` = `1`, `"forever"` = `2`"""  # actions.c:400
        self.action.append({"back_to_back_functions": value})  # type: ignore[attr-defined]
        return self

    def change_context(self: _Self, value: str) -> _Self:
        """Switch to a named **context** (same machinery as the `change_context` function)"""  # actions.c:249
        self.action.append({"change_context": value})  # type: ignore[attr-defined]
        return self

    def change_step(self: _Self, value: str) -> _Self:
        """Switch to a named **step** (or `"next"`)"""  # actions.c:259
        self.action.append({"change_step": value})  # type: ignore[attr-defined]
        return self

    def change_voice(self: _Self, value: str | ChangeVoiceAction) -> _Self:
        """Staged at `actions.c:483`, applied by `ai_threads.c` `apply_pending_voice_change`. The string (or the object's `voice`) is an `engine.voice:model` spec. Change the agent's voice mid-call by rebinding the **current language's** voice node (`cur_aish`) to an arbitrary `engine.voice:model` — works in both `~LN` (Mode A) and ASR-driven (Mode B) multilingual modes, since `cur_aish` is the current language's node in both. Cross-engine is intended (e.g. switch to a fish/groq voice for its sound/delivery tags). Staged on the session thread; the output thread closes+reopens the handle at the next batch boundary (never mid-utterance). Writes the node's **configured** identity, so the new voice **persists across later language re-selects of that node for the rest of the call**; a voice that will not open falls back to the fallback voice. Not persisted across calls (the voice list is rebuilt from SWML each session)"""  # actions.c:483
        self.action.append({"change_voice": value})  # type: ignore[attr-defined]
        return self

    def clear_dynamic_hints(self: _Self, value: bool | str) -> _Self:
        """Clear both dynamic hint lists and restart speech detection"""  # actions.c:643
        self.action.append({"clear_dynamic_hints": value})  # type: ignore[attr-defined]
        return self

    def context_switch(self: _Self, value: str | ContextSwitchAction) -> _Self:
        """Replace the system prompt / start a new conversation context. Object form: `{system_prompt, user_prompt, system_pom, user_pom, consolidate, full_reset}`. `system_pom`/`user_pom` render to prompt text; prompts are expanded against prompt vars + post_data; `consolidate:true` summarizes first"""  # actions.c:658
        self.action.append({"context_switch": value})  # type: ignore[attr-defined]
        return self

    def end_of_speech_timeout(self: _Self, value: int) -> _Self:
        """Set end-of-speech detection timeout (must be >0)"""  # actions.c:353
        self.action.append({"end_of_speech_timeout": value})  # type: ignore[attr-defined]
        return self

    def extensive_data(self: _Self, value: bool | str) -> _Self:
        """Enable extensive data in the function/conversation log"""  # actions.c:414
        self.action.append({"extensive_data": value})  # type: ignore[attr-defined]
        return self

    def functions_on_speaker_timeout(self: _Self, value: bool | str) -> _Self:
        """Set whether functions may fire on speaker timeout"""  # actions.c:410
        self.action.append({"functions_on_speaker_timeout": value})  # type: ignore[attr-defined]
        return self

    def hangup(self: _Self, value: bool | str) -> _Self:
        """Set `offhook = 0` (hang up). Note: a graceful "say goodbye" hangup is the **built-in `hangup` function**, not this action"""  # actions.c:335
        self.action.append({"hangup": value})  # type: ignore[attr-defined]
        return self

    def hold(self: _Self, value: int | str | HoldAction) -> _Self:
        """Put the call on hold for N seconds. Accepts a number, a time string (`"5m"`, `"1:30"` via `parse_time`), or an object `{timeout, step, timeout_step}`. Default 300s; values <0 or >900 clamp to 300. `step` / `timeout_step` are optional destinations applied **when the hold ends** — see below"""  # actions.c:269
        self.action.append({"hold": value})  # type: ignore[attr-defined]
        return self

    def playback_bg(self: _Self, value: str | PlaybackBgAction) -> _Self:
        """Play an audio file in the background. `{wait:true}` makes the agent wait for it. Replaces any currently-open background file"""  # actions.c:759
        self.action.append({"playback_bg": value})  # type: ignore[attr-defined]
        return self

    def replace_in_history(self: _Self, value: str | Literal[True]) -> _Self:
        """Replace the function call's text in conversation history. A string is stored prefixed with `~LN(<language>)-; `; `true` stores an empty string"""  # actions.c:420
        self.action.append({"replace_in_history": value})  # type: ignore[attr-defined]
        return self

    def say(self: _Self, value: str) -> _Self:
        """Speak text immediately via TTS, then wait for speaking to finish. Also logs `tl_manual_say`"""  # actions.c:475
        self.action.append({"say": value})  # type: ignore[attr-defined]
        return self

    def set_global_data(self: _Self, value: dict[str, Any]) -> _Self:
        """Merge keys into global data, then refresh prompt vars. Gated by `swaig_set_global_data`"""  # actions.c:562
        self.action.append({"set_global_data": value})  # type: ignore[attr-defined]
        return self

    def set_meta_data(self: _Self, value: dict[str, Any]) -> _Self:
        """Merge keys into the calling function's metadata store (keyed by its `meta_data_token`)"""  # actions.c:523
        self.action.append({"set_meta_data": value})  # type: ignore[attr-defined]
        return self

    def settings(self: _Self, value: dict[str, Any]) -> _Self:
        """Modify LLM settings at runtime (`parse_json_settings`). Gated by `swaig_allow_settings`"""  # actions.c:506
        self.action.append({"settings": value})  # type: ignore[attr-defined]
        return self

    def speech_event_timeout(self: _Self, value: int) -> _Self:
        """Set speech event timeout (must be >0)"""  # actions.c:367
        self.action.append({"speech_event_timeout": value})  # type: ignore[attr-defined]
        return self

    def stop(self: _Self, value: bool | str) -> _Self:
        """Stop the AI agent immediately (interrupt + `running = 0`)"""  # actions.c:516
        self.action.append({"stop": value})  # type: ignore[attr-defined]
        return self

    def stop_playback_bg(
        self: _Self, value: bool | str | int | dict[str, Any] | list[Any] | None
    ) -> _Self:
        """Stop/close the background audio file"""  # actions.c:749
        self.action.append({"stop_playback_bg": value})  # type: ignore[attr-defined]
        return self

    def toggle_functions(self: _Self, value: list[dict[str, Any]]) -> _Self:
        """Enable/disable functions. `active` via `check_active`: `-1` default/toggle, `0` off, `1+` use-count. **Only affects functions sharing the calling function's `meta_data_token`** (`actions.c:419-420`)"""  # actions.c:430
        self.action.append({"toggle_functions": value})  # type: ignore[attr-defined]
        return self

    def transfer(self: _Self, value: str | TransferAction) -> _Self:
        """Transfer the call to `dest`. `summarize:true` sets `transfer_summary`. Sets `openai_transfer_check` var, interrupts, stops the loop. Ignored if already interrupted"""  # actions.c:381
        self.action.append({"transfer": value})  # type: ignore[attr-defined]
        return self

    def unset_global_data(self: _Self, value: str | list[str]) -> _Self:
        """Remove key(s) from global data, then refresh prompt vars. Gated by `swaig_set_global_data`"""  # actions.c:579
        self.action.append({"unset_global_data": value})  # type: ignore[attr-defined]
        return self

    def unset_meta_data(self: _Self, value: str | list[str]) -> _Self:
        """Remove key(s) from the calling function's metadata store"""  # actions.c:541
        self.action.append({"unset_meta_data": value})  # type: ignore[attr-defined]
        return self

    def user_event(self: _Self, value: dict[str, Any]) -> _Self:
        """Fire relay event `calling.user_event` with the object as payload"""  # actions.c:242
        self.action.append({"user_event": value})  # type: ignore[attr-defined]
        return self

    def user_input(self: _Self, value: str) -> _Self:
        """Push text onto the input queue as if the user spoke it"""  # actions.c:605
        self.action.append({"user_input": value})  # type: ignore[attr-defined]
        return self

    def wait_for_user(
        self: _Self, value: bool | int | Literal["answer_first"] | str
    ) -> _Self:
        """`true` = `1`, a number sets a count, `"answer_first"` = `2` (require caller answer)"""  # actions.c:341
        self.action.append({"wait_for_user": value})  # type: ignore[attr-defined]
        return self
