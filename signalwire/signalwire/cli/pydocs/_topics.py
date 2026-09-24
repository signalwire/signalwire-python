"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

The hand-written part of sw-pydocs: one entry per topic.

Keep each body to what a reader needs to choose an approach and avoid known
mistakes, and point to the installed docs for the rest. Facts that can be read
from the installed package (versions, commands, skills, signatures) belong in
the renderers, not here. tests/unit/cli/test_pydocs.py checks that every file
and API name listed here exists.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    """One ``sw-pydocs <name>`` page."""

    name: str
    title: str
    summary: str
    body: str
    # (path under the docs root, what it's for)
    docs: tuple[tuple[str, str], ...] = ()
    # Paths under the docs root
    examples: tuple[str, ...] = ()
    # Dotted names that ``sw-pydocs api`` resolves
    api: tuple[str, ...] = ()
    related: tuple[str, ...] = ()
    # A section the renderer generates from the installed package
    live: str | None = None


_QUICKSTART = Topic(
    name="quickstart",
    title="Quickstart: a working agent in one file",
    summary="The smallest complete agent, and how to run and test it",
    body="""\
```python
from signalwire import AgentBase, FunctionResult


class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent", route="/agent")
        self.add_language(name="English", code="en-US", voice="inworld.Mark")
        self.prompt_add_section("Role", body="You are a helpful assistant.")

    @AgentBase.tool()
    def get_time(self) -> FunctionResult:
        \"\"\"Get the current time.\"\"\"
        from datetime import datetime

        return FunctionResult(f"The time is {datetime.now():%H:%M}.")


if __name__ == "__main__":
    MyAgent().run()
```

- `run()` starts a web server on port 3000 (or `PORT`). It serves the agent's
  SWML document at `/agent` and its tools at `/agent/swaig`. On AWS Lambda,
  Google Cloud Functions, Azure Functions or CGI, it handles the platform's
  request instead.
- Every endpoint except the `/health` and `/ready` probes needs basic auth.
  Set `SWML_BASIC_AUTH_USER` and `SWML_BASIC_AUTH_PASSWORD`; otherwise the
  agent generates credentials, which `agent.get_basic_auth_credentials()`
  returns.
- To take calls, SignalWire must reach the agent over HTTPS: deploy it, or use
  a tunnel during development and set `SWML_PROXY_URL_BASE` to the public URL.
  Then point a phone number's SWML webhook at
  `https://USER:PASSWORD@HOST/agent`, in the dashboard or with the REST client
  (`rest/examples/rest_bind_phone_to_swml_webhook.py`).

Test it without a call:

```bash
swaig-test my_agent.py --list-tools
swaig-test my_agent.py --dump-swml
swaig-test my_agent.py --exec get_time
```
""",
    docs=(
        ("README.md", "The SDK's overview and quickstarts for agents, RELAY and REST"),
        ("docs/agent_guide.md", "The main guide to building agents"),
    ),
    examples=(
        "examples/quickstart_agent.py",
        "examples/quickstart_relay.py",
        "examples/quickstart_rest.py",
    ),
    api=(
        "signalwire.AgentBase",
        "signalwire.FunctionResult",
        "signalwire.AgentBase.run",
    ),
    related=("agents", "tools", "testing", "deploy"),
)

_AGENTS = Topic(
    name="agents",
    title="AI agents (AgentBase)",
    summary="Voice and text AI agents: how they work and how they're built",
    body="""\
An agent is a Python web service, and SignalWire runs the conversation. When a
call arrives, SignalWire fetches the agent's SWML document (prompt, voice,
languages, tools, settings) and runs speech recognition, the LLM and
text-to-speech itself. When the model calls a tool, SignalWire sends the call
to the agent's `/swaig` endpoint, and your handler returns a `FunctionResult`.
Your code never handles audio.

Build one by subclassing `AgentBase` and configuring it in `__init__`:

- Voice and language: `add_language()`. Prompt: `prompt_add_section()` or
  `set_prompt_text()` (`sw-pydocs prompts`).
- Tools: `@AgentBase.tool`, `define_tool()`, or DataMap tools that run on
  SignalWire (`sw-pydocs tools`, `sw-pydocs datamap`).
- Ready-made tools: `add_skill()` (`sw-pydocs skills`).
- Multi-step workflows: `define_contexts()` (`sw-pydocs contexts`).
- An end-of-call summary: `set_post_prompt()`, received by `on_summary()`.

Serving: `run()` or `serve()` for one agent, `AgentServer` for several agents
in one process, and `get_app()` or `as_router()` to mount an agent in an
existing FastAPI app.

Per-call configuration: `set_dynamic_config_callback()` configures a copy of
the agent for each request, from its query parameters, body and headers, for
per-tenant prompts, voices and tools. The callback runs in a worker thread,
at the same time as other calls' callbacks. Don't keep per-caller state on the
shared agent instance.

Configuration precedence: constructor arguments, then the config file, then
environment variables, then defaults.
""",
    docs=(
        (
            "docs/agent_guide.md",
            "The main guide: prompts, tools, skills, contexts, serving",
        ),
        (
            "docs/architecture.md",
            "How the pieces fit: mixins, request flow, configuration",
        ),
        (
            "docs/api_reference.md",
            "Reference for AgentBase and the other public classes",
        ),
        ("docs/sdk_features.md", "What the SDK adds over writing SWML by hand"),
        ("docs/configuration.md", "Config files and environment variables"),
        (
            "docs/pgi_agent_guide.md",
            "How to design agents that stay within their rules",
        ),
    ),
    examples=(
        "examples/simple_agent.py",
        "examples/simple_static_agent.py",
        "examples/simple_dynamic_agent.py",
        "examples/declarative_agent.py",
        "examples/comprehensive_dynamic_agent.py",
        "examples/multi_agent_server.py",
        "examples/custom_path_agent.py",
    ),
    api=(
        "signalwire.AgentBase",
        "signalwire.AgentServer",
        "signalwire.AgentBase.set_dynamic_config_callback",
        "signalwire.AgentBase.get_app",
        "signalwire.AgentBase.on_summary",
    ),
    related=("prompts", "tools", "contexts", "skills", "pgi", "deploy"),
)

