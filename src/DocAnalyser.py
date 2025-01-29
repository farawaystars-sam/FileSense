from transformers import pipeline  # pipeline to import required BART model
import nltk  # Natural Language Toolkit for text processing
from nltk.corpus import stopwords  # Stopwords for NLP tasks
from nltk.tokenize import word_tokenize  # Tokenization of text
import re  # Regular expressions for text processing
import fitz  # PyMuPDF library for extracting text from PDFs


# Global declarations
# Zero-shot Classification Model for Document Classification
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Download NLTK data for text processing
nltk.download('punkt')
nltk.download('stopwords')


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using PyMuPDF.
    
    Parameters:
    - pdf_path (str): Path to the PDF file.
    
    Returns:
    - str: Extracted text content.
    """
    text = ""
    try:
        with fitz.open(pdf_path) as pdf:
            for page_num in range(len(pdf)):
                text += pdf[page_num].get_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text


def classify_document(file_path):
    """
    Classify a document file using Zero-shot classification.
    
    Parameters:
    - file_path (str): Path to the document file.
    
    Returns:
    - str: Predicted label for the document.
    """
    try:
        # Extract text based on file type
        if file_path.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        
        # Define candidate labels (you can modify these as needed)
        candidate_labels = ["technology", "finance", "legal", "contracts", "vegetations", "communication"]

        
        # Clean and classify the text
        clean_text = re.sub(r'\s+', ' ', text.strip())
        classification = classifier(clean_text, candidate_labels, multi_label=True)
        
        # Extract top category with high score
        label = max(classification['labels'], key=lambda label: classification['scores'][classification['labels'].index(label)])
        
        return label
    except Exception as e:
        print(f"Error classifying document {file_path}: {e}")
        return "unclassified"