"""
A verb's body as SWML has it: an object for most verbs, and a string, number
or array for those that take one, through add_verb, add_verb_to_section, the
service's and the builder's verb methods, and the agent's call-flow hooks.
"""

from typing import Any

import pytest

from signalwire import AgentBase
from signalwire.core.swml_builder import SWMLBuilder
from signalwire.core.swml_service import SWMLService
from signalwire.utils.schema_utils import SchemaUtils, SchemaValidationError

SCALAR_BODIES: list[tuple[str, Any]] = [
    ("cond", [{"when": "vars.a == 1", "then": [{"hangup": {}}]}]),
    ("label", "start"),
    ("unset", ["a", "b"]),
    ("unset", "a"),
    ("sleep", "%{vars.delay}"),
    ("return", "done"),
]


@pytest.mark.parametrize("validation", [True, False])
@pytest.mark.parametrize(("verb", "body"), SCALAR_BODIES)
def test_scalar_and_array_bodies_are_kept(verb: str, body: Any, validation: bool) -> None:
    # #141: both insertion methods keep them, with validation on or off
    service = SWMLService(name="example", schema_validation=validation)
    assert service.add_verb(verb, body) is True
    assert service.add_verb_to_section("other", verb, body) is True
    sections = service.get_document()["sections"]
    assert sections["main"] == [{verb: body}]
    assert sections["other"] == [{verb: body}]


def test_a_body_the_schema_refuses_raises_in_any_section() -> None:
    service = SWMLService(name="example")
    with pytest.raises(SchemaValidationError):
        service.add_verb("label", ["not", "a", "name"])
    with pytest.raises(SchemaValidationError):
        service.add_verb_to_section("other", "label", 42)
    assert service.get_document()["sections"]["main"] == []
    assert "other" not in service.get_document()["sections"]


@pytest.mark.parametrize("value", [True, False, -2, 0])
def test_sleep_refuses_booleans_and_durations_the_platform_wont_run(value: Any) -> None:
    # #149: the integer shortcut is validated like any other body
    service = SWMLService(name="example")
    with pytest.raises(SchemaValidationError, match="sleep"):
        service.add_verb("sleep", value)
    with pytest.raises(SchemaValidationError, match="sleep"):
        service.add_verb_to_section("other", "sleep", value)
    with pytest.raises(SchemaValidationError, match="sleep"):
        service.add_verb("sleep", {"duration": value})


@pytest.mark.parametrize("value", [-1, 1, 5000])
def test_sleep_takes_minus_one_and_positive_durations(value: int) -> None:
    service = SWMLService(name="example")
    service.add_verb("sleep", value)
    assert service.get_document()["sections"]["main"] == [{"sleep": value}]


def test_validation_off_keeps_any_sleep_value() -> None:
    service = SWMLService(name="example", schema_validation=False)
    service.add_verb("sleep", -2)
    assert service.get_document()["sections"]["main"] == [{"sleep": -2}]


@pytest.mark.parametrize("make", [lambda s: s, SWMLBuilder])
def test_verb_methods_take_a_positional_body(make: Any) -> None:
    # #142: as the generated declarations say
    service = SWMLService(name="example")
    target = make(service)
    target.label("start")
    target.cond([{"when": "vars.a == 1", "then": [{"hangup": {}}]}])
    target.unset("x")
    target.connect({"to": "+15551234567"})
    target.connect(config={"to": "+15551234568"})
    target.label(value="end")
    assert service.get_document()["sections"]["main"] == [
        {"label": "start"},
        {"cond": [{"when": "vars.a == 1", "then": [{"hangup": {}}]}]},
        {"unset": "x"},
        {"connect": {"to": "+15551234567"}},
        {"connect": {"to": "+15551234568"}},
        {"label": "end"},
    ]


def test_keyword_options_still_work_and_merge_with_an_object_body() -> None:
    service = SWMLService(name="example")
    service.connect(to="+15551234567")
    service.connect({"to": "+15551234567"}, timeout=10)
    assert service.get_document()["sections"]["main"] == [
        {"connect": {"to": "+15551234567"}},
        {"connect": {"to": "+15551234567", "timeout": 10}},
    ]
    with pytest.raises(TypeError, match="not both"):
        service.label("start", extra=1)


def test_a_builder_method_chains() -> None:
    builder = SWMLBuilder(SWMLService(name="example"))
    # The generated declaration types unset's body as a mapping until porting-sdk's
    # generator gives scalar bodies their types (#151-#154)
    assert builder.label("start").unset("x") is builder  # type: ignore[arg-type]


@pytest.mark.parametrize("make", [lambda s: s, SWMLBuilder])
def test_return_is_reachable_as_return_(make: Any) -> None:
    # #143: return is a Python keyword
    service = SWMLService(name="example")
    target = make(service)
    target.return_("done")
    target.return_({"status": "ok"})
    assert service.get_document()["sections"]["main"] == [
        {"return": "done"},
        {"return": {"status": "ok"}},
    ]


def test_answer_takes_sip_credentials() -> None:
    # #144
    service = SWMLService(name="example")
    SWMLBuilder(service).answer(max_duration=60, username="u", password="p")
    assert service.get_document()["sections"]["main"] == [
        {"answer": {"max_duration": 60, "username": "u", "password": "p"}}
    ]


def test_play_takes_a_status_url() -> None:
    # #145
    service = SWMLService(name="example")
    builder = SWMLBuilder(service)
    builder.play(url="say:Hello", status_url="https://example.com/status")
    builder.play(urls=["say:One", "say:Two"], status_url="https://example.com/s")
    assert service.get_document()["sections"]["main"] == [
        {"play": {"url": "say:Hello", "status_url": "https://example.com/status"}},
        {"play": {"urls": ["say:One", "say:Two"], "status_url": "https://example.com/s"}},
    ]


@pytest.mark.parametrize("hook", ["pre_answer", "post_answer", "post_ai"])
def test_hooks_check_a_verb_when_its_added(hook: str) -> None:
    # #148: a bad config fails at registration, naming the verb
    agent = AgentBase(name="example", route="/", basic_auth=("u", "p"), suppress_logs=True)
    add = getattr(agent, f"add_{hook}_verb")
    with pytest.raises(SchemaValidationError, match="request"):
        add("request", {})
    add("request", {"url": "https://example.com/hook", "method": "POST"})
    add("sleep", 500)
    swml = agent._render_swml()
    assert '"sleep": 500' in swml


def test_the_answer_hook_checks_its_config() -> None:
    agent = AgentBase(name="example", route="/", basic_auth=("u", "p"), suppress_logs=True)
    with pytest.raises(SchemaValidationError):
        agent.add_answer_verb({"max_duration": "an hour"})
    agent.add_answer_verb({"max_duration": 3600})


def test_the_fallback_validator_finds_required_fields_behind_refs() -> None:
    # #150: without a full validator, required fields are still found through
    # $ref and union branches
    schema = SchemaUtils()
    schema._full_validator = None
    ok, errors = schema.validate_verb("send_sms", {})
    assert not ok
    assert any("to_number" in e or "from_number" in e for e in errors)
    assert schema.validate_verb("request", {})[0] is False
    assert schema.validate_verb("request", {"url": "https://x", "method": "GET"}) == (True, [])
    assert schema.validate_verb("sleep", {})[0] is False
    assert schema.validate_verb("sleep", 5000) == (True, [])
    assert schema.validate_verb("label", "start") == (True, [])
