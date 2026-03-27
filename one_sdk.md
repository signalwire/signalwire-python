# Response: One SDK, Every Platform

## The Doc is Right — and We Already Started Building This

The One SDK vision describes what our Agents SDK fleet already does in several areas, and exposes where it falls short. Having just ported the SDK to 7 languages (Python, TypeScript, Go, Ruby, Perl, Java, C++) and built a porting guide to keep them in sync, here's a concrete assessment of where the fleet stands relative to this vision and what needs to change.

---

## Where We Already Follow the Design Language

### Consistent Entity Names Across All 7 SDKs

| Concept | Python | TypeScript | Go | Ruby | Perl | Java | C++ |
|---------|--------|-----------|-----|------|------|------|-----|
| Agent | `AgentBase` | `AgentBase` | `AgentBase` | `AgentBase` | `AgentBase` | `AgentBase` | `AgentBase` |
| Tool result | `SwaigFunctionResult` | `SwaigFunctionResult` | `FunctionResult` | `FunctionResult` | `FunctionResult` | `FunctionResult` | `FunctionResult` |
| Server-side tool | `DataMap` | `DataMap` | `DataMap` | `DataMap` | `DataMap` | `DataMap` | `DataMap` |
| Workflow | `ContextBuilder` | `ContextBuilder` | `ContextBuilder` | `ContextBuilder` | `ContextBuilder` | `ContextBuilder` | `ContextBuilder` |
| Multi-agent | `AgentServer` | `AgentServer` | `AgentServer` | `AgentServer` | `AgentServer` | `AgentServer` | `AgentServer` |
| Skills | `add_skill()` | `addSkill()` | `AddSkill()` | `add_skill()` | `add_skill()` | `addSkill()` | `add_skill()` |
| RELAY call | `Call` | `Call` | `Call` | `Call` | `Call` | `Call` | `Call` |
| REST client | `SignalWireClient` | `SignalWireClient` | `SignalWireClient` | `SignalWireClient` | `SignalWireClient` | `SignalWireClient` | `SignalWireClient` |

The entity names are already consistent. A developer who knows the Python SDK recognizes the Go SDK immediately. This is the design language principle working.

### Same Action Names

Every SDK uses the same 40+ action names on FunctionResult: `connect`, `hangup`, `hold`, `say`, `play_background_file`, `record_call`, `send_sms`, `tap`, `sip_refer`, `join_conference`, `update_global_data`, `switch_context`, `execute_rpc`. The only variation is casing convention per language (snake_case in Python/Ruby/Perl/C++, camelCase in TypeScript/Java/Go).

### Same Parameter Shapes

Every SDK generates identical SWML JSON. The `set_param("realtime", {"voice": "verse", "vad_type": "server_vad"})` call produces the same JSON structure in every language. The parameter shapes are the design language — the SWML schema is the shared specification.

### Same Skills System

All 18 skills exist in every SDK with the same names, same tool names, same parameter schemas. `add_skill("datetime")` works identically across all 7 languages.

### Same REST Namespaces

All 21 REST API namespaces (Fabric, Calling, PhoneNumbers, Datasphere, Video, Compat, etc.) exist in every SDK with the same method names and paths.

### Platform-Native Idioms

Each SDK uses its platform's natural patterns:

| Pattern | Python | TypeScript | Go | Ruby | Java | Perl | C++ |
|---------|--------|-----------|-----|------|------|------|-----|
| Tool handler | `@tool()` decorator | `defineTool({})` | `DefineTool(ToolDefinition{})` | `define_tool() { block }` | `define_tool(handler => sub {})` | `defineTool(name, handler)` | lambda |
| Verb methods | `__getattr__` | `method_missing` via generated | explicit methods | `method_missing` | `AUTOLOAD` | explicit methods | explicit methods |
| HTTP server | FastAPI | Hono | net/http | Rack/WEBrick | Plack/PSGI | com.sun.net.httpserver | cpp-httplib |
| Async | asyncio | async/await | goroutines | threads | threads | threads/AnyEvent | std::thread |
| Framework mount | FastAPI router | Hono middleware | http.Handler | `mount rack_app` | PSGI app | Servlet | — |

