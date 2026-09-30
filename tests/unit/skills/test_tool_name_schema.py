"""
The tool_name entry in each multi-instance skill's parameter schema.

SkillBase gives every multi-instance skill a tool_name entry whose default is
the skill name. Several skills name their tool something else when tool_name
isn't set, spider uses tool_name as a prefix, and info_gatherer and
claude_skills don't use it at all, so the schema (which sw-pydocs and
configuration tools show) described tools the skills never register.
"""

from typing import Any
from unittest.mock import Mock

import pytest

from signalwire.core.skill_base import SkillBase
from signalwire.skills.api_ninjas_trivia.skill import ApiNinjasTriviaSkill
from signalwire.skills.claude_skills.skill import ClaudeSkillsSkill
from signalwire.skills.datasphere.skill import DataSphereSkill
from signalwire.skills.datasphere_serverless.skill import DataSphereServerlessSkill
from signalwire.skills.info_gatherer.skill import InfoGathererSkill
from signalwire.skills.native_vector_search.skill import NativeVectorSearchSkill
from signalwire.skills.play_background_file.skill import PlayBackgroundFileSkill
from signalwire.skills.spider.skill import SpiderSkill
from signalwire.skills.swml_transfer.skill import SWMLTransferSkill
from signalwire.skills.web_search.skill import WebSearchSkill


@pytest.mark.parametrize(
    ("skill_class", "default"),
    [
        (NativeVectorSearchSkill, "search_knowledge"),
        (DataSphereSkill, "search_knowledge"),
        (DataSphereServerlessSkill, "search_knowledge"),
        (SWMLTransferSkill, "transfer_call"),
        (ApiNinjasTriviaSkill, "get_trivia"),
        (WebSearchSkill, "web_search"),
        (PlayBackgroundFileSkill, "play_background_file"),
    ],
)
def test_schema_default_is_the_tool_name_used(
    skill_class: type[SkillBase], default: str
) -> None:
    entry = skill_class.get_parameter_schema()["tool_name"]
    assert entry["default"] == default
    assert entry["type"] == "string"
    assert entry["required"] is False


def test_spider_tool_name_is_a_prefix_with_no_default() -> None:
    entry = SpiderSkill.get_parameter_schema()["tool_name"]
    assert "default" not in entry
    assert "<tool_name>_scrape_url" in entry["description"]


@pytest.mark.parametrize(
    ("skill_class", "naming_param"),
    [(InfoGathererSkill, "prefix"), (ClaudeSkillsSkill, "tool_prefix")],
)
def test_skills_that_ignore_tool_name_do_not_list_it(
    skill_class: type[SkillBase], naming_param: str
) -> None:
    schema = skill_class.get_parameter_schema()
    assert "tool_name" not in schema
    assert naming_param in schema


def _registered_names(agent: Mock) -> list[str]:
    names = [
        call.args[0]["function"]
        for call in agent.register_swaig_function.call_args_list
    ]
    names += [call.kwargs["name"] for call in agent.define_tool.call_args_list]
    return names


@pytest.mark.parametrize(
    ("skill_class", "params"),
    [
        (
            DataSphereServerlessSkill,
            {
                "space_name": "example",
                "project_id": "project",
                "token": "token",
                "document_id": "doc",
            },
        ),
        (
            SWMLTransferSkill,
            {"transfers": {"/sales/i": {"url": "https://example.com/sales"}}},
        ),
    ],
)
def test_registered_tool_matches_schema_default(
    skill_class: type[SkillBase], params: dict[str, Any]
) -> None:
    agent = Mock()
    skill = skill_class(agent, params)
    assert skill.setup() is True
    skill.register_tools()
    default = skill_class.get_parameter_schema()["tool_name"]["default"]
    assert _registered_names(agent) == [default]