_PROMPTS = Topic(
    name="prompts",
    title="Prompts, voice and model settings",
    summary="Prompt sections, post-prompt summaries, languages, voices and LLM parameters",
    body="""\
- The Prompt Object Model builds the prompt from titled sections:
  `prompt_add_section(title, body=..., bullets=[...])`,
  `prompt_add_subsection()` and `prompt_add_to_section()`. `set_prompt_text()`
  sets a plain prompt instead. A `PROMPT_SECTIONS` class attribute declares the
  sections on the class.
- `set_post_prompt(text)` asks the model for a summary when the conversation
  ends. `on_summary(summary, raw_data)` receives it.
- `add_language(name, code, voice)` sets the language and voice.
  `add_hints()` and `add_pronunciation()` help speech recognition and
  text-to-speech with your vocabulary.
- `set_params()` sets the platform's AI settings.
  `set_prompt_llm_params()` and `set_post_prompt_llm_params()` set model
  parameters such as `temperature` and `top_p`. Nothing is sent unless you set
  it.
- `set_global_data()` and `update_global_data()` hold session data for the
  call. It isn't a database, and the model doesn't see all of it: tools,
  templates and prompts expose what they choose.

Keep prompts short and put rules that matter in code: a prompt asks, a tool
handler enforces (`sw-pydocs pgi`).
""",
    docs=(
        ("docs/agent_guide.md", "Prompt building, languages and voices, global data"),
        ("docs/llm_parameters.md", "Model parameters for the prompt and post-prompt"),
    ),
    examples=(
        "examples/declarative_agent.py",
        "examples/llm_params_demo.py",
        "examples/session_and_state_demo.py",
    ),
    api=(
        "signalwire.AgentBase.prompt_add_section",
        "signalwire.AgentBase.set_prompt_text",
        "signalwire.AgentBase.set_post_prompt",
        "signalwire.AgentBase.add_language",
        "signalwire.AgentBase.set_params",
        "signalwire.AgentBase.set_prompt_llm_params",
        "signalwire.AgentBase.set_global_data",
    ),
    related=("agents", "tools", "pgi"),
)

_TOOLS = Topic(
    name="tools",
    title="Tools (SWAIG functions) and FunctionResult",
    summary="Functions the model can call, and what they return",
    body="""\
A tool is a function the model can ask to call. SignalWire sends the call to
the agent's `/swaig` endpoint, and the SDK runs your handler. A plain `def`
handler runs in a worker thread, so handlers for different calls run at the
same time: guard state they share. An `async def` handler runs on the event
loop and must not block it.

Declare a tool with type hints, and the SDK builds its schema. The docstring's
summary is the tool's description, and its `Args:` describe the parameters:

```python
@AgentBase.tool()
def get_order_status(self, order_id: str) -> FunctionResult:
    \"\"\"Look up an order's status.

    Args:
        order_id: The order number the caller gives
    \"\"\"
    order = orders.find(order_id)  # your code decides what's true
    return FunctionResult(
        tool_result=f"Order {order_id} shipped {order.shipped_on}.",
        tool_prompt="Tell the caller when the order shipped.",
    )
```

Or give the schema yourself, with a handler that takes `(args, raw_data)`:
`@AgentBase.tool(name=..., description=..., parameters={"type": "object",
"properties": {...}})`. `define_tool()` registers one at runtime.

- The description and parameter descriptions are prompt text: the model reads
  them to decide when to call the tool.
- `FunctionResult`'s response is context for the model, not speech. Keep facts
  (`tool_result`) apart from instructions (`tool_prompt`).
- Actions such as `connect()`, `hangup()`, `hold()`, `send_sms()`,
  `update_global_data()` and `swml_change_step()` run on the platform. Set
  `post_process=True` when the caller must hear something before one lands.
- Tools are secure by default: each call must carry a token minted into that
  call's SWML.
- A tool call is a request from the model, not an authorization. Check
  identity, state and business rules in the handler.
""",
    docs=(
        ("docs/swaig_reference.md", "Every FunctionResult method and action"),
        (
            "docs/agent_guide.md",
            "Defining tools, fillers, native functions and security",
        ),
        (
            "docs/pgi_agent_guide.md",
            "What a tool may decide, and what code must enforce",
        ),
    ),
    examples=(
        "examples/swaig_features_agent.py",
        "examples/call_flow_and_actions_demo.py",
        "examples/session_and_state_demo.py",
        "examples/record_call_example.py",
        "examples/room_and_sip_example.py",
        "examples/tap_example.py",
    ),
    api=(
        "signalwire.AgentBase.tool",
        "signalwire.AgentBase.define_tool",
        "signalwire.FunctionResult",
        "signalwire.FunctionResult.connect",
        "signalwire.FunctionResult.swml_change_step",
    ),
    related=("datamap", "contexts", "skills", "security", "pgi"),
)

