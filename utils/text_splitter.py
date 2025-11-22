# utils/text_splitter.py
import re
from typing import List

SENTENCE_END_RE = re.compile(r'([.!?।\n])')  # includes common sentence enders (Urdu/Hindi danda optional)

def split_text_to_chunks(text: str, chunk_size: int = 4000) -> List[str]:
    """
    Split `text` into chunks not exceeding `chunk_size` characters.
    Tries to split on sentence boundaries; if a sentence is longer than chunk_size,
    it does a hard split.
    """
    if not text:
        return []

    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= chunk_size:
        return [text]

    parts = SENTENCE_END_RE.split(text)
    sentences = []
    for i in range(0, len(parts), 2):
        chunk = parts[i].strip()
        if i + 1 < len(parts):
            chunk += parts[i + 1]  # include the punctuation
        if chunk:
            sentences.append(chunk.strip())

    chunks = []
    current = ""
    for s in sentences:
        if not s:
            continue
        if len(current) + len(s) + 1 <= chunk_size:
            current = (current + " " + s).strip() if current else s
        else:
            if current:
                chunks.append(current)
            if len(s) > chunk_size:
                # hard split long sentence
                for i in range(0, len(s), chunk_size):
                    chunks.append(s[i:i+chunk_size])
                current = ""
            else:
                current = s
    if current:
        chunks.append(current)
    return chunks
