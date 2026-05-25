"""
Smart Multilingual AI-Powered Academic Assistant
Phase 1 MVP: RAG-based PDF chatbot for academic materials
With OCR support for image-based PDFs and PDF file retrieval
"""
import os

# Disable Chroma telemetry logs
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Hide warnings
import warnings
warnings.filterwarnings("ignore")

import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any
import re
from datetime import datetime
import time

from dotenv import load_dotenv

# Add parent directory to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

# LangChain Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.schema import Document

# OCR imports for image-based PDFs
import pytesseract
from pdf2image import convert_from_path

# ========== IMPORTANT: Configure Tesseract Path ==========
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Add this import at the top of main.py (if not already there)
from translation import TranslationWrapper
# ========== Configure Poppler Path ==========
# Try multiple possible poppler locations
POPPLER_PATH = None
possible_poppler_paths = [
    project_root / "poppler" / "Library" / "bin",
    Path(r'C:\Program Files\poppler\Library\bin'),
    Path(r'C:\poppler\bin'),
    Path(r'C:\poppler\Library\bin'),
]

for path in possible_poppler_paths:
    if path and path.exists():
        POPPLER_PATH = str(path)
        print(f"✅ Poppler found at: {POPPLER_PATH}")
        break

if not POPPLER_PATH:
    print("⚠️ Poppler not found. Install from: https://github.com/oschwartz10612/poppler-windows/releases/")
    print("   Download the latest release (e.g., Release-24.08.0-0.zip)")
    print("   Extract to: C:\\Program Files\\poppler\\")

import chromadb 
chromadb.api.client.SharedSystemClient.clear_system_cache()

# ========== SIMPLE TRANSLATOR (No external APIs needed) ==========
class SimpleTranslator:
    """Simple translator that doesn't require external APIs"""
    
    # Basic word mappings for common terms
    WORD_MAPPINGS = {
        'hi': {
            'what': 'क्या',
            'is': 'है',
            'lexical': 'लेक्सिकल',
            'analysis': 'विश्लेषण',
            'compiler': 'कंपाइलर',
            'design': 'डिजाइन',
            'token': 'टोकन',
            'give': 'दो',
            'me': 'मुझे',
            'pdf': 'पीडीएफ',
            'timetable': 'टाइमटेबल',
            'I': 'मैं',
            'don\'t': 'नहीं',
            'know': 'जानता',
            'answer': 'जवाब',
            'based': 'आधारित',
            'on': 'पर',
            'the': '',
            'provided': 'दिए गए',
            'context': 'संदर्भ',
            'only': 'केवल',
            'states': 'बताता है',
            'but': 'लेकिन',
            'does': 'करता है',
            'not': 'नहीं',
            'define': 'परिभाषित',
            'sorry': 'क्षमा करें',
            'error': 'त्रुटि',
            'occurred': 'हुई',
        },
        'gu': {
            'what': 'શું',
            'is': 'છે',
            'lexical': 'લેક્સિકલ',
            'analysis': 'વિશ્લેષણ',
            'compiler': 'કોમ્પાઇલર',
            'design': 'ડિઝાઇન',
            'token': 'ટોકન',
            'give': 'આપો',
            'me': 'મને',
            'pdf': 'પીડીએફ',
            'timetable': 'ટાઇમટેબલ',
            'i': 'હું',
            'dont': 'નથી',
            'know': 'જાણતો',
            'answer': 'જવાબ',
        },
        'mr': {
            'what': 'काय',
            'is': 'आहे',
            'lexical': 'लेक्सिकल',
            'analysis': 'विश्लेषण',
            'compiler': 'कंपाइलर',
            'design': 'डिझाइन',
            'token': 'टोकन',
            'give': 'द्या',
            'me': 'मला',
            'pdf': 'पीडीएफ',
            'timetable': 'टाइमटेबल',
        },
        'ta': {
            'what': 'என்ன',
            'is': 'உள்ளது',
            'lexical': 'லெக்சிகல்',
            'analysis': 'பகுப்பாய்வு',
            'compiler': 'மொழிமாற்றி',
            'design': 'வடிவமைப்பு',
            'token': 'டோக்கன்',
            'give': 'கொடு',
            'me': 'எனக்கு',
            'pdf': 'பிடிஎஃப்',
            'timetable': 'நேர அட்டவணை',
        },
        'te': {
            'what': 'ఏమిటి',
            'is': 'ఉంది',
            'lexical': 'లెక్సికల్',
            'analysis': 'విశ్లేషణ',
            'compiler': 'కంపైలర్',
            'design': 'రూపకల్పన',
            'token': 'టోకెన్',
            'give': 'ఇవ్వండి',
            'me': 'నాకు',
            'pdf': 'పిడిఎఫ్',
            'timetable': 'కాలపట్టిక',
        }
    }
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Simple word-by-word translation"""
        if source_lang == target_lang or source_lang not in self.WORD_MAPPINGS:
            return text
        
        mapping = self.WORD_MAPPINGS[source_lang]
        words = text.lower().split()
        translated_words = []
        
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)
            translated = mapping.get(clean_word, word)
            translated_words.append(translated)
        
        return ' '.join(translated_words)


class LanguageDetector:
    """Simple language detector"""
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language from text"""
        if not text:
            return 'en'
        
        # Check for Devanagari script (Hindi, Marathi)
        devanagari = any('\u0900' <= char <= '\u097F' for char in text)
        if devanagari:
            # Simple differentiation - check for Marathi specific patterns
            marathi_patterns = ['ला', 'नी', 'चा', 'ची', 'चे', 'म्हणजे']
            if any(pattern in text for pattern in marathi_patterns):
                return 'mr'
            return 'hi'
        
        # Check for Gujarati script
        if any('\u0A80' <= char <= '\u0AFF' for char in text):
            return 'gu'
        
        # Check for Tamil script
        if any('\u0B80' <= char <= '\u0BFF' for char in text):
            return 'ta'
        
        # Check for Telugu script
        if any('\u0C00' <= char <= '\u0C7F' for char in text):
            return 'te'
        
        # Default to English
        return 'en'
    
    @staticmethod
    def get_language_name(lang_code: str) -> str:
        names = {
            'en': 'English', 'hi': 'Hindi', 'gu': 'Gujarati',
            'mr': 'Marathi', 'ta': 'Tamil', 'te': 'Telugu'
        }
        return names.get(lang_code, 'English')


