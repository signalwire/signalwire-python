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

## Python stdlib: threading / sys / builtins

Thread: threading.Thread — stdlib
exit: sys.exit — stdlib
insert: list.insert / sys.path.insert — stdlib builtin / list method
input: builtin input() / pipecat `transport.input()` — stdlib or third-party
add: set.add — stdlib builtin method
title: str.title — stdlib builtin method
setdefault: dict.setdefault / os.environ.setdefault — stdlib builtin method
init: generic initializer name — stdlib / third-party (pinecone.init shown in search comparison)

## argparse (stdlib)

ArgumentParser: argparse.ArgumentParser — stdlib
add_argument: argparse.ArgumentParser.add_argument — stdlib
parse_known_args: argparse.ArgumentParser.parse_known_args — stdlib

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
