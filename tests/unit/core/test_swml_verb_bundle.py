"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
The SWML verbs a type checker sees are the verbs the runtime installs.

Two surfaces carry the verb set:

* the static ``swml_verbs_generated._SwmlVerbs`` Protocol that ``SWMLBuilder``
  inherits under ``TYPE_CHECKING``, generated from porting-sdk's ``schema.json``; and
* the methods ``SWMLBuilder`` installs on each instance from the bundled
  ``signalwire/schema.json``.

The bundle once fell eight verbs behind the stub (echo, execute_rpc, ring, set_meta,
stream, stop_stream, transcribe, transcribe_stop): ``builder.echo()`` type-checked and
raised ``AttributeError``. These tests hold the two sets equal, pin the eight verbs'
wire shape, and keep the deprecated verbs (dial, eval, if) out.

The bundle's freshness against porting-sdk itself is checked by the SCHEMA-BUNDLE gate
(``scripts/check_schema_bundle.py``), which has a porting-sdk checkout to compare with.
"""

import copy
import hashlib
import json
import keyword
import types
from pathlib import Path
from typing import Any

import pytest

import signalwire
from signalwire.core import swml_verbs_generated as gen
from signalwire.core.swml_builder import SWMLBuilder
from signalwire.core.swml_service import SWMLService

_PACKAGE_DIR = Path(signalwire.__file__).resolve().parent
_BUNDLE = _PACKAGE_DIR / "schema.json"
_RECORD = _PACKAGE_DIR / "schema.json.sha256"


def _stub_methods() -> set[str]:
    return {
        name
        for name, value in vars(gen._SwmlVerbs).items()
        if isinstance(value, types.FunctionType) and not name.startswith("__")
    }


def _installed_methods(builder: SWMLBuilder) -> set[str]:
    """The verb methods a caller can write as ``builder.<name>(...)``: plain
    identifiers that are not class attributes (the hand-written answer/hangup/ai/
    play/say are, and the stub leaves them out) and resolve, through the real
    ``__getattr__``, to a callable. Candidates are the stub's names plus every verb
    the runtime lists, raw and keyword-escaped, so a one-sided verb is still probed."""
    utils = builder.service.schema_utils
    assert utils is not None
    listed = set(utils.get_all_verb_names())
    candidates = _stub_methods() | listed | {f"{v}_" for v in listed}
    found: set[str] = set()
    for name in candidates:
        if not name.isidentifier() or keyword.iskeyword(name) or name.startswith("_"):
            continue
        if hasattr(SWMLBuilder, name):
            continue
        try:
            value = getattr(builder, name)
        except AttributeError:
            continue
        if callable(value):
            found.add(name)
    return found


def _service() -> SWMLService:
    return SWMLService(name="verb-bundle", route="/verb-bundle")


def _reload(service: SWMLService, schema: dict[str, Any]) -> None:
    utils = service.schema_utils
    assert utils is not None
    utils.schema = schema
    utils.verbs = utils._extract_verb_definitions()
    utils._init_full_validator()


def _last_verb(builder: SWMLBuilder) -> dict[str, Any]:
    main = builder.build()["sections"]["main"]
    last = main[-1]
    assert isinstance(last, dict)
    return last


class TestRuntimeMatchesStub:
    """Runtime-installed verb methods == stub-declared verb methods."""

    def test_every_stub_method_is_installed(self) -> None:
        builder = SWMLBuilder(_service())
        assert _stub_methods() - _installed_methods(builder) == set()

    def test_every_installed_method_is_in_the_stub(self) -> None:
        builder = SWMLBuilder(_service())
        assert _installed_methods(builder) - _stub_methods() == set()

    def test_the_comparison_is_not_empty(self) -> None:
        assert len(_stub_methods()) > 30

    def test_removing_a_verb_from_the_bundle_breaks_equality(self) -> None:
        """Negative control: a bundle without echo installs no echo, and the
        comparison reports it."""
        service = _service()
        utils = service.schema_utils
        assert utils is not None
        schema: dict[str, Any] = copy.deepcopy(utils.schema)
        arms = schema["$defs"]["SWMLMethod"]["anyOf"]
        schema["$defs"]["SWMLMethod"]["anyOf"] = [
            a for a in arms if a.get("$ref") != "#/$defs/Echo"
        ]
        assert len(schema["$defs"]["SWMLMethod"]["anyOf"]) == len(arms) - 1
        _reload(service, schema)
        builder = SWMLBuilder(service)
        assert _stub_methods() - _installed_methods(builder) == {"echo"}

    def test_an_extra_bundle_verb_breaks_equality(self) -> None:
        """Negative control, other direction: a verb the stub lacks is reported."""
        service = _service()
        utils = service.schema_utils
        assert utils is not None
        schema: dict[str, Any] = copy.deepcopy(utils.schema)
        schema["$defs"]["ControlVerb"] = {
            "type": "object",
            "properties": {"control_verb": {"type": "object", "properties": {}}},
            "required": ["control_verb"],
        }
        schema["$defs"]["SWMLMethod"]["anyOf"].append({"$ref": "#/$defs/ControlVerb"})
        _reload(service, schema)
        builder = SWMLBuilder(service)
        assert _installed_methods(builder) - _stub_methods() == {"control_verb"}


class TestBundleRecord:
    """schema.json.sha256 names the bundled bytes (the port-side record porting-sdk's
    fanout_schema.py writes beside each copy)."""

    def test_record_matches_bundle(self) -> None:
        recorded = _RECORD.read_text(encoding="utf-8").split()[0]
        assert recorded == hashlib.sha256(_BUNDLE.read_bytes()).hexdigest()


# (verb, config, expected wire body). Each config is valid against the bundled schema.
_FANOUT_VERBS: list[tuple[str, dict[str, Any]]] = [
    ("echo", {"timeout": 30}),
    ("execute_rpc", {"method": "ai_message", "params": {"role": "system"}}),
    ("ring", {}),
    ("set_meta", {"public": {"tier": "gold"}, "private": {"crm_id": "42"}}),
    ("stream", {"url": "wss://example.com/audio", "track": "both_tracks"}),
    ("stop_stream", {"control_id": "stream_001"}),
    ("transcribe", {"status_url": "https://example.com/transcribe-status"}),
    ("transcribe_stop", {}),
]


class TestFanoutVerbs:
    """The eight verbs the bundle had fallen behind on."""

    @pytest.mark.parametrize("verb", [v for v, _ in _FANOUT_VERBS])
    def test_verb_is_installed(self, verb: str) -> None:
        builder = SWMLBuilder(_service())
        assert verb in _installed_methods(builder)
        assert verb in _stub_methods()

    @pytest.mark.parametrize(("verb", "config"), _FANOUT_VERBS)
    def test_verb_emits_its_schema_shape(
        self, verb: str, config: dict[str, Any]
    ) -> None:
        service = _service()
        builder = SWMLBuilder(service)
        result = getattr(builder, verb)(config)
        assert result is builder
        assert _last_verb(builder) == {verb: config}
        utils = service.schema_utils
        assert utils is not None
        valid, errors = utils.validate_verb(verb, config)
        assert valid, errors

    def test_typed_calls(self) -> None:
        """The stub's calling convention (one positional config) works at runtime."""
        builder = SWMLBuilder(_service())
        builder.echo({"timeout": 5}).ring().transcribe_stop()
        builder.stream({"url": "wss://example.com/s"}).stop_stream({"control_id": "s"})
        builder.set_meta({"public": {"k": "v"}}).transcribe(
            {"status_url": "https://e.com/t"}
        )
        builder.execute_rpc({"method": "ai_message"})
        main = builder.build()["sections"]["main"]
        assert main == [
            {"echo": {"timeout": 5}},
            {"ring": {}},
            {"transcribe_stop": {}},
            {"stream": {"url": "wss://example.com/s"}},
            {"stop_stream": {"control_id": "s"}},
            {"set_meta": {"public": {"k": "v"}}},
            {"transcribe": {"status_url": "https://e.com/t"}},
            {"execute_rpc": {"method": "ai_message"}},
        ]

    def test_keyword_form_still_works(self) -> None:
        builder = SWMLBuilder(_service())
        # The stub declares only the positional form; the keyword form is the
        # runtime's own, so it is called through an untyped reference.
        stream: Any = builder.stream
        stream(url="wss://example.com/k", codec=None)
        assert _last_verb(builder) == {"stream": {"url": "wss://example.com/k"}}

    def test_keywords_merge_over_config(self) -> None:
        builder = SWMLBuilder(_service())
        echo: Any = builder.echo
        echo({"timeout": 5}, timeout=9)
        assert _last_verb(builder) == {"echo": {"timeout": 9}}

    def test_service_installs_them_too(self) -> None:
        service = _service()
        for verb, config in _FANOUT_VERBS:
            assert getattr(service, verb)(config) is True
        emitted = [next(iter(v)) for v in service.get_document()["sections"]["main"]]
        assert emitted == [v for v, _ in _FANOUT_VERBS]


