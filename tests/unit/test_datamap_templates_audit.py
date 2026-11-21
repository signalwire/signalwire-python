"""
Guard the DataMap template corrections of cloud-product issues 21197 and 22588.

Scans docs/*.md, the examples and the package sources (not the tests) for
templates that the platform doesn't expand as written:

- ${response.x}: a webhook's output reads the response's fields from the root.
- ${enc:url:x}: there is no enc:url helper.
- @{strftime ...}: the function is strftime_tz.
- ?q=${args.x}: an argument in a URL query string must be encoded.
- ${args.x} in a webhook's output, foreach or expressions: the arguments are
  ${input.args.x} there.
- ${x} for a declared argument where the template reads the call data: the
  arguments are under args.

Prose is scanned in the docs. A line that warns about one of these forms on
purpose carries the warning marker, which Markdown doesn't render; a source
line carries it as a comment. Docstrings and comments in the sources are not
scanned.
"""

import ast
import contextlib
import json
import re
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
WARNING_MARKER = "datamap-audit: warning"

TEXT_RULES = [
    (re.compile(r"[$%]\{response\."), "a webhook's output reads the response's fields from the root; there is no response. prefix"),
    (re.compile(r"\$\{enc:url:"), "there is no enc:url helper; write ${enc:args.x}"),
    (re.compile(r"@\{strftime "), "there is no strftime function; write @{strftime_tz <zone> <format>}"),
    (re.compile(r"[?&][A-Za-z0-9_]+=[$%]\{args\."), "an argument in a URL query string must be encoded: ${enc:args.x}"),
]

# ${args.x}, with or without helpers such as enc:, but not ${input.args.x}
WEBHOOK_ARGS = re.compile(r"[$%]\{(?:[a-z_]+:)*args\.")
WEBHOOK_ARGS_WHY = "${args.x} is empty in a webhook's output, foreach and expressions; write ${input.args.x}"

Report = Callable[[str, str, str], None]  # (where, why, text)


def _bare_why(name: str) -> str:
    return f"the argument {name!r} is under args here; write ${{args.{name}}}"


def _bare_findings(text: str, params: list[str]) -> list[str]:
    """Why text reads a declared argument without args, once per argument."""
    return [
        _bare_why(name)
        for name in params
        if re.search(r"[$%]\{(?:[a-z_]+:)*" + re.escape(name) + r"[}.\[]", text)
    ]


# --- Markdown -------------------------------------------------------------


def scan_markdown(path: Path, report: Report) -> None:
    """Check every line against TEXT_RULES, and each JSON or Python code block."""
    in_fence, lang, start = False, "", 0
    block: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), start=1):
        if WARNING_MARKER not in line:
            for rule, why in TEXT_RULES:
                if rule.search(line):
                    report(f"{path}:{number}", why, line)
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_fence:
                in_fence, lang, start, block = True, stripped[3:].strip(), number + 1, []
                continue
            in_fence = False
            body = "\n".join(block)
            where = f"{path}:{start}"

            def json_report(why: str, text: str, where: str = where) -> None:
                report(where, why, text)

            with contextlib.suppress(ValueError):  # not JSON, or a JSON excerpt
                walk_json(json.loads(body), [], json_report)
            if lang == "python":
                scan_python_snippet(path, start, body, report)
            continue
        if in_fence:
            block.append(line)


def walk_json(value: Any, params: list[str], report: Callable[[str, str], None]) -> None:
    """Check each object with "webhooks" as a data_map.

    The parameters are those of the nearest enclosing function definition.
    """
    if isinstance(value, dict):
        props = value.get("parameters", {})
        if isinstance(props, dict) and isinstance(props.get("properties"), dict):
            params = list(props["properties"])
        if "webhooks" in value:
            check_json_data_map(value, params, report)
        for child in value.values():
            walk_json(child, params, report)
    elif isinstance(value, list):
        for child in value:
            walk_json(child, params, report)


def _json_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _json_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _json_strings(child)


def check_json_data_map(data_map: dict[str, Any], params: list[str], report: Callable[[str, str], None]) -> None:
    webhooks = data_map.get("webhooks")
    for webhook in webhooks if isinstance(webhooks, list) else []:
        if not isinstance(webhook, dict):
            continue
        for key in ("output", "foreach", "expressions"):
            for text in _json_strings(webhook.get(key)):
                if WEBHOOK_ARGS.search(text):
                    report(WEBHOOK_ARGS_WHY, text)
        for key in ("url", "params"):
            for text in _json_strings(webhook.get(key)):
                for why in _bare_findings(text, params):
                    report(why, text)
    for key in ("output", "expressions"):
        for text in _json_strings(data_map.get(key)):
            for why in _bare_findings(text, params):
                report(why, text)


