"""
Language Detection Module
Detects user input language from multiple Indian languages
"""
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import re

# Set seed for consistent results
DetectorFactory.seed = 0


class LanguageDetector:
    """
    Detects language from user query
    Supports: English, Hindi, Gujarati, Marathi, Tamil, Telugu
    """
    
    # Unicode ranges for Indian languages
    LANGUAGE_RANGES = {
        'gu': range(0x0A80, 0x0AFF),  # Gujarati
        'ta': range(0x0B80, 0x0BFF),  # Tamil
        'te': range(0x0C00, 0x0C7F),  # Telugu
        'hi': range(0x0900, 0x097F),  # Hindi/Devanagari
        'mr': range(0x0900, 0x097F),  # Marathi/Devanagari
    }
    
    # Marathi-specific character patterns
    MARATHI_PATTERNS = [
        'लॉ', 'ल्या', 'ली', 'ले', 'चा', 'ची', 'चे', 'नी', 'ना', 'ते', 'ता',
        'म्हणजे', 'आहे', 'काय', 'नाही', 'होते', 'ती', 'तो'
    ]
    
    # Common words/phrases for better detection
    HINDI_WORDS = ['क्या', 'है', 'मैं', 'आप', 'यह', 'वह', 'कैसे', 'कब', 'कहाँ', 'होता']
    MARATHI_WORDS = ['काय', 'आहे', 'मी', 'तू', 'हा', 'ती', 'कसे', 'केव्हा', 'कुठे', 'म्हणजे', 'नाही']
    GUJARATI_WORDS = ['શું', 'છે', 'હું', 'તમે', 'આ', 'તે', 'કેવી', 'ક્યારે', 'ક્યાં']
    TAMIL_WORDS = ['என்ன', 'உள்ளது', 'நான்', 'நீங்கள்', 'இது', 'அது', 'எப்படி', 'எப்போது', 'எங்கே']
    TELUGU_WORDS = ['ఏమిటి', 'ఉంది', 'నేను', 'మీరు', 'ఇది', 'అది', 'ఎలా', 'ఎప్పుడు', 'ఎక్కడ']
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect the language of input text
        Returns: language code (en, hi, gu, mr, ta, te)
        """
        if not text or not text.strip():
            return 'en'
        
        text = text.strip()
        
        # METHOD 1: Check for Indian scripts using Unicode ranges
        for lang, unicode_range in LanguageDetector.LANGUAGE_RANGES.items():
            for char in text[:100]:  # Check first 100 chars
                if ord(char) in unicode_range:
                    # Differentiate between Hindi and Marathi
                    if lang == 'hi' or lang == 'mr':
                        return LanguageDetector._differentiate_hindi_marathi(text)
                    return lang
        
        # METHOD 2: Check for Romanized Indian languages (Hinglish, etc.)
        detected = LanguageDetector._detect_romanized_languages(text)
        if detected:
            return detected
        
        # METHOD 3: Fallback to langdetect for English and other languages
        try:
            lang_code = detect(text)
            # Map langdetect codes to our supported languages (2-letter codes)
            mapping = {
                'hi': 'hi', 'gu': 'gu', 'mr': 'mr', 
                'ta': 'ta', 'te': 'te', 'en': 'en'
            }
            result = mapping.get(lang_code, 'en')
            return result
        except LangDetectException:
            return 'en'
    
    @staticmethod
    def _differentiate_hindi_marathi(text: str) -> str:
        """
        Differentiate between Hindi and Marathi script
        Enhanced with better scoring
        """
        text_lower = text.lower()
        
        # Marathi specific patterns (higher weight)
        marathi_score = 0
        for pattern in LanguageDetector.MARATHI_PATTERNS:
            if pattern in text_lower:
                marathi_score += 2  # Higher weight for patterns
        
        # Check for common Marathi words
        for word in LanguageDetector.MARATHI_WORDS:
            if word in text_lower:
                marathi_score += 3  # Even higher weight for full words
        
        # Check for Hindi words
        hindi_score = 0
        for word in LanguageDetector.HINDI_WORDS:
            if word in text_lower:
                hindi_score += 1
        
        # Decision based on scores
        if marathi_score > hindi_score:
            return 'mr'
        else:
            return 'hi'
    
    @staticmethod
    def _detect_romanized_languages(text: str) -> str:
        """
        Detect romanized Indian languages (Hinglish, etc.)
        Using common word patterns
        """
        words = text.lower().split()
        
        # Create score dictionary
        scores = {'hi': 0, 'gu': 0, 'mr': 0, 'ta': 0, 'te': 0}
        
        # Check for common words in each language
        for word in words:
            if word in LanguageDetector.HINDI_WORDS:
                scores['hi'] += 1
            if word in LanguageDetector.GUJARATI_WORDS:
                scores['gu'] += 1
            if word in LanguageDetector.MARATHI_WORDS:
                scores['mr'] += 1
            if word in LanguageDetector.TAMIL_WORDS:
                scores['ta'] += 1
            if word in LanguageDetector.TELUGU_WORDS:
                scores['te'] += 1
        
        # Get max score
        max_score = max(scores.values())
        if max_score > 0:
            for lang, score in scores.items():
                if score == max_score:
                    return lang
        
        return None
    
    @staticmethod
    def get_language_name(lang_code: str) -> str:
        """Convert language code to full name"""
        names = {
            'en': 'English',
            'hi': 'Hindi',
            'gu': 'Gujarati',
            'mr': 'Marathi',
            'ta': 'Tamil',
            'te': 'Telugu'
        }
        return names.get(lang_code, 'English')