class TestKeywordVerb:
    """``return`` is a Python keyword: the stub declares ``return_`` and the
    runtime installs the same name, emitting the wire key ``return``."""

    def test_return_is_installed_as_return_(self) -> None:
        builder = SWMLBuilder(_service())
        builder.return_({})
        assert _last_verb(builder) == {"return": {}}

    def test_service_return_(self) -> None:
        service = _service()
        assert service.return_({}) is True
        assert service.get_document()["sections"]["main"][-1] == {"return": {}}


class TestDeprecatedVerbsInTheBundle:
    """dial/eval/if ship in the bundle flagged deprecated, and are not installed."""

    @pytest.mark.parametrize(
        ("wrapper", "verb"), [("Dial", "dial"), ("Eval", "eval"), ("If", "if")]
    )
    def test_flagged_and_absent(self, wrapper: str, verb: str) -> None:
        defs = json.loads(_BUNDLE.read_text(encoding="utf-8"))["$defs"]
        body = defs[wrapper]["properties"][verb]
        assert defs[wrapper].get("deprecated") is True or body.get("deprecated") is True
        service = _service()
        builder = SWMLBuilder(service)
        assert not hasattr(builder, verb)
        assert not hasattr(builder, f"{verb}_")
        assert not hasattr(service, verb)