# --- Python ---------------------------------------------------------------


def _docstrings(tree: ast.AST) -> set[int]:
    """The ids of the docstring nodes, which are prose and not scanned."""
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                ids.add(id(body[0].value))
    return ids


def _strings(node: ast.AST) -> Iterator[tuple[int, str]]:
    """The string constants under a node, with their line numbers.

    The arguments of a .replace() call are left out: they rewrite a template
    on purpose, such as ${args. into ${input.args.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        yield node.lineno, node.value
        return
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "replace":
        yield from _strings(node.func.value)
        return
    for child in ast.iter_child_nodes(node):
        yield from _strings(child)


def _string_value(node: ast.AST | None) -> str:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else ""


def _dict_keys(node: ast.AST | None) -> list[str]:
    if not isinstance(node, ast.Dict):
        return []
    return [key for key in (_string_value(k) for k in node.keys if k is not None) if key]


def _argument(call: ast.Call, position: int, name: str) -> ast.AST | None:
    """A call's argument by position or by keyword."""
    if position < len(call.args):
        return call.args[position]
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    return None


def _call_name(call: ast.Call) -> str:
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    if isinstance(call.func, ast.Name):
        return call.func.id
    return ""


def check_python_ast(tree: ast.AST, report: Callable[[int, str, str], None]) -> None:
    """Apply the data_map rules to a dict literal under a "webhooks" key (as
    the built-in skills write it), and to a chain of DataMap builder calls."""
    in_chain: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values, strict=True):
                if key is not None and _string_value(key) == "webhooks":
                    check_webhooks_literal(value, report)
        elif isinstance(node, ast.Call) and id(node) not in in_chain:
            calls: list[ast.Call] = []
            current: ast.expr | None = node
            while isinstance(current, ast.Call):
                calls.insert(0, current)
                in_chain.add(id(current))
                current = current.func.value if isinstance(current.func, ast.Attribute) else None
            check_builder_chain(calls, report)


def check_webhooks_literal(node: ast.AST, report: Callable[[int, str, str], None]) -> None:
    """Report ${args.x} in the output, foreach and expressions of each webhook
    in a webhooks list literal."""
    if not isinstance(node, ast.List):
        return
    for webhook in node.elts:
        if not isinstance(webhook, ast.Dict):
            continue
        for key, value in zip(webhook.keys, webhook.values, strict=True):
            if key is not None and _string_value(key) in ("output", "foreach", "expressions"):
                for lineno, text in _strings(value):
                    if WEBHOOK_ARGS.search(text):
                        report(lineno, WEBHOOK_ARGS_WHY, text)


def check_builder_chain(calls: list[ast.Call], report: Callable[[int, str, str], None]) -> None:
    params: list[str] = []
    in_webhook = False

    def bare(nodes: list[ast.AST | None]) -> None:
        for node in nodes:
            for lineno, text in _strings(node) if node is not None else []:
                for why in _bare_findings(text, params):
                    report(lineno, why, text)

    def webhook_args(nodes: list[ast.AST | None]) -> None:
        for node in nodes:
            for lineno, text in _strings(node) if node is not None else []:
                if WEBHOOK_ARGS.search(text):
                    report(lineno, WEBHOOK_ARGS_WHY, text)

    for call in calls:
        name = _call_name(call)
        arguments: list[ast.AST | None] = [*call.args, *(k.value for k in call.keywords)]
        if name == "create_simple_api_tool":  # (name, url, response_template, parameters, ...)
            params += _dict_keys(_argument(call, 3, "parameters"))
            in_webhook = True
            bare([_argument(call, 1, "url")])
            webhook_args([_argument(call, 2, "response_template")])
        elif name == "create_expression_tool":  # (name, patterns, parameters)
            params += _dict_keys(_argument(call, 2, "parameters"))
            bare([_argument(call, 1, "patterns")])
        elif name == "parameter":
            if param := _string_value(_argument(call, 0, "name")):
                params.append(param)
        elif name == "webhook":
            in_webhook = True
            bare([_argument(call, 1, "url")])
        elif name in ("params", "body", "expression", "fallback_output"):
            bare(arguments)
        elif name in ("output", "foreach", "webhook_expressions") and in_webhook:
            webhook_args(arguments)


