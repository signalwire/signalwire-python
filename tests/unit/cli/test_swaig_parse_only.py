"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for the ``swaig-test`` ``--parse-only`` / ``--dry-run`` flag.

Contract (canonical reference form mirrored by every SDK port):
- ``--parse-only`` (alias ``--dry-run``) validates the invocation's arguments and
  exits WITHOUT loading the agent, touching the filesystem, or making a network
  request.
- Valid arguments -> prints exactly ``parse OK`` and returns 0.
- Invalid arguments (unknown flag, missing required positional, mutually-exclusive
  flags) -> non-zero exit (argparse usage error is exit code 2).
- Position-independent: works whether it precedes or follows ``--exec`` (``--exec``
  otherwise swallows every trailing token as a function argument).
- Never checks whether the agent file exists on disk -- a syntactically valid
  invocation naming a non-existent file still reports ``parse OK``.
"""

import sys  # noqa: E402

import pytest  # noqa: E402

from signalwire.cli.test_swaig import main  # noqa: E402


def _run(argv: list[str], monkeypatch: pytest.MonkeyPatch) -> int:
    """Invoke swaig-test main() with the given argv (excluding argv[0])."""
    monkeypatch.setattr(sys, "argv", ["swaig-test", *argv])
    return main()


class TestParseOnlyValid:
    def test_valid_invocation_returns_zero_and_prints_parse_ok(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        rc = _run(["examples/my_agent.py", "--list-tools", "--parse-only"], monkeypatch)
        out = capsys.readouterr().out
        assert rc == 0
        assert out.strip() == "parse OK"

    def test_dry_run_is_an_exact_alias(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        rc = _run(["examples/my_agent.py", "--dump-swml", "--dry-run"], monkeypatch)
        out = capsys.readouterr().out
        assert rc == 0
        assert out.strip() == "parse OK"

    def test_does_not_require_the_agent_file_to_exist(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # File existence is a runtime concern, not an argument-validity concern.
        rc = _run(
            ["/definitely/not/here.py", "--list-tools", "--parse-only"], monkeypatch
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert out.strip() == "parse OK"
        assert "not found" not in out

    def test_position_independent_after_exec(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # --exec consumes trailing tokens as function args; --parse-only must still
        # be honored when it trails the --exec invocation (where the DOC-CLI gate
        # appends it).
        rc = _run(
            ["examples/my_agent.py", "--exec", "foo", "--param", "v", "--parse-only"],
            monkeypatch,
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert out.strip() == "parse OK"


class TestParseOnlyInvalid:
    def test_unknown_flag_exits_nonzero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with pytest.raises(SystemExit) as exc:
            _run(
                ["examples/my_agent.py", "--parse-only", "--no-such-flag"], monkeypatch
            )
        assert exc.value.code != 0

    def test_missing_required_positional_exits_nonzero(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        with pytest.raises(SystemExit) as exc:
            _run(["--parse-only"], monkeypatch)
        assert exc.value.code != 0

    def test_mutually_exclusive_flags_rejected_under_parse_only(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # --route and --agent-class cannot both be supplied; --parse-only does not
        # soften this validation.
        with pytest.raises(SystemExit) as exc:
            _run(
                [
                    "examples/my_agent.py",
                    "--route",
                    "/x",
                    "--agent-class",
                    "Y",
                    "--parse-only",
                ],
                monkeypatch,
            )
        assert exc.value.code != 0
