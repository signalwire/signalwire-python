# Changelog

## [3.4.0] - 2026-08-24

Covers everything landed since 3.2.0. 3.3.0 was never tagged or documented, so
its contents are folded in here.

### New Features
- AI Chat: added `signalwire.ai_chat` — `AIChatClient`, an async client for the
  AI Chat service (`POST https://{space}.signalwire.com/api/ai/chat`). HTTP
  Basic `project:api_token` with the space in the hostname and a JSON-RPC body
  carrying pure payload; identity never rides in the body. Methods:
  `create_conversation`, `chat`, `end`, `delete`, `log`, `summarize`, with
  JSON-RPC error codes mapped to typed exceptions.
- AI Chat: added `ChatGateway`, a back-for-frontend so browser widgets never
  hold a chat-service token. The page talks to your host, your host holds the
  credential, and the conversation id the page carries is an HMAC-signed handle
  it cannot forge or repoint at someone else's conversation. Four methods:
  `start` (creates, and can post the opening turn so the agent greets first),
  `chat`, `log` (tab-scoped resume replays the transcript), `end`.
- AI Chat: `ChatGateway` now reports `conversation_timeout` on create, `start`
  and `log`. A conversation idle past its timeout is ended server-side and the
  next message quietly opens a different one, with the transcript above it
  still reading as continuous; the browser cannot see that coming from the
  JSON-RPC result alone, and the gateway is the only component that knows.
- AI Chat: added `HandoffRouter` (`ai_chat/handoff.py`) for the `/handoff`,
  `/escalate` and `/say` routes the SignalWire address widget already targets
  against a `ChatGateway` URL. Owns the wire contract only — routes, nonce,
  ordering guarantee, spend guards.
- Agent: capability declaration and post-prompt normalization.
- SWML schema: typed `ai_sidecar` verb and `RingbackConfig`, merged to 169
  `$defs` while preserving the SDK-side `x-sdk-*` annotations.

### FunctionResult
- `response` may now be an object separating outcome from instruction:
  `{"tool_result": ..., "tool_prompt": ...}`, via `set_tool_response()` or the
  new `tool_result=` / `tool_prompt=` constructor arguments. `tool_result` is
  what the tool DID, for the model to reason from; `tool_prompt` is what the
  model should SAY. Splitting them stops a status line being read aloud and
  stops an instruction being mistaken for data. The plain string form is
  unchanged.
- `hold()` takes an optional prompt as its first argument and sets `response`
  and `post_process` itself. The hold action carries no prompt of its own, and
  during hold speech detection is paused and the agent will not respond, so
  anything the caller needs to hear has to be said before the action lands.
  An int in that position is still treated as the timeout, so `hold(120)` and
  `hold(timeout=120)` are unchanged.
- `hold()` gained `step` and `timeout_step`, which route the call to a chosen
  step when the hold ends — `step` when it is released early, `timeout_step`
  when it expires. These are deferred: they fire when the hold actually ends,
  unlike `swml_change_step()`, which applies immediately and would move the
  caller before the hold begins. Omitting both emits the bare integer form.
- `rpc_ai_message()` accepts `global_data`, merged into the target call's
  `global_data`, and `message_text` is now optional. Added
  `rpc_ai_global_data()` for the data-only case. A message competes for
  attention with everything else arriving on that turn; data is silent until a
  prompt expands it with `${global_data.key}`, which makes it the better
  channel for content a later step needs to speak.
- Docs: corrected the class docstring's description of `response`. It said
  "Text the AI should say back to the user", which reads as a script; the SWML
  schema defines it as "a static response text or message returned to the AI
  agent's context". It is an instruction the model reads and interprets, not
  speech played to the caller. Documented the second-person form and when
  `post_process` is required.

### Fixes
- Search: `count` truncates results instead of reordering them. The candidate
  pool was `count * 3` and every stage of `_process_candidates` reads the whole
  pool, so a smaller pool could drop a document's keyword hit, cost it the
  agreement boost, and sink it — retrieval quality depended on how many results
  you asked for.
