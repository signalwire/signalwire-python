"""
Regression tests for two reference functions that used to be dead code:

  * ``signalwire.list_skills()`` lazy-imported a non-existent ``cli.helpers``
    module and so ALWAYS raised ``NotImplementedError``.
  * ``SkillRegistry.discover_skills()`` was a deprecated no-op returning ``None``.

Both must now return the real skill inventory (they delegate to the registry's
working ``list_skills()`` scan). These tests pin the fix so it can't regress.
"""
import signalwire
from signalwire.skills.registry import skill_registry


def test_top_level_list_skills_returns_real_inventory() -> None:
    skills = signalwire.list_skills()
    assert isinstance(skills, list)
    assert len(skills) > 0, "list_skills() must return the skill inventory, not raise/empty"
    names = {s["name"] for s in skills}
    # core built-in skills must be discoverable
    assert {"datetime", "math"} <= names, f"expected built-ins missing from {sorted(names)}"
    for s in skills:
        assert s["name"], "each skill needs a name"
        assert s["description"], "each skill needs a description"
        assert "version" in s and "required_packages" in s


def test_discover_skills_returns_inventory_not_none() -> None:
    discovered = skill_registry.discover_skills()
    assert discovered is not None, "discover_skills() must not be a no-op returning None"
    assert isinstance(discovered, list) and len(discovered) > 0
    # discover_skills mirrors the registry's list_skills scan exactly
    assert {s["name"] for s in discovered} == {s["name"] for s in skill_registry.list_skills()}
