# Tests for AI-generated user stories (output/stories.json)

import json
from pathlib import Path
import re

import pytest

STORIES_FILE = Path(__file__).parent.parent / "output" / "stories.json"
MODULES = ["LOGIN", "CART", "PAYMENT", "REFUND"]


@pytest.fixture
def all_stories():
    """Load stories.json once and give it to the tests."""
    return json.loads(STORIES_FILE.read_text(encoding="utf-8"))


def test_stories_file_exists():
    assert STORIES_FILE.exists(), "stories.json not found - run: tools.py save <Module>"


def test_all_modules_saved(all_stories):
    for module in MODULES:
        assert module in all_stories, f"{module} stories are missing"
        assert len(all_stories[module]) > 0, f"{module} has no stories"

        # ---------- Data-driven tests: one test per story ----------

def _load_all_stories():
    """Flatten all modules into one list of stories (used by parametrize)."""
    if not STORIES_FILE.exists():
        return []
    data = json.loads(STORIES_FILE.read_text(encoding="utf-8"))
    return [story for module_stories in data.values() for story in module_stories]


ALL_STORIES = _load_all_stories()
REQUIRED_FIELDS = [
    "story_id", "title", "as_a", "i_want", "so_that",
    "requirement_ids", "acceptance_criteria", "status",
]


@pytest.mark.parametrize("story", ALL_STORIES, ids=lambda s: s.get("story_id", "?"))
def test_story_has_all_fields(story):
    missing = [field for field in REQUIRED_FIELDS if not story.get(field)]
    assert not missing, f"{story.get('story_id')} is missing or has empty: {missing}"


@pytest.mark.parametrize("story", ALL_STORIES, ids=lambda s: s.get("story_id", "?"))
def test_story_requirement_ids_valid(story):
    for req_id in story["requirement_ids"]:
        assert re.fullmatch(r"BR-[A-Z]+-\d{2}|NFR-\d{2}", req_id), \
            f"{story['story_id']} has an invalid requirement ID: {req_id}"




@pytest.mark.parametrize("story", ALL_STORIES, ids=lambda s: s.get("story_id", "?"))
def test_story_has_at_least_two_acceptance_criteria(story):
    count = len(story["acceptance_criteria"])
    assert count >= 2, f"{story['story_id']} has only {count} acceptance criteria (need >= 2)"


@pytest.mark.parametrize("story", ALL_STORIES, ids=lambda s: s.get("story_id", "?"))
def test_acceptance_criteria_have_given_when_then(story):
    for i, ac in enumerate(story["acceptance_criteria"], start=1):
        for part in ["given", "when", "then"]:
            assert ac.get(part, "").strip(), \
                f"{story['story_id']} AC-{i} has an empty '{part}'"