- Search: subsection chunks are retrievable.
- REST/docs: corrected the documented `live_transcribe` call shape. The docs
  showed `live_transcribe(call_id, action="start", lang="en")`, but the
  generated signature takes `action` as a keyword-only TypedDict union and has
  no `lang`/`from_lang`/`to_lang` parameters, so copying the documented call
  raised `TypeError`.

### Notes for upgraders
- `rpc_ai_message()` raises `ValueError` when given neither `message_text` nor
  `global_data`. Positional callers are unaffected; a caller previously passing
  `message_text=None` produced a malformed RPC and now gets an exception.

## [3.2.0] - 2026-07-14

### New Features
- REST: added the `client.messages` resource for the native messaging API
  (`/api/messaging`): `create` sends an SMS/MMS message
  (`POST /api/messaging/messages`) and `update` redacts a previously sent
  message's body (`PATCH /api/messaging/messages/{message_id}`). This is the
  plural send/redact resource, distinct from the singular message *logs*
  reachable via `client.logs.messages`.

## [3.1.0] - 2026-07-14

### New Features
- REST: added the `client.projects` CRUD resource for the project-management
  API (`/api/projects`), including `rotate_signing_key`.

## [3.0.2] - 2026-07-11

- REST: `ReadResource.paginate()` wires the `PaginatedIterator` into every list
  resource so callers can page through all results (follows `links.next`).
- Docs: corrected env-var names and documented previously-undocumented knobs
  (including the proxy/SSRF trust toggles);
  fixed stale skill/namespace counts and phantom method references.

## [3.0.1] - 2026-04-12

- Update install instructions and PyPI URLs to use `signalwire-sdk`

## [3.0.0] - 2026-04-12

- Version bump

## [1.1.0] - 2026-03-17

- Version bump

## [1.0.22] - 2026-03-17

- Version bump

## [1.0.19] - 2026-02-19

### New Features
- Add full JSON Schema validation with `jsonschema-rs`
  - `SchemaValidationError` exception on validation failures
  - Option to disable schema validation
- Add RPC action methods for cross-call communication
- Add gather steps for structured data collection in contexts
- Add `replace` action for step history manipulation
- Add `add_dynamic_hints()` and `clear_dynamic_hints()` to `SwaigFunctionResult`
- Add `Context.get_step()` and `ContextBuilder.get_context()`, deep-copy contexts per call
- Add `remove_step()`, `move_step()`, and `clear_sections()` to Context/Step
- Add inline content kwargs to `Context.add_step()`
- Add `skip_prompt` flag to `SkillBase` for suppressing default POM injection
- Add namespaced `global_data` helpers to `SkillBase`
- Auto-hide SWAIG functions once gather questions are completed

### New Skills
- Add `google_maps` skill for address validation and route computation
- Add `info_gatherer` skill for structured information collection
- Add `claude_skills` skill for loading Claude Code SKILL.md files

### Bug Fixes
- Fix ~60 bugs found in comprehensive security and code audit
- Fix bug with invalid token handling
- Fix spurious error log when SWAIG function is called with empty raw arguments
- Fix `set_global_data` to merge without clobbering existing keys
- Remove deprecated `pkg_resources` usage

### Testing
- Expand test coverage from 52% to 78% with 1,820 new tests
- Fix all 145 pre-existing test failures

## [1.0.18] - 2026-01-26

- Fix `record_call()` default timeouts causing silent recording failures
  - Change `initial_timeout` and `end_silence_timeout` defaults from `0.0` to `None`
  - Timeout parameters now only included in SWML when explicitly set
- Add SWML schema search MCP server (`mcp/swml-schema-search/`)
- Fix bug in vector search scoring for pgvector backend
- Fix `fetch_conversation` response handling in post_prompt endpoint

## [1.0.17] - 2025-12-21

- Add GitHub Actions for automated PyPI publishing
  - `publish-dev.yml`: Publishes dev versions (X.Y.Z.devN) on push to main
  - `publish-release.yml`: Publishes stable releases on version tags (v*)

## [1.0.16] - 2025-12-11

