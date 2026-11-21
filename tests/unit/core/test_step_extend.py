"""
Step._extend: how one layer adds to a step another layer made (used by
signalwire.operations), keeping what the step has.
"""

from signalwire.core.contexts import Step


def _step() -> Step:
    return Step("main")


def test_text_and_functions_join_what_the_step_has() -> None:
    step = _step().set_text("Help them.").set_functions(["a", "b"])
    step._extend("Also look things up.", ["b", "c"])
    data = step.to_dict()
    assert data["text"] == "Help them.\n\nAlso look things up."
    assert data["functions"] == ["a", "b", "c"]


def test_a_step_written_in_sections_gets_a_section() -> None:
    step = _step().add_section("Task", "Help them.")
    step._extend("Also look things up.", ["c"], section="What else you can do")
    text = step.to_dict()["text"]
    assert "Task" in text and "What else you can do" in text and "Also look things up." in text
    assert step.to_dict()["functions"] == ["c"]


def test_a_step_with_no_functions_of_its_own_takes_them() -> None:
    step = _step().set_text("Help them.")
    step._extend("", ["x"])
    assert step.to_dict()["functions"] == ["x"]
    assert step.to_dict()["text"] == "Help them."