_DATAMAP = Topic(
    name="datamap",
    title="DataMap: tools that run on SignalWire",
    summary="Tools that call an HTTP API from SignalWire's servers, with no webhook to your code",
    body="""\
A DataMap tool calls an HTTP API from SignalWire's servers, or matches
patterns in its arguments, and fills the result into the model's context from
a template. Your server isn't involved when the tool runs.

```python
from signalwire import DataMap, FunctionResult

weather = (
    DataMap("get_weather")
    .description("Get the current weather for a city")
    .parameter("city", "string", "City name", required=True)
    .webhook("GET", "https://api.example.com/weather?city=${enc:url:args.city}")
    .output(FunctionResult("Weather in ${args.city}: ${current.summary}"))
)
self.register_swaig_function(weather.to_swaig_function())
```

- A template reads a path from the root of the call's data: `${args.city}`
  for an argument, `${global_data.x}`, `${meta_data.x}`, and call details
  such as `${call_id}`. When a webhook responds, its JSON object's fields join
  the root, so an API that returns `{"current": {...}}` is read as
  `${current.summary}`, with no `response.` prefix. An array response is
  `${array[0].x}`. The platform expands templates, not the SDK.
- Prefix helpers transform a value, left to right: `${lc:enc:args.city}` takes
  `args.city`, lowercases it, then URL-encodes it. `@{...}` functions format
  dates and phone numbers, and more; the guide's section 4 lists them all.
- A webhook's `params` are its JSON request body, set with `.params()`.
- `swaig-test --exec` simulates a DataMap tool locally, including its HTTP
  request.
- Use DataMap for simple lookups. Use a Python tool when the result depends on
  your own logic, authorization or state.
""",
    docs=(
        (
            "docs/datamap_guide.md",
            "The DataMap builder, templates, expressions and testing",
        ),
    ),
    examples=(
        "examples/data_map_demo.py",
        "examples/advanced_datamap_demo.py",
        "examples/joke_skill_demo.py",
    ),
    api=(
        "signalwire.DataMap",
        "signalwire.AgentBase.register_swaig_function",
        "signalwire.create_simple_api_tool",
        "signalwire.create_expression_tool",
    ),
    related=("tools", "testing"),
)

_CONTEXTS = Topic(
    name="contexts",
    title="Contexts and steps",
    summary="Multi-step workflows, per-step tools, and gathering answers",
    body="""\
`define_contexts()` returns a `ContextBuilder`. Each context holds steps, and
each step has its own prompt text, its own tools and its own exits:

```python
builder = self.define_contexts()
ctx = builder.add_context("default")  # a single context must be named "default"
ctx.add_step("identify").set_text("Ask for the caller's account number.") \\
    .set_functions(["verify_account"]).set_valid_steps([])
ctx.add_step("help").set_text("Help with the account.") \\
    .set_functions(["get_balance", "transfer_to_agent"])
```

- Set `set_functions()` on every step. A step that doesn't set it can keep the
  previous step's tools; `set_functions([])` gives it none.
- `set_valid_steps()` and `set_valid_contexts()` limit where the model may
  move. To move only after your code has checked something, leave them empty
  and return `FunctionResult().swml_change_step(...)` from the handler.
- `set_step_criteria()` guides the model; it doesn't enforce anything.
- `set_gather_info()` and `add_gather_question()` collect answers one question
  at a time.
""",
    docs=(
        (
            "docs/contexts_guide.md",
            "Contexts, steps, navigation, gather mode and history",
        ),
        (
            "docs/pgi_agent_guide.md",
            "Scoping tools per step and code-owned transitions",
        ),
    ),
    examples=(
        "examples/contexts_demo.py",
        "examples/gather_info_demo.py",
        "examples/gather_per_question_functions_demo.py",
        "examples/step_function_inheritance_demo.py",
    ),
    api=(
        "signalwire.AgentBase.define_contexts",
        "signalwire.ContextBuilder",
        "signalwire.Context",
        "signalwire.Step",
        "signalwire.Step.set_functions",
        "signalwire.Step.set_gather_info",
        "signalwire.FunctionResult.swml_change_step",
    ),
    related=("tools", "pgi", "prompts"),
)

