"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

from datetime import datetime, timezone
import pytz
from typing import Any, ClassVar

from signalwire.core.skill_base import SkillBase
from signalwire.core.function_result import FunctionResult


class DateTimeSkill(SkillBase):
    """Provides current date, time, and timezone information"""

    SKILL_NAME = "datetime"
    SKILL_DESCRIPTION = "Get current date, time, and timezone information"
    SKILL_VERSION = "1.0.0"
    REQUIRED_PACKAGES: ClassVar[list[str]] = ["pytz"]
    REQUIRED_ENV_VARS: ClassVar[list[str]] = []

    def setup(self) -> bool:
        """Setup the datetime skill"""
        return self.validate_packages()

    def register_tools(self) -> None:
        """Register datetime tools with the agent"""

        self.define_tool(
            name="get_current_time",
            description="Get the current time, optionally in a specific timezone",
            parameters={
                "timezone": {
                    "type": "string",
                    "description": "Timezone name (e.g., 'America/New_York', 'Europe/London'). Defaults to UTC.",
                }
            },
            handler=self._get_time_handler,
        )

        self.define_tool(
            name="get_current_date",
            description="Get the current date",
            parameters={
                "timezone": {
                    "type": "string",
                    "description": "Timezone name for the date. Defaults to UTC.",
                }
            },
            handler=self._get_date_handler,
        )

    def _get_time_handler(self, args, raw_data):
        """Handler for get_current_time tool"""
        timezone_name = args.get("timezone", "UTC")

        try:
            if timezone_name.upper() == "UTC":
                tz = timezone.utc
            else:
                tz = pytz.timezone(timezone_name)

            now = datetime.now(tz)
            time_str = now.strftime("%I:%M:%S %p %Z")

            return FunctionResult(f"The current time is {time_str}")

        except Exception as e:
            return FunctionResult(f"Error getting time: {e!s}")

    def _get_date_handler(self, args, raw_data):
        """Handler for get_current_date tool"""
        timezone_name = args.get("timezone", "UTC")

        try:
            if timezone_name.upper() == "UTC":
                tz = timezone.utc
            else:
                tz = pytz.timezone(timezone_name)

            now = datetime.now(tz)
            date_str = now.strftime("%A, %B %d, %Y")

            return FunctionResult(f"Today's date is {date_str}")

        except Exception as e:
            return FunctionResult(f"Error getting date: {e!s}")

    def get_hints(self) -> list[str]:
        """Return speech recognition hints"""
        # Currently no hints provided, but you could add them like:
        # return ["time", "date", "today", "now", "current", "timezone"]
        return []

    def get_prompt_sections(self) -> list[dict[str, Any]]:
        """Return prompt sections to add to agent"""
        return [
            {
                "title": "Date and Time Information",
                "body": "You can provide current date and time information.",
                "bullets": [
                    "Use get_current_time to tell users what time it is",
                    "Use get_current_date to tell users today's date",
                    "Both tools support different timezones",
                ],
            }
        ]

    @classmethod
    def get_parameter_schema(cls) -> dict[str, dict[str, Any]]:
        """
        Get the parameter schema for the datetime skill

        The datetime skill has no custom parameters - it inherits only
        the base parameters from SkillBase.
        """
        # Get base schema from parent
        return super().get_parameter_schema()

        # No additional parameters for datetime skill
