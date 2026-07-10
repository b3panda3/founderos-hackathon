"""Text chunking utility for RAG pipeline."""

from typing import Optional


class TextChunker:
    """Splits text into chunks for vector storage."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def split_text(self, text: str, metadata: Optional[dict] = None) -> list[dict]:
        """
        Split text into overlapping chunks, preserving paragraph boundaries.
        Returns list of {"text": ..., "metadata": ...} dicts.
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}
        paragraphs = self._split_paragraphs(text)
        chunks = []
        current_chunk = ""
        chunk_index = 0

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + para
            else:
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "metadata": {
                            **metadata,
                            "chunk_index": chunk_index,
                            "char_count": len(current_chunk),
                        },
                    })
                    chunk_index += 1
                # Keep overlap from previous chunk
                if current_chunk and self.chunk_overlap > 0:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + "\n\n" + para
                else:
                    current_chunk = para

        # Don't forget the last chunk
        if len(current_chunk) >= self.min_chunk_size:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_index,
                    "char_count": len(current_chunk),
                },
            })

        return chunks

    def _split_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs, handling various separators."""
        import re
        # Split on double newlines, or single newlines followed by capitalization
        paragraphs = re.split(r'\n\s*\n', text)
        # Further split very long paragraphs
        result = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(para) > self.chunk_size * 1.5:
                # Split long paragraphs at sentence boundaries
                sentences = re.split(r'(?<=[.!?])\s+', para)
                current = ""
                for sent in sentences:
                    if len(current) + len(sent) + 1 <= self.chunk_size:
                        current += (" " if current else "") + sent
                    else:
                        if current:
                            result.append(current)
                        current = sent
                if current:
                    result.append(current)
            else:
                result.append(para)
        return result