_SKILLS = Topic(
    name="skills",
    title="Skills: ready-made capabilities",
    summary="Built-in skills (web search, datetime, knowledge search, ...) and writing your own",
    body="""\
A skill adds tools, prompt sections and hints to an agent in one call:

```python
self.add_skill("datetime")
self.add_skill("web_search", {"api_key": "...", "search_engine_id": "..."})
```

- A skill that allows several instances takes a `tool_name` parameter, so each
  instance gets its own tool.
- `sw-pydocs skills <name>` shows a skill's parameters and its README.
- Write your own by subclassing `SkillBase`: set `SKILL_NAME` and
  `SKILL_DESCRIPTION`, and implement `setup()` and `register_tools()`. Load
  skills from another directory with `add_skill_directory()`.
""",
    docs=(
        ("docs/skills_system.md", "How skills load, and how to write one"),
        ("docs/skills_parameter_schema.md", "How skills describe their parameters"),
        (
            "docs/third_party_skills.md",
            "Packaging and loading skills from outside the SDK",
        ),
    ),
    examples=(
        "examples/skills_demo.py",
        "examples/joke_agent.py",
        "examples/wikipedia_demo.py",
        "examples/web_search_agent.py",
        "examples/web_search_multi_instance_demo.py",
        "examples/datasphere_multi_instance_demo.py",
    ),
    api=(
        "signalwire.AgentBase.add_skill",
        "signalwire.core.skill_base.SkillBase",
        "signalwire.add_skill_directory",
    ),
    related=("agents", "search", "mcp"),
    live="skills",
)

_PREFABS = Topic(
    name="prefabs",
    title="Prefab agents",
    summary="Ready-made agents for surveys, intake, reception, FAQs and concierge",
    body="""\
Prefabs are `AgentBase` subclasses for common jobs. Configure one with
constructor arguments, or subclass it to change its prompt and tools.
""",
    docs=(("docs/agent_guide.md", "Prefab agents and their options"),),
    examples=(
        "examples/info_gatherer_example.py",
        "examples/dynamic_info_gatherer_example.py",
        "examples/survey_agent_example.py",
        "examples/receptionist_agent_example.py",
        "examples/concierge_agent_example.py",
        "examples/faq_bot_agent.py",
    ),
    api=("signalwire.prefabs",),
    related=("agents",),
    live="prefabs",
)

_SWML = Topic(
    name="swml",
    title="SWML services: call flows without an AI agent",
    summary="Build and serve SWML documents: IVRs, routing, recording, any verb",
    body="""\
SWML is the JSON document that tells SignalWire what to do with a call.
`AgentBase` writes one with an `ai` verb. `SWMLService` builds any document,
from any verbs, and serves it the same way:

```python
from signalwire import SWMLService

service = SWMLService(name="greeter", route="/greeter")
service.add_verb("answer", {})
service.add_verb("play", {"url": "say:Thanks for calling."})
service.add_verb("hangup", {})
service.serve()
```

- Documents are validated against the SWML schema that ships with the package.
- `mcp/swml-schema-search/` is an MCP server that answers questions about that
  schema, for coding agents.
""",
    docs=(
        ("docs/swml_service_guide.md", "SWMLService and SWMLBuilder"),
        ("docs/architecture.md", "How SWML documents are built and served"),
        ("mcp/swml-schema-search/README.md", "An MCP server for looking up SWML verbs"),
    ),
    examples=(
        "examples/basic_swml_service.py",
        "examples/swml_service_example.py",
        "examples/dynamic_swml_service.py",
        "examples/swml_service_routing_example.py",
        "examples/auto_vivified_example.py",
        "examples/swmlservice_swaig_standalone.py",
        "examples/swmlservice_ai_sidecar.py",
    ),
    api=(
        "signalwire.SWMLService",
        "signalwire.SWMLBuilder",
        "signalwire.SWMLService.add_verb",
    ),
    related=("agents", "relay", "rest"),
)

