"""
A verb method's positional body is added or refused, never silently dropped.

Verb methods take one positional body (the generated static surface declares
``verb(config)``) as well as keyword arguments. ``add_verb`` accepts an object
body, plus ``sleep``'s integer form; a positional non-object body it cannot
add raises ``TypeError`` instead of producing a document without the verb.
"""

from typing import Any

import pytest

from signalwire import SWMLService
from signalwire.core.swml_builder import SWMLBuilder
from signalwire.utils.schema_utils import SchemaValidationError


def _service() -> SWMLService:
    return SWMLService(name="verbs", route="/verbs")


def _main(service: SWMLService) -> list[Any]:
    main: list[Any] = service.get_document()["sections"]["main"]
    return main


class TestPositionalNonObjectBody:
    def test_builder_refuses_a_string_body(self) -> None:
        service = _service()
        with pytest.raises(TypeError, match=r"label\(\) takes an object body"):
            SWMLBuilder(service).label("start")  # type: ignore[arg-type]  # the wrong form under test
        assert _main(service) == []

    def test_service_refuses_a_string_body(self) -> None:
        service = _service()
        with pytest.raises(TypeError, match=r"label\(\) takes an object body"):
            service.label("start")
        assert _main(service) == []


class TestAcceptedBodiesUnchanged:
    def test_keyword_body(self) -> None:
        service = _service()
        SWMLBuilder(service).label(label="start")  # type: ignore[call-arg]  # runtime keyword form; the static stub declares only `config`
        assert _main(service) == [{"label": {"label": "start"}}]

    def test_mapping_body(self) -> None:
        service = _service()
        SWMLBuilder(service).label({"label": "start"})
        assert _main(service) == [{"label": {"label": "start"}}]

    def test_sleep_integer_body(self) -> None:
        service = _service()
        SWMLBuilder(service).sleep(1000)  # type: ignore[arg-type]  # runtime integer form; the static stub declares only `config`
        assert _main(service) == [{"sleep": 1000}]

    def test_an_invalid_keyword_body_still_raises_schema_validation(self) -> None:
        service = _service()
        with pytest.raises(SchemaValidationError):
            SWMLBuilder(service).label(label=123)  # type: ignore[call-arg]  # runtime keyword form
        assert _main(service) == []
