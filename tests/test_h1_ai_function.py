"""
Part H.1 — Edge-case tests for the AI-generated function `parse_credits` in tools.py.

Chosen function: parse_credits(text: str) -> tuple[int, int]
Rationale: This function was designed/refined with AI assistance and is the core
           parsing utility that determines tuition calculations.

Edge cases covered:
  a. Empty input ("" or [])
  b. Zero-value credits (0 credits)
  c. Very large value (100_000 credits)
  d. Vietnamese text with diacritics
  e. Wrong data types / negative integers
"""

import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.tools import parse_credits


# ── a. Empty input ──────────────────────────────────────────────────────────────

def test_empty_string_raises():
    """Empty string contains no digit → must raise InvalidRequest."""
    with pytest.raises(InvalidRequest):
        parse_credits("")


def test_whitespace_only_raises():
    """Whitespace-only input has no digit → must raise InvalidRequest."""
    with pytest.raises(InvalidRequest):
        parse_credits("   ")


# ── b. Zero value (0 credits) ───────────────────────────────────────────────────

def test_zero_credits_parsed():
    """0 is a valid digit; function should return (0, 0) — caller validates range."""
    result = parse_credits("fee for 0 credits")
    assert result == (0, 0)


def test_zero_credits_zero_retake():
    """Explicit 0 retake alongside 0 credits."""
    result = parse_credits("0 credits 0 retake")
    assert result == (0, 0)


# ── c. Very large value (100_000 credits) ───────────────────────────────────────

def test_large_credits_parsed():
    """100_000 credits should be parsed without error (range enforcement is in tuition())."""
    result = parse_credits("tuition for 100000 credits")
    assert result == (100_000, 0)


def test_large_credits_with_retake():
    """Large credits combined with large retake value."""
    result = parse_credits("100000 credits and 5000 retake")
    assert result == (100_000, 5_000)


# ── d. Vietnamese text with diacritics ──────────────────────────────────────────

def test_vietnamese_mixed_text():
    """Numbers embedded in Vietnamese sentences should still be extracted."""
    result = parse_credits("học phí cho 18 tín chỉ và 2 học lại")
    assert result == (18, 0)  # "học lại" ≠ "retake" keyword → retake=0


def test_vietnamese_with_retake_keyword():
    """Vietnamese text that also contains the English 'retake' keyword."""
    result = parse_credits("tính học phí 15 tín chỉ và 3 retake")
    assert result == (15, 3)


def test_vietnamese_no_number_raises():
    """Pure Vietnamese with no digits → must raise InvalidRequest."""
    with pytest.raises(InvalidRequest):
        parse_credits("học phí là bao nhiêu?")


# ── e. Wrong data types / negative integers ─────────────────────────────────────

def test_negative_number_in_text():
    """
    Regex \\d+ never matches a leading '-', so '-5 credits' yields digit 5.
    parse_credits should return (5, 0) — the negative sign is invisible to it.
    Range validation is the responsibility of tuition().
    """
    result = parse_credits("fee for -5 credits")
    assert result == (5, 0)


def test_non_string_input_raises():
    """Passing a non-string (e.g. None) should raise TypeError, not silently succeed."""
    with pytest.raises((TypeError, AttributeError)):
        parse_credits(None)  # type: ignore[arg-type]


def test_integer_input_raises():
    """Passing a plain integer should raise TypeError."""
    with pytest.raises((TypeError, AttributeError)):
        parse_credits(42)  # type: ignore[arg-type]


def test_list_input_raises():
    """Passing a list should raise TypeError."""
    with pytest.raises((TypeError, AttributeError)):
        parse_credits([18, 2])  # type: ignore[arg-type]


# ── Regression: original happy-path still works ─────────────────────────────────

def test_standard_case():
    """Baseline from the original test suite must still pass."""
    assert parse_credits("tuition for 18 credits and 2 retake") == (18, 2)


def test_retake_same_number():
    """Duplicate numbers where retake matches credits value."""
    assert parse_credits("fee 2 credits 2 retake") == (2, 2)
