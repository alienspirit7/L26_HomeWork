"""Book API search utilities - OpenLibrary and Google Books."""

from __future__ import annotations
from typing import Optional
import requests
from dataclasses import dataclass


@dataclass
class BookInfo:
    """Book information from API."""
    title: str
    author: str
    isbn: str = ""
    publisher: str = ""
    cover_url: str = ""
    found: bool = True


def search_openlibrary(title: str, author: str = None) -> Optional[BookInfo]:
    """Search OpenLibrary API for book."""
    try:
        query = f"title:{title}"
        if author:
            query += f"+author:{author}"
        
        url = f"https://openlibrary.org/search.json?q={query}&limit=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        if not data.get("docs"):
            return None
        
        book = data["docs"][0]
        return BookInfo(
            title=book.get("title", ""),
            author=", ".join(book.get("author_name", [])),
            isbn=book.get("isbn", [""])[0] if book.get("isbn") else "",
            publisher=", ".join(book.get("publisher", [])[:1]),
            found=True,
        )
    except Exception as e:
        print(f"OpenLibrary search error: {e}")
        return None


def search_google_books(title: str, author: str = None, api_key: str = None) -> Optional[BookInfo]:
    """Search Google Books API for book."""
    try:
        query = title
        if author:
            query += f"+inauthor:{author}"
        
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
        if api_key:
            url += f"&key={api_key}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        if not data.get("items"):
            return None
        
        book = data["items"][0]["volumeInfo"]
        isbn = ""
        for ident in book.get("industryIdentifiers", []):
            if ident.get("type") in ["ISBN_13", "ISBN_10"]:
                isbn = ident.get("identifier", "")
                break
        
        return BookInfo(
            title=book.get("title", ""),
            author=", ".join(book.get("authors", [])),
            isbn=isbn,
            publisher=book.get("publisher", ""),
            cover_url=book.get("imageLinks", {}).get("thumbnail", ""),
            found=True,
        )
    except Exception as e:
        print(f"Google Books search error: {e}")
        return None