class TranslationWrapper:
    """Translation wrapper for the chatbot"""
    
    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.translator = SimpleTranslator()
        self.detector = LanguageDetector()
        self.current_language = 'en'
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """Process multilingual query"""
        # Detect language
        detected_lang = self.detector.detect_language(user_input)
        self.current_language = detected_lang
        
        # Translate to English if needed
        if detected_lang != 'en':
            english_query = self.translator.translate(user_input, detected_lang, 'en')
            print(f"📝 Translated to English: {english_query}")
        else:
            english_query = user_input
        
        # Check if it's a PDF request
        is_pdf_req, pdf_name = self.chatbot.is_pdf_request(english_query)
        
        if is_pdf_req:
            result = self.chatbot.retrieve_pdf(pdf_name)
            response_text = result.get('message', '')
            is_pdf_response = True
            sources = []
            context_chunks = 0
            pdf_result = result
        else:
            try:
                qa_result = self.chatbot.answer_question(english_query)
                response_text = qa_result.get('answer', '')
                is_pdf_response = False
                sources = qa_result.get('sources', [])
                context_chunks = qa_result.get('context_chunks', 0)
                pdf_result = None
            except Exception as e:
                response_text = f"Sorry, an error occurred: {str(e)}"
                is_pdf_response = False
                sources = []
                context_chunks = 0
                pdf_result = None
        
        # Translate response back to user's language
        if detected_lang != 'en' and response_text:
            translated_response = self.translator.translate(response_text, 'en', detected_lang)
        else:
            translated_response = response_text
        
        return {
            'original_query': user_input,
            'detected_language': detected_lang,
            'english_query': english_query,
            'response_translated': translated_response,
            'is_pdf_request': is_pdf_response,
            'sources': sources,
            'context_chunks': context_chunks,
            'pdf_result': pdf_result
        }