_RELAY = Topic(
    name="relay",
    title="RELAY: real-time call and message control",
    summary="Drive live calls and messages over WebSocket with async Python",
    body="""\
`RelayClient` holds a WebSocket connection to SignalWire. Your code answers
and places calls, and then drives them step by step: play, record, collect
digits, detect, connect, conference, transcribe, and send or receive messages.

```python
from signalwire.relay import RelayClient

client = RelayClient(contexts=["default"])  # credentials from the environment


@client.on_call
async def handle(call):
    await call.answer()
    action = await call.play([{"type": "tts", "params": {"text": "Welcome!"}}])
    await action.wait()
    await call.hangup()


client.run()
```

- Credentials come from the arguments or from `SIGNALWIRE_PROJECT_ID`,
  `SIGNALWIRE_API_TOKEN` and `SIGNALWIRE_SPACE`.
- Operations that take time return an action: `await action.wait()` for its
  result.
- Choose RELAY when your code controls the call, an AI agent when the model
  holds the conversation, and REST for managing resources over HTTP.
""",
    docs=(
        ("relay/README.md", "Overview of the RELAY client"),
        ("relay/docs/getting-started.md", "Connecting, receiving calls, first steps"),
        ("relay/docs/client-reference.md", "RelayClient reference"),
        ("relay/docs/call-methods.md", "Every Call method"),
        ("relay/docs/events.md", "Events and their payloads"),
        ("relay/docs/messaging.md", "Sending and receiving messages"),
    ),
    examples=(
        "examples/quickstart_relay.py",
        "relay/examples/relay_answer_and_welcome.py",
        "relay/examples/relay_dial_and_play.py",
        "relay/examples/relay_ivr_connect.py",
    ),
    api=(
        "signalwire.relay.RelayClient",
        "signalwire.relay.Call",
        "signalwire.relay.Message",
    ),
    related=("rest", "swml", "agents"),
)

_REST = Topic(
    name="rest",
    title="REST client",
    summary="Manage SignalWire resources over HTTP: numbers, Fabric, calls, video, messaging",
    body="""\
`RestClient` is a synchronous HTTP client with one namespace per API area:

```python
from signalwire.rest import RestClient

client = RestClient()  # SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN, SIGNALWIRE_SPACE
client.phone_numbers.search(areacode="512")
client.fabric.ai_agents.create(name="Support Bot", prompt={"text": "You are helpful."})
```

- `client.calling` sends commands to live calls, such as play and record.
- Errors raise `SignalWireRestError`.
""",
    docs=(
        ("rest/README.md", "Overview of the REST client"),
        ("rest/docs/getting-started.md", "Credentials and first requests"),
        ("rest/docs/client-reference.md", "RestClient reference"),
        ("rest/docs/namespaces.md", "Every namespace and its operations"),
        ("rest/docs/calling.md", "Commands for live calls"),
        (
            "rest/docs/fabric.md",
            "Fabric resources: AI agents, subscribers, SWML scripts",
        ),
    ),
    examples=(
        "examples/quickstart_rest.py",
        "rest/examples/rest_manage_resources.py",
        "rest/examples/rest_bind_phone_to_swml_webhook.py",
        "rest/examples/rest_phone_number_management.py",
        "rest/examples/rest_calling_play_and_record.py",
        "rest/examples/rest_calling_ivr_and_ai.py",
        "rest/examples/rest_fabric_swml_and_callflows.py",
        "rest/examples/rest_fabric_subscribers_and_sip.py",
        "rest/examples/rest_fabric_conferences_and_routing.py",
        "rest/examples/rest_video_rooms.py",
        "rest/examples/rest_queues_mfa_and_recordings.py",
        "rest/examples/rest_datasphere_search.py",
        "rest/examples/rest_10dlc_registration.py",
    ),
    api=("signalwire.rest.RestClient", "signalwire.rest.SignalWireRestError"),
    related=("relay", "swml", "deploy"),
    live="rest",
)

_SEARCH = Topic(
    name="search",
    title="Search: knowledge bases for agents",
    summary="Build document indexes with sw-search and let agents search them",
    body="""\
Build an index from documents, then give an agent a tool that searches it.

```bash
pip install "signalwire-sdk[search]"
sw-search ./docs --output knowledge.swsearch
sw-search search knowledge.swsearch "how do I reset my password"
```

```python
self.add_skill("native_vector_search", {
    "tool_name": "search_knowledge",
    "description": "Search the product documentation",
    "index_file": "knowledge.swsearch",
})
```

- A `.swsearch` file is a portable SQLite index. For a shared index, use
  `--backend pgvector`, or run a search service and point the skill's
  `remote_url` at it.
- The `search` extra builds and searches indexes of text and Markdown.
  `search-full` adds PDF, Word, Excel, PowerPoint and other formats,
  `search-nlp` adds spaCy, `pgvector` adds PostgreSQL, and `search-all` has
  all of them.
- Build and query with the same embedding model.
""",
    docs=(
        ("docs/search_overview.md", "How search works, and which pieces to use"),
        ("docs/search_indexing.md", "Building indexes: sources, chunking, models"),
        ("docs/search_integration.md", "Adding search to an agent"),
        (
            "docs/search_deployment.md",
            "Search services, pgvector and production setups",
        ),
        ("docs/search_troubleshooting.md", "Fixing common search problems"),
    ),
    examples=(
        "examples/sigmond_simple.py",
        "examples/sigmond_native_search.py",
        "examples/sigmond_remote_search.py",
        "examples/pgvector_search_agent.py",
        "examples/search_with_custom_formatter.py",
        "examples/search_server_standalone.py",
    ),
    api=(
        "signalwire.search.IndexBuilder",
        "signalwire.search.SearchEngine",
        "signalwire.search.SearchService",
    ),
    related=("skills", "tutorials"),
)

