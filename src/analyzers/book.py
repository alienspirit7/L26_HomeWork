"""Book verification analyzer using OCR and book APIs."""

from __future__ import annotations
from typing import List, Tuple
import re
import numpy as np
import pytesseract
from PIL import Image
from src.models import BookVerificationResult
from src.analyzers.book_api import search_openlibrary, search_google_books


class BookAnalyzer:
    """Analyzes book covers for authenticity verification."""
    
    SPELLING_PATTERNS = [
        r'\b[A-Z][a-z]*[A-Z]+[a-z]*\b',
        r'\b\w*[^a-zA-Z\s\'-]\w*\b',
    ]
    
    def __init__(self, google_books_api_key: str = None):
        self.google_books_api_key = google_books_api_key
    
    def _extract_text(self, image: np.ndarray) -> str:
        """Extract text from image using OCR."""
        try:
            return pytesseract.image_to_string(Image.fromarray(image), config='--psm 6').strip()
        except Exception as e:
            print(f"OCR error: {e}")
            return ""
    
    def _parse_book_details(self, text: str) -> Tuple[str, str]:
        """Parse title and author from OCR text."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        title, author = "", ""
        if lines:
            title = lines[0]
            for line in lines[1:]:
                if any(kw in line.lower() for kw in ['by ', 'author']):
                    author = line.replace('by ', '').replace('By ', '').strip()
                    break
                if len(line) > 3 and not author:
                    author = line
        return title, author
    
    def _check_spelling(self, text: str) -> List[str]:
        """Check for AI-generated text artifacts."""
        errors = []
        for pattern in self.SPELLING_PATTERNS:
            errors.extend(re.findall(pattern, text))
        
        for word in text.split():
            if any(ord(c) > 127 for c in word):
                if not self._is_valid_unicode(word):
                    errors.append(word)
        
        repeated = re.findall(r'(\w)\1{3,}', text)
        errors.extend([f"Repeated: {r}" for r in repeated])
        return list(set(errors))
    
    def _is_valid_unicode(self, word: str) -> bool:
        """Check if unicode characters are valid."""
        for c in word:
            code = ord(c)
            if code > 127 and not (0x00C0 <= code <= 0x017F):
                return False
        return True
    
    def analyze(self, image: np.ndarray) -> BookVerificationResult:
        """Perform book verification analysis.
        
        Score interpretation:
        - Low score (0.0-0.3) = likely authentic (real readable text)
        - High score (0.7-1.0) = likely fake (gibberish/AI-generated text)
        """
        findings, score = [], 0.3  # Start assuming authentic
        
        ocr_text = self._extract_text(image)
        if not ocr_text:
            # No text detected - slightly suspicious but inconclusive
            return BookVerificationResult(score=0.5, findings=["No text detected"], book_found=False, ocr_text="")
        
        title, author = self._parse_book_details(ocr_text)
        findings.append(f"Detected title: {title}")
        if author:
            findings.append(f"Detected author: {author}")
        
        spelling_errors = self._check_spelling(ocr_text)
        if spelling_errors:
            findings.append(f"Spelling issues: {spelling_errors}")
            # AI-generated gibberish is THE STRONGEST fake indicator
            # Base penalty + additional for each error found
            error_count = len(spelling_errors)
            score += 0.35 + min(0.25, error_count * 0.05)  # Max +0.6 for many errors
        
        book_info = search_openlibrary(title, author)
        if not book_info:
            book_info = search_google_books(title, author, self.google_books_api_key)
        
        book_found = book_info is not None
        if book_found:
            # Real book found - strong authenticity signal
            findings.append(f"Book found: '{book_info.title}' by {book_info.author}")
            score -= 0.15
        else:
            # Book not found - could be rare book or fake
            findings.append("Book not found in online databases")
            score += 0.1
        
        return BookVerificationResult(
            score=max(0.0, min(1.0, score)),
            findings=findings,
            book_found=book_found,
            book_title=book_info.title if book_info else title,
            book_author=book_info.author if book_info else author,
            spelling_errors=spelling_errors,
            ocr_text=ocr_text,
        )