class PDFProcessor:
    """Enhanced PDF processor with OCR support for image-based PDFs"""
    
    @staticmethod
    def is_scanned_pdf(pdf_path: str, sample_pages: int = 2) -> bool:
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            total_text = " ".join([doc.page_content for doc in docs[:sample_pages]])
            if len(total_text.strip()) < 100:
                return True
            return False
        except:
            return True
    
    @staticmethod
    def extract_text_with_ocr(pdf_path: str, dpi: int = 300) -> List[Document]:
        print(f"🔍 Using OCR for scanned PDF: {os.path.basename(pdf_path)}")
        documents = []
        
        try:
            print(f"📄 Converting PDF pages to images...")
            images = None
            
            if POPPLER_PATH:
                try:
                    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=POPPLER_PATH)
                    print(f"   Using poppler from: {POPPLER_PATH}")
                except Exception as e:
                    print(f"   Error with poppler: {e}")
                    images = convert_from_path(pdf_path, dpi=dpi)
            else:
                images = convert_from_path(pdf_path, dpi=dpi)
            
            if not images:
                raise Exception("Could not convert PDF to images")
            
            print(f"   Processing {len(images)} pages...")
            
            for page_num, image in enumerate(images, start=1):
                print(f"  • Page {page_num}/{len(images)}")
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(image, config=custom_config)
                
                if text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": Path(pdf_path).name,
                            "page": page_num,
                            "ocr_processed": True
                        }
                    )
                    documents.append(doc)
                    print(f"     ✅ Extracted {len(text)} characters")
                else:
                    print(f"     ⚠️ No text found")
                    
        except Exception as e:
            print(f"❌ OCR Error: {e}")
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
        return documents
    
    @staticmethod
    def load_pdf_with_ocr_fallback(pdf_path: str) -> List[Document]:
        print(f"• Loading: {Path(pdf_path).name}")
        
        if PDFProcessor.is_scanned_pdf(pdf_path):
            print(f"  📸 Detected as image-based PDF, using OCR...")
            documents = PDFProcessor.extract_text_with_ocr(pdf_path)
        else:
            print(f"  📝 Detected as text-based PDF...")
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            print(f"     ✅ Loaded {len(documents)} pages")
            
        return documents


