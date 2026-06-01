"""
Chunking Service — splits parsed text into semantic chunks with overlap.
Uses sentence-aware splitting to never break mid-sentence.
"""

import re
from app.config import get_settings

settings = get_settings()


def chunk_pages(pages: list[dict], chunk_size: int = None, chunk_overlap: int = None) -> list[dict]:
    """
    Split parsed pages into overlapping chunks.
    Each chunk carries its source page number for citations.

    Args:
        pages: Output of document_parser.parse_document()
        chunk_size: Max characters per chunk (default from settings)
        chunk_overlap: Overlap characters between chunks (default from settings)

    Returns:
        List of chunk dicts: [{"text": "...", "page": 1, "chunk_index": 0}, ...]
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    all_chunks = []
    chunk_index = 0

    for page_data in pages:
        page_num = page_data["page"]
        text = page_data["text"]

        # Split into sentences first (sentence-aware chunking)
        sentences = _split_into_sentences(text)

        current_chunk = ""
        for sentence in sentences:
            # If adding this sentence would exceed chunk_size, save current chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                all_chunks.append({
                    "text": current_chunk.strip(),
                    "page": page_num,
                    "chunk_index": chunk_index,
                    "char_count": len(current_chunk.strip()),
                })
                chunk_index += 1

                # Overlap: keep the tail of the current chunk
                if chunk_overlap > 0:
                    current_chunk = current_chunk[-chunk_overlap:] + " " + sentence
                else:
                    current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # Don't forget the last chunk from this page
        if current_chunk.strip():
            all_chunks.append({
                "text": current_chunk.strip(),
                "page": page_num,
                "chunk_index": chunk_index,
                "char_count": len(current_chunk.strip()),
            })
            chunk_index += 1

    return all_chunks


def _split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences using regex.
    Handles: periods, question marks, exclamation marks.
    Preserves abbreviations like "Dr.", "U.S.", etc.
    """
    # Split on sentence-ending punctuation followed by space + uppercase
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    # Filter out empty strings
    return [s.strip() for s in sentences if s.strip()]
