"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Tests for sw-pydocs, the SDK's documentation command.

Most of what sw-pydocs prints is read from the package, but the topics are
written by hand, so these tests check that everything a topic names exists:
its files, its examples, its API names and the topics it links to.
"""

import ast
import importlib
import re
import subprocess
import sys
from pathlib import Path

import pytest

from signalwire.cli.pydocs import main
from signalwire.cli.pydocs import _api
from signalwire.cli.pydocs._agents_note import NOTE_BEGIN, NOTE_END, init, note
from signalwire.cli.pydocs._bundle import docs_root, is_doc_file
from signalwire.cli.pydocs._files import all_doc_files, headings, resolve, section
from signalwire.cli.pydocs._render import (
    COMMAND_SUMMARIES,
    example_descriptions,
    render_llms_txt,
    render_topic,
)
from signalwire.cli.pydocs._topics import (
    START_HERE,
    TOPIC_GROUPS,
    TOPICS,
    TOPICS_BY_NAME,
    Topic,
)

ROOT = docs_root()
PACKAGE = Path(__file__).resolve().parents[3] / "signalwire" / "signalwire"


def _snippets(topic: Topic) -> list[str]:
    return re.findall(r"```python\n(.*?)```", topic.body, re.DOTALL)


def _run(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, str, str]:
    code = main(list(args))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_docs_root_is_the_checkout() -> None:
    # Tests run from a source checkout, which stands in for the installed copy
    assert ROOT is not None
    assert (ROOT / "docs" / "agent_guide.md").is_file()


class TestTopics:
    """Everything a topic names must exist, since it's written by hand."""

    @pytest.mark.parametrize("topic", TOPICS, ids=lambda t: t.name)
    def test_docs_exist_and_ship(self, topic: Topic) -> None:
        assert ROOT is not None
        for rel, purpose in topic.docs:
            assert purpose
            if rel.startswith("signalwire/"):
                assert (PACKAGE.parent / rel).is_file(), rel
            else:
                assert (ROOT / rel).is_file(), rel
                assert is_doc_file(rel), f"{rel} isn't installed with the package"

    @pytest.mark.parametrize("topic", TOPICS, ids=lambda t: t.name)
    def test_examples_exist_and_ship(self, topic: Topic) -> None:
        assert ROOT is not None
        for rel in topic.examples:
            assert (ROOT / rel).is_file(), rel
            assert is_doc_file(rel), rel

    @pytest.mark.parametrize("topic", TOPICS, ids=lambda t: t.name)
    def test_api_names_resolve(self, topic: Topic) -> None:
        for name in topic.api:
            assert _api.resolve(name), name

    def test_links_name_topics(self) -> None:
        for topic in TOPICS:
            for name in topic.related:
                assert name in TOPICS_BY_NAME, (topic.name, name)
        for _, names in START_HERE:
            for name in names:
                assert name in TOPICS_BY_NAME, name

    def test_groups_list_every_topic_once(self) -> None:
        grouped = [name for _, names in TOPIC_GROUPS for name in names]
        assert sorted(grouped) == sorted(TOPICS_BY_NAME)

    @pytest.mark.parametrize("topic", TOPICS, ids=lambda t: t.name)
    def test_python_snippets_compile(self, topic: Topic) -> None:
        # Each snippet parses, and every name it imports from the SDK exists
        for number, code in enumerate(_snippets(topic)):
            tree = ast.parse(code, f"<{topic.name} snippet {number}>")
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "signalwire":
                    module = importlib.import_module(node.module or "")
                    missing = [alias.name for alias in node.names if not hasattr(module, alias.name)]
                    assert missing == [], (topic.name, node.module, missing)

    def test_quickstart_agent_renders(self) -> None:
        namespace: dict[str, object] = {"__name__": "quickstart"}
        exec(_snippets(TOPICS_BY_NAME["quickstart"])[0], namespace)  # noqa: S102  # our own snippet
        agent = namespace["MyAgent"]()  # type: ignore[operator]  # a class the snippet defines
        swml = agent._render_swml()
        assert "get_time" in swml

    def test_swml_service_renders(self) -> None:
        code = _snippets(TOPICS_BY_NAME["swml"])[0].replace("service.serve()", "")
        namespace: dict[str, object] = {}
        exec(code, namespace)  # noqa: S102  # our own snippet
        document = namespace["service"].get_document()  # type: ignore[attr-defined]  # an SWMLService
        assert [next(iter(verb)) for verb in document["sections"]["main"]] == ["answer", "play", "hangup"]

    @pytest.mark.parametrize("topic", TOPICS, ids=lambda t: t.name)
    def test_renders(self, topic: Topic) -> None:
        text = render_topic(topic, ROOT, [])
        assert text.startswith(f"# {topic.title}")
        if topic.docs:
            # How to read one part of a long doc, beside the list of docs
            assert "sw-pydocs show <path> --toc" in text


