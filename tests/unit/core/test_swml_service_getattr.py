"""SWMLService.__getattr__: attribute misses must not recurse.

``__getattr__`` runs on every failed attribute lookup and its body reaches for
``self.log`` and ``self.schema_utils``. Both are assigned during ``__init__``,
and ``log`` well before ``schema_utils`` -- so on a partially constructed
instance, resolving either one re-entered ``__getattr__``, which reached for it
again, until the stack ran out.

Two things made that expensive to diagnose rather than merely broken: the
traceback named the *dependency* rather than the attribute access that started
it, and an application cannot fix it without overriding ``__getattr__`` on the
base class, which is forking the SDK.

These tests pin the guard and, just as importantly, pin that the guard did not
turn every legitimate verb lookup into an AttributeError.
"""

import pytest

from signalwire.core.swml_service import SWMLService


def _unconstructed() -> SWMLService:
    """An instance whose __init__ never ran -- neither log nor schema_utils."""
    return SWMLService.__new__(SWMLService)


class TestNoRecursion:
    def test_missing_attribute_raises_rather_than_recursing(self) -> None:
        with pytest.raises(AttributeError):
            _ = _unconstructed().some_typo_attribute

    def test_error_names_the_attribute_actually_requested(self) -> None:
        """Not the dependency that happened to be missing underneath it."""
        with pytest.raises(AttributeError) as exc:
            _ = _unconstructed().some_typo_attribute
        assert "some_typo_attribute" in str(exc.value)
        assert "schema_utils" not in str(exc.value)

    @pytest.mark.parametrize("name", ["log", "schema_utils", "_verb_methods_cache"])
    def test_own_dependencies_short_circuit(self, name: str) -> None:
        """The three names __getattr__ needs can never be resolved through it."""
        with pytest.raises(AttributeError):
            getattr(_unconstructed(), name)

    @pytest.mark.parametrize("name", ["__deepcopy__", "__copy__", "__wrapped__"])
    def test_dunder_probes_are_rejected_cheaply(self, name: str) -> None:
        """copy/pickle/inspect probe these constantly; none can be a SWML verb.

        Only dunders that `object` does not itself provide are listed --
        `__getstate__` exists on every object from Python 3.11, so it resolves
        before `__getattr__` is ever consulted.
        """
        with pytest.raises(AttributeError):
            getattr(_unconstructed(), name)

    def test_hasattr_is_false_rather_than_exploding(self) -> None:
        assert not hasattr(_unconstructed(), "definitely_not_here")


class TestVerbLookupStillWorks:
    """The guard must not break the feature __getattr__ exists for."""

    def test_valid_verb_resolves_to_a_callable(self) -> None:
        service = SWMLService(name="t", route="/t", schema_validation=False)
        assert callable(service.answer)

    def test_invalid_attribute_on_a_live_instance_still_raises(self) -> None:
        service = SWMLService(name="t", route="/t", schema_validation=False)
        with pytest.raises(AttributeError):
            _ = service.not_a_verb_at_all
