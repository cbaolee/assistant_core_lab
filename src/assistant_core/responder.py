from typing import Protocol

from assistant_core.errors import ProviderError
from assistant_core.knowledge import Rule


class Responder(Protocol):
    """Interface for anything that can turn a handbook rule into an answer."""

    def explain(self, question: str, rule: Rule) -> str:
        """Return an answer to the question, based on the given rule."""
        ...


class TemplateResponder:
    """No-AI responder. Used as the fallback when the main responder fails."""

    def explain(self, question: str, rule: Rule) -> str:
        """Return the rule title and text without any rewriting."""
        return f"{rule.title}: {rule.text}"


class StubLLMResponder:
    """Fake LLM for tests and offline use. Can simulate a provider failure."""

    def __init__(self, fail: bool = False) -> None:
        """Create the stub. Set `fail=True` to make every call raise ProviderError."""
        self.fail = fail

    def explain(self, question: str, rule: Rule) -> str:
        """Return a fixed-format answer, or raise ProviderError when `fail` is set."""
        if self.fail:
            raise ProviderError("stub provider unavailable")
        return f"Based on '{rule.title}': {rule.text}"
