import spacy
from bs4 import BeautifulSoup
import re

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ")
    # remove extra whitespaces
    return re.sub(r'\s+', ' ', text).strip()

def normalize_text(text: str) -> str:
    cleaned_text = clean_html(text)
    doc = nlp(cleaned_text)
    
    # Tokenize, lowercase, and remove stop words & punctuation
    tokens = [
        token.text.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and token.is_alpha
    ]
    return " ".join(tokens)
