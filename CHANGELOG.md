# Changelog

## [Unreleased]

Webhook signatures and SWAIG tokens are now enforced on every path, including
serverless. Skills that fetch URLs no longer reach internal addresses through
redirects, the agent's `/mcp` endpoint requires basic auth, and `async def`
tool handlers run. The package now installs its documentation, and
`sw-pydocs` prints it.

### Added
- `sw-pydocs`: the SDK's documentation for the installed version, for people
  and coding agents. With no arguments it prints an index; `sw-pydocs <topic>`
  covers an area, with the installed docs to read, examples and API names;
  `sw-pydocs api <name>` prints a signature, docstring and members from the
  installed code; and `examples`, `grep`, `show` and `path` find the installed
  files. `python -m signalwire` runs it too.
- The wheel installs the docs, examples and tutorials, under
  `signalwire/_docs/`, so it's about twice as large (1.7 MB).
- `sw-pydocs init` adds a section to a project's `AGENTS.md` that tells coding
  agents to use `sw-pydocs`, and `sw-agent-init` writes it into new projects.
- The package's `llms.txt` lists the installed docs.

### Changed
- Importing `signalwire.cli` no longer imports `swaig-test`, so the SDK's other
  commands start about 0.8 seconds sooner.

### Fixed
- Security: `serve()` (and so `run()`) registered its catch-all route before the
  agent's router, so every request reached the handlers without the webhook
  signature check. With a `signing_key` set, an unsigned `POST` to the SWML,
  SWAIG or post-prompt endpoint was accepted. The router now comes first, and
  the catch-alls in `serve()`, `mount()` and `AgentServer` run the same check
  before dispatching, so the agent's bare route and slash variants such as
  `/agent//swaig` are covered too.
- Security: a `secure=True` SWAIG function ran when the request carried no
  token at all, or a token but no `call_id`; only a wrong token was refused.
  Now a secure function runs only with a valid token for that function and
  call. The token is checked against the agent that runs the function, so a
  secure tool registered by per-call configuration needs its token too.
- Security: routing-callback paths (`register_routing_callback`) render SWML
  like the root, and now need a signature like the root when a `signing_key`
  is set.
- Tokens for a call whose id contains a dot (composed conversation ids such as
  `root.2`) never validated, so that call's secure functions were refused.
- Security: a `POST` to the post-prompt endpoint now needs the token minted
  into the post-prompt URL. It was validated only when present, and processed
  either way. A request whose URL and body name different calls is refused,
  so one call's token can't deliver another call's summary.
- Security: serverless requests (Lambda, CGI, Cloud Functions, Azure Functions,
  and `AgentServer`'s CGI and Lambda modes) never checked signatures or SWAIG
  tokens, and `AgentServer`'s serverless modes didn't check basic auth. They now
  share one request path with the web server's rules: running a function or
  delivering a summary takes a POST, and every POST needs a valid signature
  when a `signing_key` is set, whatever its path.
- Serverless: post-prompt summaries reach `on_summary`, with the same token
  check as on the web server; before, the post-prompt URL was treated as a
  function name and the summary was lost.
- Serverless: SWML is rendered for the call the request names, with per-call
  configuration applied (it sees the request's query and headers), so its
  tokens validate when the call's functions run. Function calls get the same
  per-call configuration, so a tool it registers can run.
  Tool calls on a route other than `/` now reach the function (they failed with
  "Function 'agent/swaig' not found"), as do CGI calls to `/swaig` and Azure
  calls whose URL has a query string. CGI responses now carry a status and
  headers, `AgentServer` passes a function its arguments rather than the whole
  request body, and `AgentServer` serves an agent registered at `/`.
- Serverless signature checks rebuild the public URL the way the web server
  does. Behind trusted forwarded headers the platform's path prefix (a CGI
  script, an Azure function app) is kept, and for API Gateway REST events,
  which lose the query's original encoding, both encodings are tried.
- `get_app()` serves the agent's route without a trailing slash (it answered
  204), and `/agentswaig` is no longer treated as `/agent/swaig`.
