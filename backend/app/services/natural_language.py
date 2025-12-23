"""Natural language parser for quick task creation."""
import re
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional

try:
    from dateutil import parser as dateutil_parser
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False


class NaturalLanguageParser:
    """Parse task details from natural language input."""

    # Priority keywords
    PRIORITY_HIGH = ['urgent', 'asap', 'important', 'high priority', 'critical', '!!!', '!!!', 'priority high']
    PRIORITY_LOW = ['low', 'maybe', 'someday', 'low priority', 'eventually', 'priority low']

    # Recurrence patterns
    RECURRENCE_PATTERNS = {
        'daily': r'\b(daily|every day|each day)\b',
        'weekly': r'\b(weekly|every week|each week)\b',
        'monthly': r'\b(monthly|every month|each month)\b',
        'yearly': r'\b(yearly|every year|annually)\b',
    }

    @classmethod
    def parse(cls, text: str) -> Dict[str, Any]:
        """
        Parse natural language task input.

        Args:
            text: Natural language input like "Call mom tomorrow urgent"

        Returns:
            Dict with parsed task fields: title, description, priority_id,
            due_date, is_recurring, recurrence_pattern

        Examples:
            >>> NaturalLanguageParser.parse("Call mom tomorrow urgent")
            {'title': 'Call mom', 'priority_id': 3, 'due_date': '2025-12-24', ...}
        """
        result = {
            'title': text,
            'description': '',
            'priority_id': 2,  # Default medium
            'due_date': None,
            'is_recurring': False,
            'recurrence_pattern': None,
        }

        # Extract priority
        priority = cls._extract_priority(text)
        if priority:
            result['priority_id'] = priority
            text = cls._remove_priority_keywords(text)

        # Extract due date
        due_date = cls._extract_due_date(text)
        if due_date:
            result['due_date'] = due_date
            text = cls._remove_date_keywords(text)

        # Extract recurrence
        recurrence = cls._extract_recurrence(text)
        if recurrence:
            result['is_recurring'] = True
            result['recurrence_pattern'] = recurrence
            text = cls._remove_recurrence_keywords(text)

        # Clean up title - remove common filler words
        text = cls._clean_title(text)
        result['title'] = text.strip().strip('.,;!')

        # If title is empty after parsing (e.g., only keywords were provided),
        # generate a default title
        if not result['title']:
            if result['priority_id'] == 3:
                result['title'] = "High priority task"
            elif result['priority_id'] == 1:
                result['title'] = "Low priority task"
            elif result['is_recurring']:
                result['title'] = f"Recurring {result['recurrence_pattern']} task"
            elif result['due_date']:
                result['title'] = "Task"
            else:
                result['title'] = "New task"

        return result

    @classmethod
    def _extract_priority(cls, text: str) -> Optional[int]:
        """Extract priority level from text."""
        text_lower = text.lower()
        if any(word in text_lower for word in cls.PRIORITY_HIGH):
            return 3  # High
        if any(word in text_lower for word in cls.PRIORITY_LOW):
            return 1  # Low
        return None

    @classmethod
    def _extract_due_date(cls, text: str) -> Optional[str]:
        """
        Extract due date from text.

        Returns:
            Date string in YYYY-MM-DD format or None
        """
        today = date.today()

        # Relative dates
        if re.search(r'\btoday\b', text, re.I):
            return today.isoformat()
        if re.search(r'\btomorrow\b', text, re.I):
            return (today + timedelta(days=1)).isoformat()

        # Day of week
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(days):
            if re.search(rf'\b{day}\b', text, re.I):
                days_ahead = (i - today.weekday() + 7) % 7
                if days_ahead == 0:
                    days_ahead = 7  # Next occurrence, not today
                return (today + timedelta(days=days_ahead)).isoformat()

        # "next [day]"
        for i, day in enumerate(days):
            if re.search(rf'\bnext {day}\b', text, re.I):
                days_ahead = (i - today.weekday() + 7) % 7 + 7
                return (today + timedelta(days=days_ahead)).isoformat()

        # Number patterns: "in 3 days", "in 2 weeks"
        match = re.search(r'in (\d+) (day|days|week|weeks)', text, re.I)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            if 'day' in unit:
                return (today + timedelta(days=num)).isoformat()
            elif 'week' in unit:
                return (today + timedelta(weeks=num)).isoformat()

        # Try dateutil parser as fallback if available
        if DATEUTIL_AVAILABLE:
            try:
                parsed = dateutil_parser.parse(text, fuzzy=True)
                if parsed.date() >= today:
                    return parsed.date().isoformat()
            except (ValueError, TypeError):
                pass

        return None

    @classmethod
    def _extract_recurrence(cls, text: str) -> Optional[str]:
        """Extract recurrence pattern from text."""
        text_lower = text.lower()
        for pattern, regex in cls.RECURRENCE_PATTERNS.items():
            if re.search(regex, text_lower):
                return pattern
        return None

    @classmethod
    def _remove_priority_keywords(cls, text: str) -> str:
        """Remove priority keywords from text."""
        for keyword in cls.PRIORITY_HIGH + cls.PRIORITY_LOW:
            text = re.sub(rf'\b{re.escape(keyword)}\b', '', text, flags=re.I)
        return text

    @classmethod
    def _remove_date_keywords(cls, text: str) -> str:
        """Remove date keywords from text."""
        text = re.sub(r'\btoday\b', '', text, flags=re.I)
        text = re.sub(r'\btomorrow\b', '', text, flags=re.I)

        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            text = re.sub(rf'\b{re.escape(day)}\b', '', text, flags=re.I)
            text = re.sub(rf'\bnext {re.escape(day)}\b', '', text, flags=re.I)

        text = re.sub(r'\bin \d+ (day|days|week|weeks)\b', '', text, flags=re.I)

        # Remove "by" preposition often used with dates
        text = re.sub(r'\bby\b', '', text, flags=re.I)

        return text

    @classmethod
    def _remove_recurrence_keywords(cls, text: str) -> str:
        """Remove recurrence keywords from text."""
        for pattern, regex in cls.RECURRENCE_PATTERNS.items():
            text = re.sub(regex, '', text, flags=re.I)
        return text

    @classmethod
    def _clean_title(cls, text: str) -> str:
        """Clean up title by removing extra whitespace and common filler words."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove common filler phrases at the start
        filler_phrases = [
            r'^\s*(i need to|i gotta|i have to|remember to|don\'t forget to|gotta)\s+',
            r'^\s*(need to|have to|must)\s+',
        ]
        for phrase in filler_phrases:
            text = re.sub(phrase, '', text, flags=re.I)

        return text
