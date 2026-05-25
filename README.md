# Campus Mind AI

> Your Intelligent Multilingual Academic Assistant

---

## Overview

Campus Mind AI is an AI-powered multilingual university assistant designed to help students interact with academic resources in a smarter and more accessible way.

The system combines:

* Multilingual AI support
* RAG-based PDF Question Answering
* OCR for scanned/image PDFs
* Timetable assistance
* Intelligent PDF retrieval
* Gemini AI integration

Users can ask questions in multiple Indian languages and receive responses in the same language while the backend internally processes everything in English for efficient retrieval and accuracy.

---

# Features

## Multilingual Support

Supports all major Indian languages including:

* English
* Hindi
* Gujarati
* Marathi
* Tamil
* Telugu
* Kannada
* Malayalam
* Bengali
* Punjabi
* Odia
* Assamese
* Urdu
* Sanskrit
  and more.

Features:

* Automatic language detection
* Query translation
* Response translation
* Seamless multilingual interaction

---

## RAG-Based PDF Question Answering

The chatbot can:

* Extract knowledge from PDFs
* Retrieve relevant context
* Generate intelligent answers
* Explain academic topics
* Summarize concepts

Powered using:

* LangChain
* ChromaDB
* HuggingFace Embeddings
* Gemini AI

---

## OCR Support

Supports scanned and image-based PDFs using OCR.

Capabilities:

* Detect scanned PDFs automatically
* Extract text using Tesseract OCR
* Process image-based academic documents

---

## Intelligent PDF Retrieval

Students can directly request PDFs.

Examples:

* "Provide me the CD PDF"
* "मुझे टाइमटेबल पीडीएफ दो"
* "Show timetable document"

The assistant retrieves and exports the requested file automatically.

---

## Timetable Assistance

Provides timetable-related assistance such as:

* Today's schedule
* Subject timings
* Document retrieval for timetable PDFs

---

# Architecture

```text
User Query
    ↓
Language Detection
    ↓
Translation to English
    ↓
RAG Pipeline / PDF Retrieval
    ↓
Gemini AI Response
    ↓
Translation Back to User Language
    ↓
Final Response
```

---

# Tech Stack

## Backend

* Python
* LangChain
* ChromaDB
* HuggingFace Embeddings
* Google Gemini AI

## OCR

* Tesseract OCR
* pdf2image
* Poppler

## Translation

* Lingva Translate API
* Language Detection

## AI & NLP

* Retrieval-Augmented Generation (RAG)
* Semantic Search
* Vector Embeddings

---

# Project Structure

```text
CampusMindAI/
│
├── backend/
│   ├── main.py
│   ├── translation/
│   ├── vector_db/
│   └── exported_pdfs/
│
├── study_materials/
├── poppler/
├── requirements.txt
├── README.md
└── .env
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/campus-mind-ai.git
cd campus-mind-ai
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

---

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

## 4. Setup Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-1.5-flash
```

---

# Run Project

```bash
python main.py
```

---

# Example Queries

## English

* What is lexical analysis?

## Hindi

* लेक्सिकल एनालिसिस क्या है?

## Gujarati

* લેક્સિકલ એનાલિસિસ શું છે?

## Marathi

* लेक्सिकल एनालिसिस म्हणजे काय?

## Telugu

* లెక్సికల్ అనాలిసిస్ అంటే ఏమిటి?

## Tamil

* லெக்சிக்கல் அனாலிசிஸ் என்றால் என்ன?

## Sanskrit

* लेक्सिकल् एनालिसिस् किम् अस्ति?

---

# Future Improvements

* Voice Input Support
* Text-to-Speech Responses
* Modern Frontend Dashboard
* Cloud Deployment
* Mobile Responsive UI
* Personalized Student Profiles
* Analytics Dashboard

---

# Planned Frontend Features

* Modern AI chat interface
* Multilingual UI
* Voice assistant
* Embedded PDF viewer
* Smart sidebar
* Timetable dashboard
* Chat history
* Dark mode support

---

# AI Capabilities

Campus Mind AI combines:

* Natural Language Processing
* Semantic Search
* Retrieval-Augmented Generation
* OCR-based document understanding
* Multilingual translation pipeline

to create a complete intelligent academic ecosystem.

---

# Contributing

Contributions are welcome.
Feel free to fork the repository and submit pull requests.

---

# License

This project is licensed under the MIT License.

---

# Developed By

Vaidehi Koranne

---

# Support

If you like this project, consider giving it a star on GitHub.