_LIVEWIRE = Topic(
    name="livewire",
    title="LiveWire: LiveKit Agents code on SignalWire",
    summary="Run agents written against the LiveKit Agents API on SignalWire",
    body="""\
`signalwire.livewire` offers the LiveKit Agents API (`Agent`, `AgentSession`,
`function_tool`, `run_app` and friends), so LiveKit agent code can run on
SignalWire with changed imports. SignalWire's platform runs speech
recognition, the LLM and text-to-speech, so the speech and model plugin
classes are there for compatibility.
""",
    docs=(
        ("livewire/README.md", "What LiveWire supports"),
        ("livewire/docs/migration-guide.md", "Moving a LiveKit agent to LiveWire"),
    ),
    examples=(
        "livewire/examples/livewire_basic_agent.py",
        "livewire/examples/livewire_multi_tool.py",
        "livewire/examples/livewire_handoff.py",
    ),
    api=(
        "signalwire.livewire.Agent",
        "signalwire.livewire.AgentSession",
        "signalwire.livewire.function_tool",
        "signalwire.livewire.run_app",
    ),
    related=("agents",),
)

_MCP = Topic(
    name="mcp",
    title="MCP: Model Context Protocol",
    summary="Expose agent tools over MCP, call MCP servers from agents, and the MCP gateway",
    body="""\
- An agent as an MCP server: `enable_mcp_server()` adds an `/mcp` endpoint
  that offers the agent's tools to MCP clients. It requires the agent's basic
  auth credentials.
- MCP servers as an agent's tools: `add_mcp_server(url, headers=...)` lets the
  platform discover and call a remote MCP server's tools during the call.
- MCP servers that run locally: the `mcp_gateway` skill and the `mcp-gateway`
  service bridge them to SWAIG tools.
""",
    docs=(
        ("docs/mcp_integration.md", "The /mcp endpoint and add_mcp_server()"),
        ("docs/mcp_gateway_reference.md", "The MCP gateway service and skill"),
        ("mcp_gateway/README.md", "Running the gateway, including with Docker"),
        ("mcp/swml-schema-search/README.md", "An MCP server for the SWML schema"),
    ),
    examples=("examples/mcp_agent.py", "examples/mcp_gateway_demo.py"),
    api=(
        "signalwire.AgentBase.enable_mcp_server",
        "signalwire.AgentBase.add_mcp_server",
    ),
    related=("tools", "skills"),
)

_CHAT = Topic(
    name="chat",
    title="AI chat gateway and client",
    summary="Browser text chat with an agent, without exposing the project token",
    body="""\
A chat widget in a web page can't hold the project's API token. The AI chat
gateway runs on your server, holds the token, and gives the browser only a
publishable key. `AIChatClient` is the Python client for the chat service.
""",
    docs=(
        ("docs/ai_chat_gateway.md", "Setting up the gateway, keys and the chat client"),
    ),
    api=("signalwire.AIChatClient",),
    related=("agents", "security"),
)

_BEDROCK = Topic(
    name="bedrock",
    title="Amazon Bedrock agents",
    summary="Agents that use Amazon Bedrock's speech-to-speech model",
    body="""\
`BedrockAgent` is an `AgentBase` that renders an Amazon Bedrock prompt
instead of the standard AI verb. Prompts, tools, skills and contexts work the
same way. `set_inference_params()` sets `temperature`, `top_p` and
`max_tokens`, and `set_voice()` takes one of the voices Bedrock offers.
""",
    docs=(("docs/bedrock_agent.md", "BedrockAgent's options and differences"),),
    examples=(
        "examples/bedrock_agent_run.py",
        "examples/bedrock_with_skills.py",
        "examples/bedrock_server_test.py",
        "examples/bedrock_agent_test.py",
    ),
    api=("signalwire.BedrockAgent", "signalwire.BedrockAgent.set_inference_params"),
    related=("agents",),
)

_DEPLOY = Topic(
    name="deploy",
    title="Deploying agents",
    summary="Servers, serverless platforms, containers, public URLs and TLS",
    body="""\
- `run()` works out where it's running. As a plain process or in a container,
  it starts a web server. On AWS Lambda, Google Cloud Functions, Azure
  Functions or CGI, it handles the platform's event.
- SignalWire calls back to the URLs in the agent's SWML. Behind a proxy,
  load balancer or tunnel, set `SWML_PROXY_URL_BASE` to the public base URL.
- Serve TLS directly with `SWML_SSL_ENABLED`, `SWML_SSL_CERT_PATH` and
  `SWML_SSL_KEY_PATH`, or terminate it in front of the agent.
- Run several agents in one process with `AgentServer`.
- `sw-agent-init` creates a project for a local server or a cloud function,
  and `sw-agent-dokku` deploys to Dokku.
- With more than one replica, set `SIGNALWIRE_SWAIG_SECRET` to the same value
  on each, so a tool token minted by one validates on another.
""",
    docs=(
        (
            "docs/cloud_functions_guide.md",
            "Lambda, Google Cloud Functions and Azure Functions",
        ),
        ("docs/configuration.md", "Config files and environment variables"),
        ("docs/security.md", "Auth, signatures, tokens and TLS in production"),
        ("docs/web_service.md", "Serving static files alongside agents"),
    ),
    examples=(
        "examples/lambda_agent.py",
        "examples/kubernetes_ready_agent.py",
        "examples/Dockerfile.k8s",
        "examples/k8s-deployment.yaml",
        "examples/Dockerfile.flexible",
        "examples/multi_agent_server.py",
    ),
    api=(
        "signalwire.AgentBase.run",
        "signalwire.AgentServer",
        "signalwire.AgentBase.get_app",
    ),
    related=("security", "config", "testing"),
)

