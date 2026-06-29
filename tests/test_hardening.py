"""Tests for the robustness helpers added to the enrichment and KEV steps.

The pipeline step files have numeric prefixes (05_, 09_), so they are loaded by
path rather than a plain import.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def _load(module_name, filename):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def enrich():
    return _load("enrich_blog", "05_enrich_blog.py")


@pytest.fixture(scope="module")
def kev():
    return _load("kev_analysis", "09_kev_analysis.py")


# --- 05_enrich_blog.extract_numbers ----------------------------------------
def test_extract_numbers_matches_with_and_without_commas(enrich):
    # The old regex only caught comma-grouped numbers; both spellings must
    # normalize to the same value so a reformat is not flagged as a loss.
    assert enrich.extract_numbers("6,730") == enrich.extract_numbers("6730")
    assert enrich.extract_numbers("6,730") == {6730.0}


def test_extract_numbers_captures_decimals_and_percentages(enrich):
    nums = enrich.extract_numbers("one every 7.4 minutes, only 0.24% exploited")
    assert 7.4 in nums
    assert 0.24 in nums


def test_extract_numbers_detects_a_dropped_statistic(enrich):
    original = enrich.extract_numbers("34,601 CVEs, up 48.8%")
    rewritten = enrich.extract_numbers("many CVEs, up 48.8%")
    lost = original - rewritten
    assert 34601.0 in lost


# --- 09_kev_analysis.is_ransomware -----------------------------------------
@pytest.mark.parametrize(
    "value,expected",
    [
        ("Known", True),
        ("known", True),
        ("Unknown", False),
        (True, True),
        (False, False),
        ("yes", True),
        ("", False),
        (None, False),
    ],
)
def test_is_ransomware_normalization(kev, value, expected):
    assert kev.is_ransomware(value) is expected
