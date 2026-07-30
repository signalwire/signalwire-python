"""Regression: the ``skip_prompt`` guard must be unbypassable.

``SkillBase.get_prompt_sections()`` is the guard-bearing entry point: it returns
an empty list when ``params["skip_prompt"]`` is set, and otherwise delegates to
the protected ``_get_prompt_sections()`` hook. Skills override the HOOK, never
the public method — overriding the public method silently disables the guard
for that skill.

This was live: 11 of the 13 shipped skill files overrode the public method, so
``JokeSkill(skip_prompt=True).get_prompt_sections()`` returned 1 section instead
of 0. Two tests here:

1. a structural sweep asserting no shipped skill class overrides the public
   method (catches a NEW skill that reintroduces the bypass), and
2. a behavioural check on a representative skill that DOES emit sections.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Any
from unittest.mock import Mock

import pytest

import signalwire.skills as skills_pkg
from signalwire.core.skill_base import SkillBase
from signalwire.skills.joke.skill import JokeSkill
from signalwire.skills.math.skill import MathSkill


def _iter_skill_modules() -> list[str]:
    """Every shipped skill module (including non-``skill.py`` variants)."""
    names: list[str] = []
    for mod in pkgutil.iter_modules(skills_pkg.__path__):
        if not mod.ispkg:
            continue
        pkg = importlib.import_module(f"signalwire.skills.{mod.name}")
        names.extend(
            f"signalwire.skills.{mod.name}.{sub.name}"
            for sub in pkgutil.iter_modules(pkg.__path__)
            if not sub.ispkg
        )
    return names


def _iter_skill_classes() -> list[type[SkillBase]]:
    """All shipped SkillBase subclasses.

    Import failures are NOT swallowed: a silently skipped module would shrink
    the sweep below and let a bypassing skill through unnoticed.
    """
    classes: list[type[SkillBase]] = []
    for name in _iter_skill_modules():
        module = importlib.import_module(name)
        classes.extend(
            obj
            for obj in vars(module).values()
            if isinstance(obj, type)
            and issubclass(obj, SkillBase)
            and obj is not SkillBase
            and obj.__module__ == name
        )
    return classes


class TestSkipPromptGuardIsUnbypassable:
    def test_no_shipped_skill_overrides_the_public_method(self) -> None:
        """Skills override ``_get_prompt_sections``, never ``get_prompt_sections``.

        An override of the public method bypasses the ``skip_prompt`` guard for
        that skill, which is exactly the defect this file guards against.
        """
        classes = _iter_skill_classes()
        assert classes, "no skill classes discovered — the sweep would be vacuous"
        offenders = [
            f"{cls.__module__}.{cls.__name__}"
            for cls in classes
            if "get_prompt_sections" in vars(cls)
        ]
        assert offenders == [], (
            "these skills override the PUBLIC get_prompt_sections(), which "
            "bypasses the skip_prompt guard in SkillBase; override the "
            f"protected _get_prompt_sections() hook instead: {offenders}"
        )

    def test_base_delegates_to_the_protected_hook(self) -> None:
        class _Skill(SkillBase):
            SKILL_NAME = "t"
            SKILL_DESCRIPTION = "t"

            def setup(self) -> bool:
                return True

            def register_tools(self) -> None:
                pass

            def _get_prompt_sections(self) -> list[dict[str, Any]]:
                return [{"title": "T", "body": "B"}]

        assert len(_Skill(agent=Mock(), params={}).get_prompt_sections()) == 1
        assert (
            _Skill(agent=Mock(), params={"skip_prompt": True}).get_prompt_sections()
            == []
        )

    @pytest.mark.parametrize(
        ("factory", "expected_default"),
        [
            (lambda p: JokeSkill(agent=Mock(), params={"api_key": "k", **p}), 1),
            (lambda p: MathSkill(agent=Mock(), params=dict(p)), 1),
        ],
        ids=["joke", "math"],
    )
    def test_real_skill_honours_skip_prompt(
        self, factory: Any, expected_default: int
    ) -> None:
        default = factory({})
        default.setup()
        assert len(default.get_prompt_sections()) == expected_default

        skipped = factory({"skip_prompt": True})
        skipped.setup()
        assert skipped.get_prompt_sections() == []