_SECURITY = Topic(
    name="security",
    title="Security",
    summary="Basic auth, webhook signatures, tool tokens and URL-fetch protection",
    body="""\
- Basic auth protects every endpoint except the `/health` and `/ready`
  probes. Set `SWML_BASIC_AUTH_USER` and `SWML_BASIC_AUTH_PASSWORD`, or let the
  agent generate credentials.
- Webhook signatures: with a `signing_key` (or `SIGNALWIRE_SIGNING_KEY`), every
  POST must carry a valid SignalWire signature. That covers SignalWire's
  requests for the SWML document, its tool calls and its summaries. A GET for
  the SWML document needs only basic auth.
- Tool tokens: a secure tool runs only with the token minted into that call's
  SWML. `swaig_secret` (or `SIGNALWIRE_SWAIG_SECRET`) keeps tokens valid across
  replicas and restarts.
- The spider and web_search skills, which fetch URLs that callers and search
  results supply, refuse private and internal addresses, redirects included.
  `SWML_ALLOW_PRIVATE_URLS` allows them.
- Security is also a design question: what the model can see and request, and
  what the handlers enforce (`sw-pydocs pgi`).
""",
    docs=(
        ("docs/security.md", "Every security setting and what it protects"),
        ("docs/pgi_agent_guide.md", "Keeping authority in code, not in the model"),
    ),
    api=("signalwire.AgentBase", "signalwire.AgentBase.get_basic_auth_credentials"),
    related=("deploy", "config", "pgi", "tools"),
)

_CONFIG = Topic(
    name="config",
    title="Configuration and environment variables",
    summary="Config files, precedence, and the SDK's environment variables",
    body="""\
Settings come from constructor arguments, then a config file
(`config_file=...`), then environment variables, then defaults, in that order
of precedence.
""",
    docs=(
        ("docs/configuration.md", "Config file format and lookup"),
        ("docs/architecture.md", "The configuration section lists the main variables"),
        ("docs/security.md", "Security-related settings"),
    ),
    related=("deploy", "security"),
    live="env",
)

_TESTING = Topic(
    name="testing",
    title="Testing agents",
    summary="Test tools and SWML locally with swaig-test, and in unit tests",
    body="""\
```bash
swaig-test agent.py --list-tools                  # the tools the agent defines
swaig-test agent.py --dump-swml                   # the SWML document it serves
swaig-test agent.py --exec lookup_order --order_id 1234
swaig-test agent.py --simulate-serverless lambda --dump-swml
swaig-test agent.py --verbose --exec lookup_order --order_id 1234  # with logs
```

- Files with several agents: pick one with `--route` or `--agent-class`.
- In unit tests, construct the agent and call its handlers as methods, or
  test your domain code directly. Keep business rules in plain functions so
  they're testable without the SDK.
- A local test doesn't prove the voice path. Place real calls before
  production.
""",
    docs=(
        ("docs/cli_guide.md", "swaig-test's options and simulation"),
        ("docs/pgi_agent_guide.md", "Testing levels and adversarial scenarios"),
        (
            "tutorial/full-guardrails-agent/tutorial/10-testing-and-running.md",
            "Testing a complete agent, step by step",
        ),
    ),
    examples=("examples/README.md",),
    related=("cli", "tools", "datamap"),
)

_CLI = Topic(
    name="cli",
    title="Command-line tools",
    summary="The commands the SDK installs",
    body="""\
Each command takes `--help`. `swaig-test` and `sw-search` are documented in
the CLI guide.
""",
    docs=(("docs/cli_guide.md", "swaig-test, sw-search and the other commands"),),
    related=("testing", "search", "deploy"),
    live="cli",
)