class AcademicAssistant:
    """Main Academic Assistant Class"""

    def __init__(self):
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.gemini_api_key:
            print("⚠️ Warning: GOOGLE_API_KEY not found in .env file")

        self.model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))

        self.study_materials_dir = project_root / "study_materials"
        self.vector_db_dir = project_root / "vector_db"
        self.pdf_export_dir = project_root / "exported_pdfs"

        self.vector_store = None
        self.qa_chain = None

        self.study_materials_dir.mkdir(exist_ok=True)
        self.vector_db_dir.mkdir(exist_ok=True)
        self.pdf_export_dir.mkdir(exist_ok=True)
        
        self.available_pdfs = {}
        
        # Rate limiting for Gemini API
        self.last_request_time = 0
        self.min_request_interval = 2  # 2 seconds between requests

    def load_pdfs(self) -> List[Any]:
        print("\n📚 Loading PDFs...")
        print("-" * 40)
        
        documents = []
        print(f"Study Material Path: {self.study_materials_dir}")
        
        pdf_files = [
            file for file in self.study_materials_dir.iterdir()
            if file.is_file() and file.suffix.lower() == ".pdf"
        ]
        
        if not pdf_files:
            raise FileNotFoundError(f"No PDFs found in {self.study_materials_dir}")
            
        print(f"\nFound {len(pdf_files)} PDF(s):")
        
        for pdf_path in pdf_files:
            self.available_pdfs[pdf_path.name.lower()] = pdf_path
            pdf_docs = PDFProcessor.load_pdf_with_ocr_fallback(str(pdf_path))
            
            for doc in pdf_docs:
                doc.metadata["source"] = pdf_path.name
                doc.metadata["pdf_path"] = str(pdf_path)
                
            documents.extend(pdf_docs)
            
        print(f"\n✅ Loaded {len(documents)} total pages")
        print(f"📄 Available PDFs: {', '.join(self.available_pdfs.keys())}")
        
        return documents

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        print("\n✂️ Splitting documents into chunks...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks")
        return chunks

    def create_embeddings(self, chunks: List[Any]):
        print("\n🔢 Creating embeddings...")
        
        # Use sentence-transformers directly to avoid deprecation warning
        from sentence_transformers import SentenceTransformer
        from langchain_community.embeddings import HuggingFaceEmbeddings
        
        embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        print("📦 Storing embeddings in ChromaDB...")
        
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(self.vector_db_dir),
            collection_name="academic_materials"
        )
        
        print("✅ Vector database created")

    def initialize_qa_chain(self):
        print("\n🤖 Initializing Gemini model...")
        
        if not self.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        try:
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.gemini_api_key,
                temperature=0.1,
                convert_system_message_to_human=True
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
                return_source_documents=True
            )
            
            print(f"✅ QA chain initialized")
        except Exception as e:
            print(f"❌ Failed: {e}")
            raise

    def is_pdf_request(self, question: str) -> tuple:
        question_lower = question.lower()
        
        patterns = [
            r'(?:provide|get|give|show|send|share|download)\s+(?:me\s+)?(?:the\s+)?([\w\s]+?)\s+pdf',
            r'(?:where\s+is\s+)?([\w\s]+?)\s+pdf',
            r'pdf\s+(?:named\s+)?([\w\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question_lower)
            if match:
                requested_name = match.group(1).strip()
                for pdf_name in self.available_pdfs.keys():
                    if requested_name in pdf_name or pdf_name.startswith(requested_name):
                        return True, pdf_name
        return False, None

    def retrieve_pdf(self, pdf_name: str) -> Dict[str, Any]:
        matching_pdfs = []
        for available_name, pdf_path in self.available_pdfs.items():
            if pdf_name.lower() in available_name or available_name.startswith(pdf_name.lower()):
                matching_pdfs.append((available_name, pdf_path))
        
        if not matching_pdfs:
            return {
                "success": False,
                "message": f"PDF '{pdf_name}' not found. Available: {', '.join(self.available_pdfs.keys())}"
            }
        
        pdf_name_match, pdf_path = matching_pdfs[0]
        export_path = self.pdf_export_dir / pdf_path.name
        shutil.copy2(pdf_path, export_path)
        
        return {
            "success": True,
            "message": f"Found PDF: {pdf_name_match}",
            "pdf_path": str(export_path),
            "pdf_name": pdf_name_match,
            "file_size": f"{pdf_path.stat().st_size / 1024:.2f} KB"
        }

    def answer_question(self, question: str) -> Dict[str, Any]:
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        is_pdf_req, pdf_name = self.is_pdf_request(question)
        
        if is_pdf_req:
            result = self.retrieve_pdf(pdf_name)
            return {
                "is_pdf_request": True,
                "answer": result["message"],
                "sources": [],
                "context_chunks": 0,
                "pdf_result": result
            }
        
        if not self.qa_chain:
            raise ValueError("QA Chain not initialized")
        
        try:
            result = self.qa_chain.invoke({"query": question})
            self.last_request_time = time.time()
            
            source_pdfs = set()
            for doc in result["source_documents"]:
                if "source" in doc.metadata:
                    source_pdfs.add(doc.metadata["source"])
            
            return {
                "is_pdf_request": False,
                "answer": result["result"],
                "sources": list(source_pdfs),
                "context_chunks": len(result["source_documents"]),
                "pdf_result": None
            }
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                return {
                    "is_pdf_request": False,
                    "answer": "⚠️ API quota exceeded. Please try again later or upgrade your Gemini plan.",
                    "sources": [],
                    "context_chunks": 0,
                    "pdf_result": None
                }
            return {
                "is_pdf_request": False,
                "answer": f"Error: {error_msg}",
                "sources": [],
                "context_chunks": 0,
                "pdf_result": None
            }

    def setup(self):
        print("=" * 60)
        print("🤖 ACADEMIC ASSISTANT SETUP")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%A, %B %d, %Y')}")
        
        print("\n📚 PROCESSING DOCUMENTS")
        
        documents = self.load_pdfs()
        chunks = self.chunk_documents(documents)
        self.create_embeddings(chunks)
        self.initialize_qa_chain()
        
        print("\n✅ SETUP COMPLETE!")
        print("=" * 60)

    def interactive_mode(self):
        """
        Start chatbot interaction with direct Google Translate (No external module)
        """
        # Import Google Translate directly here
        try:
            from googletrans import Translator
            translator = Translator()
            google_translate_available = True
            print("✅ Google Translate ready")
        except ImportError:
            google_translate_available = False
            print("⚠️ Install: pip install googletrans==3.1.0a0")
        
        print("\n💬 MULTILINGUAL CHATBOT")
        print("Supported: English, Hindi, Gujarati, Marathi, Tamil, Telugu")
        print("Type 'exit' to quit, 'help' for examples")
        print("-" * 50)
        
        while True:
            try:
                question = input("\n📝 You: ").strip()
                
                if question.lower() in ["exit", "quit", "bye"]:
                    print("\n👋 Goodbye!")
                    break
                
                if question.lower() == "help":
                    print("\n📖 EXAMPLES:")
                    print("  English: What is a token?")
                    print("  Hindi: टोकन क्या है?")
                    print("  Marathi: टोकन म्हणजे काय?")
                    continue
                
                if not question:
                    continue
                
                # ========== STEP 1: Detect Language ==========
                detected_lang = 'en'
                for char in question[:100]:
                    if '\u0900' <= char <= '\u097F':
                        detected_lang = 'hi'  # Hindi/Marathi default
                        # Check for Marathi specific words
                        if any(word in question for word in ['म्हणजे', 'आहे', 'काय']):
                            detected_lang = 'mr'
                        break
                    elif '\u0A80' <= char <= '\u0AFF':
                        detected_lang = 'gu'
                        break
                    elif '\u0B80' <= char <= '\u0BFF':
                        detected_lang = 'ta'
                        break
                    elif '\u0C00' <= char <= '\u0C7F':
                        detected_lang = 'te'
                        break
                
                lang_names = {'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi', 'gu': 'Gujarati', 'ta': 'Tamil', 'te': 'Telugu'}
                print(f"🌐 Detected: {lang_names.get(detected_lang, 'English')}")
                
                # ========== STEP 2: Translate to English ==========
                if detected_lang != 'en' and google_translate_available:
                    try:
                        translated = translator.translate(question, src=detected_lang, dest='en')
                        english_query = translated.text
                        print(f"📝 English: {english_query}")
                    except Exception as e:
                        print(f"⚠️ Translation error: {e}")
                        english_query = question
                else:
                    english_query = question
                
                # ========== STEP 3: Get Answer from Chatbot ==========
                # Check if PDF request
                is_pdf_req, pdf_name = self.is_pdf_request(english_query)
                
                if is_pdf_req:
                    result = self.retrieve_pdf(pdf_name)
                    response_text = result.get('message', '')
                    sources = []
                else:
                    qa_result = self.answer_question(english_query)
                    response_text = qa_result.get('answer', '')
                    sources = qa_result.get('sources', [])
                
                # ========== STEP 4: Translate Response Back ==========
                if detected_lang != 'en' and google_translate_available and response_text:
                    try:
                        back = translator.translate(response_text, src='en', dest=detected_lang)
                        final_response = back.text
                    except:
                        final_response = response_text
                else:
                    final_response = response_text
                
                # ========== STEP 5: Display Response ==========
                print("\n" + "=" * 50)
                print("💡 ANSWER")
                print("=" * 50)
                print(final_response)
                
                if sources:
                    print(f"\n📚 Sources: {', '.join(sources)}")
                print("=" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    try:
        print("\n🚀 STARTING ACADEMIC ASSISTANT")
        
        assistant = AcademicAssistant()
        assistant.setup()
        assistant.interactive_mode()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    sys.exit(main())