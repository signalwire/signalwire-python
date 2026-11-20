"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

FunctionResult class for handling the response format of SWAIG function calls

The SDK's installed documentation covers this module: run ``sw-pydocs tools``, or ``sw-pydocs`` for the index.
"""

import json
import re
from typing import Any, Literal

# A SWML variable reference, such as ${timeout}, which the schema accepts
# wherever it accepts an integer or a boolean
_SWML_VAR = re.compile(r"^[$%]\{.*\}$")


def _swml_int(
    name: str,
    value: Any,
    minimum: int | None = None,
    maximum: int | None = None,
) -> Any:
    """Return ``value`` as an int for a SWML verb, or raise ValueError.

    Accepts an int, an integral float, a string of digits, or a SWML variable
    reference, which is passed through as written. An int must be within
    ``minimum`` and ``maximum`` when they are given.
    """
    number: int | None = None
    if isinstance(value, str):
        text = value.strip()
        if _SWML_VAR.match(text):
            return text
        digits = text.lstrip("-")
        # isdigit() also accepts digits such as "²", which int() refuses
        if digits.isascii() and digits.isdigit():
            number = int(text)
    elif isinstance(value, int) and not isinstance(value, bool):
        number = value
    elif isinstance(value, float) and value.is_integer():
        number = int(value)
    in_range = number is not None and (
        (minimum is None or number >= minimum)
        and (maximum is None or number <= maximum)
    )
    if not in_range:
        if minimum is not None and maximum is not None:
            expected = f"an integer from {minimum} to {maximum}"
        elif minimum is not None:
            expected = f"an integer of at least {minimum}"
        elif maximum is not None:
            expected = f"an integer of at most {maximum}"
        else:
            expected = "an integer"
        raise ValueError(f"{name} must be {expected}, got {value!r}")
    return number


def _swml_text(value: Any) -> str:
    """A checked int or bool as the string a SWML verb reads: "true", "30"."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _swml_bool(name: str, value: Any) -> Any:
    """Return ``value`` as a bool for a SWML verb, or raise ValueError.

    Accepts a bool, the strings "true" and "false" in any case, or a SWML
    variable reference, which is passed through as written.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text.lower() in ("true", "false"):
            return text.lower() == "true"
        if _SWML_VAR.match(text):
            return text
    raise ValueError(f"{name} must be a boolean, got {value!r}")


class FunctionResult:
    """Build the value a SWAIG tool function returns: a response prompt plus actions.

    `FunctionResult` is the return type for all SWAIG tool functions, whether they
    are defined with the `tool()` decorator or `define_tool()` on `AgentBase`. It
    wraps a response (a prompt the AI reads, not text it speaks verbatim) and an
    ordered list of actions (transfers, SMS, data updates, context switches, and
    more). Every method returns `self`, so calls chain into one fluent expression.

    The result object has three main components:

    1. `response`: A PROMPT injected into the model's context. NOT speech. It may be
       a plain string, or an object separating outcome from instruction, such as
       `{"tool_result": "status: on hold", "tool_prompt": "Tell the caller you
       are placing them on hold."}`. See `set_tool_response()`.
    2. `action`: Ordered list of structured actions to execute. Actions run
       sequentially in the order they were added.
    3. `post_process`: Whether to let the AI take another turn before executing
       actions.

    IMPORTANT - `response` is a prompt, not a script. The SWML schema defines it
    as "a static response text or message returned to the AI agent's context".
    The model reads it and then decides what to say. It is NOT played to the
    caller verbatim.

    It can carry facts, an instruction, or both. The clearest form keeps them
    apart, with the facts in `tool_result` and the instruction in `tool_prompt`:

    ```python
    FunctionResult(tool_result="Order 1234 shipped Tuesday.",
                   tool_prompt="Tell the caller when their order shipped.")
    FunctionResult("Order 1234 shipped Tuesday.")                    # facts
    FunctionResult("Tell the caller their order shipped Tuesday.")   # instruction
    FunctionResult("Your order shipped Tuesday.")                    # avoid
    ```

    Avoid the last form, a line written for the caller. It usually still "works"
    because the model tends to parrot it, but it's interpreted, not spoken, so it
    will drift, get rephrased, or be merged with other context.

    Post-processing behavior:

    - `post_process=False` (default): Execute actions immediately after the AI
      response.
    - `post_process=True`: Let the AI respond to the user one more time, then
      execute actions.

    Use `post_process=True` whenever the caller must HEAR something before the
    action takes effect, because many actions end or suspend the AI's turn:
    `hold` pauses speech detection entirely, `connect`/`transfer` replace the
    leg, `hangup` ends the call. Anything not said before those land is never
    said at all. It is also useful for confirmation workflows like "I'll transfer
    you to sales. Do you have any other questions first?" (the AI can handle the
    follow-up, then execute the transfer).

    Attributes:
        response: The prompt injected into the model's context. Either a plain
            string (default `""`) or a `{"tool_result": ..., "tool_prompt": ...}`
            object built by `set_tool_response()`.
        action: Ordered list of action objects to execute (default `[]`).
        post_process: When `True`, the AI responds to the prompt and takes one
            more conversational turn with the user before executing actions.
            When `False` (default), actions execute immediately after the
            response.

    Warning:
        Terminal actions like `connect(final=True)` and `hangup()` end the call
        flow. Place them last in the chain so that preceding actions (data
        updates, SMS, and so on) have a chance to execute.

    Example:
        ```python
        result = FunctionResult("Tell them you found their order")

        # With actions
        result = (
            FunctionResult("I'll transfer you to support")
            .add_action("transfer", {"dest": "support"})
        )

        # With multiple actions
        result = (
            FunctionResult("Processing your request")
            .add_actions([
                {"set_global_data": {"key": "value"}},
                {"play": {"url": "music.mp3"}}
            ])
        )

        # A chain: the data update and SMS run before the terminal transfer
        result = (
            FunctionResult(
                "Tell the caller you are transferring them to billing and ask if "
                "they need anything else first.",
                post_process=True,
            )
            .update_global_data({"transferred": True})
            .send_sms(
                to_number="+15551234567",
                from_number="+15559876543",
                body="You are being transferred to billing.",
            )
            .connect("+15551234567", final=True)  # terminal: goes last
        )
        ```
    """

    def __init__(
        self,
        response: str | dict[str, Any] | None = None,
        post_process: bool = False,
        tool_result: str | None = None,
        tool_prompt: str | None = None,
    ):
        """Initialize a new SWAIG function result.

        Args:
            response: Optional PROMPT to inject into the model's context: facts or an
                instruction the model reads, not speech played to the caller. Write
                an instruction in the second person (`"Tell the caller their order
                shipped Tuesday."`). A plain string or a `tool_result`/`tool_prompt`
                dict. See the class docstring.
            post_process: Whether to let AI take another turn before executing
                actions. Defaults to False (execute actions immediately after the
                response). Set True when the caller must hear something before the
                action lands (hold, connect, transfer, hangup).
            tool_result: Factual outcome of the call, such as `"status: on hold"`.
                When either `tool_result` or `tool_prompt` is given, the response
                takes the structured form built by `set_tool_response()` and replaces
                `response`.
            tool_prompt: Instruction for what the model should say next, in the second
                person. Pairs with `tool_result`.
        """
        self.response: str | dict[str, Any] = response if response is not None else ""
        self.action: list[dict[str, Any]] = []
        self.post_process = post_process

        if tool_result is not None or tool_prompt is not None:
            self.set_tool_response(tool_result=tool_result, tool_prompt=tool_prompt)

    def set_response(self, response: str) -> "FunctionResult":
        """Set or replace the response after construction.

        The response is a prompt injected into the model's context, not text spoken
        verbatim, so write it as an instruction in the second person. To separate a
        factual outcome from the speaking instruction, use `set_tool_response()`
        instead.

        Args:
            response: Instruction for the model, such as `"Tell the caller their order
                shipped yesterday."`

        Returns:
            This `FunctionResult`, for chaining.
        """
        self.response = response
        return self

    def set_tool_response(
        self, tool_result: str | None = None, tool_prompt: str | None = None
    ) -> "FunctionResult":
        """Set the structured response form, separating outcome from instruction.

        `response` may be a plain string, or an object with up to two distinct keys:

        ```python
        {"tool_result": "status: on hold",
         "tool_prompt": "Tell the caller you are placing them on hold."}
        ```

        - `tool_result`: what the tool DID. A factual status line for the model to
          reason from ("hold initiated", "payment declined", "3 seats left").
        - `tool_prompt`: what the model should now SAY. An instruction, second
          person, exactly like the string form of `response`.

        Splitting them keeps the model from reading a status line aloud, and keeps the
        spoken instruction from being mistaken for data. For a single instruction
        string, use `set_response()`.

        Args:
            tool_result: Factual outcome of the call. Omit if there is nothing to
                report beyond the instruction.
            tool_prompt: Instruction for what to say next. Omit for a silent
                status-only result.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult().set_tool_response(
                tool_result="payment declined",
                tool_prompt="Tell the caller the card was declined and offer another.",
            )
            ```
        """
        payload: dict[str, Any] = {}
        if tool_result is not None:
            payload["tool_result"] = tool_result
        if tool_prompt is not None:
            payload["tool_prompt"] = tool_prompt
        self.response = payload
        return self

    def set_post_process(self, post_process: bool) -> "FunctionResult":
        """Enable or disable post-processing after construction.

        When post-processing is enabled, the AI speaks the response and takes one more
        conversational turn with the user before executing actions. This is useful for
        confirmation workflows.

        Args:
            post_process: True to let AI respond once more before executing actions,
                False to execute actions immediately after the response.

        Returns:
            This `FunctionResult`, for chaining.
        """
        self.post_process = post_process
        return self

    def add_action(self, name: str, data: Any) -> "FunctionResult":
        """Append a raw action to the action list.

        Prefer the named convenience methods (`connect()`, `hangup()`, `say()`, and
        so on) for common operations.

        Args:
            name: The name/type of the action (for example `"hold"`, `"hangup"`,
                `"set_global_data"`).
            data: The action payload. Can be a string, boolean, dict, or list
                depending on the action type.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = (
                FunctionResult("Processing your request.")
                .add_action("set_global_data", {"status": "active"})
                .add_action("hold", 60)
            )
            ```
        """
        self.action.append({name: data})
        return self

    def add_actions(self, actions: list[dict[str, Any]]) -> "FunctionResult":
        """Append multiple raw actions at once.

        Each action dictionary is added to the action list in order.

        Args:
            actions: List of action dictionaries to append. Each dictionary should map
                a single action name to its payload.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult("Processing your request.").add_actions([
                {"set_global_data": {"key": "value"}},
                {"hold": 60},
            ])
            ```
        """
        self.action.extend(actions)
        return self

    def connect(
        self, destination: str, final: bool = True, from_addr: str | None = None
    ) -> "FunctionResult":
        """Add a connect action to transfer/connect the call to another destination.

        This is a convenience method that abstracts the SWML `connect` verb, so users
        don't need to manually construct SWML documents.

        Transfer behavior:

        - `final=True`: Permanent transfer. The call exits the agent completely, and
          SWML replaces the agent and the call continues there.
        - `final=False`: Temporary transfer. If the far end hangs up, the call returns
          to the agent to continue the conversation.

        The action carries the SWML document plus a `transfer` flag of `"true"` or
        `"false"` that follows `final`.

        Args:
            destination: Where to connect the call: a phone number in E.164 format
                (for example `"+15551234567"`) or a SIP address (for example
                `"support@company.com"`).
            final: Whether this is a permanent transfer (True, terminal) or temporary
                (False). Defaults to True.
            from_addr: Optional caller ID override (phone number or SIP address). If
                None, no `from` is sent and the current call's from address is used.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            # Permanent transfer to a phone number
            result.connect("+15551234567", final=True)

            # Temporary transfer to a SIP address with a custom caller ID
            result.connect("support@company.com", final=False, from_addr="+15559876543")
            ```
        """
        # Build the connect verb parameters
        connect_params = {"to": destination}
        if from_addr is not None:
            connect_params["from"] = from_addr

        # Create the SWML action
        swml_action = {
            "SWML": {
                "sections": {"main": [{"connect": connect_params}]},
                "version": "1.0.0",
            },
            "transfer": str(final).lower(),  # Convert boolean to "true"/"false" string
        }

        # Add to actions list
        self.action.append(swml_action)
        return self

    def swml_transfer(
        self, dest: str, ai_response: str, final: bool = True
    ) -> "FunctionResult":
        """Add a SWML transfer action with an AI response set up for the return.

        This is a virtual helper that generates SWML to transfer the call to another
        destination and sets up an AI response for when the transfer completes and
        control returns to the agent. The SWML sets `ai_response` and then runs a
        `transfer` verb to `dest`.

        For transfers, you typically want to enable post-processing so the AI speaks
        the response first before executing the transfer.

        Note:
            For simple phone-number or SIP transfers, use `connect()` instead. Use
            `swml_transfer()` to hand off to another SWML document and set up a
            return message.

        Args:
            dest: Destination URL for the transfer (SWML endpoint, SIP address, etc.).
            ai_response: Message the AI should say when the transfer completes and
                control returns to the agent. Only meaningful when `final=False`.
            final: Whether this is a permanent transfer (True) or temporary (False).
                Defaults to True (same as `connect()`).

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            # Permanent transfer (default)
            result = (
                FunctionResult("I'm transferring you to support", post_process=True)
                .swml_transfer(
                    "https://support.example.com/swml",
                    "Goodbye!",  # Won't be used since final=True by default
                )
            )

            # Temporary transfer with return
            result.swml_transfer(
                "https://support.example.com/swml",
                "The support call is complete. How else can I help?",
                final=False,
            )
            ```
        """
        # Create the SWML action structure directly
        swml_action = {
            "SWML": {
                "version": "1.0.0",
                "sections": {
                    "main": [
                        {"set": {"ai_response": ai_response}},
                        {"transfer": {"dest": dest}},
                    ]
                },
            },
            "transfer": str(final).lower(),  # Convert boolean to "true"/"false" string
        }

        # Add to actions list directly
        self.action.append(swml_action)

        return self

    def update_global_data(self, data: dict[str, Any]) -> "FunctionResult":
        """Update global agent data variables.

        This is a convenience method that abstracts the `set_global_data` action.
        Global data persists across the entire agent session and is available in
        prompt variables (`${global_data.key}`) and can be accessed by all functions.

        Args:
            data: Dictionary of key-value pairs to merge into the global data. Existing
                keys are overwritten; new keys are added.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult("Saved.").update_global_data({"plan": "premium"})
            ```
        """
        return self.add_action("set_global_data", data)

    def swml_user_event(self, event_data: dict[str, Any]) -> "FunctionResult":
        """Send a user event through SWML to update the client UI.

        This is a convenience method for sending user events to connected clients,
        commonly used for real-time UI updates in interactive applications (a
        scoreboard, dealing cards, showing status).

        Args:
            event_data: Dictionary containing the event payload. Include a `"type"`
                key to help clients distinguish between event types, for example
                `{"type": "cards_dealt", "player_hand": [...], "score": 21}`.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = (
                FunctionResult("You have blackjack!")
                .swml_user_event({
                    "type": "cards_dealt",
                    "player_hand": ["A", "K"],
                    "dealer_hand": ["9", "7"],
                    "player_score": 21,
                })
            )
            ```
        """
        swml_action = {
            "sections": {"main": [{"user_event": {"event": event_data}}]},
            "version": "1.0.0",
        }

        return self.add_action("SWML", swml_action)

    def swml_change_step(self, step_name: str) -> "FunctionResult":
        """Force the conversation into a specific step in the current context.

        This is a workflow-level transition driven by your webhook, not by the
        model. Webhook-triggered step changes bypass any `valid_steps` clamp
        on the current step (the model's `next_step` tool is the constrained
        path; this is the unconstrained one). Use it when something the user
        said unambiguously requires moving the flow forward. Steps are defined with
        `ContextBuilder` and represent discrete stages in a workflow (for example
        "greeting", "verification", "checkout").

        Communicating intent to the destination step:

        When the model arrives at the new step, the next thing it sees in
        history is the tool result that contained this action, that is, your
        `FunctionResult`'s `response` text. Put your "why" there. The model
        reads it before the new step's injected instructions:

        ```python
        FunctionResult(
            "Premium plan confirmed. Now collecting payment details."
        ).swml_change_step("collect_payment")
        ```

        For structured data the destination step needs (account number,
        plan tier, etc.), pair this with `update_global_data()` and reference
        the values from the destination step's `text` via `${var}` expansion:

        ```python
        (FunctionResult("Premium plan confirmed.")
            .update_global_data({"plan": "premium", "billing_cycle": "annual"})
            .swml_change_step("collect_payment"))
        ```

        And in the destination step's text:

        ```python
        step.set_text(
            "Collect payment for the ${plan} plan, billed ${billing_cycle}. "
            "Confirm the amount with the user before proceeding."
        )
        ```

        Args:
            step_name: Name of the step to transition to. The step must exist in the
                current context.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = (
                FunctionResult("Starting a new hand")
                .update_global_data({"chips": 1000})
                .swml_change_step("betting")
            )
            ```
        """
        return self.add_action("change_step", step_name)

    def refresh_step(self, step_name: str) -> "FunctionResult":
        """Enter the current step again: it starts over, its text expanded with the
        global data now.

        The platform expands a step's `${global_data.*}` values when the
        step is entered. Current releases expand the text again before a
        request whenever a value it reads has changed, so new global data
        reaches the model without this. Earlier releases, and a realtime
        model, keep the values from entry: there, return this with the
        current step's name, after `update_global_data` in the same
        result, to show the new ones. Entering a step starts it over: its
        `history` mode applies again, so under "hide" the step's dialogue
        so far leaves the model's context too.

        The same action as `swml_change_step(step_name)`.

        Args:
            step_name: The name of the step the call is in.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = (
                FunctionResult("Added the drink.")
                .update_global_data({"order_total": "$14.50"})
                .refresh_step("take_order")
            )
            ```
        """
        return self.swml_change_step(step_name)

    def swml_change_context(self, context_name: str) -> "FunctionResult":
        """Force the conversation into a different context.

        Contexts represent distinct operational modes (for example "sales", "support",
        "billing"), each with their own prompts, tools, and steps defined with
        `ContextBuilder`. Webhook-triggered context changes bypass any
        `valid_contexts` clamp. Step state resets (cur_step = 0) on entry. The new
        context's first step's instructions are injected on the next turn.

        Communicating intent to the destination context:

        Same pattern as `swml_change_step`: the model reads your `FunctionResult`'s
        `response` text as the tool result before it sees the destination context's
        first step. Put your reason there:

        ```python
        FunctionResult(
            "I'm transferring you to billing because your question is "
            "about an invoice charge."
        ).swml_change_context("billing")
        ```

        For structured carry-over, use `update_global_data()` and reference the
        values via `${var}` expansion in the destination context's step text.

        Note:
            Conversation history is preserved across context switches unless the
            destination context is marked `isolated=True`. The model retains
            everything the user said in the previous context, so you do not need to
            re-state it.

        Args:
            context_name: Name of the context to switch to. Must exist in the agent's
                context map.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = (
                FunctionResult("Transferring you to technical support.")
                .update_global_data({"original_issue": "no dial tone"})
                .swml_change_context("technical_support")
            )
            ```
        """
        return self.add_action("change_context", context_name)

    def execute_swml(
        self, swml_content: "str | dict[str, Any] | Any", transfer: bool = False
    ) -> "FunctionResult":
        """Execute SWML content with optional transfer behavior.

        This is the escape hatch for advanced use cases not covered by the named
        convenience methods. Most use cases are covered by the specific action methods
        (`connect()`, `record_call()`, `send_sms()`, and so on); use `execute_swml()`
        when you need SWML features they don't offer.

        A string is parsed as JSON; if it isn't valid JSON it is sent as
        `{"raw_swml": <the string>}`. A dict is copied. An object with a `to_dict()`
        method is converted with it. The action is `{"SWML": <document>}`, plus a
        sibling `"transfer": "true"` when `transfer` is True.

        Args:
            swml_content: The SWML, in one of three forms:

                - String: raw SWML JSON text (parsed internally)
                - Dict: SWML data structure
                - SWML object: any object with a `to_dict()` method, such as the
                  SignalWire SWML SDK object

            transfer: Whether the call should exit the agent after the SWML runs. When
                False (default), the SWML runs inline and the agent continues.

        Returns:
            This `FunctionResult`, for chaining.

        Raises:
            TypeError: If `swml_content` is not a string, a dict, or an object with a
                `to_dict()` method.

        Example:
            ```python
            result = FunctionResult("Sending that now.").execute_swml({
                "version": "1.0.0",
                "sections": {"main": [{"play": {"url": "say:Goodbye"}}]},
            })
            ```
        """
        # Detect input type and normalize to appropriate format
        if isinstance(swml_content, str):
            # Raw SWML string - parse to dict so the action carries a document
            try:
                import json

                swml_data: dict[str, Any] = json.loads(swml_content)
            except (json.JSONDecodeError, ValueError):
                swml_data = {"raw_swml": swml_content}
        elif hasattr(swml_content, "to_dict"):
            # SWML SDK object - convert to dict
            swml_data = swml_content.to_dict()
        elif isinstance(swml_content, dict):
            # Dict - make a copy to avoid mutating caller's data
            swml_data = dict(swml_content)
        else:
            raise TypeError("swml_content must be string, dict, or SWML object")

        # transfer rides BESIDE the SWML document, not inside it — the same
        # shape connect() and swml_transfer() emit. Inside the document it is
        # not a SWML key and the call never exits the agent.
        action: dict[str, Any] = {"SWML": swml_data}
        if transfer:
            action["transfer"] = "true"

        self.action.append(action)
        return self

    def hangup(self) -> "FunctionResult":
        """Terminate the call.

        Warning:
            This is a terminal action: the call ends once the platform runs it.
            Always place `hangup()` last in the chain.

        Returns:
            This `FunctionResult`, for chaining.
        """
        return self.add_action("hangup", True)

    def hold(
        self,
        prompt: str | int | None = None,
        timeout: int = 300,
        step: str | None = None,
        timeout_step: str | None = None,
    ) -> "FunctionResult":
        """Put the call on hold, optionally announcing it and routing what happens next.

        The caller hears hold music until the hold is released or the timeout
        expires. The SWML hold action carries no prompt of its own. And during hold,
        speech detection is paused and the agent will not respond, so anything the
        caller needs to hear has to be said BEFORE the action lands.

        Passing `prompt` wires that up for you. It becomes the result's response (a
        prompt into the model's context, not speech) as
        `{"tool_result": "status: on hold", "tool_prompt": prompt}` and switches on
        post_process, so the model takes one more turn and speaks before the hold
        executes:

        ```python
        FunctionResult().hold("Tell the caller you are placing them on hold.", 120)
        ```

        `step` and `timeout_step` land the caller in a chosen step when the hold
        ends, which is how you scope what they can do on the way back. A held call
        otherwise resumes in the step it left, still holding whatever tool put it
        on hold. Note this is deferred: the transition fires when the hold actually
        ends, unlike `swml_change_step()` which applies immediately. Returning both
        a hold and a change_step in one result moves the caller before the hold
        even begins.

        ```python
        FunctionResult().hold(
            "Tell the caller you are checking if they are available.",
            300,
            step="back_with_agent",         # they were released early
            timeout_step="take_a_message",  # nobody picked up
        )
        ```

        Either may be omitted, and they may name the same step. Omitting both emits
        the bare integer form (the action is the timeout number alone) and the caller
        resumes where they were.

        Args:
            prompt: Instruction for the model to deliver before the hold takes effect,
                in the second person. Sets `response` and `post_process=True`. Passing
                an int here is treated as `timeout`, so `hold(120)` keeps working.
            timeout: Maximum hold duration in seconds. Clamped to the range 0 to 900;
                default 300.
            step: Step to move to when the call is taken off hold. Without it the
                caller resumes in the step they left.
            timeout_step: Step to move to when the hold times out. Defaults to the
                platform's behaviour (resume in place) when omitted.

        Returns:
            This `FunctionResult`, for chaining.
        """
        # Back-compat: hold(120) used to mean hold(timeout=120). `bool` subclasses
        # `int`, so it is excluded explicitly — a bool is neither a prompt nor a
        # timeout, and dropping it here keeps the remaining type `str | None`.
        if isinstance(prompt, bool):
            prompt = None
        elif isinstance(prompt, int):
            timeout, prompt = prompt, None

        if prompt is not None:
            self.set_tool_response(tool_result="status: on hold", tool_prompt=prompt)
            self.post_process = True

        # Clamp timeout to valid range
        timeout = max(0, min(timeout, 900))

        # Bare integer unless routing is requested, so existing output is unchanged
        if step is None and timeout_step is None:
            return self.add_action("hold", timeout)

        hold_config: dict[str, Any] = {"timeout": timeout}
        if step is not None:
            hold_config["step"] = step
        if timeout_step is not None:
            hold_config["timeout_step"] = timeout_step
        return self.add_action("hold", hold_config)

    def wait_for_user(
        self,
        enabled: bool | None = None,
        timeout: int | None = None,
        answer_first: bool = False,
    ) -> "FunctionResult":
        """Control how the agent waits for user input.

        Adds a `wait_for_user` action. The arguments are evaluated in priority
        order: `answer_first` takes precedence, then `timeout`, then `enabled`. If
        none are provided, the action value is `True`.

        Args:
            enabled: Sent as the action value when neither `answer_first` nor
                `timeout` is given. `True` makes the agent wait for the caller to
                speak. `False` is sent as `false`, which the platform ignores: it
                does not turn off a wait that is already set.
            timeout: Sent as the action value. Despite the name, the platform reads
                a number as a count of caller turns, not as a duration in seconds.
            answer_first: When True, sends the string `"answer_first"`. Takes
                precedence over the other arguments.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult("Take your time.").wait_for_user(enabled=True)
            ```
        """
        wait_value: str | int | bool
        if answer_first:
            wait_value = "answer_first"
        elif timeout is not None:
            wait_value = timeout
        elif enabled is not None:
            wait_value = enabled
        else:
            wait_value = True

        return self.add_action("wait_for_user", wait_value)

    def stop(self) -> "FunctionResult":
        """Stop the agent execution.

        This halts the AI from processing further and can be used to interrupt the
        current speech flow.

        Returns:
            This `FunctionResult`, for chaining.
        """
        return self.add_action("stop", True)

    def say(self, text: str) -> "FunctionResult":
        """Make the agent speak specific text.

        The text is spoken in the agent's configured voice, bypassing the normal LLM
        response flow.

        Args:
            text: Text for the agent to speak.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult().say("Thanks for waiting.")
            ```
        """
        return self.add_action("say", text)

    def play_background_file(
        self, filename: str, wait: bool = False
    ) -> "FunctionResult":
        """Play an audio or video file in the background.

        The conversation continues while the file plays. With `wait=False` the action
        is the filename alone; with `wait=True` it is `{"file": filename, "wait":
        True}`.

        Args:
            filename: URL or path of the audio/video file to play (for example
                `"https://example.com/hold-music.mp3"`).
            wait: When True, suppresses the agent's attention-getting behavior during
                playback, so the agent does not try to re-engage the user while the
                file plays. Defaults to False.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult("One moment.").play_background_file(
                "https://example.com/hold-music.mp3", wait=True
            )
            ```
        """
        if wait:
            return self.add_action("playback_bg", {"file": filename, "wait": True})
        return self.add_action("playback_bg", filename)

    def stop_background_file(self) -> "FunctionResult":
        """Stop the currently playing background file.

        Returns:
            This `FunctionResult`, for chaining.
        """
        return self.add_action("stop_playback_bg", True)

    def add_dynamic_hints(self, hints: list[str | dict[str, Any]]) -> "FunctionResult":
        """Add dynamic speech recognition hints during a call.

        Hints improve speech recognition accuracy for domain-specific vocabulary,
        product names, or uncommon words. Each hint can be a simple string or a
        pronunciation pattern object that maps misrecognized speech to the correct
        text.

        Note:
            When the agent runs in multilingual mode (`set_multilingual()`), string
            hints are not passed to speech recognition. Pattern objects still rewrite
            the transcript.

        Args:
            hints: List of hints, where each entry is either:

                - A string: a word or phrase to boost recognition (for example
                  `"SignalWire"`)
                - A dict with a pronunciation pattern:

                  - `"pattern"`: Regex pattern to match in recognized speech
                  - `"replace"`: Replacement text when the pattern matches
                  - `"ignore_case"`: Optional bool for case-insensitive matching

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = (
                FunctionResult("I'll listen for that name")
                .add_dynamic_hints([
                    "Cabby",
                    {"pattern": "cab bee", "replace": "Cabby", "ignore_case": True}
                ])
            )
            ```
        """
        return self.add_action("add_dynamic_hints", hints)

    def clear_dynamic_hints(self) -> "FunctionResult":
        """Clear all dynamic speech recognition hints.

        Removes every hint previously added via `add_dynamic_hints()`. Static hints
        defined on the agent at configuration time are not affected.

        Returns:
            This `FunctionResult`, for chaining.
        """
        self.action.append({"clear_dynamic_hints": {}})
        return self

    def set_end_of_speech_timeout(self, milliseconds: int) -> "FunctionResult":
        """Adjust the end-of-speech timeout.

        This is the milliseconds of silence after speech has been detected that
        finalize speech recognition. A shorter value makes the agent respond faster; a
        longer value gives the caller more time to pause mid-sentence.

        Args:
            milliseconds: Timeout in milliseconds.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult("Take your time.").set_end_of_speech_timeout(1200)
            ```
        """
        return self.add_action("end_of_speech_timeout", milliseconds)

    def set_speech_event_timeout(self, milliseconds: int) -> "FunctionResult":
        """Adjust the speech event timeout.

        This is the milliseconds since the last speech detection event to wait before
        finalizing recognition. It works better than `set_end_of_speech_timeout()` in
        noisy environments.

        Args:
            milliseconds: Timeout in milliseconds.

        Returns:
            This `FunctionResult`, for chaining.
        """
        return self.add_action("speech_event_timeout", milliseconds)

    def remove_global_data(self, keys: str | list[str]) -> "FunctionResult":
        """Remove global agent data variables.

        Args:
            keys: A single key string, or a list of key strings, to remove from global
                data.

        Returns:
            This `FunctionResult`, for chaining.
        """
        return self.add_action("unset_global_data", keys)

    def set_semantic_state(self, state: dict[str, Any]) -> "FunctionResult":
        """
        Set the semantic state the call's semantic gates judge, besides the
        dialogue.

        The state is ``global_data.semantic_state``, and this replaces it as a
        whole: to change one field, send the whole state with that field
        changed, and send ``{}`` to reset it. Keep it to what the application
        has established, such as an order the caller confirmed, rather than
        what the caller claims; nothing else from the global data reaches the
        decision model.

        A change starts a proposal, the dialogue of a gate with
        ``dialogue="proposal"``, as of the start of the result's action list,
        so a ``say`` anywhere in the same result, such as the read-back, is in
        it. Set the state before the ``say`` all the same: when the caller
        talks over a ``say``, the platform skips the rest of the result's
        actions, so a state set after it could be lost. Platform releases
        before the whole-list rule also date a proposal from its own action
        object, which the same order covers. ``signalwire.patterns.Proposal``
        does this.

        Args:
            state: The semantic state

        Returns:
            self for method chaining
        """
        return self.update_global_data({"semantic_state": state})

    def set_metadata(self, data: dict[str, Any]) -> "FunctionResult":
        """Set metadata scoped to the current function's `meta_data_token`.

        Each function maintains its own independent metadata store.

        Args:
            data: Dictionary of key-value pairs to store as metadata.

        Returns:
            This `FunctionResult`, for chaining.
        """
        return self.add_action("set_meta_data", data)

    def remove_metadata(self, keys: str | list[str]) -> "FunctionResult":
        """Remove metadata from the current function's `meta_data_token` scope.

        Args:
            keys: A single key string, or a list of key strings, to remove from
                metadata.

        Returns:
            This `FunctionResult`, for chaining.
        """
        return self.add_action("unset_meta_data", keys)

    def change_voice(self, voice: str) -> "FunctionResult":
        """
        Change the AI's voice for the rest of the call.

        The new voice replaces the current language's voice, from the next
        batch of speech on, never mid-utterance, and stays for that language
        for the rest of the call. It may be on another engine than the
        current one. A voice that won't open falls back to the fallback
        voice.

        Args:
            voice: The voice as ``engine.voice:model``, the form a language's
                voice takes, such as ``"elevenlabs.rachel"``

        Returns:
            self for method chaining

        Raises:
            ValueError: If voice is empty
        """
        if not isinstance(voice, str) or not voice.strip():
            raise ValueError("voice must be a non-empty string")
        return self.add_action("change_voice", voice)

    def toggle_functions(
        self, function_toggles: list[dict[str, Any]]
    ) -> "FunctionResult":
        """Enable or disable specific SWAIG functions at runtime.

        This lets you control which tools are available to the AI at different points
        in the conversation, for example enabling payment functions only after
        identity verification.

        Args:
            function_toggles: List of toggle objects. Each must contain `"function"`
                (name of the SWAIG function to toggle) and `"active"` (True to enable,
                False to disable).

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult("Verified.").toggle_functions([
                {"function": "take_payment", "active": True},
                {"function": "verify_identity", "active": False},
            ])
            ```
        """
        return self.add_action("toggle_functions", function_toggles)

    def enable_functions_on_timeout(self, enabled: bool = True) -> "FunctionResult":
        """Enable function calls on speaker timeout.

        When enabled, the agent can invoke functions after the user has been silent
        for the configured timeout period.

        Args:
            enabled: True (default) to allow function calls on speaker timeout, False
                to disable.

        Returns:
            This `FunctionResult`, for chaining.
        """
        return self.add_action("functions_on_speaker_timeout", enabled)

    def set_semantic_gate_mark(self, name: str) -> "FunctionResult":
        """
        Set a mark that semantic gates judge the dialogue from.

        A gate with ``since=name`` judges the dialogue from the agent's
        first turn at or after the mark, at most its ``history`` entries.
        The mark is set as of the start of the result's action list, so a
        ``say`` anywhere in the same result is after it; setting it again
        moves it. Marks last for the call. Platform releases before the
        whole-list rule set it as of the start of its own action object:
        set it before ``say`` there.

        Args:
            name: 1 to 64 letters, digits or underscores.

        Returns:
            self for method chaining

        Raises:
            ValueError: For a name the platform would refuse.
        """
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_]{1,64}", name):
            raise ValueError(
                f"a mark name is 1 to 64 letters, digits or underscores, got {name!r}"
            )
        return self.add_action("semantic_gate_mark", name)

    def no_barge_next_response(self) -> "FunctionResult":
        """
        Have the next spoken reply play whole, such as a read-back the caller
        should hear in full before answering.

        From the start of the next request until a reply that speaks has
        played, the caller's words neither cut the reply nor cancel its
        request: they're held and delivered after it. For semantic gates, an
        answer begun during the reply reads as cutting it at that point, as
        a barge would.

        Returns:
            self for method chaining
        """
        return self.add_action("no_barge_next_response", True)

    def back_to_back_functions(self, value: bool | str = True) -> "FunctionResult":
        """
        Set whether the model may call another function right after a
        function result, without answering in words first.

        "forever", the call's default, chains freely. False makes the model
        answer in words after a function result: the request after one goes
        out with ``tool_choice: "none"``. True, while chaining is off, allows
        one more chain: the next request after a function result may call
        one, and then it's off again. True never lowers "forever". The
        setting lasts for the call, one set by a gate's ``on_fail`` too:
        after a refused gate turns it off, a later result sets "forever" to
        turn it back on, or every later tool result needs words after it.
        Text pipeline only: a realtime model doesn't read it.

        Args:
            value: True, False or "forever".

        Returns:
            self for method chaining

        Raises:
            ValueError: For any other value, which the platform ignores.
        """
        if not isinstance(value, bool) and value != "forever":
            raise ValueError(
                f'back_to_back_functions takes True, False or "forever", got {value!r}'
            )
        return self.add_action("back_to_back_functions", value)

    def enable_extensive_data(self, enabled: bool = True) -> "FunctionResult":
        """Send full data to the LLM for this turn only.

        On subsequent turns the full data is replaced with a smaller replacement.
        Useful for one-time data-heavy responses that would otherwise bloat the
        conversation history.

        Args:
            enabled: True (default) to send extensive data this turn only, False to
                disable.

        Returns:
            This `FunctionResult`, for chaining.
        """
        return self.add_action("extensive_data", enabled)

    def replace_in_history(self, text: str | bool = True) -> "FunctionResult":
        """After the first send, replace the tool_call and result pair in the history.

        Use this to remove sensitive information (credit card numbers, SSNs) or
        replace verbose tool results with concise summaries.

        Args:
            text: A string replaces the tool_call and result pair with an assistant
                message containing this text. True (default) removes the pair from
                history entirely.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            # Remove the exchange entirely
            result = FunctionResult("Card verified.").replace_in_history(True)

            # Replace it with a short summary
            result = FunctionResult("Found 40 orders.").replace_in_history(
                "The caller's order history was retrieved."
            )
            ```
        """
        return self.add_action("replace_in_history", text)

    def update_settings(self, settings: dict[str, Any]) -> "FunctionResult":
        """Update agent runtime settings.

        Changes take effect for subsequent LLM turns. Supported settings:

        - `frequency-penalty`: Float (-2.0 to 2.0)
        - `presence-penalty`: Float (-2.0 to 2.0)
        - `max-tokens`: Integer (0 to 4096)
        - `top-p`: Float (0.0 to 1.0)
        - `confidence`: Float (0.0 to 1.0)
        - `barge-confidence`: Float (0.0 to 1.0)
        - `temperature`: Float (0.0 to 2.0, clamped to 1.5)

        Each key named replaces its current value; every other setting keeps
        its value, the prompt's own included. A key the model doesn't take is
        ignored. A key can't be removed: to undo one, set it to the value you
        want, such as the model's default. Platform releases before the merge
        reset every key not named to the model's default.

        Args:
            settings: Dictionary of settings to update, keyed as listed above.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult("Okay.").update_settings({"temperature": 0.3})
            ```
        """
        return self.add_action("settings", settings)

    def switch_context(
        self,
        system_prompt: str | None = None,
        user_prompt: str | None = None,
        consolidate: bool = False,
        full_reset: bool = False,
    ) -> "FunctionResult":
        """Change the agent's context/prompt during the conversation.

        This is more flexible than `swml_change_context()`, which switches to a
        pre-defined named context. When only `system_prompt` is provided (no other
        arguments), the action is the prompt string, a simple context switch. When
        other arguments are given, the action is an object with fine-grained control.

        Args:
            system_prompt: The new prompt. The conversation so far is set aside
                and the model continues from the agent's base prompt plus this one,
                added as a system message.
            user_prompt: A user message to inject into the conversation after the
                context switch.
            consolidate: When True, the conversation is summarized first, and the
                summary carries into the new context.
            full_reset: When True, `system_prompt` replaces the agent's base prompt
                instead of being added after it.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            # Simple prompt swap
            result = FunctionResult("Switching.").switch_context(
                system_prompt="You are now a billing specialist."
            )

            # Full reset with a user message
            result = FunctionResult("Starting over.").switch_context(
                system_prompt="You are a returns specialist.",
                user_prompt="I'd like to return an item.",
                full_reset=True,
            )
            ```
        """
        if system_prompt and not user_prompt and not consolidate and not full_reset:
            # Simple string context switch
            return self.add_action("context_switch", system_prompt)
        # Advanced object context switch
        context_data: dict[str, Any] = {}
        if system_prompt:
            context_data["system_prompt"] = system_prompt
        if user_prompt:
            context_data["user_prompt"] = user_prompt
        if consolidate:
            context_data["consolidate"] = True
        if full_reset:
            context_data["full_reset"] = True
        return self.add_action("context_switch", context_data)

    def simulate_user_input(self, text: str) -> "FunctionResult":
        """Queue simulated user input.

        The AI agent processes the injected text as it would process real speech
        input. Useful for driving automated workflows or confirmations.

        Args:
            text: Text to simulate as user input.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult("Confirming.").simulate_user_input("Yes, please.")
            ```
        """
        return self.add_action("user_input", text)

    def send_sms(
        self,
        to_number: str,
        from_number: str,
        body: str | None = None,
        media: list[str] | None = None,
        tags: list[str] | None = None,
        region: str | None = None,
    ) -> "FunctionResult":
        """Send a text message to a PSTN phone number using SWML.

        This is a virtual helper that generates a SWML `send_sms` verb. At least one
        of `body` or `media` must be provided.

        Args:
            to_number: Destination phone number in E.164 format (for example
                `"+15551234567"`).
            from_number: Sender phone number in E.164 format.
            body: Text body of the message (optional if `media` is provided).
            media: List of media URLs to include as MMS attachments (optional if
                `body` is provided).
            tags: List of tags to associate with the message.
            region: Region to originate the message from.

        Returns:
            This `FunctionResult`, for chaining.

        Raises:
            ValueError: If neither body nor media is provided.

        Example:
            ```python
            # Text message
            result = FunctionResult("I sent you a text.").send_sms(
                to_number="+15551234567",
                from_number="+15559876543",
                body="Your order has shipped.",
            )

            # MMS with media
            result = FunctionResult("I sent the photo.").send_sms(
                to_number="+15551234567",
                from_number="+15559876543",
                media=["https://example.com/photo.jpg"],
            )
            ```
        """
        # Validate that at least body or media is provided
        if not body and not media:
            raise ValueError("Either body or media must be provided")

        # Build the send_sms parameters
        sms_params: dict[str, Any] = {
            "to_number": to_number,
            "from_number": from_number,
        }

        # Add optional parameters
        if body:
            sms_params["body"] = body
        if media:
            sms_params["media"] = media
        if tags:
            sms_params["tags"] = tags
        if region:
            sms_params["region"] = region

        # Generate SWML document
        swml_doc = {
            "version": "1.0.0",
            "sections": {"main": [{"send_sms": sms_params}]},
        }

        # Use execute_swml to add the action
        return self.execute_swml(swml_doc)

    def pay(
        self,
        payment_connector_url: str,
        input_method: str = "dtmf",
        status_url: str | None = None,
        payment_method: str = "credit-card",
        timeout: int = 5,
        max_attempts: int = 1,
        security_code: bool = True,
        postal_code: bool | str = True,
        min_postal_code_length: int = 0,
        token_type: str = "reusable",  # noqa: S107  # false positive: SWML pay-verb field name, the value "reusable" is a mode, not a secret
        charge_amount: str | None = None,
        currency: str = "usd",
        language: str = "en-US",
        voice: str = "woman",
        description: str | None = None,
        valid_card_types: str = "visa mastercard amex",
        parameters: list[dict[str, str]] | None = None,
        prompts: list[dict[str, Any]] | None = None,
        ai_response: str
        | None = "The payment status is ${pay_result}, do not mention anything else about collecting payment if successful.",
    ) -> "FunctionResult":
        """Collect and process a payment using the SWML `pay` verb.

        This is a virtual helper that generates SWML for payment processing. The
        `pay` verb walks the caller through entering card details by DTMF, then
        submits to your payment connector endpoint. The SWML also sets `ai_response`
        after the `pay` verb.

        Args:
            payment_connector_url: URL of your payment processing endpoint
                (required). SignalWire sends the collected card data to this URL.
            input_method: How the caller provides card details. The SWML pay verb
                only accepts "dtmf" (schema `input` is `const: "dtmf"`): the caller
                enters digits on the keypad. The earlier "voice" option was never
                valid.
            status_url: URL to receive payment status change notifications.
            payment_method: Payment method ("credit-card" is currently supported).
            timeout: Seconds to wait for the next digit (default: 5).
            max_attempts: Number of retry attempts (default: 1).
            security_code: Whether to prompt for the security code (default: True).
            postal_code: Whether to prompt for the postal code (True or False), or a
                string with the actual postal code to use without prompting.
            min_postal_code_length: Minimum postal code digits (default: 0).
            token_type: Payment token type, "one-time" (single use) or "reusable"
                (can be charged again later). Default: "reusable".
            charge_amount: Amount to charge as a decimal string (for example
                `"49.99"`).
            currency: Currency code (default: "usd").
            language: Language for prompts (default: "en-US").
            voice: TTS voice to use (default: "woman").
            description: Custom payment description.
            valid_card_types: Space-separated accepted card types (default: "visa
                mastercard amex").
            parameters: List of name/value pairs to send to the payment connector.
                Build entries with `create_payment_parameter()`.
            prompts: List of custom prompt configurations that override the default
                payment prompts. Build entries with `create_payment_prompt()`.
            ai_response: Value for the `ai_response` variable the SWML sets after the
                `pay` verb. The `${pay_result}` variable is replaced with the payment
                outcome. The default tells the AI the payment status and not to
                mention collecting payment further if it succeeded. The `set` is
                always emitted, so `None` sends a null value rather than omitting it.

        `timeout`, `max_attempts` and `min_postal_code_length` must be integers,
        and `security_code` a boolean; each also accepts a SWML variable
        reference such as `${timeout}`. They're sent as strings, as is a
        boolean `postal_code`: the platform's pay verb requires `security_code`
        and `postal_code` to be strings, and reads all five as strings.

        Returns:
            This `FunctionResult`, for chaining.

        Raises:
            ValueError: If timeout, max_attempts or min_postal_code_length isn't an
                integer, or security_code isn't a boolean.

        Example:
            ```python
            result = FunctionResult("Tell the caller you will take payment now.").pay(
                payment_connector_url="https://example.com/pay",
                charge_amount="49.99",
                parameters=[FunctionResult.create_payment_parameter("order", "1234")],
                prompts=[
                    FunctionResult.create_payment_prompt(
                        "payment-card-number",
                        [FunctionResult.create_payment_action("Say", "Enter card.")],
                    )
                ],
            )
            ```
        """
        # Build the pay parameters. The platform reads timeout, max_attempts,
        # min_postal_code_length, security_code and postal_code as strings, and
        # its SWML validation refuses a security_code or postal_code that isn't
        # one, so each is checked, then sent as a string.
        pay_params: dict[str, Any] = {
            "payment_connector_url": payment_connector_url,
            "input": input_method,
            "payment_method": payment_method,
            "timeout": _swml_text(_swml_int("timeout", timeout)),
            "max_attempts": _swml_text(_swml_int("max_attempts", max_attempts)),
            "security_code": _swml_text(_swml_bool("security_code", security_code)),
            "min_postal_code_length": _swml_text(
                _swml_int("min_postal_code_length", min_postal_code_length)
            ),
            "token_type": token_type,
            "currency": currency,
            "language": language,
            "voice": voice,
            "valid_card_types": valid_card_types,
        }

        # postal_code is a boolean (whether to ask for it) or the postal code
        # itself; either way it's sent as a string
        pay_params["postal_code"] = (
            _swml_text(postal_code) if isinstance(postal_code, bool) else postal_code
        )

        # Add optional parameters
        if status_url:
            pay_params["status_url"] = status_url
        if charge_amount:
            pay_params["charge_amount"] = charge_amount
        if description:
            pay_params["description"] = description
        if parameters:
            pay_params["parameters"] = parameters
        if prompts:
            pay_params["prompts"] = prompts

        # Generate SWML document
        swml_doc = {
            "version": "1.0.0",
            "sections": {
                "main": [{"pay": pay_params}, {"set": {"ai_response": ai_response}}]
            },
        }

        # Use execute_swml to add the action
        return self.execute_swml(swml_doc)

    def record_call(
        self,
        control_id: str | None = None,
        stereo: bool = False,
        format: Literal["wav", "mp3", "mp4"] = "wav",
        direction: Literal["speak", "listen", "both"] = "both",
        terminators: str | None = None,
        beep: bool = False,
        input_sensitivity: float = 44.0,
        initial_timeout: float | None = None,
        end_silence_timeout: float | None = None,
        max_length: float | None = None,
        status_url: str | None = None,
    ) -> "FunctionResult":
        """Start background call recording using SWML.

        This is a virtual helper that generates SWML to start recording the call in
        the background. Unlike foreground recording, the script continues executing
        while recording happens in the background.

        Note:
            For continuous call recording, omit `initial_timeout` and
            `end_silence_timeout`. Those are for voicemail-style recordings that stop
            on silence. Use `stop_record_call()` to end continuous recordings.

        Args:
            control_id: Identifier for this recording. Pass the same ID to
                `stop_record_call()` to stop this specific recording.
            stereo: Record in stereo (True) or mono (False, default).
            format: Recording file format: "wav" (default), "mp3" or "mp4".
            direction: Audio direction to record: "speak" (what the agent says),
                "listen" (what the caller says) or "both" (default).
            terminators: DTMF digits that stop recording when pressed (for example
                `"#"`).
            beep: Play a beep before recording (default: False).
            input_sensitivity: Input sensitivity for recording (default: 44.0).
            initial_timeout: Seconds to wait for speech to begin before stopping
                (for voicemail-style recording).
            end_silence_timeout: Seconds of silence after speech to wait before
                stopping (for voicemail-style recording).
            max_length: Maximum recording length in seconds.
            status_url: URL to send recording status events to.

        Returns:
            This `FunctionResult`, for chaining.

        Raises:
            ValueError: If format is not "wav", "mp3" or "mp4", or direction is not
                "speak", "listen" or "both".

        Example:
            ```python
            # Continuous recording of both sides
            result = FunctionResult("Recording started.").record_call(
                control_id="main", format="mp3"
            )

            # Voicemail-style recording
            result = FunctionResult("Leave a message.").record_call(
                control_id="vm", initial_timeout=5, end_silence_timeout=3, beep=True
            )
            ```
        """
        # Validate format parameter (matches the SWML record_call verb schema,
        # $defs/RecordCall.format = {wav, mp3, mp4})
        if format not in ["wav", "mp3", "mp4"]:
            raise ValueError("format must be 'wav', 'mp3', or 'mp4'")

        # Validate direction parameter
        if direction not in ["speak", "listen", "both"]:
            raise ValueError("direction must be 'speak', 'listen', or 'both'")

        # Build the record_call parameters
        record_params: dict[str, Any] = {
            "stereo": stereo,
            "format": format,
            "direction": direction,
            "beep": beep,
            "input_sensitivity": input_sensitivity,
        }

        # Add optional parameters
        if control_id:
            record_params["control_id"] = control_id
        if terminators:
            record_params["terminators"] = terminators
        if initial_timeout is not None:
            record_params["initial_timeout"] = initial_timeout
        if end_silence_timeout is not None:
            record_params["end_silence_timeout"] = end_silence_timeout
        if max_length is not None:
            record_params["max_length"] = max_length
        if status_url:
            record_params["status_url"] = status_url

        # Generate SWML document
        swml_doc = {
            "version": "1.0.0",
            "sections": {"main": [{"record_call": record_params}]},
        }

        # Use execute_swml to add the action
        return self.execute_swml(swml_doc)

    def stop_record_call(self, control_id: str | None = None) -> "FunctionResult":
        """Stop an active background call recording using SWML.

        This is a virtual helper that generates SWML to stop a recording that was
        started with `record_call()`.

        Args:
            control_id: Identifier of the recording to stop. If not provided, the most
                recent recording is stopped.

        Returns:
            This `FunctionResult`, for chaining.
        """
        # Build the stop_record_call parameters
        stop_params = {}
        if control_id:
            stop_params["control_id"] = control_id

        # Generate SWML document
        swml_doc = {
            "version": "1.0.0",
            "sections": {"main": [{"stop_record_call": stop_params}]},
        }

        # Use execute_swml to add the action
        return self.execute_swml(swml_doc)

    def join_room(self, name: str) -> "FunctionResult":
        """Join a RELAY room using SWML.

        This is a virtual helper that generates SWML to join a RELAY room, which
        enables multi-party communication and collaboration.

        Args:
            name: The name of the room to join (required).

        Returns:
            This `FunctionResult`, for chaining.
        """
        # Build the join_room parameters
        join_params = {"name": name}

        # Generate SWML document
        swml_doc = {
            "version": "1.0.0",
            "sections": {"main": [{"join_room": join_params}]},
        }

        # Use execute_swml to add the action
        return self.execute_swml(swml_doc)

    def sip_refer(self, to_uri: str) -> "FunctionResult":
        """Send SIP REFER to a SIP call using SWML.

        This is a virtual helper that generates SWML to send a SIP REFER message,
        which is used for call transfer in SIP environments (attended or blind
        transfers within SIP-based phone systems and PBX deployments).

        Note:
            For standard phone-number or SIP-address transfers, use `connect()`
            instead. Use `sip_refer()` when the transfer must be performed via the SIP
            REFER mechanism, for example to a PBX extension.

        Args:
            to_uri: The SIP URI to send the REFER to (required), for example
                `"sip:1001@pbx.example.com"`.

        Returns:
            This `FunctionResult`, for chaining.
        """
        # Build the sip_refer parameters
        refer_params = {"to_uri": to_uri}

        # Generate SWML document
        swml_doc = {
            "version": "1.0.0",
            "sections": {"main": [{"sip_refer": refer_params}]},
        }

        # Use execute_swml to add the action
        return self.execute_swml(swml_doc)

    def join_conference(
        self,
        name: str,
        muted: bool = False,
        beep: str = "true",
        start_on_enter: bool = True,
        end_on_exit: bool = False,
        wait_url: str | None = None,
        max_participants: int | None = None,
        record: str = "do-not-record",
        region: str | None = None,
        trim: str = "trim-silence",
        coach: str | None = None,
        status_callback_event: str | None = None,
        status_callback: str | None = None,
        status_callback_method: str = "POST",
        recording_status_callback: str | None = None,
        recording_status_callback_method: str = "POST",
        recording_status_callback_event: str = "completed",
        result: Any | None = None,
    ) -> "FunctionResult":
        """Join an ad-hoc audio conference with RELAY and CXML calls using SWML.

        This is a virtual helper that generates SWML to join audio conferences with
        extensive configuration options for moderation, call management, recording and
        event callbacks. When every parameter except `name` is at its default, the
        `join_conference` verb is just the conference name; passing any non-default
        parameter sends the full object form, containing only the non-default values.

        Args:
            name: Name of the conference (required, not empty). All participants
                joining the same name are in the same conference.
            muted: Whether to join muted (default: False).
            beep: Beep configuration, one of "true" (beep on enter and exit), "false",
                "onEnter" or "onExit" (default: "true").
            start_on_enter: Whether the conference starts when this participant enters
                (default: True). When False, the participant waits until another
                participant with start_on_enter set joins.
            end_on_exit: Whether the conference ends for all participants when this
                participant exits (default: False).
            wait_url: SWML URL for hold music played while waiting for the conference
                to start (default: None for the default hold music).
            max_participants: Maximum participants, an integer of 2 or more, or a SWML
                variable reference (default: None, which leaves it out so the
                platform's default applies).
            record: Recording mode, "do-not-record" (default) or "record-from-start".
            region: Conference region (default: None).
            trim: Silence trimming in recordings, "trim-silence" (default) or
                "do-not-trim".
            coach: SWML Call ID or CXML CallSid of a participant who can coach (whisper
                to) this participant without the others hearing (default: None).
            status_callback_event: Space-separated events to report: "start", "end",
                "join", "leave", "mute", "hold", "modify", "speaker", "announcement"
                (default: None).
            status_callback: URL for conference status callbacks (default: None).
            status_callback_method: HTTP method for status callbacks, "GET" or "POST"
                (default: "POST").
            recording_status_callback: URL for recording status callbacks (default:
                None).
            recording_status_callback_method: HTTP method for recording status
                callbacks, "GET" or "POST" (default: "POST").
            recording_status_callback_event: Space-separated recording events to
                report: "in-progress", "completed", "absent" (default: "completed").
            result: Result handling: an object `{}` switches on `return_value`, an
                array `[]` switches on conditions (default: None).

        Returns:
            This `FunctionResult`, for chaining.

        Raises:
            ValueError: If beep, record, trim, status_callback_method or
                recording_status_callback_method isn't one of its allowed values, if
                max_participants isn't an integer of at least 2, or if name is empty.

        Example:
            ```python
            # Simple conference
            result = FunctionResult("Joining.").join_conference("team-sync")

            # Moderated, recorded conference
            result = FunctionResult("Joining the conference.").join_conference(
                "board-call",
                beep="onEnter",
                record="record-from-start",
                max_participants=10,
                status_callback="https://example.com/events",
                status_callback_event="start end join leave",
            )
            ```
        """
        # Validate beep parameter
        valid_beep_values = ["true", "false", "onEnter", "onExit"]
        if beep not in valid_beep_values:
            raise ValueError(f"beep must be one of {valid_beep_values}")

        # The platform requires a positive number, and its conference refuses
        # fewer than 2; it sets no upper limit
        if max_participants is not None:
            max_participants = _swml_int(
                "max_participants", max_participants, minimum=2
            )

        # Validate record parameter
        valid_record_values = ["do-not-record", "record-from-start"]
        if record not in valid_record_values:
            raise ValueError(f"record must be one of {valid_record_values}")

        # Validate trim parameter
        valid_trim_values = ["trim-silence", "do-not-trim"]
        if trim not in valid_trim_values:
            raise ValueError(f"trim must be one of {valid_trim_values}")

        # Validate status_callback_method
        valid_methods = ["GET", "POST"]
        if status_callback_method not in valid_methods:
            raise ValueError(f"status_callback_method must be one of {valid_methods}")
        if recording_status_callback_method not in valid_methods:
            raise ValueError(
                f"recording_status_callback_method must be one of {valid_methods}"
            )

        # Build the join_conference parameters - start with required parameter
        if isinstance(name, str) and not name.strip():
            raise ValueError("name cannot be empty")

        # For simple case, can just be the conference name
        if (
            not muted
            and beep == "true"
            and start_on_enter
            and not end_on_exit
            and wait_url is None
            and max_participants is None
            and record == "do-not-record"
            and region is None
            and trim == "trim-silence"
            and coach is None
            and status_callback_event is None
            and status_callback is None
            and status_callback_method == "POST"
            and recording_status_callback is None
            and recording_status_callback_method == "POST"
            and recording_status_callback_event == "completed"
            and result is None
        ):
            # Simple form - just the conference name
            join_params: str | dict[str, Any] = name
        else:
            # Full object form with parameters
            join_params = {"name": name}

            # Add non-default parameters
            if muted:
                join_params["muted"] = muted
            if beep != "true":
                join_params["beep"] = beep
            if not start_on_enter:
                join_params["start_on_enter"] = start_on_enter
            if end_on_exit:
                join_params["end_on_exit"] = end_on_exit
            if wait_url:
                join_params["wait_url"] = wait_url
            if max_participants is not None:
                join_params["max_participants"] = max_participants
            if record != "do-not-record":
                join_params["record"] = record
            if region:
                join_params["region"] = region
            if trim != "trim-silence":
                join_params["trim"] = trim
            if coach:
                join_params["coach"] = coach
            if status_callback_event:
                join_params["status_callback_event"] = status_callback_event
            if status_callback:
                join_params["status_callback"] = status_callback
            if status_callback_method != "POST":
                join_params["status_callback_method"] = status_callback_method
            if recording_status_callback:
                join_params["recording_status_callback"] = recording_status_callback
            if recording_status_callback_method != "POST":
                join_params["recording_status_callback_method"] = (
                    recording_status_callback_method
                )
            if recording_status_callback_event != "completed":
                join_params["recording_status_callback_event"] = (
                    recording_status_callback_event
                )
            if result is not None:
                join_params["result"] = result

        # Generate SWML document
        swml_doc = {
            "version": "1.0.0",
            "sections": {"main": [{"join_conference": join_params}]},
        }

        # Use execute_swml to add the action
        return self.execute_swml(swml_doc)

    def tap(
        self,
        uri: str,
        control_id: str | None = None,
        direction: Literal["speak", "listen", "both"] = "both",
        codec: Literal["PCMU", "PCMA"] = "PCMU",
        rtp_ptime: int = 20,
        status_url: str | None = None,
    ) -> "FunctionResult":
        """Start a background call tap using SWML.

        This is a virtual helper that generates SWML to start a background call tap.
        Media is streamed over WebSocket or RTP to a customer-controlled URI.

        Args:
            uri: Destination of the tap media stream (required). Formats:
                `rtp://IP:port`, `ws://example.com` or `wss://example.com`.
            control_id: Identifier for this tap. Pass the same ID to `stop_tap()` to
                end this specific tap. If omitted, the platform generates one and
                stores it in the `tap_control_id` variable.
            direction: Direction of audio to tap: "speak" (what the party says),
                "listen" (what the party hears) or "both" (default). The direction is
                always sent.
            codec: Codec for the media stream: "PCMU" (G.711 mu-law, default) or
                "PCMA" (G.711 A-law).
            rtp_ptime: Packetization time in milliseconds for RTP streams; a positive
                integer (default: 20).
            status_url: URL for tap status change requests.

        Returns:
            This `FunctionResult`, for chaining.

        Raises:
            ValueError: If direction or codec is invalid, or rtp_ptime is not a
                positive integer.

        Example:
            ```python
            result = FunctionResult("Monitoring enabled.").tap(
                "wss://example.com/tap", control_id="qa", direction="both"
            )
            ```
        """
        # Validate direction parameter
        valid_directions = ["speak", "listen", "both"]
        if direction not in valid_directions:
            raise ValueError(f"direction must be one of {valid_directions}")

        # Validate codec parameter
        valid_codecs = ["PCMU", "PCMA"]
        if codec not in valid_codecs:
            raise ValueError(f"codec must be one of {valid_codecs}")

        # Validate rtp_ptime
        if rtp_ptime <= 0:
            raise ValueError("rtp_ptime must be a positive integer")

        # Build the tap parameters
        tap_params: dict[str, Any] = {"uri": uri}

        # Add optional parameters if they differ from defaults
        if control_id:
            tap_params["control_id"] = control_id
        # Always sent: the verb's own default is "speak", not this helper's
        # "both", so omitting it would tap less than the caller asked for.
        tap_params["direction"] = direction
        if codec != "PCMU":
            tap_params["codec"] = codec
        if rtp_ptime != 20:
            tap_params["rtp_ptime"] = rtp_ptime
        if status_url:
            tap_params["status_url"] = status_url

        # Generate SWML document
        swml_doc = {"version": "1.0.0", "sections": {"main": [{"tap": tap_params}]}}

        # Use execute_swml to add the action
        return self.execute_swml(swml_doc)

    def stop_tap(self, control_id: str | None = None) -> "FunctionResult":
        """Stop an active tap stream using SWML.

        This is a virtual helper that generates SWML to stop a tap stream started with
        `tap()`.

        Args:
            control_id: Identifier of the tap to stop (optional). If not set, the last
                tap started is stopped.

        Returns:
            This `FunctionResult`, for chaining.
        """
        # Build the stop_tap parameters (empty object when no control_id)
        stop_params = {"control_id": control_id} if control_id else {}

        # Generate SWML document
        swml_doc = {
            "version": "1.0.0",
            "sections": {"main": [{"stop_tap": stop_params}]},
        }

        # Use execute_swml to add the action
        return self.execute_swml(swml_doc)

    def execute_rpc(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        call_id: str | None = None,
        node_id: str | None = None,
    ) -> "FunctionResult":
        """Execute an RPC method on a call using SWML.

        This is the generic, low-level interface for cross-call communication. For
        common operations, prefer the specific helpers `rpc_dial()`,
        `rpc_ai_message()` and `rpc_ai_unhold()`.

        Args:
            method: The RPC method to execute (for example "dial", "ai_message",
                "ai_unhold").
            params: Parameters for the RPC method (optional; omitted when empty).
            call_id: Target call ID for the RPC (optional).
            node_id: Target node ID for the RPC (optional).

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = (
                FunctionResult("Executing RPC")
                .execute_rpc(
                    method="ai_message",
                    call_id="some-call-id",
                    params={"role": "system", "message_text": "Hello"}
                )
            )
            ```
        """
        # Build the execute_rpc parameters
        rpc_params: dict[str, Any] = {"method": method}

        if call_id:
            rpc_params["call_id"] = call_id
        if node_id:
            rpc_params["node_id"] = node_id
        if params:
            rpc_params["params"] = params

        # Generate SWML document
        swml_doc = {
            "version": "1.0.0",
            "sections": {"main": [{"execute_rpc": rpc_params}]},
        }

        # Use execute_swml to add the action
        return self.execute_swml(swml_doc)

    def rpc_dial(
        self,
        to_number: str,
        from_number: str,
        dest_swml: str,
        device_type: str = "phone",
    ) -> "FunctionResult":
        """Dial out to a number with a destination SWML URL using `execute_rpc`.

        This is commonly used in call screening scenarios: place the caller on hold
        with `hold()`, then dial out to a human whose call is handled by a separate
        SWML agent, with `dest_swml` specifying what agent handles the outbound leg.

        Args:
            to_number: Phone number to dial (E.164 format).
            from_number: Caller ID to use (E.164 format).
            dest_swml: URL of the SWML document that handles the outbound call leg.
                It typically runs a screening agent that can accept, reject, or take
                a message.
            device_type: Device type for the outbound leg, typically "phone"
                (default: "phone").

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = (
                FunctionResult("Please hold while I connect you.")
                .hold(timeout=120)
                .rpc_dial(
                    to_number="+15551234567",
                    from_number="+15559876543",
                    dest_swml="https://example.com/call-agent?caller=John"
                )
            )
            ```
        """
        return self.execute_rpc(
            method="dial",
            params={
                "devices": {
                    "type": device_type,
                    "params": {"to_number": to_number, "from_number": from_number},
                },
                "dest_swml": dest_swml,
            },
        )

    def rpc_ai_message(
        self,
        call_id: str,
        message_text: str | None = None,
        role: str = "system",
        global_data: dict[str, Any] | None = None,
    ) -> "FunctionResult":
        """Send a message and/or global_data to an AI agent on another call.

        Useful for cross-call coordination, such as notifying a held caller's agent
        about a status change or handing it a value to speak later. Two payloads,
        either or both:

        - `message_text` lands as a turn in the other agent's conversation, so it
          competes for attention with everything else arriving that moment.
        - `global_data` is MERGED into the other call's global_data, where it is
          silent until something expands it. That makes it the better channel
          for content a later prompt needs to speak, because you can write
          `${global_data.your_key}` directly into the step that will run.

        Setting data and letting the destination step expand it beats injecting a
        message and hoping the model picks it out of a crowded turn:

        ```python
        # sender
        (result.rpc_ai_message(call_id, global_data={"decline_message": msg})
               .rpc_ai_unhold(call_id))

        # destination step, on the other call
        step.set_text("Tell the caller: ${global_data.decline_message}")
        ```

        Args:
            call_id: The call ID of the target call whose AI agent receives the
                message.
            message_text: Optional message text to inject into the target AI's
                conversation.
            role: Role for the injected message, typically "system" for instructions
                (default: "system"). Sent only when `message_text` is given.
            global_data: Optional object merged into the target call's global_data.
                See also `rpc_ai_global_data()`.

        Returns:
            This `FunctionResult`, for chaining.

        Raises:
            ValueError: If neither message_text nor global_data is given.

        Example:
            ```python
            result = FunctionResult("Noted.").rpc_ai_message(
                "target-call-id", "No one is available. Please take a message."
            )
            ```
        """
        params: dict[str, Any] = {}
        if message_text is not None:
            params["role"] = role
            params["message_text"] = message_text
        if global_data is not None:
            params["global_data"] = global_data
        if not params:
            raise ValueError("rpc_ai_message needs message_text, global_data, or both")

        return self.execute_rpc(method="ai_message", call_id=call_id, params=params)

    def rpc_ai_global_data(
        self, call_id: str, data: dict[str, Any]
    ) -> "FunctionResult":
        """Merge data into another call's global_data, with no conversation turn.

        Thin wrapper over `rpc_ai_message(global_data=...)`. Use it when the other
        call needs a value rather than an instruction: the destination prompt reads it
        back with `${global_data.key}`.

        Args:
            call_id: The call ID of the target call.
            data: Object merged into that call's global_data. Existing keys not in
                `data` are left in place.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = FunctionResult("Passed it along.").rpc_ai_global_data(
                "target-call-id", {"decline_message": "Nobody can take your call."}
            )
            ```
        """
        return self.rpc_ai_message(call_id=call_id, global_data=data)

    def rpc_ai_unhold(self, call_id: str) -> "FunctionResult":
        """Unhold another call using `execute_rpc`.

        This releases a call from hold, typically used after injecting a message to
        the held caller's AI agent with `rpc_ai_message()`.

        Args:
            call_id: The call ID of the call to release from hold.

        Returns:
            This `FunctionResult`, for chaining.

        Example:
            ```python
            result = (
                FunctionResult("Understood, I'll let them know.")
                .rpc_ai_message(call_id, "No one is available. Please take a message.")
                .rpc_ai_unhold(call_id)
            )
            ```
        """
        return self.execute_rpc(method="ai_unhold", call_id=call_id, params={})

    @staticmethod
    def create_payment_prompt(
        for_situation: str,
        actions: list[dict[str, str]],
        card_type: str | None = None,
        error_type: str | None = None,
    ) -> dict[str, Any]:
        """Create a payment prompt structure for use with the `pay()` method.

        Payment prompts customize the TTS messages played during different stages of
        payment collection.

        Args:
            for_situation: The payment stage this prompt applies to (for example
                `"payment-card-number"`, `"expiration-date"`, `"security-code"`,
                `"postal-code"`).
            actions: List of prompt actions, each with `type` and `phrase` keys. Build
                each entry with `create_payment_action()`.
            card_type: Space-separated card types this prompt applies to (for example
                `"visa mastercard"`).
            error_type: Space-separated error types this prompt handles.

        Returns:
            The prompt dictionary, to pass in the `prompts` list of `pay()`.
        """
        prompt = {"for": for_situation, "actions": actions}

        if card_type:
            prompt["card_type"] = card_type
        if error_type:
            prompt["error_type"] = error_type

        return prompt

    @staticmethod
    def create_payment_action(action_type: str, phrase: str) -> dict[str, str]:
        """Create a payment action for use in payment prompts.

        Args:
            action_type: "Say" for text-to-speech or "Play" for an audio file.
            phrase: The sentence to say (for "Say") or the URL to play (for "Play").

        Returns:
            The action dictionary, for use in `create_payment_prompt()`.
        """
        return {"type": action_type, "phrase": phrase}

    @staticmethod
    def create_payment_parameter(name: str, value: str) -> dict[str, str]:
        """Create a payment parameter for use with the `pay()` method.

        Args:
            name: Parameter name.
            value: Parameter value.

        Returns:
            The parameter dictionary, for the `parameters` list of `pay()`.
        """
        return {"name": name, "value": value}

    def to_dict(self) -> dict[str, Any]:
        """Convert to the JSON structure expected by SWAIG.

        Called automatically when the result is returned from a tool function; you
        rarely need to call it directly. The output contains `response` (if set),
        `action` (if any actions were added), and `post_process` (only when True and
        actions are present). If neither `response` nor `action` is present, the
        result is `{"response": "Action completed."}`.

        Returns:
            Dictionary in SWAIG function response format.
        """
        # Create the result object
        result: dict[str, Any] = {}

        # Add response if present
        if self.response:
            result["response"] = self.response

        # Add action if present
        if self.action:
            result["action"] = self.action

        # Add post_process if enabled and we have actions
        # (post_process only matters when there are actions to execute)
        if self.post_process and self.action:
            result["post_process"] = True

        # Ensure we have at least one of response or action
        if not result:
            # Default response if neither is present
            result["response"] = "Action completed."

        return result


#: The tool result a handler that raised gets, ``{function}`` its name. A
#: handler can fail after it did what it was asked, so the model must not
#: report success or failure.
TOOL_ERROR_RESULT = (
    "{function} failed before it finished, so whether it took effect is unknown."
)
#: The tool prompt that goes with TOOL_ERROR_RESULT.
TOOL_ERROR_PROMPT = (
    "Don't tell the user it worked or that it didn't. Tell them it couldn't be "
    "confirmed, and offer to check or try again."
)
#: The tool result for a handler that returned an empty dict.
TOOL_NO_RESULT = "{function} returned no result, so whether it took effect is unknown."


def tool_error_result(function: str) -> FunctionResult:
    """Return the result the model gets when a tool's handler raised.

    The exception itself is logged, not sent: its text can hold internals, and the
    model would read it as the outcome. The model gets a `tool_result` saying the
    function failed before it finished so whether it took effect is unknown, and a
    `tool_prompt` telling it not to claim success or failure but to say it could
    not be confirmed and offer to check or try again.

    Args:
        function: The name of the tool function whose handler raised.

    Returns:
        A `FunctionResult` built from `TOOL_ERROR_RESULT` and `TOOL_ERROR_PROMPT`.
    """
    return FunctionResult(
        tool_result=TOOL_ERROR_RESULT.format(function=function),
        tool_prompt=TOOL_ERROR_PROMPT,
    )


class ToolRefusal(Exception):
    """Raise from a tool handler to decline the call with a known outcome.

    The model gets `tool_result`, what is true now (nothing was done, and why), and
    `tool_prompt`, what to do next, in place of a crash result that says the
    outcome is unknown. Use it for a precondition the handler checks itself: an
    item out of stock, an account that isn't found.

    Example:
        ```python
        if not stock.available(item):
            raise ToolRefusal(
                f"place_order was not run: {item} is out of stock.",
                "Tell the caller, and offer the similar items in stock.",
            )
        ```
    """

    def __init__(self, tool_result: str, tool_prompt: str | None = None) -> None:
        """Create a refusal.

        Args:
            tool_result: What is true now: that nothing was done, and why. Also
                the exception's message.
            tool_prompt: What the model should do or say next. Omit for a
                status-only result.
        """
        super().__init__(tool_result)
        self.tool_result = tool_result
        self.tool_prompt = tool_prompt

    def result(self) -> FunctionResult:
        """Return the result the model gets for this refusal.

        Returns:
            A `FunctionResult` carrying `tool_result` and `tool_prompt`.
        """
        return FunctionResult(
            tool_result=self.tool_result, tool_prompt=self.tool_prompt
        )


def settle_result(function: str, result: Any) -> Any:
    """Shape what a handler returned into a result the model can read as it is.

    This avoids claiming an outcome the handler didn't report. None keeps its
    long-standing "Function executed successfully". A dict with a `response` or an
    `action` is a SWAIG result already and is returned unchanged. Any other dict is
    the handler's data: the model gets it as JSON in `response`. An empty dict says
    the outcome is unknown. Any other value is returned unchanged.

    Args:
        function: The name of the tool function whose handler returned `result`.
        result: What the handler returned.

    Returns:
        A `FunctionResult` for None, a dict with a `response` string for handler
        data, or `result` itself otherwise.
    """
    if result is None:
        return FunctionResult("Function executed successfully")
    if isinstance(result, dict) and "response" not in result and "action" not in result:
        if not result:
            return {"response": TOOL_NO_RESULT.format(function=function)}
        return {"response": json.dumps(result, default=str)}
    return result


# Backwards-compatible alias. Older docs, skill READMEs, and external
# tutorials import this as `SwaigFunctionResult`. Both names refer to the
# same class — pick whichever reads better in your code.
SwaigFunctionResult = FunctionResult