_TUTORIALS = Topic(
    name="tutorials",
    title="Tutorials",
    summary="Step-by-step lessons, from a first agent to a production-shaped one",
    body="""\
- Fred (`tutorial/fred/`): a first agent that searches Wikipedia, with a
  skill, custom functions, testing and Docker. Start here if SignalWire is
  new.
- PC Builder Pro (`tutorial/multi_agents/`): sales and support agents with
  knowledge bases built by `sw-search`, several agents on one server, and
  extending agents.
- Penny (`tutorial/full-guardrails-agent/`): a reservation line built so the
  model can't exceed its authority: rules in code, per-step tools, a
  verification gate, and tests. Read it before building an agent that takes
  real actions.
""",
    docs=(
        ("tutorial/fred/tutorial/README.md", "Fred: a first agent"),
        (
            "tutorial/multi_agents/README.md",
            "PC Builder Pro: knowledge bases and multiple agents",
        ),
        (
            "tutorial/full-guardrails-agent/tutorial/README.md",
            "Penny: a guarded, tested agent",
        ),
    ),
    related=("quickstart", "pgi", "search"),
)

_PGI = Topic(
    name="pgi",
    title="Designing agents that stay within their rules (PGI)",
    summary="What the model decides, what code enforces: read before building a real agent",
    body="""\
Programmatically Governed Inference (PGI): program what the model can see and
request at each stage, while software stays responsible for what actually
happens. The model interprets language and picks from the tools you expose.
Your code owns identity, authorization, business rules, state changes and
side effects.

- A tool call is a request, not an authorization. Check it in the handler.
- Expose only the tools the current step needs, and set them on every step.
- Move between steps from code (`swml_change_step()`) when a check must pass
  first. A prompt, a step's criteria or a model-supplied `approved=True` is
  never the only enforcement.
- `global_data` is session data, not a database. Keep per-caller state off the
  shared agent instance.
- A tool's response is context for the model, not speech.
- The substitution test: if the model were replaced by a scripted UI, would
  the backend still enforce the same rules?

The guide has the full rules, a capability index, a tested reference
implementation, and testing and review checklists.
""",
    docs=(
        ("docs/pgi_agent_guide.md", "The PGI implementation guide for coding agents"),
        (
            "docs/programmatically_governed_inference.md",
            "The discipline itself: why the model gets no authority, and the four constraint layers",
        ),
        (
            "docs/developer_pain_points.md",
            "Problems P01-P36 that the guide cites, what the SDK and platform provide, and what stays yours",
        ),
        (
            "tutorial/full-guardrails-agent/tutorial/README.md",
            "A complete agent built this way, lesson by lesson",
        ),
    ),
    api=(
        "signalwire.Step.set_functions",
        "signalwire.FunctionResult.swml_change_step",
        "signalwire.FunctionResult",
    ),
    related=("tools", "contexts", "security", "testing", "tutorials"),
)

TOPICS: tuple[Topic, ...] = (
    _QUICKSTART,
    _AGENTS,
    _PROMPTS,
    _TOOLS,
    _DATAMAP,
    _CONTEXTS,
    _SKILLS,
    _PREFABS,
    _PGI,
    _SWML,
    _RELAY,
    _REST,
    _SEARCH,
    _LIVEWIRE,
    _MCP,
    _CHAT,
    _BEDROCK,
    _DEPLOY,
    _SECURITY,
    _CONFIG,
    _TESTING,
    _CLI,
    _TUTORIALS,
)

TOPICS_BY_NAME = {topic.name: topic for topic in TOPICS}

# How the index groups the topics
TOPIC_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Build AI agents",
        (
            "quickstart",
            "agents",
            "prompts",
            "tools",
            "datamap",
            "contexts",
            "skills",
            "prefabs",
            "pgi",
        ),
    ),
    ("Call control and APIs", ("swml", "relay", "rest")),
    ("Knowledge and integrations", ("search", "livewire", "mcp", "chat", "bedrock")),
    ("Run and test", ("deploy", "security", "config", "testing", "cli")),
    ("Learn", ("tutorials",)),
)

# The index's "start here" rows: (what you want to do, the topics to read)
START_HERE: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Answer calls with an AI agent", ("quickstart", "agents")),
    ("Design an agent that takes real actions safely", ("pgi",)),
    ("Give an agent tools", ("tools", "datamap", "skills")),
    ("Build a multi-step workflow", ("contexts",)),
    ("Add a knowledge base", ("search",)),
    ("Control live calls from code", ("relay",)),
    ("Manage numbers and resources", ("rest",)),
    ("Route calls without AI", ("swml",)),
    ("Deploy", ("deploy", "security")),
    ("Test without a phone call", ("testing",)),
    ("Learn step by step", ("tutorials",)),
)

# The index's short list of rules that prevent the most common mistakes
RULES_OF_THUMB: tuple[str, ...] = (
    "Check names and signatures with `sw-pydocs api` instead of recalling them: "
    "the API changes between versions.",
    "A tool call is a request from the model, not an authorization. Enforce "
    "identity, state and business rules in the handler.",
    "A tool's response is context for the model, not speech. Keep facts "
    "(`tool_result`) apart from instructions (`tool_prompt`).",
    "Set the tools on every step of a workflow, and move between steps from code "
    "when a check must pass first.",
    "Keep per-caller state off the shared agent instance. `global_data` lasts for "
    "the call; anything durable belongs in your own storage.",
    "Test with `swaig-test` before a live call, and with a live call before "
    "production.",
)