def scan_python_file(path: Path, report: Report) -> None:
    source = path.read_text(encoding="utf-8")
    lines = source.split("\n")
    tree = ast.parse(source, filename=str(path))
    docstrings = _docstrings(tree)

    def marked(lineno: int) -> bool:
        return WARNING_MARKER in lines[lineno - 1]

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            if any(marked(n) for n in range(node.lineno, (node.end_lineno or node.lineno) + 1)):
                continue
            for rule, why in TEXT_RULES:
                if rule.search(node.value):
                    report(f"{path}:{node.lineno}", why, node.value)
    check_python_ast(tree, lambda lineno, why, text: report(f"{path}:{lineno}", why, text))


def scan_python_snippet(path: Path, start: int, body: str, report: Report) -> None:
    """Check a Python code block from the docs with the builder rules.

    One that doesn't parse (an excerpt, say) is left to the text rules.
    """
    try:
        tree = ast.parse(body)
    except SyntaxError:
        return
    check_python_ast(tree, lambda lineno, why, text: report(f"{path}:{start + lineno - 1}", why, text))


# --- Tests ----------------------------------------------------------------


def _source_files() -> Iterator[Path]:
    for path in sorted((ROOT / "examples").rglob("*.py")):
        yield path
    for path in sorted((ROOT / "signalwire" / "signalwire").rglob("*.py")):
        yield path


def test_datamap_templates() -> None:
    findings: list[str] = []

    def report(where: str, why: str, text: str) -> None:
        findings.append(f"{where}: {why}: {text.strip()!r}")

    docs = sorted((ROOT / "docs").glob("*.md"))
    assert docs, f"no docs found under {ROOT / 'docs'}"
    for path in docs:
        scan_markdown(path, report)
    for path in _source_files():
        scan_python_file(path, report)

    assert not findings, "\n".join(findings)


def test_datamap_templates_finds_each_rule(tmp_path: Path) -> None:
    """Each rule reports its sample, and a marked warning line passes."""
    doc = "\n".join([
        f"There's no `${{enc:url:x}}`. <!-- {WARNING_MARKER} -->",
        "- Built-in functions: `@{strftime %Y-%m-%d}`",
        "```json",
        json.dumps({
            "function": "f",
            "parameters": {"properties": {"query": {"type": "string"}}},
            "data_map": {
                "webhooks": [{
                    "url": "https://example.com/s?q=${args.query}&p=${query}",
                    "output": {"response": "${response.total} for ${args.query}"},
                }],
                "output": {"response": "No ${enc:url:args.query}"},
            },
        }, indent=2),
        "```",
        "```python",
        'dm = (DataMap("f")',
        '    .parameter("city", "string", "City", required=True)',
        '    .webhook("GET", "https://example.com/w/${city}")',
        '    .output(FunctionResult("Weather in ${args.city}")))',
        'tool = create_simple_api_tool(name="g", url="https://example.com/g/${zip}",',
        '    response_template="Zip ${args.zip}", parameters={"zip": {"type": "string"}})',
        "```",
        "",
    ])
    path = tmp_path / "sample.md"
    path.write_text(doc, encoding="utf-8")

    found: dict[str, int] = {}
    scan_markdown(path, lambda _, why, __: found.__setitem__(why, found.get(why, 0) + 1))

    expected = {
        TEXT_RULES[0][1]: 1,  # ${response.total}
        TEXT_RULES[1][1]: 1,  # ${enc:url:args.query} in the block; the marked line passes
        TEXT_RULES[2][1]: 1,  # @{strftime
        TEXT_RULES[3][1]: 1,  # ?q=${args.query}
        WEBHOOK_ARGS_WHY: 3,  # the JSON output, and the two Python outputs
        _bare_why("query"): 1,
        _bare_why("city"): 1,
        _bare_why("zip"): 1,
    }
    assert found == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        # A string the platform would see is scanned; a docstring isn't
        ('"""Not ${response.x}."""\nURL = "https://x/?q=${args.q}"\n', [TEXT_RULES[3][1]]),
        # A marked line passes
        (f'HINT = "write ${{x}}, not ${{response.x}}"  # {WARNING_MARKER}\n', []),
        # A webhooks literal: the output is checked, but not inside a call
        (
            'T = {"webhooks": [{"output": {"response": "${args.q}"},'
            ' "expressions": [{"output": {"response": msg.replace("${args.", "${input.args.")}}]}]}\n',
            [WEBHOOK_ARGS_WHY],
        ),
    ],
)
def test_datamap_templates_python_sources(tmp_path: Path, source: str, expected: list[str]) -> None:
    path = tmp_path / "sample.py"
    path.write_text(source, encoding="utf-8")
    found: list[str] = []
    scan_python_file(path, lambda _, why, __: found.append(why))
    assert found == expected
