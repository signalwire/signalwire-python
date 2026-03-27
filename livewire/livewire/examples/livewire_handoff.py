#!/usr/bin/env python3
"""
LiveWire agent handoff example.

Demonstrates how to use AgentHandoff to transfer between agents in a
multi-agent scenario -- same pattern as LiveKit, running on SignalWire.

Usage:
    python livewire_handoff.py
"""

from signalwire.livewire import (
    Agent,
    AgentSession,
    AgentServer,
    AgentHandoff,
    JobContext,
    function_tool,
    run_app,
)


# -- Tools for the greeter agent -------------------------------------------

@function_tool
def transfer_to_support() -> str:
    """Transfer the caller to a technical support agent."""
    return "Transferring you to technical support now."


# -- Tools for the support agent -------------------------------------------

@function_tool
def lookup_ticket(ticket_id: str) -> str:
    """Look up a support ticket by ID."""
    return f"Ticket {ticket_id}: Status is 'In Progress'. Last update 2 hours ago."


@function_tool
def create_ticket(summary: str) -> str:
    """Create a new support ticket."""
    return f"Created ticket #12345 with summary: {summary}"


# -- Agent definitions -----------------------------------------------------

greeter_agent = Agent(
    instructions=(
        "You are a friendly receptionist.  Greet the caller and determine "
        "if they need technical support.  If so, use the transfer_to_support "
        "tool."
    ),
    tools=[transfer_to_support],
)

support_agent = Agent(
    instructions=(
        "You are a technical support specialist.  Help the caller with "
        "their issue.  You can look up existing tickets or create new ones."
    ),
    tools=[lookup_ticket, create_ticket],
)


# -- Entrypoint ------------------------------------------------------------

server = AgentServer()


@server.rtc_session(agent_name="handoff-demo")
async def entrypoint(ctx: JobContext):
    await ctx.connect()

    # Start with the greeter
    session = AgentSession()
    await session.start(greeter_agent, room=ctx.room)
    session.generate_reply(
        instructions="Welcome the caller and ask how you can help."
    )

    # In a real app you would listen for the handoff signal and then:
    #   handoff = AgentHandoff(support_agent)
    #   session.update_agent(support_agent)


if __name__ == "__main__":
    run_app(server)