- Support PORT environment variable for server port configuration
- Add Slack notification support to `sw-agent-dokku` deploy workflow template

## [1.0.15] - 2025-12-09

- Fix catch-all handler overshadowing custom routes in `sw-agent-dokku` generated apps
- Fix static files and routes without trailing slash for gunicorn compatibility
- Add tests for AgentServer custom route handling

## [1.0.14] - 2025-12-09

- Add WebRTC calling support to `sw-agent-dokku` generated apps
  - Dynamic token generation via `/get_token` endpoint (24-hour expiration)
  - `/get_credentials` endpoint for curl examples in web UI
  - `/get_resource_info` endpoint for SignalWire dashboard integration
  - Auto-create/update SWML handlers on startup
  - Enhanced web UI with WebRTC calling controls and audio settings
- Add SignalWire credentials to generated `app.json` and `.env.example` templates
- Add `requests` dependency to generated requirements.txt

## [1.0.13] - 2025-12-09

- Add `sw-agent-dokku` CLI for scaffolding Dokku deployments
  - Simple mode: generates Procfile, runtime.txt, requirements.txt, CHECKS
  - CI/CD mode: adds GitHub Actions workflows for auto-deployment
  - Web interface option: `--web` flag for static file serving
- Register `/health` and `/ready` endpoints in `AgentServer.__init__()` for gunicorn compatibility
- Fix static files auth by using `AgentServer.serve_static_files()` in templates

## [1.0.12] - 2025-12-08

- Export `SkillBase` from `signalwire_agents.skills` for convenience imports

## [1.0.11] - 2025-12-06

- Add `mcp-gateway` as installed CLI command (`pip install "signalwire-agents[mcp-gateway]"`)
- Move MCP Gateway core files into `signalwire_agents/mcp_gateway/` package
- Add flask and flask-limiter as optional `[mcp-gateway]` dependencies
- Add cloud function support to `sw-agent-init` CLI tool
- Fix `sw-agent-init` to generate swaig-test compatible app.py
- Add comprehensive test script for `sw-agent-init`

## [1.0.10] - 2025-11-30

- Fix Google Cloud Functions /swaig endpoint to support function name in request body
- Add URL detection for Google Cloud Functions to generate correct webhook URLs in SWML

## [1.0.9] - 2025-11-30

- Add Azure Functions serverless support with proper URL detection for webhook URLs
- Add Google Cloud Functions serverless support
- Fix Flask header iteration bug in Google Cloud Functions auth check (use .get() instead of iteration)
- Fix Azure Functions auth check to use .get() method for headers
- Improve serverless mixin to properly detect base URL from request for correct SWML webhook URLs

## [1.0.8] - 2025-11-29

- Fix tool definitions in docs to include parameters
- Add sw-agent-init CLI tool and man pages for all CLI tools

## [1.0.7] - 2025-11-27

- Version bump

## [1.0.6] - 2025-11-27

- Update documentation for contexts, datamap, API reference, SWAIG actions, and function results
- Add comprehensive example testing suite (tests/test_examples.py)
- Add static file serving example

## [1.0.5] - 2025-11-26

- Add setuptools version upper bound (<81) to fix compatibility issues

## [1.0.4] - 2025-11-26

- Add call flow verb insertion API for customizing SWML call flow
  - `add_pre_answer_verb()` - Add verbs before answering (ringback, screening, routing)
  - `add_post_answer_verb()` - Add verbs after answer, before AI (welcome messages, disclaimers)
  - `add_post_ai_verb()` - Add verbs after AI ends (cleanup, transfers, logging)
  - `add_answer_verb()` - Configure the answer verb (max_duration, etc.)
  - `clear_pre_answer_verbs()`, `clear_post_answer_verbs()`, `clear_post_ai_verbs()`
- Fix `auto_answer=False` constructor parameter to actually skip the answer verb
- Add validation for pre-answer safe verbs with helpful warnings

## [1.0.3] - 2025-11-24

- Version bump

## [1.0.2] - 2025-11-24

- Version bump

## [1.0.1] - 2025-11-23

- Version bump

## [1.0.0] - 2025-11-22

- Version bump

