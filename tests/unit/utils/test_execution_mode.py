"""
Tests for execution-mode detection helpers — ``get_execution_mode``
in ``signalwire.core.logging_config`` and ``is_serverless_mode`` in
``signalwire.utils``. These determine whether the SDK is running as a
long-lived server or in a serverless invocation environment (AWS
Lambda, GCP Cloud Functions, Azure Functions, CGI).

Cross-language SDK contract: every port that adapts to serverless
deployments must check the same environment variables.
"""

import os
from unittest.mock import patch

import pytest


from signalwire.core.logging_config import get_execution_mode
from signalwire.utils import is_serverless_mode


class TestGetExecutionMode:
    def test_default_is_server(self) -> None:
        # Clear all detected env vars; should default to "server".
        env_keys = [
            "GATEWAY_INTERFACE",
            "AWS_LAMBDA_FUNCTION_NAME",
            "LAMBDA_TASK_ROOT",
            "FUNCTION_TARGET",
            "K_SERVICE",
            "GOOGLE_CLOUD_PROJECT",
            "AZURE_FUNCTIONS_ENVIRONMENT",
            "FUNCTIONS_WORKER_RUNTIME",
            "AzureWebJobsStorage",
        ]
        with patch.dict(os.environ, {}, clear=False):
            for k in env_keys:
                os.environ.pop(k, None)
            assert get_execution_mode() == "server"

    def test_cgi_detected_via_gateway_interface(self) -> None:
        with patch.dict(os.environ, {"GATEWAY_INTERFACE": "CGI/1.1"}, clear=False):
            assert get_execution_mode() == "cgi"

    def test_lambda_detected_via_function_name(self) -> None:
        with patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": "my-fn"}, clear=False):
            os.environ.pop("GATEWAY_INTERFACE", None)
            assert get_execution_mode() == "lambda"

    def test_lambda_detected_via_task_root(self) -> None:
        with patch.dict(os.environ, {"LAMBDA_TASK_ROOT": "/var/task"}, clear=False):
            os.environ.pop("GATEWAY_INTERFACE", None)
            os.environ.pop("AWS_LAMBDA_FUNCTION_NAME", None)
            assert get_execution_mode() == "lambda"

    def test_google_cloud_function_detected(self) -> None:
        with patch.dict(os.environ, {"FUNCTION_TARGET": "my_handler"}, clear=False):
            for k in (
                "GATEWAY_INTERFACE",
                "AWS_LAMBDA_FUNCTION_NAME",
                "LAMBDA_TASK_ROOT",
            ):
                os.environ.pop(k, None)
            assert get_execution_mode() == "google_cloud_function"

    @pytest.mark.parametrize(
        "env",
        [
            {
                "K_SERVICE": "my-service",
                "K_REVISION": "my-service-00001",
                "PORT": "8080",
            },
            {"GOOGLE_CLOUD_PROJECT": "my-project"},
            {"K_SERVICE": "my-service", "GOOGLE_CLOUD_PROJECT": "my-project"},
        ],
    )
    def test_cloud_run_and_a_project_alone_are_server_mode(
        self, env: dict[str, str]
    ) -> None:
        """Cloud Run sets K_SERVICE for every service, and GOOGLE_CLOUD_PROJECT
        is set on many machines. Neither means a Cloud Function, whose
        Functions Framework sets FUNCTION_TARGET."""
        with patch.dict(os.environ, env, clear=False):
            for k in (
                "GATEWAY_INTERFACE",
                "AWS_LAMBDA_FUNCTION_NAME",
                "LAMBDA_TASK_ROOT",
                "FUNCTION_TARGET",
                "AZURE_FUNCTIONS_ENVIRONMENT",
                "FUNCTIONS_WORKER_RUNTIME",
                "AzureWebJobsStorage",
            ):
                os.environ.pop(k, None)
            assert get_execution_mode() == "server"

    def test_a_function_on_cloud_run_is_a_cloud_function(self) -> None:
        """A second-generation function runs on Cloud Run, so it has K_SERVICE
        too; FUNCTION_TARGET is what decides."""
        env = {"FUNCTION_TARGET": "main", "K_SERVICE": "my-function"}
        with patch.dict(os.environ, env, clear=False):
            for k in (
                "GATEWAY_INTERFACE",
                "AWS_LAMBDA_FUNCTION_NAME",
                "LAMBDA_TASK_ROOT",
            ):
                os.environ.pop(k, None)
            assert get_execution_mode() == "google_cloud_function"

    def test_azure_function_detected(self) -> None:
        with patch.dict(
            os.environ, {"AZURE_FUNCTIONS_ENVIRONMENT": "Production"}, clear=False
        ):
            for k in (
                "GATEWAY_INTERFACE",
                "AWS_LAMBDA_FUNCTION_NAME",
                "LAMBDA_TASK_ROOT",
                "FUNCTION_TARGET",
                "K_SERVICE",
                "GOOGLE_CLOUD_PROJECT",
            ):
                os.environ.pop(k, None)
            assert get_execution_mode() == "azure_function"


class TestIsServerlessMode:
    def test_server_mode_is_not_serverless(self) -> None:
        env_keys = [
            "GATEWAY_INTERFACE",
            "AWS_LAMBDA_FUNCTION_NAME",
            "LAMBDA_TASK_ROOT",
            "FUNCTION_TARGET",
            "K_SERVICE",
            "GOOGLE_CLOUD_PROJECT",
            "AZURE_FUNCTIONS_ENVIRONMENT",
            "FUNCTIONS_WORKER_RUNTIME",
            "AzureWebJobsStorage",
        ]
        with patch.dict(os.environ, {}, clear=False):
            for k in env_keys:
                os.environ.pop(k, None)
            assert is_serverless_mode() is False

    def test_lambda_is_serverless(self) -> None:
        with patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": "fn"}, clear=False):
            os.environ.pop("GATEWAY_INTERFACE", None)
            assert is_serverless_mode() is True

    def test_cgi_is_serverless(self) -> None:
        # CGI is not a long-running server — counts as serverless.
        with patch.dict(os.environ, {"GATEWAY_INTERFACE": "CGI/1.1"}, clear=False):
            assert is_serverless_mode() is True