class TestExamples:
    def test_every_example_has_a_description(self) -> None:
        # examples/README.md describes each example; sw-pydocs reads it
        assert ROOT is not None
        described = example_descriptions(ROOT)
        missing = [
            path.relative_to(ROOT).as_posix()
            for path in sorted((ROOT / "examples").glob("*.py"))
            if not described.get(path.relative_to(ROOT).as_posix(), ("", ""))[1]
        ]
        assert missing == []

    def test_topic_filter(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "examples", "relay")
        assert code == 0
        assert "relay_dial_and_play.py" in out
        assert "simple_agent.py" not in out

    def test_word_filter(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "examples", "bedrock")
        assert code == 0
        assert "bedrock_with_skills.py" in out

    def test_no_match(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "examples", "no-such-example-zz")
        assert code == 0
        assert "No examples match" in out


class TestIndex:
    def test_index(self, capsys: pytest.CaptureFixture[str]) -> None:
        import signalwire

        code, out, _ = _run(capsys)
        assert code == 0
        assert f"SignalWire SDK for Python {signalwire.__version__}" in out
        for name in TOPICS_BY_NAME:
            assert f"`{name}`" in out
        assert f"Docs root: {ROOT}" in out

    def test_topics_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "topics")
        assert code == 0
        assert all(f"`{name}`" in out for name in TOPICS_BY_NAME)

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "--help")
        assert code == 0
        assert "usage: sw-pydocs" in out

    def test_version(self, capsys: pytest.CaptureFixture[str]) -> None:
        import signalwire

        code, out, _ = _run(capsys, "--version")
        assert (code, out.strip()) == (0, signalwire.__version__)


