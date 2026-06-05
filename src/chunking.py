from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        # Split on sentence boundaries: ". ", "! ", "? ", or ".\n"
        # Use re.split with a capturing group to keep the delimiters
        parts = re.split(r'(?<=[.!?])\s+|(?<=\.)\n', text)

        # Clean up empty parts
        sentences = [s.strip() for s in parts if s.strip()]

        if not sentences:
            return [text.strip()]

        # Group sentences into chunks
        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk = " ".join(group).strip()
            if chunk:
                chunks.append(chunk)

        return chunks if chunks else [text.strip()]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        # Start the recursive splitting with all separators available
        return self._split(text, list(self.separators))

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Base case: text already fits in one chunk
        if len(current_text) <= self.chunk_size:
            return [current_text]

        # No more separators — hard-cut at chunk_size
        if not remaining_separators:
            chunks: list[str] = []
            for start in range(0, len(current_text), self.chunk_size):
                piece = current_text[start : start + self.chunk_size]
                if piece:
                    chunks.append(piece)
            return chunks

        # Try the first separator
        sep = remaining_separators[0]
        next_separators = remaining_separators[1:]

        if sep == "":
            # Character-level fallback: hard-cut
            chunks = []
            for start in range(0, len(current_text), self.chunk_size):
                piece = current_text[start : start + self.chunk_size]
                if piece:
                    chunks.append(piece)
            return chunks

        if sep not in current_text:
            # Separator not present — try the next one
            return self._split(current_text, next_separators)

        # Split by separator
        parts = current_text.split(sep)

        # Merge parts back into chunks that respect chunk_size
        result: list[str] = []
        current_chunk = ""

        for part in parts:
            if not part:
                continue
            # Check if adding this part (with separator) would exceed limit
            candidate = current_chunk + sep + part if current_chunk else part
            if len(candidate) <= self.chunk_size:
                current_chunk = candidate
            else:
                # Save the current accumulated chunk first
                if current_chunk:
                    result.append(current_chunk)
                # If the part itself is too large, recurse with remaining separators
                if len(part) > self.chunk_size:
                    sub_chunks = self._split(part, next_separators)
                    result.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part

        if current_chunk:
            result.append(current_chunk)

        return result if result else [current_text]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = _dot(vec_a, vec_b)
    mag_a = math.sqrt(_dot(vec_a, vec_a))
    mag_b = math.sqrt(_dot(vec_b, vec_b))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot_product / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        result: dict = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count > 0 else 0.0
            result[name] = {
                "count": count,
                "avg_length": round(avg_length, 2),
                "chunks": chunks,
            }

        return result
