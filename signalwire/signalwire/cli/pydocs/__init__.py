"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

sw-pydocs: the SDK's documentation, from the installed package.

Written for people and for coding agents. With no arguments it prints an
index; each topic lists the concepts, the installed files to read, examples
and API names; ``api`` reads signatures and docstrings from the installed
code, so the answers always match the installed version.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

USAGE = """\
usage: sw-pydocs [<topic> [name] | <command> ...]

  sw-pydocs                      the index: what the SDK does, where to start
  sw-pydocs <topic>              one area: concepts, files to read, examples, API
  sw-pydocs topics               every topic, one line each
  sw-pydocs api <name>           signature, docstring and members of a name
  sw-pydocs examples [filter]    examples with descriptions and paths
  sw-pydocs grep <regex>         search the installed docs and examples
  sw-pydocs show <file>          print a doc (--toc for headings, --section <heading>)
  sw-pydocs path [file]          where the docs are, or one file's full path
  sw-pydocs init [--skill]       add a note about sw-pydocs to AGENTS.md
  sw-pydocs --version            the installed SDK version
"""

_COMMANDS = ("topics", "api", "examples", "grep", "show", "path", "init", "help")


def _out(text: str) -> int:
    """Write ``text`` to stdout, ending it with a newline, and return exit status 0."""
    sys.stdout.write(text if text.endswith("\n") else text + "\n")
    return 0


def _err(text: str, code: int = 1) -> int:
    """Write ``text`` to stderr, ending it with a newline, and return ``code``."""
    sys.stderr.write(text if text.endswith("\n") else text + "\n")
    return code


def _cmd_api(argv: list[str]) -> int:
    """Run ``sw-pydocs api``: print a name's signature and docstring."""
    from . import _api

    parser = argparse.ArgumentParser(
        prog="sw-pydocs api", description="Show an SDK name's signature and docstring."
    )
    parser.add_argument(
        "name",
        help="such as AgentBase, FunctionResult.connect or signalwire.relay.Call",
    )
    args = parser.parse_args(argv)
    found = _api.resolve(args.name)
    if not found:
        hint = _api.suggestions(args.name)
        more = f" Similar names: {', '.join(hint)}." if hint else ""
        return _err(
            f"No SDK name {args.name!r} found.{more} Try `sw-pydocs grep {args.name}`."
        )
    if len(found) > 1:
        names = "\n".join(
            f"- `{item.name}`: {_api.summary(item.obj)}" for item in found[1:]
        )
        return _out(_api.render(found[0]) + f"\n## Other matches\n\n{names}\n")
    return _out(_api.render(found[0]))


def _cmd_examples(argv: list[str]) -> int:
    """Run ``sw-pydocs examples``: list the installed examples, optionally filtered."""
    from ._bundle import docs_root
    from ._render import render_examples

    parser = argparse.ArgumentParser(
        prog="sw-pydocs examples", description="List the installed examples."
    )
    parser.add_argument("filter", nargs="?", help="a topic name, or a word to look for")
    args = parser.parse_args(argv)
    return _out(render_examples(docs_root(), args.filter))


def _cmd_grep(argv: list[str]) -> int:
    """Run ``sw-pydocs grep``: search the docs, examples and optionally code."""
    from ._bundle import docs_root
    from ._files import all_doc_files, grep, package_dir, source_files

    parser = argparse.ArgumentParser(
        prog="sw-pydocs grep", description="Search the installed docs and examples."
    )
    parser.add_argument("pattern", help="a regular expression, matched ignoring case")
    parser.add_argument(
        "--code", action="store_true", help="also search the SDK's source code"
    )
    parser.add_argument(
        "--limit", type=int, default=100, help="most lines to print (default 100)"
    )
    args = parser.parse_args(argv)
    try:
        pattern = re.compile(args.pattern, re.IGNORECASE)
    except re.error as e:
        return _err(f"Invalid regular expression: {e}", 2)
    root = docs_root()
    files = all_doc_files(root)
    if args.limit < 1:
        return _err("--limit must be 1 or more.", 2)
    if args.code:
        base = package_dir()
        for path in source_files():
            files["signalwire/" + path.relative_to(base).as_posix()] = path
    matches, total = grep(pattern, files, args.limit)
    if not matches:
        return _err(f"No matches for {args.pattern!r}.")
    lines = [f"{files[m.rel]}:{m.line}: {m.text}" for m in matches]
    if total > len(matches):
        lines.append(
            f"... {total - len(matches)} more; narrow the pattern or raise --limit."
        )
    return _out("\n".join(lines))


def _cmd_show(argv: list[str]) -> int:
    """Run ``sw-pydocs show``: print an installed doc, its headings, or one section."""
    from ._bundle import docs_root
    from ._files import all_doc_files, headings, is_text, resolve, section

    parser = argparse.ArgumentParser(
        prog="sw-pydocs show", description="Print an installed doc."
    )
    parser.add_argument(
        "file", help="a path from sw-pydocs, a file name, or a name such as agent_guide"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--toc", action="store_true", help="list the headings, with line numbers"
    )
    group.add_argument(
        "--section",
        metavar="HEADING",
        help="print the first section whose heading contains this",
    )
    args = parser.parse_args(argv)
    files = all_doc_files(docs_root())
    matches = resolve(args.file, files)
    if not matches:
        return _err(
            f"No installed doc matches {args.file!r}. `sw-pydocs grep` searches their text."
        )
    if len(matches) > 1:
        listing = "\n".join(f"- {m}" for m in matches[:20])
        return _err(f"{args.file!r} matches several docs; name one:\n{listing}")
    rel = matches[0]
    if not is_text(rel):
        return _err(f"{files[rel]} isn't a text file.")
    text = files[rel].read_text(encoding="utf-8")
    if args.toc:
        marks = headings(text)
        if not marks:
            return _out(f"{files[rel]} has no headings.")
        return _out(
            "\n".join(f"{m.line:>6}  {'  ' * (m.level - 1)}{m.text}" for m in marks)
        )
    if args.section:
        found = section(text, args.section)
        if found is None:
            return _err(
                f"No heading in {rel} contains {args.section!r}. `--toc` lists them."
            )
        heading, body = found
        return _out(f"<!-- {files[rel]}:{heading.line} -->\n{body}")
    return _out(text)


