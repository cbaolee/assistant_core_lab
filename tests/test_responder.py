import pytest

from assistant_core.errors import AssistantError, ProviderError
from assistant_core.knowledge import Rule
from assistant_core.responder import Responder, StubLLMResponder, TemplateResponder


@pytest.fixture
def rule() -> Rule:
    """A sample handbook rule shared by all tests."""
    return Rule(
        id="H26-5.3",
        title="Thesis registration",
        text="Students may register a thesis when they have at least 120 accumulated credits.",
    )


def test_template_responder_returns_title_and_text(rule: Rule) -> None:
    """The template answer is exactly 'title: text'."""
    answer = TemplateResponder().explain("thesis", rule)
    assert answer == f"{rule.title}: {rule.text}"


def test_stub_responder_returns_answer(rule: Rule) -> None:
    """The stub answer names the rule and contains its text."""
    answer = StubLLMResponder().explain("thesis", rule)
    assert answer.startswith("Based on 'Thesis registration'")
    assert rule.text in answer


def test_stub_responder_fail_raises_provider_error(rule: Rule) -> None:
    """A failing stub raises ProviderError."""
    with pytest.raises(ProviderError):
        StubLLMResponder(fail=True).explain("thesis", rule)


def test_provider_error_is_an_assistant_error(rule: Rule) -> None:
    """ProviderError can be caught as the base AssistantError."""
    with pytest.raises(AssistantError):
        StubLLMResponder(fail=True).explain("thesis", rule)


def test_stub_responder_is_deterministic(rule: Rule) -> None:
    """The same input always gives the same output."""
    responder = StubLLMResponder()
    assert responder.explain("thesis", rule) == responder.explain("thesis", rule)


@pytest.mark.parametrize("responder", [TemplateResponder(), StubLLMResponder()])
def test_implementations_satisfy_responder_interface(responder: Responder, rule: Rule) -> None:
    """Both implementations can be used wherever a Responder is expected."""
    assert isinstance(responder.explain("question", rule), str)
