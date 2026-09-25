"""
swaig-test's --aws-api-gateway-id and --aws-stage options (B21).

They were parsed and never used. In Lambda simulation they now set the
function URL an API Gateway deployment presents,
https://ID.execute-api.REGION.amazonaws.com/STAGE, which the SDK reads
from AWS_LAMBDA_FUNCTION_URL.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def _swaig_test(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603  # fixed arguments: this interpreter and the CLI module
        [
            sys.executable,
            "-m",
            "signalwire.cli.swaig_test_wrapper",
            str(REPO / "examples" / "simple_agent.py"),
            "--simulate-serverless",
            "lambda",
            *args,
            "--dump-swml",
            "--raw",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_api_gateway_url_is_used_for_webhooks() -> None:
    completed = _swaig_test(
        "--aws-api-gateway-id",
        "abc123",
        "--aws-region",
        "us-west-2",
        "--aws-stage",
        "dev",
    )
    assert "abc123.execute-api.us-west-2.amazonaws.com/dev/" in completed.stdout


def test_stage_defaults_to_prod() -> None:
    completed = _swaig_test("--aws-api-gateway-id", "abc123")
    assert "abc123.execute-api.us-east-1.amazonaws.com/prod/" in completed.stdout


def test_stage_without_gateway_id_warns() -> None:
    completed = _swaig_test("--aws-stage", "dev")
    assert "--aws-stage only applies with --aws-api-gateway-id" in completed.stderr
