"""
Translation Wrapper - Direct Google Translate Only
"""
from typing import Dict, Any
from googletrans import Translator
from .language_detector import LanguageDetector


class TranslationWrapper:
    """Direct Google Translate wrapper"""
    
    def __init__(self, original_chatbot):
        self.chatbot = original_chatbot
        self.detector = LanguageDetector()
        self.translator = Translator()
        self.current_language = 'en'
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        # Detect language
        detected_lang = self.detector.detect_language(user_input)
        self.current_language = detected_lang
        
        print(f"🌐 Detected: {self.detector.get_language_name(detected_lang)}")
        
        # Translate to English
        if detected_lang != 'en':
            try:
                result = self.translator.translate(user_input, src=detected_lang, dest='en')
                english_query = result.text
                print(f"📝 English: {english_query}")
            except Exception as e:
                print(f"❌ Translation failed: {e}")
                english_query = user_input
        else:
            english_query = user_input
        
        # Get response from chatbot
        try:
            is_pdf_req, pdf_name = self.chatbot.is_pdf_request(english_query)
            
            if is_pdf_req:
                result = self.chatbot.retrieve_pdf(pdf_name)
                response_text = result.get('message', '')
                is_pdf = True
                sources = []
                chunks = 0
                pdf_result = result
            else:
                qa = self.chatbot.answer_question(english_query)
                response_text = qa.get('answer', '')
                is_pdf = False
                sources = qa.get('sources', [])
                chunks = qa.get('context_chunks', 0)
                pdf_result = None
        except Exception as e:
            response_text = f"Error: {e}"
            is_pdf = False
            sources = []
            chunks = 0
            pdf_result = None
        
        # Translate back
        if detected_lang != 'en' and response_text:
            try:
                back = self.translator.translate(response_text, src='en', dest=detected_lang)
                translated = back.text
            except:
                translated = response_text
        else:
            translated = response_text
        
        return {
            'detected_language': detected_lang,
            'response_translated': translated,
            'sources': sources,
            'is_pdf_request': is_pdf,
            'pdf_result': pdf_result,
            'context_chunks': chunks
        }