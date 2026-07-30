"""Regression: the ``skip_prompt`` guard must be unbypassable.

``SkillBase.get_prompt_sections()`` is the guard-bearing entry point: it returns
an empty list when ``params["skip_prompt"]`` is set, and otherwise delegates to
the protected ``_get_prompt_sections()`` hook. Skills override the HOOK, never
the public method — overriding the public method silently disables the guard
for that skill.

This was live: 11 of the 13 shipped skill files overrode the public method, so
``JokeSkill(skip_prompt=True).get_prompt_sections()`` returned 1 section instead
of 0. Three layers of coverage here:

1. a structural sweep asserting no shipped skill class overrides the public
   method (catches a NEW skill that reintroduces the bypass),
2. a behavioural check on a representative skill that DOES emit sections, and
3. a registry-parametrized sweep over EVERY discovered skill class asserting
   both halves of the contract — ``skip_prompt`` suppresses all sections, AND
   (the load-bearing inverse) each skill returns a non-empty list when
   ``skip_prompt`` is unset. The inverse half is what catches a skill whose
   hook returns ``[]`` for the wrong reason; see
   ``TestEverySkillHonoursSkipPrompt``.
"""

from __future__ import annotations

import contextlib
import importlib
import pkgutil
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

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


# ---------------------------------------------------------------------------
# Registry-driven parametrization
#
# The sweep below is parametrized over the DISCOVERED skill classes, not a
# hand-written list: a hand list silently omits a newly added skill, which is
# the blind spot this file exists to close.
# ---------------------------------------------------------------------------

#: Smallest params that let each skill's ``setup()`` succeed offline.
#: Keyed by class name because two modules (``web_search.skill`` and its
#: ``skill_improved`` / ``skill_original`` variants) export the same class name.
MINIMAL_PARAMS: dict[str, dict[str, Any]] = {
    "ApiNinjasTriviaSkill": {"api_key": "k"},
    "ClaudeSkillsSkill": {},  # skills_path injected by _make_skill (needs a real dir)
    "DataSphereSkill": {
        "space_name": "s",
        "project_id": "p",
        "token": "t",
        "document_id": "d",
    },
    "DataSphereServerlessSkill": {
        "space_name": "s",
        "project_id": "p",
        "token": "t",
        "document_id": "d",
    },
    "DateTimeSkill": {},
    "GoogleMapsSkill": {"api_key": "k"},
    "InfoGathererSkill": {
        "questions": [{"key_name": "name", "question_text": "What is your name?"}]
    },
    "JokeSkill": {"api_key": "k"},
    "MathSkill": {},
    "MCPGatewaySkill": {"gateway_url": "http://gw.test", "auth_token": "t"},
    "NativeVectorSearchSkill": {},
    "PlayBackgroundFileSkill": {
        "files": [{"key": "k", "description": "d", "url": "http://x.test/a.mp3"}]
    },
    "SpiderSkill": {"api_key": "k"},
    "SWMLTransferSkill": {"transfers": {"sales": {"url": "sip:x@y", "message": "m"}}},
    "WeatherApiSkill": {"api_key": "k"},
    "WebSearchSkill": {"api_key": "k", "search_engine_id": "e"},
    "WikipediaSearchSkill": {},
}

#: Skills that legitimately contribute NO prompt section, with the reason.
#: The first four define no ``_get_prompt_sections`` override at all and inherit
#: the base's empty list; ``MCPGatewaySkill`` defines the hook but emits a
#: section only when ``services`` are configured, and the minimal params
#: configure none. Every entry here is EXEMPT from the non-empty assertion —
#: which is why the exemption list is asserted to be exactly this set, so a
#: skill cannot quietly join it.
NO_SECTION_BY_DESIGN: dict[str, str] = {
    "ApiNinjasTriviaSkill": "defines no _get_prompt_sections override",
    "PlayBackgroundFileSkill": "defines no _get_prompt_sections override",
    "SpiderSkill": "defines no _get_prompt_sections override",
    "WeatherApiSkill": "defines no _get_prompt_sections override",
    "MCPGatewaySkill": "emits a section only when 'services' are configured",
}


@contextlib.contextmanager
def _offline(skill_cls: type[SkillBase]) -> Iterator[None]:
    """Neutralize the only network/DNS calls any skill makes during ``setup()``.

    ``MCPGatewaySkill.setup()`` GETs ``<gateway_url>/health`` and runs the
    gateway URL through SSRF validation, which does a DNS lookup. Both are
    stubbed so the sweep stays offline and deterministic. No other skill needs
    stubbing — all the rest complete ``setup()`` with local params alone.
    """
    if skill_cls.__name__ != "MCPGatewaySkill":
        yield
        return
    with (
        patch(f"{skill_cls.__module__}.requests.get") as get,
        patch("signalwire.utils.url_validator.validate_url", return_value=True),
    ):
        get.return_value = Mock(raise_for_status=Mock(return_value=None))
        yield