This is exactly the Apple principle: same family, different execution model per platform.

---

## Where We Deviate from the Vision

### 1. No Unified Entry Point

The doc proposes `new SignalWire({ project, token })` as the branded entry point. Our SDKs have **three separate entry points**:

- `AgentBase` for AI agents (webhook/SWML mode)
- `RelayClient` for real-time call control (WebSocket mode)
- `SignalWireClient` for REST API operations

These are three different classes with three different constructors. A developer doing AI agents never touches RelayClient. A developer doing call control never touches AgentBase. They don't feel like one SDK.

**To align with the vision:** A single `SignalWire` entry point that exposes all three as namespaces:
```python
sw = SignalWire(project=PROJECT, token=TOKEN)
sw.agents  # → AgentBase functionality
sw.voice   # → Relay call control
sw.rest    # → REST API
```

### 2. Transport is NOT Configuration — It's a Different SDK

This is the biggest gap. The One SDK doc's central thesis is "transport as configuration." Our SDKs have transport baked in:

- **AgentBase** = webhook mode (always generates SWML, always serves HTTP)
- **RelayClient** = WebSocket mode (always connects via Blade/JSON-RPC)

You can't switch between them by changing a config value. They have completely different APIs. AgentBase has `define_tool()`, `prompt_add_section()`, `render_swml()`. RelayClient has `call.play()`, `call.record()`, `call.collect()`.

**To align with the vision:** The handler code should be transport-agnostic. When you write `call.play(...)`, the SDK decides whether to emit a SWML `play` verb or send a Relay `calling.play` command based on the transport config.

This is achievable because SWML verbs and Relay methods are **almost 1:1**:

| Action | SWML Verb | Relay Method |
|--------|-----------|-------------|
| Answer | `{"answer": {}}` | `calling.answer` |
| Play | `{"play": {"url": "..."}}` | `calling.play` |
| Record | `{"record": {...}}` | `calling.record` |
| Connect | `{"connect": {"to": "..."}}` | `calling.connect` |
| AI | `{"ai": {"prompt": "..."}}` | `calling.ai` |

The mapping exists. What doesn't exist is a unified API layer that abstracts over it.

### 3. Naming Inconsistency: FunctionResult

Python calls it `SwaigFunctionResult`. The other 6 SDKs call it `FunctionResult`. The `Swaig` prefix leaks an internal protocol name that developers don't need to know. The One SDK doc specifically says: "Internal protocols are implementation details."

**To align:** Standardize on `FunctionResult` everywhere (which 6 of 7 SDKs already do).

### 4. Naming Inconsistency: Method Casing Beyond Language Convention

Some names vary beyond what language convention requires:

| Method | Python | Go | Ruby |
|--------|--------|----|------|
| Prompt | `set_prompt_text` | `SetPromptText` | `set_prompt_text` |
| Tool | `define_tool` | `DefineTool` | `define_tool` |
| Skill | `add_skill` | `AddSkill` | `add_skill` |

These are fine — they follow each language's naming convention. But:

| Concept | Python | TypeScript |
|---------|--------|-----------|
| SWML verb methods | `agent.play()`, `agent.answer()` | `agent.play()`, `agent.answer()` |
| Tool execution | `on_function_call(name, args, raw_data)` | `onFunctionCall(name, args, rawData)` |

These **are** consistent. The fleet is well-aligned on naming.

### 5. The AI Agent Layer Doesn't Map to the One SDK Patterns

The One SDK doc shows `call.answer()`, `call.prompt()`, `call.connect()` — direct call control. Our AI Agents SDK works differently:

```python
# Our current model: declare, don't command
agent = AgentBase("my-agent")
agent.set_prompt_text("You are a helpful assistant.")
agent.define_tool("get_weather", ...)
agent.run()  # serves SWML, platform calls tools via webhooks
```

vs the One SDK vision:

```python
# One SDK model: handle calls imperatively
client.voice.on_call(async (call) => {
    await call.ai(prompt="You are a helpful assistant.", tools={...})
})
```