- Logging: until something configures logging, SDK loggers printed every
  level, debug included, to stdout. They now write through stdlib logging and
  are silent until `configure_logging()` runs (as `serve()` and `run()` do) or
  the host app configures logging. `swaig-test --verbose` turns them on, and
  `swaig-test --dump-swml --raw` prints clean JSON. Every SDK logger now lives
  under the `signalwire` namespace (`agent_base` is `signalwire.agent_base`),
  so the SDK no longer shares, or reconfigures, a host app's logger that
  happens to have the same name.
- `wikipedia_search` sends a User-Agent; Wikipedia answered 403 without one.
- Security: the spider and web_search skills checked a URL before fetching it,
  then followed redirects, so a public page that redirected to an internal
  address, such as a cloud metadata service, was fetched and returned. A
  hostname whose DNS answer changed between the check and the connection had
  the same effect. They now check every request, redirects included, and
  refuse a connection to a private or internal address. `validate_url()` also
  blocks IPv4-mapped IPv6 addresses such as `::ffff:169.254.169.254`, and the
  unspecified address.
- Security: the agent's `/mcp` endpoint (`enable_mcp_server()`) had no
  authentication, and found none of the agent's tools: `tools/list` was empty
  and `tools/call` answered "Unknown tool". It now requires the agent's basic
  auth credentials, lists and calls the tools the agent runs itself (not
  DataMap or external webhook tools), and awaits `async def` handlers.
- Security: the MCP gateway's sample and generated configurations listen on
  `0.0.0.0` with the published password `changeme`. While that password is in
  use, the gateway now listens on `127.0.0.1` only, and logs a warning.
- Tool handlers defined with `async def` never ran. The SDK returned their
  coroutine, and `/swaig` answered with its repr. `/swaig` now awaits them on
  the request's event loop, and serverless, `swaig-test` and
  `SWAIGFunction.execute()` run them to completion.
- Constructor arguments take precedence over an agent's config file, as
  documented. The file's `service.name` always replaced the `name` passed to
  `AgentBase`, and its route and host replaced a `route="/"` or
  `host="0.0.0.0"` passed on purpose.
- `get_basic_auth_credentials(include_source=True)` reports where the
  credentials came from, recorded when they were resolved. It guessed from
  their values, and credentials passed to the constructor could show as
  generated.
- native_vector_search: logs no longer include the password in `remote_url`,
  and log the caller's query, the tool arguments, and error details that can
  echo the query at DEBUG only. The SWAIG request isn't logged.
- native_vector_search: the pgvector auto-build appended another full copy of
  every chunk on each start, and ignored `overwrite`. It now builds a
  collection only when it doesn't exist, or rebuilds it when `overwrite` is
  set. If it can't tell whether the collection exists, it logs an error and
  doesn't build. `IndexBuilder.build_index()` accepts `overwrite`.
- pgvector: `overwrite` failed on a database with no collections yet.
- Search service: the query cache ignored `similarity_threshold` and
  `language`, so a repeated query with a stricter threshold got the earlier
  results, and it cached the empty results of a failed search. It no longer
  logs the caller's query at INFO on a cache hit.
- Search: both markdown chunkers recorded sibling headings as parent and
  child in a document that starts at `##` or skips a level. Section paths now
  follow each heading's real level. This changes the `section`, `h1`/`h2`,
  `depth:N` tags and `metadata_text` of affected chunks in indexes built from
  now on.
- Search: `SearchIndexMigrator.migrate_pgvector_to_sqlite()` deleted the
  output index, wrote one with no chunks, and reported success. Chunk export
  was never implemented, so it now raises `NotImplementedError` before it
  connects or touches the output path.
- Search: importing `signalwire.search` no longer imports the model stack, so
  `sw-search` starts in about a second instead of 15. `openpyxl` is imported
  only to read an Excel file.
