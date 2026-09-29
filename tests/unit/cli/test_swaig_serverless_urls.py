"""
swaig-test's serverless presets and function URL flags.

The Lambda preset's function URL hid --aws-function-name and --aws-region,
so the --help-platforms example printed a us-east-1 URL. The Azure preset
named no function, giving /api/unknown. --gcp-function-url and
--azure-function-url set FUNCTION_URL and AZURE_FUNCTION_URL, which the SDK
never read. The SDK now reads both, and swaig-test leaves the preset's URL
out when the user sets the parts the URL is built from.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from signalwire.cli.simulation.mock_env import ServerlessSimulator
from signalwire.cli.test_swaig import _preset_vars_to_omit
from signalwire.core.agent_base import AgentBase

REPO = Path(__file__).resolve().parents[3]

# Variables that select another execution mode, cleared before each URL test
_MODE_VARS = (
    "GATEWAY_INTERFACE",
    "AWS_LAMBDA_FUNCTION_NAME",
    "LAMBDA_TASK_ROOT",
    "FUNCTION_TARGET",
    "K_SERVICE",
    "GOOGLE_CLOUD_PROJECT",
    "GCP_PROJECT",
    "AZURE_FUNCTIONS_ENVIRONMENT",
    "FUNCTIONS_WORKER_RUNTIME",
    "AzureWebJobsStorage",
    "FUNCTION_URL",
    "AZURE_FUNCTION_URL",
    "AZURE_FUNCTION_NAME",
    "WEBSITE_SITE_NAME",
    "SWML_PROXY_URL_BASE",
)


def _swaig_test(platform: str, *args: str) -> str:
    completed = subprocess.run(  # noqa: S603  # fixed argv: this interpreter and a repo example
        [
            sys.executable,
            "-m",
            "signalwire.cli.swaig_test_wrapper",
            str(REPO / "examples" / "simple_agent.py"),
            "--simulate-serverless",
            platform,
            *args,
            "--dump-swml",
            "--raw",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return completed.stdout


def _agent_url(monkeypatch: pytest.MonkeyPatch, env: dict[str, str]) -> str:
    for var in _MODE_VARS:
        monkeypatch.delenv(var, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    agent = AgentBase(name="url_test", route="/", schema_validation=False)
    agent._proxy_url_base = None
    return agent.get_full_url()


class TestPresetUrlOmission:
    def test_lambda_parts_without_url_omit_preset_url(self) -> None:
        overrides = {
            "AWS_LAMBDA_FUNCTION_NAME": "prod-agent",
            "AWS_REGION": "us-west-2",
        }
        assert _preset_vars_to_omit("lambda", overrides) == ["AWS_LAMBDA_FUNCTION_URL"]

    def test_lambda_explicit_url_keeps_it(self) -> None:
        overrides = {
            "AWS_REGION": "us-west-2",
            "AWS_LAMBDA_FUNCTION_URL": "https://u1.lambda-url.us-west-2.on.aws/",
        }
        assert _preset_vars_to_omit("lambda", overrides) == []

    def test_lambda_no_overrides_keeps_preset(self) -> None:
        assert _preset_vars_to_omit("lambda", {}) == []

    def test_cloud_function_parts_without_url_omit_preset_url(self) -> None:
        assert _preset_vars_to_omit("cloud_function", {"K_SERVICE": "svc"}) == [
            "FUNCTION_URL"
        ]

    def test_a_part_under_its_other_name_omits_the_preset_name(self) -> None:
        # The SDK prefers GOOGLE_CLOUD_PROJECT to GCP_PROJECT, and K_SERVICE
        # to FUNCTION_TARGET, which the preset sets
        assert _preset_vars_to_omit(
            "cloud_function", {"GCP_PROJECT": "production"}
        ) == ["FUNCTION_URL", "GOOGLE_CLOUD_PROJECT"]
        assert _preset_vars_to_omit(
            "cloud_function", {"FUNCTION_TARGET": "handler"}
        ) == ["FUNCTION_URL", "K_SERVICE"]
        assert _preset_vars_to_omit(
            "azure_function", {"AZURE_FUNCTIONS_APP_NAME": "billing"}
        ) == ["WEBSITE_SITE_NAME"]

    def test_the_preferred_name_given_omits_nothing_more(self) -> None:
        assert _preset_vars_to_omit("azure_function", {"WEBSITE_SITE_NAME": "a"}) == []
        assert _preset_vars_to_omit("cgi", {"HTTP_HOST": "example.com"}) == []


class TestServerlessSimulatorOmit:
    def test_omitted_key_is_left_out_of_the_preset(self) -> None:
        simulator = ServerlessSimulator("lambda", {}, ["AWS_LAMBDA_FUNCTION_URL"])
        assert "AWS_LAMBDA_FUNCTION_URL" not in simulator.preset_env
        assert simulator.preset_env["AWS_LAMBDA_FUNCTION_NAME"] == "test-agent-function"

    def test_omitted_key_is_cleared_and_restored(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AWS_LAMBDA_FUNCTION_URL", "https://from-shell.example.com")
        simulator = ServerlessSimulator("lambda", {}, ["AWS_LAMBDA_FUNCTION_URL"])
        simulator.activate()
        try:
            assert "AWS_LAMBDA_FUNCTION_URL" not in os.environ
        finally:
            simulator.deactivate()
        assert os.environ["AWS_LAMBDA_FUNCTION_URL"] == "https://from-shell.example.com"

    def test_two_argument_constructor_still_works(self) -> None:
        simulator = ServerlessSimulator("lambda", {"AWS_REGION": "eu-west-1"})
        assert simulator.omit == []
        assert simulator.get_current_env()["AWS_REGION"] == "eu-west-1"
        assert simulator.get_current_env()["AWS_LAMBDA_FUNCTION_URL"] == (
            "https://abc123.lambda-url.us-east-1.on.aws/"
        )

    def test_azure_preset_names_the_function(self) -> None:
        preset = ServerlessSimulator.PLATFORM_PRESETS["azure_function"]
        assert preset["AZURE_FUNCTION_NAME"] == "agent"

    def test_cloud_function_preset_sets_function_target(self) -> None:
        preset = ServerlessSimulator.PLATFORM_PRESETS["cloud_function"]
        assert preset["FUNCTION_TARGET"] == "agent"


class TestAgentFunctionUrlVariables:
    def test_function_url_wins_on_google_cloud(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        url = _agent_url(
            monkeypatch,
            {
                "FUNCTION_TARGET": "main",
                "K_SERVICE": "svc",
                "GOOGLE_CLOUD_PROJECT": "p1",
                "FUNCTION_URL": "https://europe-west1-p1.cloudfunctions.net/fn/",
            },
        )
        assert url == "https://europe-west1-p1.cloudfunctions.net/fn"

    def test_google_cloud_url_is_built_without_function_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        url = _agent_url(
            monkeypatch,
            {
                "FUNCTION_TARGET": "main",
                "K_SERVICE": "svc",
                "GOOGLE_CLOUD_PROJECT": "p1",
                "GOOGLE_CLOUD_REGION": "europe-west1",
            },
        )
        assert url == "https://europe-west1-p1.cloudfunctions.net/svc"

    def test_azure_function_url_wins(self, monkeypatch: pytest.MonkeyPatch) -> None:
        url = _agent_url(
            monkeypatch,
            {
                "FUNCTIONS_WORKER_RUNTIME": "python",
                "WEBSITE_SITE_NAME": "my-app",
                "AZURE_FUNCTION_URL": "https://my-app.azurewebsites.net/api/agent/",
            },
        )
        assert url == "https://my-app.azurewebsites.net/api/agent"

    def test_azure_url_is_built_without_function_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        url = _agent_url(
            monkeypatch,
            {
                "FUNCTIONS_WORKER_RUNTIME": "python",
                "WEBSITE_SITE_NAME": "my-app",
                "AZURE_FUNCTION_NAME": "my-func",
            },
        )
        assert url == "https://my-app.azurewebsites.net/api/my-func"


class TestSwaigTestSimulatedUrls:
    def test_help_platforms_lambda_example(self) -> None:
        out = _swaig_test(
            "lambda", "--aws-function-name", "prod-agent", "--aws-region", "us-west-2"
        )
        assert "@prod-agent.lambda-url.us-west-2.on.aws/simple/swaig/" in out
        assert "abc123.lambda-url.us-east-1" not in out

    def test_lambda_default_uses_preset_url(self) -> None:
        out = _swaig_test("lambda")
        assert "@abc123.lambda-url.us-east-1.on.aws/simple/swaig/" in out

    def test_cloud_function_project_given_as_gcp_project(self) -> None:
        out = _swaig_test("cloud_function", "--env", "GCP_PROJECT=production")
        assert "@us-central1-production.cloudfunctions.net/agent/simple/swaig/" in out
        assert "test-project" not in out

    def test_cloud_function_named_by_function_target(self) -> None:
        out = _swaig_test("cloud_function", "--env", "FUNCTION_TARGET=handler")
        assert "@us-central1-test-project.cloudfunctions.net/handler/simple/swaig/" in out

    def test_azure_app_given_as_azure_functions_app_name(self) -> None:
        out = _swaig_test("azure_function", "--env", "AZURE_FUNCTIONS_APP_NAME=billing")
        assert "@billing.azurewebsites.net/api/agent/simple/swaig/" in out

    def test_azure_default_names_the_function(self) -> None:
        out = _swaig_test("azure_function")
        assert "@my-function-app.azurewebsites.net/api/agent/simple/swaig/" in out
        assert "/api/unknown/" not in out

    def test_azure_function_url_flag(self) -> None:
        out = _swaig_test(
            "azure_function",
            "--azure-function-url",
            "https://myapp.azurewebsites.net/api/voice",
        )
        assert "@myapp.azurewebsites.net/api/voice/simple/swaig/" in out

    def test_gcp_function_url_flag(self) -> None:
        out = _swaig_test(
            "cloud_function",
            "--gcp-function-url",
            "https://europe-west1-p1.cloudfunctions.net/fn",
        )
        assert "@europe-west1-p1.cloudfunctions.net/fn/simple/swaig/" in out

    def test_gcp_parts_build_the_url(self) -> None:
        out = _swaig_test(
            "cloud_function",
            "--gcp-project",
            "p1",
            "--gcp-region",
            "europe-west1",
            "--gcp-service",
            "svc",
        )
        assert "@europe-west1-p1.cloudfunctions.net/svc/simple/swaig/" in out
