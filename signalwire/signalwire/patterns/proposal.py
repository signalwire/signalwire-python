"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

A change the caller says yes to before a tool carries it out.

This is the platform's confirm pattern. A function proposes the change: it
reads it back and records it in ``semantic_state``, in one action object,
so the proposal's dialogue starts with the read-back. The confirm tool's
semantic gates, judged on that dialogue (``dialogue="proposal"``), check
three things: that the caller's latest turn is an answer, that the answer
is a yes, and that what they answered was a read-back of this change. The
gates' questions are the platform's, as replayed against logged calls.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from signalwire.core.function_result import FunctionResult
from signalwire.core.semantic_gate import SemanticGate

#: Where the proposal is recorded in semantic_state
PROPOSAL_KEY = "proposal"


class Proposal:
    """
    A read-back the caller confirms before ``confirm_tool`` runs.

    Example:
        order = Proposal("place_order", decline_tool="change_order")

        def review_order(args, raw_data):
            text = f"That's {args['item']} for pickup at {args['time']}. Is that right?"
            return order.propose(text, raw_data=raw_data, details={"item": args["item"]})

        agent.define_tool("review_order", "Read the order back", ORDER, review_order)
        agent.define_tool("place_order", "Place the order the caller said yes to",
                          {}, place_order, gates=order.confirm_gates())
    """

    def __init__(
        self,
        confirm_tool: str,
        *,
        decline_tool: str | None = None,
        threshold: float = 0.8,
        unclear: bool = False,
    ) -> None:
        """
        Args:
            confirm_tool: The tool that carries out the change.
            decline_tool: The tool the caller's no or change goes to, named
                in what the model is told when they don't say yes.
            threshold: Each gate's threshold. The platform's measured
                value is 0.8 for yes/no gates, about 0.6 with ``unclear``.
            unclear: True to let the gates answer unclear as well (OpenAI),
                which asks the caller again.
        """
        self.confirm_tool = confirm_tool
        self.decline_tool = decline_tool
        self.threshold = threshold
        self.unclear = unclear

    def propose(
        self,
        read_back: str,
        *,
        raw_data: Mapping[str, Any] | None = None,
        details: Mapping[str, Any] | None = None,
        result: FunctionResult | None = None,
    ) -> FunctionResult:
        """
        The result of the function that proposes the change.

        The agent says ``read_back`` word for word, and the proposal is
        recorded as ``semantic_state`` ``{"proposal": read_back, "revision":
        n, **details}``, in the same action object, so the gates' proposal
        dialogue starts with the read-back. The model then waits for the
        caller's answer (``wait_for_user``).

        Args:
            read_back: The words to read back, ending with the question,
                such as "That's a large tea for pickup at five. Is that
                right?". Name everything the change covers, the way the
                caller would say it.
            raw_data: The proposing call's request, so a proposal made again
                gets the next revision: the platform marks a new proposal
                only when ``semantic_state`` changes.
            details: More of what the change is, kept in the state with it.
            result: A result to add to, in place of a new one.

        Returns:
            The result.
        """
        state: dict[str, Any] = {
            **(details or {}),
            PROPOSAL_KEY: read_back,
            "revision": _revision(raw_data) + 1,
        }
        result = result if result is not None else FunctionResult()
        result.set_tool_response(
            tool_result=f"Read back to the caller: {read_back}",
            tool_prompt=(
                f"Wait for the caller's answer. Call {self.confirm_tool} only when "
                "they say yes to this read-back."
                + (
                    f" If they say no or want a change, call {self.decline_tool}."
                    if self.decline_tool
                    else ""
                )
            ),
        )
        # One object: its say runs before its set_global_data, so the
        # read-back is the first turn of the proposal it records
        result.add_action("say", read_back)
        result.action[-1]["set_global_data"] = {"semantic_state": state}
        result.wait_for_user(True)
        return result

    def ask_again(
        self, raw_data: Mapping[str, Any], result: FunctionResult | None = None
    ) -> FunctionResult:
        """
        Read the current proposal back again, as a new revision, so the
        gates' proposal dialogue starts over with it.

        Args:
            raw_data: The request of the call asking again, which carries
                the proposal in its ``global_data``.
            result: A result to add to.

        Raises:
            ValueError: When the request carries no proposal.
        """
        state = current(raw_data)
        if state is None:
            raise ValueError(
                "there is no proposal in semantic_state to ask about again"
            )
        details = {
            k: v for k, v in state.items() if k not in (PROPOSAL_KEY, "revision")
        }
        return self.propose(
            str(state[PROPOSAL_KEY]), raw_data=raw_data, details=details, result=result
        )

    def confirm_gates(self) -> list[SemanticGate]:
        """
        The confirm tool's gates: the caller answered, the answer is a yes,
        and it was a yes to a read-back of this change. Each is judged on
        the proposal's dialogue. When one fails, the model is told why, with
        the proposal quoted from ``semantic_state`` (the platform expands
        ``${global_data...}`` in a gate's output; one that doesn't sends it
        as written), and chaining is turned off for the call
        (``back_to_back_functions(False)``), so the model answers in words
        before it calls a tool again.
        """
        tool = self.confirm_tool
        quoted = "${global_data.semantic_state.proposal}"
        decline = (
            f", or call {self.decline_tool} if they no longer want it"
            if self.decline_tool
            else ""
        )

        def blocked(why: str, then: str) -> FunctionResult:
            return FunctionResult(
                tool_result=f"{tool} was not run. {why}",
                tool_prompt=then,
            ).back_to_back_functions(False)

        gate: dict[str, Any] = {
            "threshold": self.threshold,
            "dialogue": "proposal",
        }
        if self.unclear:
            gate["unclear"] = True
            gate["on_unclear"] = blocked(
                "The caller's answer didn't settle it.",
                f'Read the change back as it stands, "{quoted}", and ask for a plain yes or no.',
            )
        return [
            SemanticGate(
                "Is the caller's latest turn in `conversation` an answer, rather than "
                "only a sound that shows they are listening, made while the agent was "
                "still talking? A caller turn began while the agent was still talking "
                "if it is marked `while_agent_talking`, or if the agent turn just "
                "before it is marked `interrupted`, which means the caller cut it off. "
                "Any other caller turn began after the agent had finished.",
                on_fail=blocked(
                    "The caller was only showing they were listening.",
                    "Finish reading the change back and ask for a plain yes or no.",
                ),
                true_means=(
                    "Their latest turn answers, with a yes, a no, or more than a sound "
                    "that shows they are listening, or it began after the agent had "
                    "finished."
                ),
                false_means=(
                    "Their latest turn is only a sound that shows they are listening, "
                    "and it began while the agent was still talking."
                ),
                id="answered",
                **gate,
            ),
            SemanticGate(
                "Is the caller's latest answer in `conversation` to the agent's request "
                "to confirm a yes to the change described in `semantic_state`? The "
                "read-back may be cut off by their answer: a yes once they have heard "
                "what the change is counts. A yes that comes with another request still "
                "counts as a yes to this change.",
                on_fail=blocked(
                    "The caller has not said yes to this change.",
                    f'Read it back, "{quoted}", and ask for a plain yes or no{decline}.',
                ),
                true_means=(
                    "Their latest answer says yes to this change, even with another "
                    "request or a cut-off read-back."
                ),
                false_means=(
                    "Their latest answer says no, hesitates, or only asks a question or "
                    "for something else."
                ),
                id="agreed",
                **gate,
            ),
            SemanticGate(
                "Did the agent read back the change in `semantic_state` before the "
                "caller's latest answer in `conversation`?",
                on_fail=blocked(
                    "What the caller answered was not a read-back of this change.",
                    f'Read the proposal back as it stands, "{quoted}", and only it, then '
                    f"ask for a yes or no{decline}.",
                ),
                true_means=(
                    "The agent's read-back, even if cut off by the answer, described "
                    "this change."
                ),
                false_means="The read-back described a different change, or none was given.",
                id="read_back",
                **gate,
            ),
        ]

    def complete(
        self, summary: str, result: FunctionResult | None = None
    ) -> FunctionResult:
        """
        Record that the change was carried out, in place of the proposal.

        Write what was done rather than clearing the state with ``{}``: a
        state that changes starts the next proposal dialogue there, and the
        model and the gates see what's settled.

        Args:
            summary: What was done, such as "Order 4471 is placed".
            result: The confirm tool's result, to add to.
        """
        result = result if result is not None else FunctionResult(tool_result=summary)
        return result.set_semantic_state({"done": summary})


def current(raw_data: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """The proposal a request's ``global_data.semantic_state`` holds, or None."""
    if not isinstance(raw_data, Mapping):
        return None
    global_data = raw_data.get("global_data")
    state = (
        global_data.get("semantic_state") if isinstance(global_data, Mapping) else None
    )
    if isinstance(state, dict) and PROPOSAL_KEY in state:
        return state
    return None


def _revision(raw_data: Mapping[str, Any] | None) -> int:
    state = current(raw_data)
    revision = state.get("revision") if state else 0
    return (
        revision if isinstance(revision, int) and not isinstance(revision, bool) else 0
    )