- `sw-search --help` lists every option; it omitted `--backend`,
  `--connection-string`, `--overwrite`, `--output-dir` and `--output-format`.
- `sw-search remote` accepts `--user` and `--password`, and no longer prints
  the endpoint's password in verbose output or errors. Its threshold option is
  `--similarity-threshold`, since higher is stricter; `--distance-threshold`
  still works.
- `swaig-test`: the DataMap simulator accepts a webhook that returns a JSON
  array, arguments the function doesn't declare get a warning, and
  `--aws-api-gateway-id` and `--aws-stage` now simulate an API Gateway URL.
- `BedrockAgent` renders `max_tokens`, `presence_penalty` and
  `frequency_penalty`, and `set_prompt_llm_params()` accepts the settings the
  Bedrock prompt defines. The examples use voices Bedrock offers.
- spider: `follow_robots_txt` is enforced, redirects included. The parameter
  schema's defaults and `extract_type` values now match what the skill does.
- Five skills declared parameter ranges as `minimum`/`maximum`; every built-in
  skill now uses `min`/`max`.
- The SWML schema search MCP server in `mcp/swml-schema-search/` finds
  `schema.json` without `SWML_SCHEMA_PATH`.
- The MCP gateway's Docker image builds and runs, and Compose passes its
  defaults instead of empty strings for unset variables.

### Deprecated
- `keyword_weight` (`SearchEngine.search()`, the pgvector backend,
  native_vector_search and `sw-search --keyword-weight`). It never changed
  ranking, and passing it now warns.
- The `large` model alias, which loads the same model as `base`. Use `base`.
- spider's `concurrent_requests`, which was never used, and the `extract_type`
  values `clean_text`, `full_text`, `html` and `custom`, which work as
  `fast_text` with a warning.

### Removed
- The standalone copies of the MCP gateway service in `mcp_gateway/`
  (`gateway_service.py`, `mcp_manager.py`, `session_manager.py` and
  `requirements.txt`). The Docker image runs the packaged `mcp-gateway`
  command.

### Notes for upgraders
- Calling a secure function directly, for example with `curl`, now needs the
  token from the function's `web_hook_url` in the SWML, fetched with
  `?call_id=<id>`. `swaig-test` is unaffected. SignalWire's own requests
  already carry the token.
- A serverless agent with a `signing_key` now validates signatures. If its
  requests start failing with 403, the platform sees a different URL than the
  one SignalWire called; set `SWML_PROXY_URL_BASE` to the public URL.
- An app that embeds an agent (`get_app()`, `as_router()`) no longer gets SDK
  log output on stdout by default. Configure `logging`, or call
  `signalwire.configure_logging()`.
- SDK logger names gained a `signalwire.` prefix. Code that configured a short
  name such as `logging.getLogger("agent_base")` should use
  `signalwire.agent_base`, or the `signalwire` namespace.
- A serverless function call must be a POST; other methods get 405.
- An MCP client that calls an agent's `/mcp` endpoint must send the agent's
  basic auth credentials.
- The MCP gateway, with the published password, listens on `127.0.0.1` only.
  Set `auth_password` (or `MCP_AUTH_PASSWORD`) to accept other connections.
  Compose now requires `MCP_AUTH_PASSWORD`, and the sample configuration,
  Compose file and scripts use port 8080, the code's default, instead of 8100.
- The MCP gateway's Docker image installs `signalwire-sdk` from PyPI (pin one
  with `--build-arg SDK_VERSION=x.y.z`), so it gets these fixes only from a
  release that includes them.
- The spider and web_search skills fetch pages directly, ignoring
  `HTTP_PROXY` and `HTTPS_PROXY`, because through a proxy the address check
  can't apply. To fetch through a proxy that blocks private destinations
  itself, set `SWML_URL_FETCH_USE_PROXY=true`. web_search's Google API request
  still uses the proxy.
