# # # # Run this to see what's available
# # # import google.generativeai as genai
# # # genai.configure(api_key="AIzaSyDndS9sRpuOlbbyHAAx6JuY4ORqIHaauUc")
# # # for model in genai.list_models():
# # #     if 'generateContent' in model.supported_generation_methods:
# # #         print(model.name)



# # # test_tesseract.py
# # import pytesseract
# # import subprocess

# # # Try to find tesseract
# # try:
# #     # Check if tesseract is in PATH
# #     result = subprocess.run(['tesseract', '--version'], 
# #                           capture_output=True, 
# #                           text=True)
# #     print("✅ Tesseract found in PATH")
# #     print(result.stdout[:200])
# # except FileNotFoundError:
# #     print("❌ Tesseract NOT found in PATH")
    
# #     # Try common installation paths
# #     common_paths = [
# #         r'C:\Program Files\Tesseract-OCR\tesseract.exe',
# #         r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
# #     ]
    
# #     for path in common_paths:
# #         import os
# #         if os.path.exists(path):
# #             print(f"✅ Found Tesseract at: {path}")
# #             # Set it for pytesseract
# #             pytesseract.pytesseract.tesseract_cmd = path
# #             print(f"✅ Set pytesseract to use: {path}")
# #             break
# #     else:
# #         print("❌ Tesseract not found. Please install it.")



# # test_multilingual.py
# import sys
# from pathlib import Path

# # Add backend to path
# sys.path.append(str(Path(__file__).parent / "backend"))

# from translation import TranslationWrapper, LanguageDetector

# # Test language detection
# detector = LanguageDetector()

# test_queries = [
#     ("What is lexical analysis?", "en"),
#     ("लेक्सिकल एनालिसिस क्या है?", "hi"),
#     ("લેક્સિકલ એનાલિસિસ શું છે?", "gu"),
#     ("लेक्सिकल एनालिसिस म्हणजे काय?", "mr"),
#     ("லெக்சிக்கல் அனாலிசிஸ் என்றால் என்ன?", "ta"),
#     ("లెక్సికల్ అనాలిసిస్ అంటే ఏమిటి?", "te"),
# ]

# print("Language Detection Test:")
# print("-" * 40)
# for query, expected in test_queries:
#     detected = detector.detect_language(query)
#     status = "✅" if detected == expected else "❌"
#     print(f"{status} Query: {query[:30]}... | Expected: {expected} | Got: {detected}")

# # Test translation (requires internet)
# print("\n\nTranslation Test:")
# print("-" * 40)

# from translation.lingva_translator import LingvaTranslator
# translator = LingvaTranslator()

# test_text = "What is lexical analysis?"
# print(f"Original: {test_text}")

# for lang in ['hi', 'gu', 'mr', 'ta', 'te']:
#     translated = translator.translate(test_text, 'en', lang)
#     print(f"{lang.upper()}: {translated}")
    
#     # Translate back to verify
#     back_to_english = translator.translate(translated, lang, 'en')
#     print(f"  Back to EN: {back_to_english}\n")



# test_fixed.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from translation.language_detector import LanguageDetector

detector = LanguageDetector()

print("=" * 60)
print("UPDATED LANGUAGE DETECTION TEST")
print("=" * 60)

test_queries = [
    ("What is lexical analysis?", "en", "English"),
    ("लेक्सिकल एनालिसिस क्या है?", "hi", "Hindi"),
    ("લેક્સિકલ એનાલિસિસ શું છે?", "gu", "Gujarati"),
    ("लेक्सिकल एनालिसिस म्हणजे काय?", "mr", "Marathi"),
    ("லெக்சிக்கல் அனாலிசிஸ் என்றால் என்ன?", "ta", "Tamil"),
    ("లెక్సికల్ అనాలిసిస్ అంటే ఏమిటి?", "te", "Telugu"),
]

print("\n{:<40} {:<8} {:<10} {}".format("Query", "Expected", "Got", "Status"))
print("-" * 80)

for query, expected_code, expected_name in test_queries:
    detected_code = detector.detect_language(query)
    detected_name = detector.get_language_name(detected_code)
    status = "✅" if detected_code == expected_code else "❌"
    
    # Truncate long queries
    display_query = query[:37] + "..." if len(query) > 40 else query
    
    print("{:<40} {:<8} {:<10} {}".format(
        display_query, expected_code, detected_code, status
    ))

print("\n" + "=" * 60)
print("Translation Test (Already Working!)")
print("=" * 60)

from translation.lingva_translator import LingvaTranslator
translator = LingvaTranslator()

test_text = "What is lexical analysis?"
print(f"\nOriginal: {test_text}\n")

for lang in ['hi', 'gu', 'mr', 'ta', 'te']:
    translated = translator.translate(test_text, 'en', lang)
    back = translator.translate(translated, lang, 'en')
    
    lang_name = detector.get_language_name(lang)
    print(f"{lang_name}: {translated}")
    print(f"  Back to EN: {back}\n")