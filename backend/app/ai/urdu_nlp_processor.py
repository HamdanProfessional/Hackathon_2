"""
Urdu NLP Processor for Enhanced Language Understanding

This module provides advanced Urdu language processing capabilities:
- Urdu text normalization and preprocessing
- Intent detection for Urdu task management commands
- Entity extraction (dates, priorities, actions)
- Roman Urdu to Urdu script conversion
- Sentiment analysis and language detection
- Task-related phrase matching and translation
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from enum import Enum

class UrduIntent(Enum):
    """Enumeration of detected Urdu intents."""
    CREATE_TASK = "create_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    SEARCH_TASKS = "search_tasks"
    GREETING = "greeting"
    HELP = "help"
    UNKNOWN = "unknown"

class UrduPriority(Enum):
    """Urdu priority mappings."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class UrduNLPProcessor:
    """
    Advanced Urdu Natural Language Processor for task management.

    Features:
    - Roman Urdu to Urdu script conversion
    - Intent detection with context awareness
    - Entity extraction (dates, priorities, actions)
    - Task phrase normalization
    - Bilingual command understanding
    """

    def __init__(self):
        """Initialize the Urdu NLP processor with dictionaries and patterns."""
        self._init_dictionaries()
        self._init_patterns()

    def _init_dictionaries(self):
        """Initialize Urdu language dictionaries."""
        # Greetings
        self.greetings = {
            'ur': ['السلام علیکم', 'سلام', 'ہیلو', 'آداب', 'خدحافظ'],
            'roman_urdu': ['assalam o alaikum', 'salam', 'hello', 'aadab', 'khuda hafiz', 'aslam o alikum'],
            'mixed': ['assalamualaikum', 'asalam-o-alaikum']
        }

        # Task action words
        self.task_actions = {
            'create': {
                'ur': ['بنانا', 'بنائیں', 'بنایا', 'تخلیق', 'شامل', 'شامل کریں', 'اضافہ', 'اکھیں'],
                'roman_urdu': ['banana', 'banayen', 'banaya', 'takhleeq', 'shamil', 'shamil karen', 'izafa', 'kahiye', 'banao'],
                'mixed': ['make task', 'create task', 'add task', 'new task']
            },
            'list': {
                'ur': ['فہرست', 'دکھائیں', 'لاشیں', 'دیکھیں', 'لیسٹ', 'کام کیا کیا ہے', 'کام'],
                'roman_urdu': ['fahrist', 'dikhaiyen', 'lashein', 'dekhein', 'list', 'kaam kya kya hai', 'kaam'],
                'mixed': ['show tasks', 'my tasks', 'what tasks', 'mere kaam']
            },
            'complete': {
                'ur': ['مکمل', 'ختم', 'ہو گیا', 'کردی', 'مکمل کریں', 'ختم کریں', 'پورا'],
                'roman_urdu': ['mukammal', 'khatam', 'ho gaya', 'kardi', 'mukammal karen', 'khatam karen', 'poora'],
                'mixed': ['complete', 'finish', 'done', 'ho gaya', 'kardiya']
            },
            'update': {
                'ur': ['اپڈیٹ', 'تبدیلی', 'بدلنا', ' تبدیل کرنا', 'نئی', 'تصحیح'],
                'roman_urdu': ['update', 'tabdeeli', 'badalna', 'tabdeel karna', 'nai', 'tasjeeh'],
                'mixed': ['change', 'modify', 'update task', 'edit']
            },
            'delete': {
                'ur': ['حذف', 'میٹاں', 'ختم کردینا', 'نکالنا', 'ہٹانا'],
                'roman_urdu': ['hazf', 'mitana', 'khatam kar dena', 'nikalna', 'hatana'],
                'mixed': ['remove', 'delete', 'mitado']
            }
        }

        # Priority words
        self.priority_words = {
            'high': {
                'ur': ['ضروری', 'فوری', 'اهم', 'بہت ضروری', 'جلدی'],
                'roman_urdu': ['zaroori', 'fori', 'ahem', 'bohat zaroori', 'jaldi'],
                'mixed': ['urgent', 'important', 'high priority', 'pehly karna']
            },
            'medium': {
                'ur': ['معمولی', 'درمیانی', 'اوسط'],
                'roman_urdu': ['mamooli', 'darmiyani', 'ausat'],
                'mixed': ['normal', 'medium', 'regular']
            },
            'low': {
                'ur': ['کم', 'غیر ضروری', 'آہستہ'],
                'roman_urdu': ['kam', 'ghair zaroori', 'aahesta'],
                'mixed': ['low priority', 'later', 'baad mein']
            }
        }

        # Time expressions
        self.time_expressions = {
            'today': {
                'ur': ['آج', 'آج'],
                'roman_urdu': ['aaj', 'aj']
            },
            'tomorrow': {
                'ur': ['کل', 'آئندہ کل'],
                'roman_urdu': ['kal', 'ayenda kal']
            },
            'yesterday': {
                'ur': ['گزستہ کل', 'پچھلے کل'],
                'roman_urdu': ['guzashta kal', 'pichlay kal']
            },
            'this_week': {
                'ur': ['اس ہفتے', 'ہفتے میں'],
                'roman_urdu': ['is hafte', 'hafte mein']
            },
            'next_week': {
                'ur': ['اگلے ہفتے', 'آیندہ ہفتے'],
                'roman_urdu': ['aglay hafte', 'ayenda hafte']
            }
        }

        # Common Urdu stop words (for processing)
        self.stop_words = {
            'ur': ['ہے', 'ہیں', 'کے', 'کی', 'کا', 'گے', 'گی', 'ہوں', 'ہو', 'کرنا', 'دینا', 'لینا', 'سے', 'پر', 'میں', 'کو', 'نے', 'بھی', 'تو', 'جو'],
            'roman_urdu': ['hai', 'hain', 'ke', 'ki', 'ka', 'ge', 'gi', 'houn', 'ho', 'karna', 'dena', 'lena', 'se', 'par', 'mein', 'ko', 'ne', 'bhi', 'to', 'jo']
        }

    def _init_patterns(self):
        """Initialize regex patterns for Urdu text processing."""
        # Urdu character ranges
        self.urdu_char_pattern = re.compile(r'[\u0600-\u06FF]')

        # Roman Urdu patterns (common transliterations)
        self.roman_urdu_patterns = [
            r'[a-zA-Z]+[a-zA-Z\s]*',  # Basic Roman Urdu
            r'(?:[a-zA-Z]+\s*)+[a-zA-Z]+'  # Multi-word Roman Urdu
        ]

        # Date patterns
        self.date_patterns = [
            # DD-MM-YYYY or YYYY-MM-DD
            r'\b\d{2,4}-\d{1,2}-\d{1,2}\b',
            # DD/MM/YYYY or YYYY/MM/DD
            r'\b\d{2,4}/\d{1,2}/\d{1,2}\b',
            # Month names
            r'\b(?:جنوری|فروری|مارچ|اپریل|مئی|جون|جولائی|اگست|ستمبر|اکتوبر|نومبر|دسمبر)\s+\d{1,4}\b',
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,4}\b'
        ]

        # Task title extraction patterns
        self.task_title_patterns = [
            # "بنائیں ٹاسک [نام]"
            r'(?:بنائیں|بنایا|شامل کریں|شامل)\s+(?:ٹاسک|کام)\s+["\']?([^"\']+)["\']?',
            # "ٹاسک [نام] بنائیں"
            r'(?:ٹاسک|کام)\s+["\']?([^"\']+)["\']?\s+(?:بنائیں|بنایا|شامل کریں)',
            # "create task [name]" mixed
            r'(?:create|make|add)\s+(?:task|todo)\s+["\']?([^"\']+)["\']?',
        ]

    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of the input text.

        Returns:
            Tuple of (language_code, confidence_score)
            language_code: 'ur', 'en', 'roman_urdu', 'mixed'
        """
        if not text or not text.strip():
            return 'unknown', 0.0

        # Count different character types
        total_chars = len(re.sub(r'\s', '', text))
        if total_chars == 0:
            return 'unknown', 0.0

        urdu_chars = len(self.urdu_char_pattern.findall(text))
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        roman_urdu_indicators = 0

        # Check for Roman Urdu indicators (mixed patterns)
        text_lower = text.lower()
        for script_type in ['roman_urdu', 'mixed']:
            for _, words in self.task_actions[script_type].items():
                for word in words:
                    if word in text_lower:
                        roman_urdu_indicators += 1

            for _, words in self.priority_words[script_type].items():
                for word in words:
                    if word in text_lower:
                        roman_urdu_indicators += 1

        # Calculate percentages
        urdu_percentage = (urdu_chars / total_chars) * 100
        english_percentage = (english_words / total_chars) * 10  # Weight words less heavily

        # Determine language
        if urdu_percentage > 50:
            return 'ur', min(urdu_percentage / 100, 1.0)
        elif roman_urdu_indicators > 0 or (urdu_percentage > 20 and english_percentage > 10):
            return 'mixed', min((roman_urdu_indicators * 10 + urdu_percentage) / 100, 1.0)
        elif english_percentage > 30:
            return 'en', min(english_percentage / 100, 1.0)
        else:
            return 'roman_urdu', min((roman_urdu_indicators * 20) / 100, 1.0)

    def normalize_text(self, text: str) -> str:
        """
        Normalize Urdu text by applying various preprocessing steps.

        Includes:
        - Case normalization
        - Punctuation handling
        - Whitespace normalization
        - Common variations normalization
        """
        if not text:
            return ""

        # Convert to lowercase for Roman Urdu
        normalized = text.lower()

        # Normalize common variations
        variations = {
            'assalam o alaikum': 'assalamualaikum',
            'aslam o alikum': 'assalamualaikum',
            'assalamualaikum': 'سلام علیکم',
            'kaam': 'کام',
            'kaam kya kya hai': 'کام کیا کیا ہے',
            'fori': 'فوری',
            'zaroori': 'ضروری',
            'hazf': 'حذف',
            'khatam': 'ختم',
            'mukammal': 'مکمل',
            'dikhaiyen': 'دکھائیں'
        }

        for variation, standard in variations.items():
            normalized = normalized.replace(variation, standard)

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def detect_intent(self, text: str, language: str = None) -> UrduIntent:
        """
        Detect the user's intent from the text.

        Args:
            text: Input text to analyze
            language: Optional language hint from detect_language()

        Returns:
            Detected intent as UrduIntent enum
        """
        if not text:
            return UrduIntent.UNKNOWN

        # Detect language if not provided
        if language is None:
            language, _ = self.detect_language(text)

        normalized_text = self.normalize_text(text)

        # Check for greetings first
        if self._is_greeting(normalized_text, language):
            return UrduIntent.GREETING

        # Check for help requests
        if self._is_help_request(normalized_text, language):
            return UrduIntent.HELP

        # Check for task-related intents
        intent_scores = {}

        for action_type, action_words in self.task_actions.items():
            score = self._calculate_intent_score(normalized_text, action_words, language)
            if score > 0:
                intent_scores[action_type] = score

        # Return the intent with highest score
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            if best_intent[1] > 0.1:  # Minimum confidence threshold
                intent_map = {
                    'create': UrduIntent.CREATE_TASK,
                    'list': UrduIntent.LIST_TASKS,
                    'complete': UrduIntent.COMPLETE_TASK,
                    'update': UrduIntent.UPDATE_TASK,
                    'delete': UrduIntent.DELETE_TASK
                }
                return intent_map.get(best_intent[0], UrduIntent.UNKNOWN)

        return UrduIntent.UNKNOWN

    def extract_task_title(self, text: str, language: str = None) -> Optional[str]:
        """
        Extract task title from user input.

        Uses multiple patterns to find task names in various formats.
        """
        if not text:
            return None

        if language is None:
            language, _ = self.detect_language(text)

        normalized_text = self.normalize_text(text)

        # Try different patterns
        for pattern in self.task_title_patterns:
            match = re.search(pattern, normalized_text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if title and len(title) > 0:
                    return self._clean_task_title(title)

        # Fallback: look for task-related keywords and extract following text
        task_indicators = ['ٹاسک', 'کام', 'task', 'todo', 'kaam']
        for indicator in task_indicators:
            if indicator in normalized_text.lower():
                parts = normalized_text.lower().split(indicator)
                if len(parts) > 1:
                    potential_title = parts[-1].strip()
                    # Remove action words from title
                    for action_words in self.task_actions.values():
                        for script_type in action_words.values():
                            for word in script_words:
                                if word in potential_title:
                                    potential_title = potential_title.replace(word, '').strip()

                    if potential_title and len(potential_title) > 2:
                        return self._clean_task_title(potential_title)

        return None

    def extract_priority(self, text: str, language: str = None) -> str:
        """
        Extract task priority from text.

        Returns: 'high', 'medium', 'low', or '' if not found
        """
        if not text:
            return ""

        if language is None:
            language, _ = self.detect_language(text)

        normalized_text = self.normalize_text(text)

        for priority_level, priority_words in self.priority_words.items():
            for script_type in priority_words.values():
                for word in priority_words:
                    if word in normalized_text:
                        return priority_level

        return ""

    def extract_date_expression(self, text: str, language: str = None) -> Optional[str]:
        """
        Extract date expressions from text.

        Returns: Standardized date expression or None
        """
        if not text:
            return None

        if language is None:
            language, _ = self.detect_language(text)

        normalized_text = self.normalize_text(text)

        # Check for predefined time expressions
        for time_expr, time_words in self.time_expressions.items():
            for script_type in time_words.values():
                for word in time_words:
                    if word in normalized_text:
                        return time_expr

        # Check for date patterns
        for pattern in self.date_patterns:
            match = re.search(pattern, normalized_text)
            if match:
                date_str = match.group()
                # Try to normalize the date format
                return self._normalize_date(date_str)

        return None

    def convert_to_standard_date(self, date_expression: str) -> Optional[str]:
        """
        Convert relative date expressions to absolute dates.

        Args:
            date_expression: Date expression like 'today', 'tomorrow', etc.

        Returns:
            Date in YYYY-MM-DD format or None if invalid
        """
        today = date.today()

        if date_expression == 'today':
            return today.strftime('%Y-%m-%d')
        elif date_expression == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime('%Y-%m-%d')
        elif date_expression == 'this_week':
            week_end = today + timedelta(days=7)
            return week_end.strftime('%Y-%m-%d')
        elif date_expression == 'next_week':
            next_week = today + timedelta(days=14)
            return next_week.strftime('%Y-%m-%d')
        elif date_expression == 'yesterday':
            yesterday = today - timedelta(days=1)
            return yesterday.strftime('%Y-%m-%d')
        else:
            # Try to parse as date string
            try:
                # Handle different formats
                if '-' in date_expression:
                    parts = date_expression.split('-')
                    if len(parts) == 3:
                        year, month, day = parts
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                elif '/' in date_expression:
                    parts = date_expression.split('/')
                    if len(parts) == 3:
                        year, month, day = parts
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            except Exception:
                pass

        return None

    def _is_greeting(self, text: str, language: str) -> bool:
        """Check if text is a greeting."""
        for script_type in self.greetings.values():
            for greeting in script_type:
                if greeting in text.lower():
                    return True
        return False

    def _is_help_request(self, text: str, language: str) -> bool:
        """Check if text is a help request."""
        help_words = ['مدد', 'help', 'کیسے', 'کیا', 'how', 'what', 'کیا کرنا']
        return any(word in text.lower() for word in help_words)

    def _calculate_intent_score(self, text: str, action_words: Dict[str, List[str]], language: str) -> float:
        """Calculate confidence score for a specific intent."""
        score = 0.0
        text_lower = text.lower()

        # Check exact matches
        for script_type, words in action_words.items():
            for word in words:
                if word in text_lower:
                    # Higher score for exact matches
                    score += 0.8 if script_type == language else 0.4

        # Check partial matches
        for script_type, words in action_words.items():
            for word in words:
                if any(part in text_lower for part in word.split()):
                    # Lower score for partial matches
                    score += 0.3 if script_type == language else 0.1

        return min(score, 1.0)

    def _clean_task_title(self, title: str) -> str:
        """Clean and normalize task title."""
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title.strip())

        # Remove punctuation at start/end
        title = title.strip('.,!?()[]{}"\'')

        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]

        return title

    def _normalize_date(self, date_str: str) -> str:
        """Normalize various date formats to standard format."""
        # This is a simplified version - could be enhanced
        date_str = date_str.strip()

        # Remove any extra characters
        date_str = re.sub(r'[^\d\-/]', '', date_str)

        return date_str

    def process_task_request(self, text: str) -> Dict[str, Any]:
        """
        Process a complete task request and extract all relevant information.

        Returns a comprehensive analysis of the user's request.
        """
        if not text:
            return {
                "status": "error",
                "message": "Empty input",
                "analysis": {}
            }

        # Detect language
        language, confidence = self.detect_language(text)

        # Normalize text
        normalized_text = self.normalize_text(text)

        # Extract components
        intent = self.detect_intent(normalized_text, language)
        task_title = self.extract_task_title(normalized_text, language)
        priority = self.extract_priority(normalized_text, language)
        date_expr = self.extract_date_expression(normalized_text, language)

        # Convert date expression if found
        due_date = None
        if date_expr:
            due_date = self.convert_to_standard_date(date_expr)

        # Build comprehensive analysis
        analysis = {
            "original_text": text,
            "normalized_text": normalized_text,
            "language": {
                "detected": language,
                "confidence": confidence
            },
            "intent": {
                "detected": intent.value,
                "description": self._get_intent_description(intent)
            },
            "extracted_entities": {
                "task_title": task_title,
                "priority": priority or "medium",
                "date_expression": date_expr,
                "due_date": due_date
            },
            "processing_metadata": {
                "processed_at": datetime.utcnow().isoformat(),
                "text_length": len(text),
                "has_urdu": language in ['ur', 'mixed', 'roman_urdu']
            }
        }

        # Generate response message
        response = self._generate_response_message(analysis)

        return {
            "status": "success",
            "analysis": analysis,
            "response": response
        }

    def _get_intent_description(self, intent: UrduIntent) -> str:
        """Get human-readable description of intent."""
        descriptions = {
            UrduIntent.CREATE_TASK: "Create a new task",
            UrduIntent.LIST_TASKS: "List or show tasks",
            UrduIntent.COMPLETE_TASK: "Mark task as completed",
            UrduIntent.UPDATE_TASK: "Update or modify a task",
            UrduIntent.DELETE_TASK: "Delete or remove a task",
            UrduIntent.SEARCH_TASKS: "Search for tasks",
            UrduIntent.GREETING: "Greeting message",
            UrduIntent.HELP: "Request for help",
            UrduIntent.UNKNOWN: "Unknown intent"
        }
        return descriptions.get(intent, "Unknown intent")

    def _generate_response_message(self, analysis: Dict[str, Any]) -> str:
        """Generate appropriate response message based on analysis."""
        language = analysis["language"]["detected"]
        intent = analysis["intent"]["detected"]
        entities = analysis["extracted_entities"]

        # Language-specific responses
        if language in ['ur', 'mixed', 'roman_urdu']:
            return self._generate_urdu_response(intent, entities, language)
        else:
            return self._generate_english_response(intent, entities)

    def _generate_urdu_response(self, intent: str, entities: Dict[str, Any], language: str) -> str:
        """Generate Urdu language response."""
        responses = {
            "create_task": f"میں '{entities.get('task_title', 'نئی ٹاسک')}' نامی ٹاسک بناتا ہوں۔",
            "list_tasks": "آپ کی ٹاسکس کی فہرست لاتا ہوں۔",
            "complete_task": "میں ٹاسک کو مکمل کرنے کی کوشش کرتا ہوں۔",
            "update_task": "میں ٹاسک کو اپ ڈیٹ کرتا ہوں۔",
            "delete_task": "میں ٹاسک کو حذف کرنے کی کوشش کرتا ہوں۔",
            "greeting": "سلام! میں آپ کی ٹاسکس منیج کرنے میں مدد کر سکتا ہوں۔",
            "help": "میں آپ کو ٹاسکس بنانے، دیکھنے، مکمل کرنے، اپ ڈیٹ کرنے، اور حذف کرنے میں مدد کر سکتا ہوں۔",
            "unknown": "مجھے سمجھ نہیں آیا۔ براہ کرم دوبارہ کوشش کریں۔"
        }
        return responses.get(intent, "کچھ غلطی ہو گئی۔")

    def _generate_english_response(self, intent: str, entities: Dict[str, Any]) -> str:
        """Generate English language response."""
        responses = {
            "create_task": f"I'll create a task '{entities.get('task_title', 'new task')}'.",
            "list_tasks": "I'll get your list of tasks.",
            "complete_task": "I'll help you complete the task.",
            "update_task": "I'll update the task for you.",
            "delete_task": "I'll delete the task for you.",
            "greeting": "Hello! I can help you manage your tasks.",
            "help": "I can help you create, view, complete, update, and delete tasks.",
            "unknown": "I didn't understand. Please try again."
        }
        return responses.get(intent, "Something went wrong.")

# Export the main processor
urdu_processor = UrduNLPProcessor()