- With `follow_robots_txt` on, the spider skips pages the site's robots.txt
  disallows. It was ignored before.
- A pgvector collection that the auto-build appended to on each start holds
  duplicate chunks. Rebuild it once with `overwrite` set.
- Rebuild markdown indexes to get the corrected section paths; existing
  indexes don't change.
- `migrate_pgvector_to_sqlite()` raises `NotImplementedError`. Rebuild the
  SQLite index from the source documents instead.
- A subclass that passes its own `route="/"` default to `AgentBase` now
  overrides a route set in the config file, even when its caller didn't pass a
  route. Forward only the arguments the caller gave.
- Code that reads `minimum`/`maximum` from a skill's parameter schema should
  read `min`/`max`.
- The credential source is `provided`, `environment`, `config file` or
  `generated`. `SWMLService` returned `auto-generated`, and `config file` is
  new.

## [3.4.3] - 2026-09-17

AI Chat gateway: browser-volunteered page context.

### Added
- `ChatGateway` forwards an optional `user_meta_data` object from the browser
  to the chat service, reaching your agent's config endpoint at
  `params.user_meta_data`. It exists so a chat agent can tailor its greeting
  from page context the way a voice agent already does from dial-time
  `userVariables` — send the same structure on both and one parse serves both
  transports. The service reads it only on the call that *creates* the
  conversation, so it is a snapshot taken at the greeting rather than a live
  feed; see `docs/ai_chat_gateway.md`. It is the single field the gateway
  forwards rather than overwrites, so it is bounded (8 KiB serialized, `413`
  past that; `400` if not an object) and stays nested under its own key where
  it cannot displace the conversation id or `config_url`. Browser-authored:
  treat it as a visitor's claim, never as authority.

## [3.4.2] - 2026-09-17

Search-index and webhook-signature fixes.

### Fixed
- Search: the FTS5 keyword index is now populated at build time. `chunks_fts` is
  an external-content table, so nothing filled it and `MATCH` returned nothing on
  a freshly built `.swsearch` — keyword search silently degraded to a LIKE scan.
  Rebuild existing indexes to gain working keyword search.
- Search: the zero-embedding fallback for a chunk that fails to embed now matches
  the loaded model's dimension instead of a hardcoded 768, which corrupted
  indexes built with a 384-dim model (the mini/all-MiniLM default).

### Added
- Webhook signature validation now accepts the stronger
  `X-SignalWire-Sha256-Signature` header (HMAC-SHA256), preferred over the SHA-1
  `X-SignalWire-Signature` when present and falling back to it so existing
  deployments keep working. New `validate_webhook_signature_sha256()` and
  `SIGNALWIRE_SHA256_SIGNATURE_HEADER` are exported from `core/security`.

## [3.4.1] - 2026-09-06

Search correctness and retrieval-quality fixes.

### Fixed
- pgvector: `SET LOCAL ivfflat.probes` was discarded before the query ran, so
  every search scanned a single list — roughly 1% of the table — and silently
  returned whatever happened to live there. Recall looked like a model problem
  and was a transaction-scope bug.
- Search results are no longer served from a stale cache after an index is
  reloaded.
- Non-semantic signals (keyword agreement) now REORDER results rather than
  choosing them: a chunk vector search never found cannot be promoted into the
  answer on keyword agreement alone, and agreement earns a bounded tiebreak
  rather than an unbounded boost.
- `_get_model_name` falls back to the default model when no connection string
  is available, instead of constructing a backend with `None`.
- Optional-dependency shims are tested with `is None` rather than truthiness,
  and `_blend` is annotated — clearing the findings CI reports when the search
  extras are installed.

### Changed
- pgvector indexes build as **HNSW** instead of IVFFlat: better recall at lower
  latency, and reproducible — IVFFlat's list assignment depends on the data
  present at build time, so the same corpus indexed twice could answer
  differently. Existing indexes keep working; rebuild to get the new type.

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

