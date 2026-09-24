# DOC_AUDIT_IGNORE.md

Identifiers that `scripts/audit_docs.py` (from the `porting-sdk` repo) would
otherwise flag as unresolved. Every entry here has a rationale: external
library, stdlib call, example-local user method, or explicit teaching-by-comparison
reference to a third-party framework.

Format: one identifier per line, optionally followed by `: <rationale>`.
Blank lines and `# …` comments are ignored.

---

## Python stdlib: os / os.path / pathlib / tempfile / shutil / glob

abspath: os.path.abspath — stdlib path helper
dirname: os.path.dirname — stdlib path helper
is_file: pathlib.Path.is_file — stdlib
read_text: pathlib.Path.read_text — stdlib
write_text: pathlib.Path.write_text — stdlib
resolve: pathlib.Path.resolve — stdlib
mkdtemp: tempfile.mkdtemp — stdlib
rmtree: shutil.rmtree — stdlib
glob: glob.glob / pathlib.Path.glob — stdlib

## Python stdlib: datetime

fromisoformat: datetime.fromisoformat — stdlib
isoformat: datetime.isoformat — stdlib
total_seconds: timedelta.total_seconds — stdlib

## Python stdlib: hashlib / random / time / secrets

hexdigest: hashlib digest.hexdigest — stdlib
md5: hashlib.md5 — stdlib
randint: random.randint — stdlib
random: random.random — stdlib
choice: random.choice — stdlib
time: time.time / prometheus_client.Histogram().time() — stdlib / prometheus helper
sleep: time.sleep — stdlib (one call); the remaining hit is `self.sleep(1000)` in auto_vivified_example.py demonstrating the SWML `sleep` verb auto-vivified on SWMLService (real, but dynamic so absent from the public surface).

## Python stdlib: logging

getLogger: logging.getLogger — stdlib
basicConfig: logging.basicConfig — stdlib
setLevel: logging.Logger.setLevel — stdlib
debug: logging.Logger.debug — stdlib logger method (also used on self.log in service classes)
info: logging.Logger.info — stdlib logger method (most common logger call)
warning: logging.Logger.warning — stdlib logger method
error: logging.Logger.error — stdlib logger method (also used on self.log in service classes)

## Python stdlib: threading / sys / builtins

Thread: threading.Thread — stdlib
exit: sys.exit — stdlib
insert: list.insert / sys.path.insert — stdlib builtin / list method
input: builtin input() / pipecat `transport.input()` — stdlib or third-party
add: set.add — stdlib builtin method
title: str.title — stdlib builtin method
setdefault: dict.setdefault / os.environ.setdefault — stdlib builtin method
init: generic initializer name — stdlib / third-party (pinecone.init shown in search comparison)
asyncio.get_running_loop: stdlib, named in docs/agent_guide.md (a synchronous handler has no running event loop)

## argparse (stdlib)

