from app.utils.text_chunking import chunk_text


def test_empty_and_whitespace_text_yield_no_chunks() -> None:
    assert chunk_text("") == []
    assert chunk_text("\n\n") == []


def test_short_text_is_one_one_indexed_chunk() -> None:
    chunks = chunk_text("alpha\nbeta\ngamma")
    assert len(chunks) == 1
    assert chunks[0].content == "alpha\nbeta\ngamma"
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 3


def test_chunks_respect_max_lines_and_overlap() -> None:
    text = "\n".join(f"line-{index}" for index in range(1, 11))
    chunks = chunk_text(text, max_lines=4, overlap=2)

    assert [chunk.start_line for chunk in chunks] == [1, 3, 5, 7]
    assert chunks[0].end_line == 4
    assert chunks[0].content.startswith("line-1")
    assert chunks[-1].end_line == 10
    assert "line-10" in chunks[-1].content