Our AgentBase is **declarative** — you configure an agent and it generates SWML. The One SDK is **imperative** — you handle call events in real-time. Both are valid, but they feel very different.

**To align:** The AI agent pattern could work as the webhook-mode implementation of the One SDK's `call.ai()` method. When `transport: 'webhook'`, `call.ai(prompt, tools)` generates the same SWML that AgentBase generates. When `transport: 'websocket'`, it sends `calling.ai` via Relay. Same handler code, different transport.

### 6. No `client.voice` / `client.messaging` Namespacing

The One SDK doc proposes `client.voice` as the namespace. Our SDKs don't have this — RELAY is accessed as `RelayClient` directly, REST as `SignalWireClient` directly. There's no unifying namespace.

---

## What We Got Right That Should Be Preserved

### The Porting Guide IS the Design Specification

The One SDK doc says: "Consistency is maintained through shared design documents, not shared code." We already built this:

- **PORTING_GUIDE.md** — The master specification (1200+ lines)
- **CHECKLIST_TEMPLATE.md** — Every feature as a checkbox
- **SWAIG_FUNCTION_RESULT_REFERENCE.md** — Exact JSON for all 40+ actions
- **SKILLS_MANIFEST.md** — All 18 skills with exact specs
- **RELAY_IMPLEMENTATION_GUIDE.md** — Wire protocol reference
- **rest-apis/*.yaml** — OpenAPI specs for all REST namespaces
- **schema.json** — SWML verb schema (the source of truth for verbs)

This is exactly what the One SDK doc needs but doesn't mention: a specification repo that keeps independent implementations in sync. We have it. It works — we just proved it by porting to 7 languages with consistent APIs.

### The Skills System is the Right Abstraction

`add_skill("datetime")` working identically across 7 languages is a good example of the design language principle. The skills system should survive into the One SDK world.

### SWML as the Webhook Protocol

The One SDK doc says webhook mode should "translate handlers into SWML documents." That's literally what AgentBase does. The entire Agents SDK exists to make SWML generation invisible to the developer. This is already built.

---

## Concrete Recommendations for the Fleet

### Short-term (no breaking changes):

1. **Rename `SwaigFunctionResult` to `FunctionResult`** in Python (the other 6 already use this name). Keep `SwaigFunctionResult` as an alias for backwards compat.

2. **Add a unified `SignalWire` entry point** as a convenience wrapper in each SDK:
   ```python
   sw = SignalWire(project="...", token="...", space="...")
   sw.agents   # returns AgentBase-like interface
   sw.relay    # returns RelayClient
   sw.rest     # returns SignalWireClient
   ```

3. **Document the mapping between SWML verbs and Relay methods** explicitly, so developers see they're the same operations over different transports.

### Medium-term (new APIs, old ones still work):

4. **Add a `call.ai()` method to the Relay Call object** that takes the same parameters as AgentBase's AI verb config. This makes the Relay client capable of starting AI agents imperatively, matching the One SDK pattern.

5. **Add transport config to AgentBase** so it can optionally use Relay instead of HTTP/SWML for tool dispatch. `AgentBase(transport='relay')` would connect to Relay and dispatch tools over WebSocket instead of webhooks.

### Long-term (One SDK architecture):

6. **Build the unified handler layer** where `call.play()`, `call.record()`, `call.ai()` work regardless of transport. This is the core of the One SDK. The implementations exist (SWML generation + Relay commands) — the work is the abstraction layer over both.

---

## Summary

Our 7-SDK fleet is **80% aligned** with the One SDK vision already:
- Same entity names, action names, parameter shapes
- Platform-native idioms per language
- Shared specification (porting guide + schema + manifests) not shared code
- Skills, prefabs, DataMap, contexts all consistent

The **20% gap** is:
- No unified entry point (`new SignalWire()`)
- Transport is a different SDK, not a config value
- The AI agent (declarative) and call control (imperative) patterns don't share an API surface
- `SwaigFunctionResult` naming in Python

The path from where we are to the One SDK vision is clear and incremental. The hardest part — getting 7 implementations to agree on names, shapes, and behaviors — is already done.
