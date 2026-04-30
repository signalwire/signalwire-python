"""
Tests for PromptObjectModel and Section — the lower-level POM data
model classes in ``signalwire.pom.pom``. Higher-level ``PomBuilder``
tests live in ``test_pom_builder.py``; these tests cover the raw
PromptObjectModel API that ports must mirror.
"""

import json
import pytest

from signalwire.pom.pom import PromptObjectModel, Section


class TestPromptObjectModelBasics:
    def test_empty_pom_has_no_sections(self):
        pom = PromptObjectModel()
        assert pom.sections == []

    def test_add_section_returns_section_instance(self):
        pom = PromptObjectModel()
        section = pom.add_section(title="Greeting")
        assert isinstance(section, Section)
        assert section.title == "Greeting"

    def test_add_section_appears_in_sections(self):
        pom = PromptObjectModel()
        pom.add_section(title="A")
        pom.add_section(title="B")
        titles = [s.title for s in pom.sections]
        assert titles == ["A", "B"]

    def test_find_section_returns_match(self):
        pom = PromptObjectModel()
        pom.add_section(title="Greeting", body="Hello")
        section = pom.find_section("Greeting")
        assert section is not None
        assert section.title == "Greeting"

    def test_find_section_returns_none_when_absent(self):
        pom = PromptObjectModel()
        assert pom.find_section("Nope") is None

    def test_render_markdown_includes_title_and_body(self):
        pom = PromptObjectModel()
        pom.add_section(title="Greeting", body="Hello world")
        md = pom.render_markdown()
        assert "Greeting" in md
        assert "Hello world" in md

    def test_render_xml_returns_xml_string(self):
        pom = PromptObjectModel()
        pom.add_section(title="Greeting", body="Hi")
        xml = pom.render_xml()
        assert "<" in xml and ">" in xml

    def test_to_dict_returns_list(self):
        pom = PromptObjectModel()
        pom.add_section(title="A", body="body-A")
        as_dict = pom.to_dict()
        assert isinstance(as_dict, list)

    def test_to_json_returns_string_with_section_title(self):
        pom = PromptObjectModel()
        pom.add_section(title="A", body="body-A")
        as_json = pom.to_json()
        assert "A" in as_json

    def test_from_json_round_trip(self):
        pom = PromptObjectModel()
        pom.add_section(title="A", body="body-A")
        as_json = pom.to_json()
        restored = PromptObjectModel.from_json(as_json)
        titles = [s.title for s in restored.sections]
        assert "A" in titles


class TestSectionBasics:
    def test_section_with_title_only(self):
        s = Section(title="Hello")
        assert s.title == "Hello"

    def test_section_add_body_replaces(self):
        # ``Section.add_body`` is documented to "Add OR REPLACE the body
        # text" — calling it overwrites any previous body.
        s = Section(title="X", body="initial")
        s.add_body("replacement")
        md = s.render_markdown()
        assert "replacement" in md
        assert "initial" not in md

    def test_section_add_bullets_appends(self):
        s = Section(title="X")
        s.add_bullets(["one", "two"])
        md = s.render_markdown()
        assert "one" in md
        assert "two" in md

    def test_section_add_subsection_returns_section(self):
        parent = Section(title="P")
        child = parent.add_subsection(title="C", body="cb")
        assert isinstance(child, Section)
        assert child.title == "C"
        assert child in parent.subsections

    def test_section_render_markdown_includes_body_and_bullets(self):
        s = Section(title="T", body="b", bullets=["x"])
        md = s.render_markdown()
        assert "T" in md and "b" in md and "x" in md


class TestPromptObjectModelYaml:
    """Round-trip tests for the YAML serialization API."""

    def test_to_yaml_returns_string_with_section_title(self):
        pom = PromptObjectModel()
        pom.add_section(title="Greeting", body="Hello")
        y = pom.to_yaml()
        assert isinstance(y, str)
        assert "Greeting" in y
        assert "Hello" in y

    def test_from_yaml_round_trip(self):
        pom = PromptObjectModel()
        pom.add_section(title="A", body="body-A", bullets=["x", "y"])
        y = pom.to_yaml()
        restored = PromptObjectModel.from_yaml(y)
        titles = [s.title for s in restored.sections]
        assert "A" in titles
        # Bullets survive the round trip
        a = restored.find_section("A")
        assert a is not None
        assert a.bullets == ["x", "y"]

    def test_from_yaml_accepts_dict_input(self):
        # The Python contract accepts either a YAML string OR a parsed dict.
        data = [{"title": "B", "body": "y"}]
        pom = PromptObjectModel.from_yaml(data)
        assert pom.find_section("B") is not None
