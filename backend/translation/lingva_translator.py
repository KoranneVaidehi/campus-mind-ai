"""
Lingva Translate API Integration with Google Translate Fallback
Fixed for Hindi and Marathi translation
"""
import requests
import time
from typing import Optional
import urllib.parse

# Try to import googletrans
try:
    from googletrans import Translator as GoogleTranslator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    print("⚠️ googletrans not installed. Run: pip install googletrans==3.1.0a0")


class LingvaTranslator:
    """
    Translator with proper Hindi/Marathi support
    """
    
    LINGVA_INSTANCES = [
        "https://lingva.ml",
        "https://translate.plasmo.com",
        "https://lingva.pussthecat.org",
    ]
    
    def __init__(self, timeout: int = 10, use_fallback: bool = True):
        self.timeout = timeout
        self.use_fallback = use_fallback
        self.current_instance = 0
        
        # Initialize Google Translate (REQUIRED for Hindi/Marathi)
        self.google_fallback = None
        if GOOGLETRANS_AVAILABLE:
            try:
                self.google_fallback = GoogleTranslator()
                print("✅ Google Translate ready for Hindi/Marathi")
            except Exception as e:
                print(f"⚠️ Google Translate init failed: {e}")
        else:
            print("❌ CRITICAL: googletrans not installed!")
            print("   Run: pip install googletrans==3.1.0a0")
        
        self.last_request_time = 0
        self.min_request_interval = 0.5
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text - FORCED Google Translate for Hindi/Marathi
        """
        if not text or not text.strip():
            return text
        
        if source_lang == target_lang:
            return text
        
        print(f"   Translating from {source_lang} to {target_lang}: {text[:50]}...")
        
        # FOR HINDI AND MARATHI: Use Google Translate directly
        if source_lang in ['hi', 'mr'] and target_lang == 'en':
            if self.google_fallback:
                translated = self._translate_google(text, source_lang, target_lang)
                if translated:
                    print(f"   ✓ Translated: {translated[:50]}...")
                    return translated
            else:
                print(f"   ❌ No translator available for {source_lang}")
                return text
        
        # For other languages, try Lingva first
        translated = self._try_lingva(text, source_lang, target_lang)
        if translated:
            return translated
        
        # Fallback to Google for other languages
        if self.google_fallback:
            translated = self._translate_google(text, source_lang, target_lang)
            if translated:
                return translated
        
        print(f"   ⚠️ Translation failed, returning original")
        return text
    
    def _try_lingva(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Try Lingva instances"""
        for attempt in range(len(self.LINGVA_INSTANCES)):
            instance_idx = (self.current_instance + attempt) % len(self.LINGVA_INSTANCES)
            instance_url = self.LINGVA_INSTANCES[instance_idx]
            
            try:
                translated = self._translate_lingva(text, source_lang, target_lang, instance_url)
                if translated:
                    self.current_instance = instance_idx
                    return translated
            except Exception as e:
                continue
        
        return None
    
    def _translate_lingva(self, text: str, source_lang: str, target_lang: str, instance: str) -> Optional[str]:
        """Translate using Lingva API"""
        try:
            source = self._map_language_code(source_lang)
            target = self._map_language_code(target_lang)
            encoded_text = urllib.parse.quote(text)
            url = f"{instance}/api/v1/{source}/{target}/{encoded_text}"
            
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                translation = data.get('translation')
                if translation and translation != text:
                    return translation
            return None
        except:
            return None
    
    def _translate_google(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Translate using googletrans"""
        try:
            lang_map = {
                'hi': 'hi', 'mr': 'mr', 'gu': 'gu', 
                'ta': 'ta', 'te': 'te', 'en': 'en'
            }
            
            source = lang_map.get(source_lang, 'auto')
            target = lang_map.get(target_lang, 'en')
            
            time.sleep(0.5)
            
            result = self.google_fallback.translate(text, src=source, dest=target)
            
            if result and result.text:
                return result.text
            return None
            
        except Exception as e:
            print(f"   Google translate error: {e}")
            return None
    
    def _map_language_code(self, lang_code: str) -> str:
        """Map to Lingva API codes"""
        mapping = {
            'en': 'en', 'hi': 'hi', 'gu': 'gu', 
            'mr': 'mr', 'ta': 'ta', 'te': 'te'
        }
        return mapping.get(lang_code, 'en')


# ============ ADD THIS MISSING CLASS ============
class SimpleLingvaClient:
    """Simpler Lingva client without fallback"""
    
    def __init__(self, base_url: str = "https://lingva.ml"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text - FORCED Google Translate for Hindi/Marathi
        """
        if not text or not text.strip():
            return text
        
        if source_lang == target_lang:
            return text
        
        print(f"   🔄 Translating from {source_lang} to {target_lang}: {text[:50]}...")
        
        # FOR HINDI AND MARATHI: Use Google Translate directly
        if source_lang in ['hi', 'mr'] and target_lang == 'en':
            if self.google_fallback:
                translated = self._translate_google(text, source_lang, target_lang)
                if translated:
                    print(f"   ✅ SUCCESS: {translated[:50]}...")
                    return translated
                else:
                    print(f"   ❌ Google translate returned None")
                    return text
            else:
                print(f"   ❌ No Google fallback available")
                return text
        
        # For other languages, try Lingva first
        translated = self._try_lingva(text, source_lang, target_lang)
        if translated:
            print(f"   ✅ Lingva success: {translated[:50]}...")
            return translated
        
        # Fallback to Google for other languages
        if self.google_fallback:
            translated = self._translate_google(text, source_lang, target_lang)
            if translated:
                print(f"   ✅ Google fallback: {translated[:50]}...")
                return translated
        
        print(f"   ❌ ALL translation methods failed")
        return text