ArgumentParser: argparse.ArgumentParser — stdlib
add_argument: argparse.ArgumentParser.add_argument — stdlib
parse_known_args: argparse.ArgumentParser.parse_known_args — stdlib
parse_args: argparse.ArgumentParser.parse_args — stdlib (the CLI examples' `parser.parse_args()`)

## structlog (third-party, used by examples/survey_agent_example.py)

configure: structlog.configure — structlog top-level
TimeStamper: structlog.processors.TimeStamper — structlog processor class
StackInfoRenderer: structlog.processors.StackInfoRenderer — structlog processor
JSONRenderer: structlog.processors.JSONRenderer — structlog processor
UnicodeDecoder: structlog.processors.UnicodeDecoder — structlog processor
PositionalArgumentsFormatter: structlog.stdlib.PositionalArgumentsFormatter — structlog
LoggerFactory: structlog.stdlib.LoggerFactory — structlog

## FastAPI / Starlette (third-party)

include_router: FastAPI.include_router — framework method
add_middleware: FastAPI.add_middleware — framework method

## pytest (third-party, used in CONTRIBUTING.md examples)

raises: pytest.raises — third-party test helper shown in the contributing guide's assertion examples

## prometheus_client (third-party)

inc: prometheus_client.Counter.inc — monitoring example in search_deployment.md

## Search-subsystem references (skip-listed in porting-sdk checklist)

# These come from docs/search_*.md and examples/search_*.py, plus
# examples/sigmond_*.py and examples/local_search_agent.py. The porting-sdk
# checklist marks search docs as SKIP_DOC_STEMS; the search skill is
# Python-only so other ports don't need to implement these symbols.

from_documents: langchain/pinecone Pinecone.from_documents — search comparison in docs/search_overview.md
split_documents: langchain RecursiveCharacterTextSplitter.split_documents — search comparison
similarity_search: langchain/pinecone Pinecone.similarity_search — search comparison
build_index: real IndexBuilder.build_index (signalwire/search/index_builder.py) — Python-only search skill, absent from the cross-port surface
build_index_from_sources: real IndexBuilder.build_index_from_sources (signalwire/search/index_builder.py) — Python-only search skill, absent from the cross-port surface
migrate_sqlite_to_pgvector: real migration helper (signalwire/search/migration.py) — Python-only search skill, absent from the cross-port surface
get_stats: real SearchEngine.get_stats (signalwire/search/search_engine.py) — Python-only search skill, absent from the cross-port surface
argsort: numpy.argsort — DIY search example in docs/search_overview.md
md: filename-extension regex false positive (matches `file.md (…`) in docs/search_overview.md processing listing
do_search: user-defined method inside a caching example in docs/search_deployment.md
_build_response: user-defined formatter callback in docs/search_troubleshooting.md
_get_cache_key: user-defined method inside a caching example in docs/search_deployment.md
_check_search_availability: user-defined method inside examples/local_search_agent.py
_create_sample_index: user-defined method inside examples/local_search_agent.py
_setup_search: user-defined method inside examples/local_search_agent.py
_setup_remote_search: user-defined method inside examples/sigmond_remote_search.py
_setup_search_skills: user-defined method inside examples/sigmond_native_search.py
_add_sdk_knowledge: user-defined method inside examples/sigmond_simple.py
_configure_personality: user-defined method inside sigmond_* examples
_configure_parameters: user-defined method inside sigmond_* examples
_configure_languages: user-defined method inside sigmond_* examples
_configure_pronunciation: user-defined method inside sigmond_* examples

## Platform-comparison docs (LiveKit, pipecat — also skip-listed)

LLM: openai.LLM — third-party class shown in docs/livekit_comparison.md
STT: deepgram.STT — third-party class shown in docs/livekit_comparison.md
TTS: cartesia.TTS — third-party class shown in docs/livekit_comparison.md

## Voice-name false positives (regex matches `inworld.Mark (…`)

Mark: voice identifier "inworld.Mark" in examples/simple_static_agent.py comment string
Blake: voice identifier "inworld.Blake" in examples/comprehensive_dynamic_agent.py docstring

## Example-local private helpers (defined within the same example file)

# These all match `def _foo` in the same file that calls `self._foo(...)`.
# They are intentionally private helpers — not part of the SDK surface.

_add_joke_function: defined in examples/joke_agent.py:54
_register_routes: defined in examples/multi_endpoint_agent.py:64
_configure_voice_and_language: defined in examples/comprehensive_dynamic_agent.py:132
_configure_tier_parameters: defined in examples/comprehensive_dynamic_agent.py:165
_configure_industry_prompts: defined in examples/comprehensive_dynamic_agent.py:206
_configure_global_data: defined in examples/comprehensive_dynamic_agent.py:266
_configure_debug_features: defined in examples/comprehensive_dynamic_agent.py:290
_configure_ab_testing: defined in examples/comprehensive_dynamic_agent.py:312
_get_enabled_features: defined in examples/comprehensive_dynamic_agent.py:331

## Example-local public helpers (defined within the same example file)

# These are public methods a user wrote on their own AgentBase/SWMLService
# subclass inside an example. Not part of the SDK surface.

setPersonality: defined in examples/simple_agent.py:277 (user-written wrapper over prompt_add_section)
setGoal: defined in examples/simple_agent.py:293 (user-written wrapper over prompt_add_section)
setInstructions: defined in examples/simple_agent.py:309 (user-written wrapper over prompt_add_section)
register_data_map_tool: defined in examples/data_map_demo.py:156 (wraps register_swaig_function)
build_default_document: defined in examples/dynamic_swml_service.py (user override of base build hook)
build_document: defined in docs/swml_service_guide.md example (user override of base build hook)
build_voicemail_document: defined in examples/basic_swml_service.py and auto_vivified_example.py (user helper)
build_ivr_document: defined in examples/basic_swml_service.py and auto_vivified_example.py (user helper)
build_transfer_document: defined in examples/basic_swml_service.py and auto_vivified_example.py (user helper)
build_recording_document: defined in examples/basic_swml_service.py (user helper)
register_customer_route: defined in examples/swml_service_routing_example.py:65 (user helper)
register_product_route: defined in examples/swml_service_routing_example.py (user helper)

## Docs-only user patterns (illustrating a pattern the user implements)

# These appear in prose code blocks that teach users how to structure agents.
# They are shown being called on `self`, but the method body is either
# defined inline in the same code block or described as "override this".

_check_basic_auth: real private method in signalwire/core/swml_service.py:894 (leading `_` excludes from public surface)
_get_new_messages: user-defined override shown in docs/agent_guide.md:2297
_configure_instructions: user-defined helper shown in docs/agent_guide.md:2503
_register_default_tools: user-defined helper shown in docs/agent_guide.md:2517
_register_custom_tools: user-defined helper shown in docs/api_reference.md:3291
_setup_contexts: user-defined helper shown in docs/api_reference.md:3257
_setup_static_config: user-defined helper shown in docs/agent_guide.md:1699
_test_api_connection: user-defined helper shown in docs/third_party_skills.md:304

register_default_tools: user-defined helper shown in docs/architecture.md:701
register_knowledge_base_tool: user-defined helper shown in docs/agent_guide.md:2522
get_customer_tier: user-defined helper shown in docs/agent_guide.md (tier-based config pattern)
get_customer_settings: user-defined helper shown in docs/agent_guide.md (tier-based config pattern)
get_customer_config: user-defined helper shown in docs/agent_guide.md (tier-based config pattern)
apply_custom_config: user-defined helper shown in docs/agent_guide.md (tier-based config pattern)
apply_default_config: user-defined helper shown in docs/agent_guide.md (tier-based config pattern)
is_valid_customer: user-defined helper shown in docs/agent_guide.md (tier-based config pattern)
load_user_preferences: user-defined helper shown in docs/agent_guide.md (lifecycle hook example)
send_to_analytics: user-defined helper shown in docs/agent_guide.md (lifecycle hook example)
alert_ops_team: user-defined helper shown in docs/api_reference.md (on_debug_event example)
schedule_follow_up: user-defined helper shown in docs/api_reference.md (on_summary example)
update_state: user-defined helper shown in docs/agent_guide.md lifecycle-hook examples; SDK does not ship built-in session storage (see agent_guide.md §Important Notes item 4)
get_state: user-defined helper shown in docs/agent_guide.md lifecycle-hook examples; SDK does not ship built-in session storage
delete_state: user-defined helper shown in docs/agent_guide.md lifecycle-hook examples; SDK does not ship built-in session storage

## Teaching-by-comparison references

setup_google_search: legacy-API straw-man shown in docs/skills_system.md §Migration Guide (labelled "Before (manual implementation)") to contrast against the modern `add_skill("web_search")` API
super: Python builtin `super().__init__(...)` shown in agent_guide.md subclassing examples — language construct, not an SDK symbol
download: third-party calls `nltk.download(...)` / `spacy download` in docs/search_overview.md troubleshooting table — not SDK methods
json.load: stdlib `json.load(f)` in docs/search_deployment.md:1305 (inspecting a chunks JSON) — stdlib, not an SDK method
silero.VAD.load: LiveKit/silero `VAD.load()` shown in docs/livekit_comparison.md:116 for contrast — external framework
DirectoryLoader.load: LangChain `DirectoryLoader(...).load()` shown in docs/search_overview.md:562 for contrast — external framework
is_function_call: LiveKit's RunResult test-framework API (`result.expect.next_event().is_function_call(...)`) shown in docs/livekit_comparison.md for contrast — external framework
next_event: LiveKit's RunResult test-framework API shown in docs/livekit_comparison.md for contrast — external framework
register_function: Pipecat's `llm.register_function()` shown in docs/pipecat_comparison.md feature-comparison table for contrast — external framework

## Tutorial series (tutorial/) — teaching apps built with third-party libs + user helpers

# The tutorial/multi_agents lessons and tutorial/fred walk a developer through
# building a full application: they call asyncio/aiohttp/asyncpg/redis APIs and
# domain helpers the *user* writes (order flow, customer DB), none of which are
# SignalWire SDK symbols. Grouped here so DOC-AUDIT stays exact on the real SDK
# surface without flagging tutorial application code.

# asyncio / aiohttp / asyncpg / redis (third-party runtime the tutorials use)
ClientSession: aiohttp.ClientSession — third-party HTTP client used in tutorial/multi_agents lessons
gather: asyncio.gather — stdlib coroutine aggregation in tutorial/multi_agents/lesson4
create_task: asyncio.create_task — stdlib task scheduling in tutorial/multi_agents lessons
acquire: asyncpg pool.acquire() connection checkout in tutorial/multi_agents/lesson5
fetch: asyncpg connection.fetch() query in tutorial/multi_agents/lesson5
create_pool: asyncpg.create_pool — third-party DB pool in tutorial/multi_agents/lesson5
create_redis_pool: aioredis pool constructor in tutorial/multi_agents/lesson5
lpop: redis LPOP command in tutorial/multi_agents/lesson5
rpush: redis RPUSH command in tutorial/multi_agents/lesson5
sub: re.sub / string helper in tutorial/multi_agents/lesson4 — not an SDK method

# user-defined application helpers the tutorials teach the reader to implement
_configure_prompt: user-defined helper shown in tutorial/multi_agents/lesson3
_expire_cache: user-defined helper shown in tutorial/multi_agents/lesson4
add_data: user-defined helper shown in tutorial/multi_agents/lesson4
add_task: user-defined helper shown in tutorial/multi_agents/lesson5
get_customer_status: user-defined helper shown in tutorial/multi_agents/lesson5
get_item_price: user-defined helper shown in tutorial/multi_agents/lesson5 (order-flow example)
get_or_create: user-defined helper shown in tutorial/multi_agents/lesson5
handle_task: user-defined helper shown in tutorial/multi_agents/lesson5
notify_customer: user-defined helper shown in tutorial/multi_agents/lesson5
process_queue: user-defined helper shown in tutorial/multi_agents/lesson5
set_persona: user-defined helper shown in tutorial/multi_agents/lesson5
submit_order: user-defined helper shown in tutorial/multi_agents/lesson5 (order-flow example)
update_order_status: user-defined helper shown in tutorial/multi_agents/lesson5

# stdlib
rstrip: str.rstrip — stdlib string method (tutorial lesson3 + skills/swml_transfer/README.md prose)
urlopen: urllib.request.urlopen — stdlib HTTP call in tutorial/fred/tutorial/appendix-docker-deployment.md

## PGI agent guide (docs/pgi_agent_guide.md): reference implementation and stdlib

# Section 6 of the guide is a five-file application (case_domain.py,
# case_workflow.py, case_handlers.py, agent.py, test_reference.py). These are
# methods and classes it defines, or stdlib calls it makes. None is an SDK symbol.

CaseStore._connect: defined in docs/pgi_agent_guide.md 6.1 (case_domain.py); opens the SQLite connection
CaseStore._key: defined in docs/pgi_agent_guide.md 6.1 (case_domain.py); validates the tenant and call id
CaseStore.submit: defined in docs/pgi_agent_guide.md 6.1 (case_domain.py); CaseHandlers.submit in 6.3 shares the name
CaseHandlers._call_id: defined in docs/pgi_agent_guide.md 6.3 (case_handlers.py)
CaseHandlers._projection: defined in docs/pgi_agent_guide.md 6.3 (case_handlers.py)
CaseHandlers._result: defined in docs/pgi_agent_guide.md 6.3 (case_handlers.py)
CaseHandlers._failure: defined in docs/pgi_agent_guide.md 6.3 (case_handlers.py)
CaseHandlers.finish: defined in docs/pgi_agent_guide.md 6.3 (case_handlers.py); called by the tests in 6.5
ReferenceTests.draft: test helper defined in docs/pgi_agent_guide.md 6.5 (test_reference.py)
agent.SupportAgent: class defined in docs/pgi_agent_guide.md 6.4 (agent.py), started with SupportAgent().run()
sqlite3.Cursor.fetchone: stdlib, used by docs/pgi_agent_guide.md 6.1
uuid.uuid4: stdlib, used by docs/pgi_agent_guide.md 6.1 to mint case references
tempfile.TemporaryDirectory: stdlib, used by docs/pgi_agent_guide.md 6.5
unittest.TestCase.addCleanup: stdlib, used by docs/pgi_agent_guide.md 6.5

## Full-guardrails tutorial (tutorial/full-guardrails-agent/)

The Penny tutorial builds a reservation agent. Its chapters quote the app's own
classes (reservations.py, handlers.py, penny.py, test_penny.py) and the stdlib.

ReservationStore._tx: defined in tutorial/full-guardrails-agent/reservations.py; opens a transaction
ReservationStore._session: defined in tutorial/full-guardrails-agent/reservations.py; loads the call's session row
ReservationStore._check_call: defined in tutorial/full-guardrails-agent/reservations.py; validates the call id
ReservationStore._now: defined in tutorial/full-guardrails-agent/reservations.py; reads the injected clock
ReservationStore.clock: defined in tutorial/full-guardrails-agent/reservations.py; the injected clock (tests pass a fake)
ReservationStore._table_free: defined in tutorial/full-guardrails-agent/reservations.py; checks one table's availability
ReservationStore._too_soon: defined in tutorial/full-guardrails-agent/reservations.py; the notice-period rule
ReservationStore._check_notice: defined in tutorial/full-guardrails-agent/reservations.py; raises when a booking is too soon
ReservationStore._validate_request: defined in tutorial/full-guardrails-agent/reservations.py; validates party size, date and time
ReservationStore.find_options: defined in tutorial/full-guardrails-agent/reservations.py; lists free tables
ReservationStore.update_draft: defined in tutorial/full-guardrails-agent/reservations.py; saves what the caller has said so far
ReservationStore.gathered: defined in tutorial/full-guardrails-agent/reservations.py; returns the draft for the step's global_data
ReservationStore.reset_request: defined in tutorial/full-guardrails-agent/reservations.py; clears the draft
ReservationStore.hold_option: defined in tutorial/full-guardrails-agent/reservations.py; holds a chosen table
ReservationStore._proposal: defined in tutorial/full-guardrails-agent/reservations.py; reads the held proposal
ReservationStore._reservation: defined in tutorial/full-guardrails-agent/reservations.py; loads a reservation by code
ReservationStore._new_code: defined in tutorial/full-guardrails-agent/reservations.py; generates a confirmation code
ReservationStore.booking_for_call: defined in tutorial/full-guardrails-agent/reservations.py; the reservation this call made
ReservationStore.request_sms: defined in tutorial/full-guardrails-agent/reservations.py; records an SMS request
ReservationStore._verified: defined in tutorial/full-guardrails-agent/reservations.py; checks that the caller has been verified
ReservationStore.verified_reservation: defined in tutorial/full-guardrails-agent/reservations.py; the reservation the caller verified for
ReservationStore.request_cancel: defined in tutorial/full-guardrails-agent/reservations.py; starts a cancellation
ReservationStore.confirm_cancel: defined in tutorial/full-guardrails-agent/reservations.py; completes a cancellation
ReservationStore.keep_reservation: defined in tutorial/full-guardrails-agent/reservations.py; abandons a cancellation
ReservationStore.save_message: defined in tutorial/full-guardrails-agent/reservations.py; stores a message for the host
ReservationStore.host_stand_open: defined in tutorial/full-guardrails-agent/reservations.py; the host-stand hours rule
ReservationStore.record_call_end: defined in tutorial/full-guardrails-agent/reservations.py; records the call's outcome
ReservationStore.seed_demo: defined in tutorial/full-guardrails-agent/reservations.py; loads demo data
Option.spoken: defined in tutorial/full-guardrails-agent/reservations.py; the text Penny reads back
Request.spoken: defined in tutorial/full-guardrails-agent/reservations.py; the text Penny reads back
Proposal.spoken: defined in tutorial/full-guardrails-agent/reservations.py; the text Penny reads back
Reservation.spoken: defined in tutorial/full-guardrails-agent/reservations.py; the text Penny reads back
PennyHandlers._gathered: defined in tutorial/full-guardrails-agent/handlers.py; the store's draft for the step
Penny._configure_voice: defined in tutorial/full-guardrails-agent/penny.py
Penny._register_tools: defined in tutorial/full-guardrails-agent/penny.py
TestHandlers.gathered: defined in tutorial/full-guardrails-agent/test_penny.py; the draft the test passes as global_data
re.fullmatch: stdlib
str.isdigit: stdlib
date.weekday: datetime.date.weekday — stdlib
datetime.date: datetime.datetime.date — stdlib
datetime.combine: datetime.datetime.combine — stdlib
functools.wraps: stdlib
logging.Logger.exception: stdlib
secrets.token_urlsafe: stdlib
io.StringIO: stdlib
contextlib.redirect_stdout: stdlib
sqlite3.Connection.executescript: stdlib
mock.patch.object: unittest.mock.patch.object — stdlib
unittest.TestCase.subTest: stdlib
unittest.TestCase.assertLogs: stdlib
