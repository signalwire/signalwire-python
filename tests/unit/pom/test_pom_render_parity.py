"""
Cross-port parity tests for ``signalwire.pom.pom``.

These tests assert the **exact** rendered shape (not just substrings) of
markdown, XML, JSON, and YAML output for the canonical scenarios that
every port (Go, Java, .NET, Ruby, TS, etc.) must reproduce byte-for-byte.

Why exact-string assertions?
  Substring assertions (``assert "Greeting" in md``) are too weak to catch
  whitespace, ordering, or indentation drift across ports.  When a port
  ships a "## Greeting\\n\\nHello\\n" renderer that emits "## Greeting\\nHello\\n"
  instead, downstream prompt assembly silently breaks.  Exact-string parity
  is the only contract that prevents that.

Each test below is the source-of-truth shape that ports must match.
Port translations live next to each port's POM module:

  - signalwire-go/pkg/pom/pom_test.go
  - (others as ported)
"""

import json
import textwrap

import yaml

from signalwire.pom.pom import PromptObjectModel, Section


# ----------------------------------------------------------------------------
# Empty POM
# ----------------------------------------------------------------------------

class TestEmptyPom:
    def test_empty_render_markdown_is_empty_string(self):
        pom = PromptObjectModel()
        assert pom.render_markdown() == ""

    def test_empty_render_xml_is_just_prompt_tags(self):
        pom = PromptObjectModel()
        expected = '<?xml version="1.0" encoding="UTF-8"?>\n<prompt>\n</prompt>'
        assert pom.render_xml() == expected

    def test_empty_to_json_is_empty_array(self):
        pom = PromptObjectModel()
        assert pom.to_json() == "[]"

    def test_empty_to_yaml(self):
        pom = PromptObjectModel()
        # PyYAML's default for an empty list is "[]\n"
        assert pom.to_yaml() == "[]\n"


# ----------------------------------------------------------------------------
# Single section with title + body
# ----------------------------------------------------------------------------

class TestSimpleSection:
    def test_render_markdown_exact(self):
        pom = PromptObjectModel()
        pom.add_section(title="Greeting", body="Hello world")
        expected = "## Greeting\n\nHello world\n"
        assert pom.render_markdown() == expected

    def test_render_xml_exact(self):
        pom = PromptObjectModel()
        pom.add_section(title="Greeting", body="Hello world")
        expected = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<prompt>\n'
            '  <section>\n'
            '    <title>Greeting</title>\n'
            '    <body>Hello world</body>\n'
            '  </section>\n'
            '</prompt>'
        )
        assert pom.render_xml() == expected


# ----------------------------------------------------------------------------
# Section with bullets
# ----------------------------------------------------------------------------

class TestBullets:
    def test_render_markdown_with_bullets(self):
        pom = PromptObjectModel()
        pom.add_section(title="Goals", body="Be helpful",
                       bullets=["Be concise", "Be clear"])
        expected = "## Goals\n\nBe helpful\n\n- Be concise\n- Be clear\n"
        assert pom.render_markdown() == expected

    def test_render_xml_with_bullets(self):
        pom = PromptObjectModel()
        pom.add_section(title="Goals", body="Be helpful",
                       bullets=["Be concise", "Be clear"])
        expected = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<prompt>\n'
            '  <section>\n'
            '    <title>Goals</title>\n'
            '    <body>Be helpful</body>\n'
            '    <bullets>\n'
            '      <bullet>Be concise</bullet>\n'
            '      <bullet>Be clear</bullet>\n'
            '    </bullets>\n'
            '  </section>\n'
            '</prompt>'
        )
        assert pom.render_xml() == expected


# ----------------------------------------------------------------------------
# Subsections
# ----------------------------------------------------------------------------

class TestSubsections:
    def test_render_markdown_with_subsection(self):
        pom = PromptObjectModel()
        s = pom.add_section(title="Top", body="Top body")
        s.add_subsection(title="Sub1", body="Sub1 body", bullets=["a", "b"])
        expected = "## Top\n\nTop body\n\n### Sub1\n\nSub1 body\n\n- a\n- b\n"
        assert pom.render_markdown() == expected

    def test_render_xml_with_subsection(self):
        pom = PromptObjectModel()
        s = pom.add_section(title="Top", body="Top body")
        s.add_subsection(title="Sub1", body="Sub1 body", bullets=["a", "b"])
        expected = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<prompt>\n'
            '  <section>\n'
            '    <title>Top</title>\n'
            '    <body>Top body</body>\n'
            '    <subsections>\n'
            '      <section>\n'
            '        <title>Sub1</title>\n'
            '        <body>Sub1 body</body>\n'
            '        <bullets>\n'
            '          <bullet>a</bullet>\n'
            '          <bullet>b</bullet>\n'
            '        </bullets>\n'
            '      </section>\n'
            '    </subsections>\n'
            '  </section>\n'
            '</prompt>'
        )
        assert pom.render_xml() == expected


# ----------------------------------------------------------------------------
# Numbered top-level sections
# ----------------------------------------------------------------------------