def _cmd_path(argv: list[str]) -> int:
    """Run ``sw-pydocs path``: print where the docs, or one doc file, are installed."""
    from ._bundle import docs_root
    from ._files import all_doc_files, resolve

    parser = argparse.ArgumentParser(
        prog="sw-pydocs path", description="Print where the docs are installed."
    )
    parser.add_argument("file", nargs="?", help="print this file's full path instead")
    args = parser.parse_args(argv)
    root = docs_root()
    if args.file is None:
        if root is None:
            return _err("The docs aren't installed with this copy of the package.")
        return _out(str(root))
    files = all_doc_files(root)
    matches = resolve(args.file, files)
    if not matches:
        return _err(f"No installed doc matches {args.file!r}.")
    return _out("\n".join(str(files[m]) for m in matches[:20]))


def _cmd_init(argv: list[str]) -> int:
    """Run ``sw-pydocs init``: add the sw-pydocs note to a project."""
    from ._agents_note import init, note

    parser = argparse.ArgumentParser(
        prog="sw-pydocs init",
        description="Add a note about sw-pydocs to a project's AGENTS.md, so coding agents start there.",
    )
    parser.add_argument(
        "--dir", default=".", help="the project directory (default: the current one)"
    )
    parser.add_argument(
        "--skill",
        action="store_true",
        help="also write an Agent Skills SKILL.md in .agents/ and .claude/",
    )
    parser.add_argument(
        "--print",
        dest="print_only",
        action="store_true",
        help="print the note; change nothing",
    )
    args = parser.parse_args(argv)
    if args.print_only:
        return _out(note())
    project = Path(args.dir)
    if not project.is_dir():
        return _err(f"{project} isn't a directory.", 2)
    changes = init(project, skill=args.skill)
    return _out("\n".join(f"{how}: {path}" for path, how in changes))


def _cmd_topic(name: str, argv: list[str]) -> int:
    """Print the topic page ``name``."""
    from ._bundle import docs_root
    from ._render import render_topic
    from ._topics import TOPICS_BY_NAME

    return _out(render_topic(TOPICS_BY_NAME[name], docs_root(), argv))


def _unknown(word: str, argv: list[str]) -> int:
    """Try the word as an API name, then as a doc, before giving up."""
    from . import _api
    from ._bundle import docs_root
    from ._files import all_doc_files, resolve
    from ._topics import TOPICS_BY_NAME

    if _api.resolve(word):
        sys.stdout.write(
            f"<!-- `{word}` isn't a topic; this is `sw-pydocs api {word}` -->\n"
        )
        return _cmd_api([word])
    if resolve(word, all_doc_files(docs_root())):
        sys.stdout.write(
            f"<!-- `{word}` isn't a topic; this is `sw-pydocs show {word}` -->\n"
        )
        return _cmd_show([word, *argv])
    import difflib

    close = difflib.get_close_matches(
        word, [*TOPICS_BY_NAME, *_COMMANDS], n=3, cutoff=0.5
    )
    more = f" Did you mean: {', '.join(close)}?" if close else ""
    return _err(
        f"No topic, command, SDK name or doc called {word!r}.{more} Run `sw-pydocs` for the index.",
        2,
    )


def main(argv: list[str] | None = None) -> int:
    """Run sw-pydocs; return the exit status."""
    args = list(sys.argv[1:] if argv is None else argv)
    from ._topics import TOPICS_BY_NAME

    if not args:
        from ._bundle import docs_root
        from ._render import render_index

        return _out(render_index(docs_root()))
    first, rest = args[0], args[1:]
    if first in ("-h", "--help", "help"):
        return _out(USAGE)
    if first == "--version":
        from ._render import version

        return _out(version())
    if first in TOPICS_BY_NAME:
        return _cmd_topic(first, rest)
    handlers = {
        "api": _cmd_api,
        "examples": _cmd_examples,
        "grep": _cmd_grep,
        "show": _cmd_show,
        "path": _cmd_path,
        "init": _cmd_init,
    }
    if first == "topics":
        from ._render import render_topic_list

        return _out(render_topic_list())
    if first in handlers:
        return handlers[first](rest)
    if first.startswith("-"):
        return _err(f"Unknown option {first!r}.\n{USAGE}", 2)
    return _unknown(first, rest)


def console_main() -> None:
    """The ``sw-pydocs`` command."""
    try:
        code = main()
        # Flush here, so a reader that stopped early fails inside this block
        sys.stdout.flush()
    except BrokenPipeError:
        # Output piped to a command that stopped reading, such as head. Point
        # stdout at the null device so Python's flush at exit can't fail again.
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)
    sys.exit(code)
