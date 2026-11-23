def semantic_chunks(text, max_chars=12000, overlap=500):
    """Bound request size while keeping paragraph boundaries where possible."""
    text = (text or "").strip()
    if not text:
        return []
    paragraphs = text.split("\n")
    chunks, current = [], ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        candidate = (current + "\n\n" + para).strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(para) > max_chars:
            for i in range(0, len(para), max_chars-overlap):
                chunks.append(para[i:i+max_chars])
            current = ""
        else:
            current = para
    if current:
        chunks.append(current)
    return chunks
