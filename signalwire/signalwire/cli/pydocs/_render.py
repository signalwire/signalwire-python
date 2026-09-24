"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Markdown output for the index, topics, examples, and the sections that are
read from the installed package.
"""

from __future__ import annotations

import ast
import importlib.metadata
import inspect
import re
from pathlib import Path
from typing import Any

from . import _api
from ._files import package_dir
from ._topics import RULES_OF_THUMB, START_HERE, TOPIC_GROUPS, TOPICS_BY_NAME, Topic

DIST_NAME = "signalwire-sdk"

# One line for each command the SDK installs.
# tests/unit/cli/test_pydocs.py checks this against pyproject.toml.
COMMAND_SUMMARIES = {
    "sw-pydocs": "This documentation: topics, API lookups, examples and docs search",
    "swaig-test": "Test an agent's tools and SWML locally, and simulate serverless platforms",
    "sw-search": "Build, validate and query search indexes for agent knowledge bases",
    "sw-agent-init": "Create a new agent project, for a local server or a cloud function",
    "sw-agent-dokku": "Deploy and manage an agent project on Dokku",
    "mcp-gateway": "Run the gateway that bridges MCP servers to SWAIG tools",
    "pom-tool": "Convert a Prompt Object Model file between JSON, YAML, Markdown and XML",
}

_EXAMPLE_ROW = re.compile(r"^\|\s*\[[^\]]+\]\(([^)]+)\)\s*\|\s*(.+?)\s*\|\s*$")
_ENV_NAME = re.compile(r"""["']((?:SWML|SIGNALWIRE)_[A-Z0-9_]+)["']""")
# Names exported in __all__, such as SIGNALWIRE_SIGNATURE_HEADER, are
# constants that share the prefix, not environment variables
_ALL_LIST = re.compile(r"__all__\s*[:=][^\]]*\]", re.DOTALL)


def version() -> str:
    """The installed SDK version."""
    import signalwire

    return str(signalwire.__version__)


def _file_line(root: Path | None, rel: str, purpose: str = "") -> str:
    if root is None:
        location = rel
    elif rel.startswith("signalwire/"):
        location = str(package_dir().parent / rel)
    else:
        location = str(root / rel)
    return f"- {location}: {purpose}" if purpose else f"- {location}"


def render_index(root: Path | None) -> str:
    """The page ``sw-pydocs`` prints with no arguments."""
    out = [
        f"# SignalWire SDK for Python {version()}: documentation",
        "",
        "This is `sw-pydocs`, the documentation that ships with the `signalwire-sdk` "
        "package. It's read from the installed package, so it matches the version you "
        "have, and it points to the docs, examples and tutorials installed with it.",
        "",
        "For coding agents: use it before writing SignalWire code, and whenever you need "
        "an API or an example. Run `sw-pydocs <topic>` for an area, `sw-pydocs api <name>` "
        "for exact signatures, and read the files the topics list. To make this the first "
        "stop for future sessions, suggest that your user run `sw-pydocs init` in the "
        "project: it adds a note to the project's AGENTS.md.",
        "",
        "## What the SDK does",
        "",
        "- AI agents (`AgentBase`): voice and text agents. SignalWire runs speech "
        "recognition, the LLM and text-to-speech; your code defines the prompt, the tools "
        "and the workflow, and serves them over HTTP.",
        "- SWML services (`SWMLService`): call flows without AI, such as IVRs, routing and "
        "recording.",
        "- RELAY (`signalwire.relay.RelayClient`): real-time control of live calls and "
        "messages over WebSocket.",
        "- REST (`signalwire.rest.RestClient`): manage numbers, Fabric resources, calls, "
        "video and messaging over HTTP.",
        "- Search: document indexes that give agents a knowledge base.",
        "- LiveWire, MCP, the AI chat gateway and Amazon Bedrock agents.",
        "",
        "## Start here",
        "",
        "| To | Run |",
        "|---|---|",
    ]
    out += [
        f"| {task} | {', '.join(f'`sw-pydocs {name}`' for name in names)} |"
        for task, names in START_HERE
    ]
    out += ["", "## Topics", ""]
    for group, names in TOPIC_GROUPS:
        out.append(f"{group}:")
        out += [f"- `{name}`: {TOPICS_BY_NAME[name].summary}" for name in names]
        out.append("")
    out += [
        "## Commands",
        "",
        "- `sw-pydocs <topic> [name]`: a topic (`skills` takes a skill name)",
        "- `sw-pydocs api <name>`: signature, docstring and members, such as "
        "`api AgentBase`, `api FunctionResult.connect` or `api signalwire.relay.Call`",
        "- `sw-pydocs examples [topic or word]`: examples, with descriptions and paths",
        "- `sw-pydocs grep <regex>`: search the installed docs and examples "
        "(`--code` searches the SDK's source too)",
        "- `sw-pydocs show <file> [--toc | --section <heading>]`: print a doc, its "
        "headings, or one section",
        "- `sw-pydocs path [file]`: where the docs are, or one file's full path",
        "- `sw-pydocs init`: add a note about sw-pydocs to a project's AGENTS.md",
        "",
        "## Files",
        "",
    ]
    if root is None:
        out += [
            "The docs, examples and tutorials aren't installed with this copy of the "
            "package. The topics and `sw-pydocs api` still work.",
            "",
        ]
    else:
        out += [
            f"Docs root: {root}",
            "",
            "Read first:",
            "",
            _file_line(
                root,
                "README.md",
                "the overview, with quickstarts for agents, RELAY and REST",
            ),
            _file_line(
                root, "docs/agent_guide.md", "the main guide to building agents"
            ),
            _file_line(
                root,
                "docs/pgi_agent_guide.md",
                "how to design agents that stay within their rules",
            ),
            _file_line(root, "examples/README.md", "every example, by category"),
            _file_line(root, "CHANGELOG.md", "what changed in each version"),
            "",
        ]
    out += ["## Rules of thumb", ""]
    out += [f"{number}. {rule}" for number, rule in enumerate(RULES_OF_THUMB, start=1)]
    return "\n".join(out).rstrip() + "\n"


def render_topic_list() -> str:
    """One line per topic."""
    out = ["# sw-pydocs topics", ""]
    for group, names in TOPIC_GROUPS:
        out.append(f"{group}:")
        out += [f"- `{name}`: {TOPICS_BY_NAME[name].summary}" for name in names]
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_topic(topic: Topic, root: Path | None, args: list[str]) -> str:
    """A topic's page."""
    out = [f"# {topic.title}", "", topic.body.rstrip(), ""]
    if topic.live:
        out += [_LIVE[topic.live](args).rstrip(), ""]
    if topic.docs:
        out += ["## Read", ""]
        out += [_file_line(root, rel, purpose) for rel, purpose in topic.docs]
        out.append("")
    if topic.examples:
        described = example_descriptions(root) if root is not None else {}
        out += ["## Examples", ""]
        out += [
            _file_line(root, rel, described.get(rel, ("", ""))[1])
            for rel in topic.examples
        ]
        out.append("")
    if topic.api:
        out += [
            "## API",
            "",
            "Run `sw-pydocs api <name>` for the signature, docstring and members.",
            "",
        ]
        for name in topic.api:
            found = _api.resolve(name)
            text = _api.summary(found[0].obj) if found else ""
            out.append(f"- `{name}`: {text}" if text else f"- `{name}`")
        out.append("")
    if topic.related:
        out += [
            "## Related",
            "",
            ", ".join(f"`sw-pydocs {name}`" for name in topic.related),
        ]
    return "\n".join(out).rstrip() + "\n"


def example_descriptions(root: Path) -> dict[str, tuple[str, str]]:
    """Each example's (category, description).

    Examples in examples/ are described by examples/README.md, which is also
    what people read. The RELAY, REST and LiveWire examples are described by
    their docstrings.
    """
    described: dict[str, tuple[str, str]] = {}
    readme = root / "examples" / "README.md"
    if readme.is_file():
        category = "Examples"
        for line in readme.read_text(encoding="utf-8").splitlines():
            if line.startswith("### "):
                category = line[4:].strip()
                continue
            match = _EXAMPLE_ROW.match(line)
            if match:
                described[f"examples/{match.group(1)}"] = (category, match.group(2))
    for bundle, category in (
        ("relay", "RELAY"),
        ("rest", "REST"),
        ("livewire", "LiveWire"),
    ):
        for path in sorted((root / bundle / "examples").glob("*.py")):
            described[path.relative_to(root).as_posix()] = (
                category,
                _docstring_summary(path),
            )
    return described


def _docstring_summary(path: Path) -> str:
    try:
        doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
    except (OSError, SyntaxError, UnicodeDecodeError):
        return ""
    for line in doc.splitlines():
        text = line.strip()
        if text and not text.startswith(
            ("Copyright", "This file is part", "Licensed under", "See LICENSE")
        ):
            return text.removeprefix("Example: ")
    return ""


def render_examples(root: Path | None, wanted: str | None) -> str:
    """The examples, grouped by category, optionally filtered."""
    if root is None:
        return "The examples aren't installed with this copy of the package.\n"
    described = example_descriptions(root)
    selected: list[str]
    if wanted and wanted in TOPICS_BY_NAME:
        selected = [
            rel for rel in TOPICS_BY_NAME[wanted].examples if rel.endswith(".py")
        ]
    elif wanted:
        lowered = wanted.lower()
        selected = [
            rel
            for rel, (category, text) in described.items()
            if lowered in rel.lower()
            or lowered in text.lower()
            or lowered in category.lower()
        ]
    else:
        selected = list(described)
    if not selected:
        return (
            f"No examples match {wanted!r}. Run `sw-pydocs examples` for all of them.\n"
        )
    out = [
        "# Examples",
        "",
        "Run an agent example with `python <path>`, or inspect it without a call: "
        "`swaig-test <path> --list-tools` or `--dump-swml`.",
        "",
    ]
    by_category: dict[str, list[str]] = {}
    for rel in selected:
        category = described.get(rel, ("Other", ""))[0]
        by_category.setdefault(category, []).append(rel)
    for category, rels in by_category.items():
        out += [f"## {category}", ""]
        out += [_file_line(root, rel, described.get(rel, ("", ""))[1]) for rel in rels]
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def _render_skills(args: list[str]) -> str:
    from signalwire.skills.registry import skill_registry

    if args:
        return _render_skill(args[0])
    skills = sorted(skill_registry.list_skills(), key=lambda s: str(s["name"]))
    out = [f"## Built-in skills ({len(skills)})", ""]
    for skill in skills:
        needs = [
            *skill.get("required_env_vars", []),
            *skill.get("required_packages", []),
        ]
        extra = f" Needs: {', '.join(needs)}." if needs else ""
        many = (
            " Allows several instances."
            if skill.get("supports_multiple_instances")
            else ""
        )
        out.append(
            f"- `{skill['name']}`: {skill['description']}.{extra}{many}".replace(
                "..", "."
            )
        )
    return "\n".join(out) + "\n"


def _render_skill(name: str) -> str:
    from signalwire.skills.registry import skill_registry

    skill_class: Any = skill_registry.get_skill_class(name)
    if skill_class is None:
        return f"## Skill {name!r}\n\nNo built-in skill has that name.\n"
    out = [f"## Skill `{name}`", "", str(skill_class.SKILL_DESCRIPTION), ""]
    readme = package_dir() / "skills" / name / "README.md"
    if readme.is_file():
        out += [f"README: {readme}", ""]
    out += ["Parameters, for `add_skill(name, {...})`:", ""]
    schema: dict[str, dict[str, Any]] = skill_class.get_parameter_schema()
    for param, spec in sorted(schema.items()):
        details = [str(spec.get("type", "any"))]
        if spec.get("required"):
            details.append("required")
        elif "default" in spec:
            details.append(f"default {spec['default']!r}")
        out.append(f"- `{param}` ({', '.join(details)}): {spec.get('description', '')}")
    return "\n".join(out) + "\n"


def _render_prefabs(args: list[str]) -> str:
    import signalwire.prefabs as prefabs

    out = ["## Prefabs", ""]
    for name in prefabs.__all__:
        cls = getattr(prefabs, name)
        doc = (inspect.getdoc(cls) or "").split("\n\n")[0].replace("\n", " ")
        out += [
            f"### {name}",
            "",
            doc,
            "",
            "```python",
            f"{name}{_api.signature(cls)}",
            "```",
            "",
        ]
    return "\n".join(out)


def _render_rest(args: list[str]) -> str:
    from signalwire.rest import RestClient

    # Placeholder credentials: listing the namespaces sends no request
    client = RestClient(project="-", token="-", host="example.signalwire.com")  # noqa: S106
    out = ["## Namespaces", ""]
    for name in sorted(n for n in vars(client) if not n.startswith("_")):
        namespace = getattr(client, name)
        members = sorted(n for n in dir(namespace) if not n.startswith("_"))
        out.append(f"- `client.{name}`: {', '.join(members)}")
    return "\n".join(out) + "\n"


def _render_env(args: list[str]) -> str:
    found: dict[str, set[str]] = {}
    base = package_dir()
    for path in sorted(base.rglob("*.py")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for match in _ENV_NAME.finditer(_ALL_LIST.sub("", text)):
            found.setdefault(match.group(1), set()).add(
                path.relative_to(base.parent).as_posix()
            )
    names = sorted(found)
    out = [
        f"## Environment variables in the installed code ({len(names)})",
        "",
        "Found in the package's source, with the files that use them; those files say "
        "what each one does.",
        "",
    ]
    for name in names:
        files = sorted(found[name])
        shown = ", ".join(files[:3]) + (
            f" and {len(files) - 3} more" if len(files) > 3 else ""
        )
        out.append(f"- `{name}`: {shown}")
    return "\n".join(out) + "\n"


def installed_commands() -> list[str]:
    """The commands the installed distribution defines.

    A source checkout run without reinstalling can have older metadata, so
    unless the metadata's version matches the code's, the known list is used.
    """
    try:
        dist = importlib.metadata.distribution(DIST_NAME)
    except importlib.metadata.PackageNotFoundError:
        return sorted(COMMAND_SUMMARIES)
    if dist.version != version():
        return sorted(COMMAND_SUMMARIES)
    names = sorted(ep.name for ep in dist.entry_points if ep.group == "console_scripts")
    return names or sorted(COMMAND_SUMMARIES)


def _render_cli(args: list[str]) -> str:
    out = ["## Commands", ""]
    out += [
        f"- `{name}`: {COMMAND_SUMMARIES.get(name, 'run it with --help')}"
        for name in installed_commands()
    ]
    return "\n".join(out) + "\n"


_LIVE = {
    "skills": _render_skills,
    "prefabs": _render_prefabs,
    "rest": _render_rest,
    "env": _render_env,
    "cli": _render_cli,
}


def render_llms_txt() -> str:
    """The package's llms.txt: the docs, by group, relative to the package.

    tests/unit/cli/test_pydocs.py checks that signalwire/signalwire/llms.txt
    matches this. To regenerate it, from the repository root:
    ``python -c "from signalwire.cli.pydocs._render import render_llms_txt;
    print(render_llms_txt(), end='')" > signalwire/signalwire/llms.txt``
    """
    out = [
        "# SignalWire SDK for Python",
        "",
        "> Build AI voice agents, control live calls over WebSocket (RELAY), and manage "
        "SignalWire resources over REST. The documentation for the installed version "
        "ships with the package.",
        "",
        "Run `sw-pydocs` for a map of the SDK, `sw-pydocs <topic>` for an area, and "
        "`sw-pydocs api <name>` for signatures read from the installed code. The links "
        "below are relative to this file, in the installed package.",
        "",
    ]
    seen: set[str] = set()
    for group, names in TOPIC_GROUPS:
        entries = []
        for name in names:
            for rel, purpose in TOPICS_BY_NAME[name].docs:
                if rel not in seen:
                    seen.add(rel)
                    entries.append(f"- [{rel}](_docs/{rel}): {purpose}")
        if entries:
            out += [f"## {group}", "", *entries, ""]
    return "\n".join(out).rstrip() + "\n"
