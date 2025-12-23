"""Tests for natural language parser."""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import pytest
from datetime import date, datetime, timedelta

from app.services.natural_language import NaturalLanguageParser


class TestNaturalLanguageParser:
    """Test suite for NaturalLanguageParser."""

    def test_parse_simple_task(self):
        """Test parsing a simple task without any modifiers."""
        result = NaturalLanguageParser.parse("Buy groceries")
        assert result['title'] == "Buy groceries"
        assert result['description'] == ''
        assert result['priority_id'] == 2  # Default medium
        assert result['due_date'] is None
        assert result['is_recurring'] is False
        assert result['recurrence_pattern'] is None

    def test_parse_high_priority_urgent(self):
        """Test parsing high priority with 'urgent' keyword."""
        result = NaturalLanguageParser.parse("Call mom urgent")
        assert result['priority_id'] == 3  # High
        assert "urgent" not in result['title'].lower()

    def test_parse_high_priority_important(self):
        """Test parsing high priority with 'important' keyword."""
        result = NaturalLanguageParser.parse("Submit report important")
        assert result['priority_id'] == 3  # High
        assert "important" not in result['title'].lower()

    def test_parse_high_priority_asap(self):
        """Test parsing high priority with 'asap' keyword."""
        result = NaturalLanguageParser.parse("Fix bug asap")
        assert result['priority_id'] == 3  # High

    def test_parse_low_priority(self):
        """Test parsing low priority."""
        result = NaturalLanguageParser.parse("Read book eventually")
        assert result['priority_id'] == 1  # Low

    def test_parse_due_date_today(self):
        """Test parsing 'today' as due date."""
        result = NaturalLanguageParser.parse("Finish homework today")
        assert result['due_date'] == date.today().isoformat()
        assert "today" not in result['title'].lower()

    def test_parse_due_date_tomorrow(self):
        """Test parsing 'tomorrow' as due date."""
        result = NaturalLanguageParser.parse("Submit assignment tomorrow")
        expected = (date.today() + timedelta(days=1)).isoformat()
        assert result['due_date'] == expected

    def test_parse_due_date_day_of_week(self):
        """Test parsing day of week as due date."""
        # Test with a specific day
        result = NaturalLanguageParser.parse("Team meeting Friday")
        # Should return next Friday's date
        assert result['due_date'] is not None
        # The title should not contain "Friday"
        assert "friday" not in result['title'].lower()

    def test_parse_due_date_next_day(self):
        """Test parsing 'next [day]' as due date."""
        result = NaturalLanguageParser.parse("Project deadline next Monday")
        # Should return next Monday's date (at least 7 days away)
        assert result['due_date'] is not None

    def test_parse_due_date_in_days(self):
        """Test parsing 'in X days' as due date."""
        result = NaturalLanguageParser.parse("Review code in 3 days")
        expected = (date.today() + timedelta(days=3)).isoformat()
        assert result['due_date'] == expected

    def test_parse_due_date_in_weeks(self):
        """Test parsing 'in X weeks' as due date."""
        result = NaturalLanguageParser.parse("Final exam in 2 weeks")
        expected = (date.today() + timedelta(weeks=2)).isoformat()
        assert result['due_date'] == expected

    def test_parse_recurrence_daily(self):
        """Test parsing daily recurrence."""
        result = NaturalLanguageParser.parse("Morning exercise daily")
        assert result['is_recurring'] is True
        assert result['recurrence_pattern'] == 'daily'

    def test_parse_recurrence_weekly(self):
        """Test parsing weekly recurrence."""
        result = NaturalLanguageParser.parse("Team sync weekly")
        assert result['is_recurring'] is True
        assert result['recurrence_pattern'] == 'weekly'

    def test_parse_recurrence_monthly(self):
        """Test parsing monthly recurrence."""
        result = NaturalLanguageParser.parse("Pay rent monthly")
        assert result['is_recurring'] is True
        assert result['recurrence_pattern'] == 'monthly'

    def test_parse_recurrence_every_day(self):
        """Test parsing 'every day' recurrence."""
        result = NaturalLanguageParser.parse("Take vitamins every day")
        assert result['is_recurring'] is True
        assert result['recurrence_pattern'] == 'daily'

    def test_parse_complex_task(self):
        """Test parsing a complex task with multiple modifiers."""
        result = NaturalLanguageParser.parse("Call mom tomorrow urgent")
        assert "mom" in result['title'].lower()
        assert result['priority_id'] == 3  # High
        expected = (date.today() + timedelta(days=1)).isoformat()
        assert result['due_date'] == expected
        assert "urgent" not in result['title'].lower()
        assert "tomorrow" not in result['title'].lower()

    def test_parse_by_preposition_removal(self):
        """Test that 'by' preposition is removed with dates."""
        result = NaturalLanguageParser.parse("Submit report by Friday")
        assert "by" not in result['title'].lower()
        assert result['due_date'] is not None

    def test_clean_title_filler_words(self):
        """Test removal of filler words at the start."""
        result = NaturalLanguageParser.parse("I need to buy milk")
        assert "need to" not in result['title'].lower()
        assert result['title'] == "buy milk"

    def test_clean_title_extra_whitespace(self):
        """Test removal of extra whitespace."""
        result = NaturalLanguageParser.parse("Buy    groceries    now")
        assert result['title'] == "Buy groceries now"

    def test_parse_with_punctuation(self):
        """Test that trailing punctuation is cleaned."""
        result = NaturalLanguageParser.parse("Buy milk!")
        assert result['title'] == "Buy milk"

    def test_parse_empty_after_cleaning(self):
        """Test handling of input that becomes empty after cleaning."""
        # If input is just keywords, we should still get a valid result
        result = NaturalLanguageParser.parse("urgent today")
        assert result['title'].strip() != ""
        assert result['priority_id'] == 3

    def test_parse_priority_variations(self):
        """Test various priority keyword variations."""
        # Test 'critical'
        result = NaturalLanguageParser.parse("Fix server critical")
        assert result['priority_id'] == 3

        # Test 'high priority'
        result = NaturalLanguageParser.parse("Update docs high priority")
        assert result['priority_id'] == 3

        # Test 'low priority'
        result = NaturalLanguageParser.parse("Archive files low priority")
        assert result['priority_id'] == 1

    def test_parse_multiple_keywords_same_category(self):
        """Test that multiple keywords of same category are handled."""
        result = NaturalLanguageParser.parse("urgent important task")
        assert result['priority_id'] == 3  # Still high, not double
        assert "urgent" not in result['title'].lower()
        assert "important" not in result['title'].lower()

    def test_parse_preserves_core_task_description(self):
        """Test that core task description is preserved."""
        result = NaturalLanguageParser.parse("Call mom tomorrow urgent about birthday party")
        assert "mom" in result['title'].lower()
        assert "birthday" in result['title'].lower() or "party" in result['title'].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