class TestLiveSections:
    """Sections read from the installed package."""

    def test_skills_lists_the_registry(self, capsys: pytest.CaptureFixture[str]) -> None:
        from signalwire.skills.registry import skill_registry

        code, out, _ = _run(capsys, "skills")
        assert code == 0
        for skill in skill_registry.list_skills():
            assert f"`{skill['name']}`" in out

    def test_one_skill(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "skills", "web_search")
        assert code == 0
        assert "`search_engine_id` (string, required)" in out
        assert "skills/web_search/README.md" in out

    def test_unknown_skill(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "skills", "no_such_skill")
        assert code == 0
        assert "No built-in skill has that name" in out

    def test_rest_namespaces(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "rest")
        assert code == 0
        assert "`client.phone_numbers`" in out
        assert "`client.fabric`" in out

    def test_env_lists_variables_not_constants(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "config")
        assert code == 0
        assert "`SWML_BASIC_AUTH_PASSWORD`" in out
        # Read through a constant holding its name
        assert "`SWML_ALLOWED_HOSTS`" in out
        # A header-name constant exported in __all__, not a variable
        assert "SIGNALWIRE_SIGNATURE_HEADER" not in out

    def test_env_skips_the_bundled_examples(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Installed, the examples sit inside the package, under _docs/
        package = tmp_path / "signalwire"
        (package / "core").mkdir(parents=True)
        (package / "_docs" / "examples").mkdir(parents=True)
        (package / "core" / "x.py").write_text('os.getenv("SWML_FROM_CODE")\n', encoding="utf-8")
        (package / "_docs" / "examples" / "e.py").write_text('os.getenv("SWML_FROM_EXAMPLE")\n', encoding="utf-8")
        monkeypatch.setattr("signalwire.cli.pydocs._files.package_dir", lambda: package)
        monkeypatch.setattr("signalwire.cli.pydocs._render.package_dir", lambda: package)
        code, out, _ = _run(capsys, "config")
        assert code == 0
        assert "`SWML_FROM_CODE`" in out
        assert "SWML_FROM_EXAMPLE" not in out

    def test_prefabs(self, capsys: pytest.CaptureFixture[str]) -> None:
        import signalwire.prefabs

        code, out, _ = _run(capsys, "prefabs")
        assert code == 0
        for name in signalwire.prefabs.__all__:
            assert f"### {name}" in out

    def test_command_summaries_match_pyproject(self) -> None:
        pyproject = (PACKAGE.parents[1] / "pyproject.toml").read_text(encoding="utf-8")
        scripts = pyproject.split("[project.scripts]", 1)[1].split("\n[", 1)[0]
        names = set(re.findall(r"^([\w-]+)\s*=", scripts, re.MULTILINE))
        assert names == set(COMMAND_SUMMARIES)


class TestApi:
    def test_class(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "api", "AgentBase")
        assert code == 0
        assert out.startswith("# class signalwire.AgentBase")
        assert "core/agent_base.py:" in out
        # Members are grouped by the mixin that defines them
        assert "### PromptMixin" in out
        assert "- `prompt_add_section(" in out

    def test_method_signature_drops_self(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "api", "FunctionResult.connect")
        assert code == 0
        assert "connect(destination: str" in out
        assert "(self" not in out

    def test_bare_name_lists_every_match(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "api", "hangup")
        assert code == 0
        assert "## Other matches" in out
        assert "signalwire.relay.Call.hangup" in out or "signalwire.FunctionResult.hangup" in out

    def test_module(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "api", "signalwire.prefabs")
        assert code == 0
        assert out.startswith("# module signalwire.prefabs")
        assert "`SurveyAgent` (class)" in out

    def test_unknown_name_suggests(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, _, err = _run(capsys, "api", "prompt_add_sectoin")
        assert code == 1
        assert "prompt_add_section" in err

    def test_bare_word_falls_back_to_api(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "DataMap")
        assert code == 0
        assert "sw-pydocs api DataMap" in out
        assert "# class signalwire.DataMap" in out

    def test_unknown_word(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, _, err = _run(capsys, "toolz")
        assert code == 2
        assert "tools" in err


class TestFiles:
    def test_resolve_by_stem(self) -> None:
        files = all_doc_files(ROOT)
        assert resolve("agent_guide", files) == ["docs/agent_guide.md"]
        assert resolve("docs/agent_guide.md", files) == ["docs/agent_guide.md"]

    def test_skill_readmes_are_included(self) -> None:
        files = all_doc_files(ROOT)
        assert "signalwire/skills/web_search/README.md" in files

    def test_show_ambiguous(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, _, err = _run(capsys, "show", "getting-started")
        assert code == 1
        assert "relay/docs/getting-started.md" in err
        assert "rest/docs/getting-started.md" in err

    def test_show_toc_and_section(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "show", "relay/docs/getting-started", "--toc")
        assert code == 0
        first = out.splitlines()[0].split(maxsplit=1)[1]
        code, out, _ = _run(capsys, "show", "relay/docs/getting-started", "--section", first)
        assert code == 0
        assert first in out

    def test_show_missing_section(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, _, err = _run(capsys, "show", "agent_guide", "--section", "no such heading zz")
        assert code == 1
        assert "--toc" in err

    def test_headings_skip_code_fences(self) -> None:
        text = "# Title\n\n```bash\n# a shell comment\n```\n\n## Next\n"
        assert [h.text for h in headings(text)] == ["Title", "Next"]

    def test_section_stops_at_a_peer_heading(self) -> None:
        text = "# A\n\n## B\nbody b\n### B1\nmore\n## C\nbody c\n"
        found = section(text, "b")
        assert found is not None
        assert found[1] == "## B\nbody b\n### B1\nmore\n"

    def test_grep(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "grep", "set_functions", "--limit", "2")
        assert code == 0
        lines = out.splitlines()
        assert len(lines) == 3
        assert "more; narrow the pattern" in lines[-1]

    def test_grep_code(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "grep", "def set_functions", "--code")
        assert code == 0
        assert "core/contexts.py" in out

    def test_grep_bad_regex(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, _, err = _run(capsys, "grep", "(")
        assert code == 2
        assert "Invalid regular expression" in err

    def test_show_takes_the_path_that_path_prints(self, capsys: pytest.CaptureFixture[str]) -> None:
        _, printed, _ = _run(capsys, "path", "agent_guide")
        code, out, _ = _run(capsys, "show", printed.strip(), "--toc")
        assert code == 0
        assert "Agent" in out

    def test_show_takes_backslashes(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "show", "docs\\agent_guide.md", "--toc")
        assert code == 0
        assert "Agent" in out

    def test_grep_limit_must_be_positive(self, capsys: pytest.CaptureFixture[str]) -> None:
        code, _, err = _run(capsys, "grep", "AgentBase", "--limit", "0")
        assert code == 2
        assert "--limit" in err

    def test_path(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert ROOT is not None
        code, out, _ = _run(capsys, "path")
        assert (code, out.strip()) == (0, str(ROOT))
        code, out, _ = _run(capsys, "path", "agent_guide")
        assert (code, out.strip()) == (0, str(ROOT / "docs" / "agent_guide.md"))


class TestInit:
    def test_creates_agents_md(self, tmp_path: Path) -> None:
        changes = init(tmp_path)
        assert changes == [(tmp_path / "AGENTS.md", "created")]
        text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert NOTE_BEGIN in text and NOTE_END in text
        assert "sw-pydocs" in text

    def test_second_run_changes_nothing(self, tmp_path: Path) -> None:
        init(tmp_path)
        assert init(tmp_path) == [(tmp_path / "AGENTS.md", "unchanged")]

    def test_appends_to_existing_and_updates_in_place(self, tmp_path: Path) -> None:
        agents = tmp_path / "AGENTS.md"
        agents.write_text("# Project\n\nOur own rules.\n", encoding="utf-8")
        init(tmp_path)
        text = agents.read_text(encoding="utf-8")
        assert text.startswith("# Project\n\nOur own rules.\n\n" + NOTE_BEGIN)
        # An old copy of the note is replaced, not duplicated
        agents.write_text(text.replace("sw-pydocs pgi", "old text") + "\nAfter.\n", encoding="utf-8")
        assert init(tmp_path) == [(agents, "updated")]
        text = agents.read_text(encoding="utf-8")
        assert text.count(NOTE_BEGIN) == 1
        assert "old text" not in text
        assert text.endswith("After.\n")

    def test_claude_md_gets_the_note_unless_it_imports_agents_md(self, tmp_path: Path) -> None:
        (tmp_path / "CLAUDE.md").write_text("# Notes\n", encoding="utf-8")
        init(tmp_path)
        assert NOTE_BEGIN in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        other = tmp_path / "other"
        other.mkdir()
        (other / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        init(other)
        assert (other / "CLAUDE.md").read_text(encoding="utf-8") == "@AGENTS.md\n"

    def test_skill(self, tmp_path: Path) -> None:
        init(tmp_path, skill=True)
        for base in (".agents", ".claude"):
            skill = (tmp_path / base / "skills" / "signalwire-sdk" / "SKILL.md").read_text(encoding="utf-8")
            assert skill.startswith("---\nname: signalwire-sdk\ndescription: ")

    def test_command(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "init", "--dir", str(tmp_path))
        assert code == 0
        assert f"created: {tmp_path / 'AGENTS.md'}" in out

    def test_print_writes_nothing(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        code, out, _ = _run(capsys, "init", "--dir", str(tmp_path), "--print")
        assert (code, out) == (0, note())
        assert not (tmp_path / "AGENTS.md").exists()


def test_llms_txt_is_current() -> None:
    committed = (PACKAGE / "llms.txt").read_text(encoding="utf-8")
    assert committed == render_llms_txt(), (
        "signalwire/signalwire/llms.txt is out of date; regenerate it as "
        "render_llms_txt()'s docstring says"
    )


def test_llms_txt_links_resolve() -> None:
    assert ROOT is not None
    for rel in re.findall(r"\]\(_docs/([^)]+)\)", render_llms_txt()):
        assert (ROOT / rel).is_file(), rel


def _subprocess_modules(code: str) -> set[str]:
    result = subprocess.run(  # noqa: S603  # fixed arguments: this interpreter and a literal script
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )
    return set(result.stdout.split())


def test_index_loads_no_heavy_modules() -> None:
    # Coding agents run sw-pydocs often; it must stay fast
    loaded = _subprocess_modules(
        "import io, sys, contextlib\n"
        "from signalwire.cli.pydocs import main\n"
        "with contextlib.redirect_stdout(io.StringIO()):\n"
        "    main([])\n"
        "print(' '.join(sys.modules))\n"
    )
    for heavy in ("numpy", "torch", "sentence_transformers", "fastapi", "signalwire.cli.test_swaig"):
        assert heavy not in loaded, heavy


def test_cli_package_imports_swaig_test_lazily() -> None:
    loaded = _subprocess_modules("import sys, signalwire.cli\nprint(' '.join(sys.modules))\n")
    assert "signalwire.cli.test_swaig" not in loaded
    import signalwire.cli

    assert signalwire.cli.test_swaig_main.__module__ == "signalwire.cli.test_swaig"


@pytest.mark.parametrize("args", [[], ["api", "AgentBase"]], ids=["short output", "long output"])
def test_closed_pipe_exits_quietly(args: list[str]) -> None:
    # Output piped into a command that stops reading, such as head. Short
    # output fits the buffer and fails only at interpreter exit; long output
    # fails while it's written.
    proc = subprocess.Popen(  # noqa: S603  # fixed arguments: this interpreter and module
        [sys.executable, "-m", "signalwire", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None and proc.stderr is not None
    proc.stdout.close()
    stderr = proc.stderr.read().decode()
    assert proc.wait(timeout=60) == 0
    assert "Exception ignored" not in stderr
    assert "BrokenPipeError" not in stderr


def test_python_m_signalwire() -> None:
    import signalwire

    result = subprocess.run(  # fixed arguments: this interpreter and module
        [sys.executable, "-m", "signalwire", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == signalwire.__version__
