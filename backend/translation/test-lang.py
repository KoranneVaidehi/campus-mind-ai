# # # from language_detector import LanguageDetector

# # # detector = LanguageDetector()

# # # test_queries = [
# # #     ("What is a token?", "en"),
# # #     ("टोकन क्या है?", "hi"),
# # #     ("ટોકન શું છે?", "gu"),
# # #     ("टोकन म्हणजे काय?", "mr"),
# # #     ("டோக்கன் என்றால் என்ன?", "ta"),
# # #     ("టోకెన్ అంటే ఏమిటి?", "te"),
# # # ]

# # # print("Language Detection Test")
# # # print("-" * 50)

# # # for query, expected in test_queries:
# # #     detected = detector.detect_language(query)
# # #     status = "✅" if detected == expected else "❌"
# # #     print(f"{status} {query[:30]:30} -> {detected} (expected: {expected})")


# # from lingva_translator import LingvaTranslator

# # translator = LingvaTranslator()

# # # Test Hindi
# # hindi_text = "टोकन क्या है?"
# # print(f"Hindi: {hindi_text}")
# # result = translator.translate(hindi_text, 'hi', 'en')
# # print(f"English: {result}\n")

# # # Test Marathi
# # marathi_text = "टोकन म्हणजे काय?"
# # print(f"Marathi: {marathi_text}")
# # result = translator.translate(marathi_text, 'mr', 'en')
# # print(f"English: {result}\n")

# """
# Test translation for Hindi and Marathi
# """
# import sys
# from pathlib import Path

# sys.path.insert(0, str(Path(__file__).parent))

# from lingva_translator import LingvaTranslator

# translator = LingvaTranslator()

# print("=" * 50)
# print("Testing Hindi/Marathi Translation")
# print("=" * 50)

# # Test Marathi
# marathi = "टोकन म्हणजे काय?"
# print(f"\nMarathi: {marathi}")
# result = translator.translate(marathi, 'mr', 'en')
# print(f"English: {result}")
# print(f"✅ Success: {result == 'what is token?' or 'token' in result.lower()}")

# # Test Hindi
# hindi = "टोकन क्या है?"
# print(f"\nHindi: {hindi}")
# result = translator.translate(hindi, 'hi', 'en')
# print(f"English: {result}")

# print("\n" + "=" * 50)



from googletrans import Translator
from language_detector import LanguageDetector

detector = LanguageDetector()
translator = Translator()

text = "टोकन क्या है?"
lang = detector.detect_language(text)
print(f"Detected: {lang}")

# Translate to English
result = translator.translate(text, src=lang, dest='en')
print(f"English: {result.text}")

# Translate back
back = translator.translate(result.text, src='en', dest=lang)
print(f"Back to Hindi: {back.text}")