from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    content: str
    start_line: int
    end_line: int


def chunk_text(text: str, max_lines: int = 80, overlap: int = 12) -> list[TextChunk]:
    lines = text.splitlines()
    if not lines:
        return []

    chunks: list[TextChunk] = []
    start = 0
    while start < len(lines):
        end = min(start + max_lines, len(lines))
        content = "\n".join(lines[start:end]).strip()
        if content:
            chunks.append(TextChunk(content=content, start_line=start + 1, end_line=end))
        if end == len(lines):
            break
        start = max(0, end - overlap)
    return chunks