class TestNumberedSections:
    def test_render_markdown_numbered_propagates_to_siblings(self):
        # Once any sibling is numbered=True, all siblings (without explicit
        # numbered=False) get numbered.
        pom = PromptObjectModel()
        pom.add_section(title="S1", body="b1", numbered=True)
        pom.add_section(title="S2", body="b2")
        expected = "## 1. S1\n\nb1\n\n## 2. S2\n\nb2\n"
        assert pom.render_markdown() == expected

    def test_render_xml_numbered_propagates(self):
        pom = PromptObjectModel()
        pom.add_section(title="S1", body="b1", numbered=True)
        pom.add_section(title="S2", body="b2")
        expected = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<prompt>\n'
            '  <section>\n'
            '    <title>1. S1</title>\n'
            '    <body>b1</body>\n'
            '  </section>\n'
            '  <section>\n'
            '    <title>2. S2</title>\n'
            '    <body>b2</body>\n'
            '  </section>\n'
            '</prompt>'
        )
        assert pom.render_xml() == expected


# ----------------------------------------------------------------------------
# Numbered bullets
# ----------------------------------------------------------------------------

class TestNumberedBullets:
    def test_render_markdown_numbered_bullets(self):
        pom = PromptObjectModel()
        pom.add_section(title="X", bullets=["one", "two"], numberedBullets=True)
        expected = "## X\n\n1. one\n2. two\n"
        assert pom.render_markdown() == expected

    def test_render_xml_numbered_bullets_use_id_attr(self):
        pom = PromptObjectModel()
        pom.add_section(title="X", bullets=["one", "two"], numberedBullets=True)
        expected = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<prompt>\n'
            '  <section>\n'
            '    <title>X</title>\n'
            '    <bullets>\n'
            '      <bullet id="1">one</bullet>\n'
            '      <bullet id="2">two</bullet>\n'
            '    </bullets>\n'
            '  </section>\n'
            '</prompt>'
        )
        assert pom.render_xml() == expected


# ----------------------------------------------------------------------------
# JSON / YAML round-trip with exact key order
# ----------------------------------------------------------------------------

class TestSerialization:
    def test_to_json_exact_shape(self):
        pom = PromptObjectModel()
        s = pom.add_section(title="A", body="ab")
        s.add_subsection(title="A1", body="a1b", bullets=["x"])
        expected = (
            '[\n'
            '  {\n'
            '    "title": "A",\n'
            '    "body": "ab",\n'
            '    "subsections": [\n'
            '      {\n'
            '        "title": "A1",\n'
            '        "body": "a1b",\n'
            '        "bullets": [\n'
            '          "x"\n'
            '        ]\n'
            '      }\n'
            '    ]\n'
            '  }\n'
            ']'
        )
        assert pom.to_json() == expected

    def test_to_yaml_exact_shape(self):
        pom = PromptObjectModel()
        s = pom.add_section(title="A", body="ab")
        s.add_subsection(title="A1", body="a1b", bullets=["x"])
        expected = (
            "- title: A\n"
            "  body: ab\n"
            "  subsections:\n"
            "  - title: A1\n"
            "    body: a1b\n"
            "    bullets:\n"
            "    - x\n"
        )
        assert pom.to_yaml() == expected

    def test_from_json_round_trip_preserves_structure(self):
        pom = PromptObjectModel()
        s = pom.add_section(title="A", body="ab")
        s.add_subsection(title="A1", body="a1b", bullets=["x", "y"])
        json_str = pom.to_json()
        restored = PromptObjectModel.from_json(json_str)
        assert restored.to_json() == json_str

    def test_from_yaml_round_trip_preserves_structure(self):
        pom = PromptObjectModel()
        s = pom.add_section(title="A", body="ab")
        s.add_subsection(title="A1", body="a1b", bullets=["x", "y"])
        yaml_str = pom.to_yaml()
        restored = PromptObjectModel.from_yaml(yaml_str)
        assert restored.to_yaml() == yaml_str


# ----------------------------------------------------------------------------
# find_section recursion
# ----------------------------------------------------------------------------

class TestFindSection:
    def test_find_section_top_level(self):
        pom = PromptObjectModel()
        pom.add_section(title="One", body="b1")
        pom.add_section(title="Two", body="b2")
        s = pom.find_section("Two")
        assert s is not None
        assert s.body == "b2"

    def test_find_section_recurses_into_subsections(self):
        pom = PromptObjectModel()
        s = pom.add_section(title="Outer", body="ob")
        s.add_subsection(title="Inner", body="ib")
        found = pom.find_section("Inner")
        assert found is not None
        assert found.body == "ib"

    def test_find_section_returns_none_for_missing(self):
        pom = PromptObjectModel()
        pom.add_section(title="Only", body="b")
        assert pom.find_section("Missing") is None


# ----------------------------------------------------------------------------
# add_pom_as_subsection
# ----------------------------------------------------------------------------

class TestAddPomAsSubsection:
    def test_add_pom_to_existing_section_by_title(self):
        host = PromptObjectModel()
        host.add_section(title="Host", body="hb")

        guest = PromptObjectModel()
        guest.add_section(title="Guest", body="gb")

        host.add_pom_as_subsection("Host", guest)
        host_section = host.find_section("Host")
        assert host_section is not None
        assert len(host_section.subsections) == 1
        assert host_section.subsections[0].title == "Guest"
        assert host_section.subsections[0].body == "gb"

    def test_add_pom_to_section_object_directly(self):
        host = PromptObjectModel()
        target = host.add_section(title="Host", body="hb")

        guest = PromptObjectModel()
        guest.add_section(title="GuestA", body="ab")
        guest.add_section(title="GuestB", body="bb")

        host.add_pom_as_subsection(target, guest)
        assert [s.title for s in target.subsections] == ["GuestA", "GuestB"]