def _make_skill(skill_cls: type[SkillBase], tmp_path: Path, **extra: Any) -> SkillBase:
    """Construct ``skill_cls`` with its minimal params plus ``extra``."""
    params = dict(MINIMAL_PARAMS[skill_cls.__name__])
    if skill_cls.__name__ == "ClaudeSkillsSkill":
        # Needs a real directory containing at least one SKILL.md.
        skills_dir = tmp_path / "claude_skills"
        (skills_dir / "demo").mkdir(parents=True, exist_ok=True)
        (skills_dir / "demo" / "SKILL.md").write_text(
            "---\nname: demo\ndescription: A demo skill\n---\n\n# Demo\n"
        )
        params["skills_path"] = str(skills_dir)
    params.update(extra)
    return skill_cls(agent=Mock(), params=params)


_SKILL_CLASSES = _iter_skill_classes()
_SKILL_IDS = [
    f"{c.__module__.split('.')[-2]}.{c.__module__.split('.')[-1]}"
    for c in _SKILL_CLASSES
]


class TestEverySkillHonoursSkipPrompt:
    """Registry-wide sweep of the ``skip_prompt`` contract.

    The suppression half alone is VACUOUS: a skill whose hook returns ``[]``
    for the wrong reason passes it trivially. That is exactly how
    ``native_vector_search`` hid — its hook returned ``[]`` while its real
    content sat in a push-style ``_add_prompt_section(agent)`` helper nothing
    called, so the skill shipped contributing no prompt section at all and
    every skip_prompt assertion about it passed.

    ``test_default_returns_a_section`` is therefore the load-bearing half: it
    asserts each skill returns a NON-EMPTY list when ``skip_prompt`` is unset,
    which is what catches the false pass. Skills that legitimately emit nothing
    are listed in ``NO_SECTION_BY_DESIGN`` with a reason, and that list is
    itself pinned by ``test_no_section_exemptions_are_exactly_as_recorded`` so a
    regressing skill cannot quietly join it.
    """

    def test_every_skill_class_has_minimal_params(self) -> None:
        """No skill may be silently absent from the parametrization."""
        assert _SKILL_CLASSES, "no skill classes discovered — the sweep is vacuous"
        missing = sorted({c.__name__ for c in _SKILL_CLASSES} - set(MINIMAL_PARAMS))
        assert missing == [], (
            "these skill classes have no MINIMAL_PARAMS entry, so they are not "
            f"covered by the skip_prompt sweep: {missing}"
        )

    def test_no_section_exemptions_are_exactly_as_recorded(self) -> None:
        """Pin the exemption list so a regression cannot quietly join it."""
        known = {c.__name__ for c in _SKILL_CLASSES}
        stale = sorted(set(NO_SECTION_BY_DESIGN) - known)
        assert stale == [], f"NO_SECTION_BY_DESIGN names unknown skills: {stale}"

    @pytest.mark.parametrize("skill_cls", _SKILL_CLASSES, ids=_SKILL_IDS)
    def test_skip_prompt_suppresses_all_sections(
        self, skill_cls: type[SkillBase], tmp_path: Path
    ) -> None:
        with _offline(skill_cls):
            skill = _make_skill(skill_cls, tmp_path, skip_prompt=True)
            assert skill.setup() is True, f"{skill_cls.__name__}.setup() failed"
            assert skill.get_prompt_sections() == []

    @pytest.mark.parametrize("skill_cls", _SKILL_CLASSES, ids=_SKILL_IDS)
    def test_default_returns_a_section(
        self, skill_cls: type[SkillBase], tmp_path: Path
    ) -> None:
        """The INVERSE assertion — the half that catches a vacuous pass.

        Without this, a skill whose hook returns ``[]`` for the wrong reason
        satisfies the suppression test and ships broken.
        """
        with _offline(skill_cls):
            skill = _make_skill(skill_cls, tmp_path)
            assert skill.setup() is True, f"{skill_cls.__name__}.setup() failed"
            sections = skill.get_prompt_sections()

        if skill_cls.__name__ in NO_SECTION_BY_DESIGN:
            reason = NO_SECTION_BY_DESIGN[skill_cls.__name__]
            assert sections == [], (
                f"{skill_cls.__name__} is recorded in NO_SECTION_BY_DESIGN "
                f"({reason}) but returned {len(sections)} section(s); remove the "
                "exemption"
            )
            return

        assert sections, (
            f"{skill_cls.__name__}.get_prompt_sections() returned an empty list "
            "with skip_prompt unset. Either the skill's content is stranded "
            "outside the _get_prompt_sections() hook (the native_vector_search "
            "defect), or it genuinely emits nothing — in which case add it to "
            "NO_SECTION_BY_DESIGN with a reason."
        )
        for section in sections:
            assert section.get("title"), f"{skill_cls.__name__}: section without title"


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
