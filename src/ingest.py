from pathlib import Path

from pypdf import PdfReader

from config import CHUNK_OVERLAP, CHUNK_SIZE, DOCS_DIR
from db import get_collection


def chunk_text(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def extract_pdf_text(file_path):
    reader = PdfReader(str(file_path))
    pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages.append(page_text)

    return "\n\n".join(pages).strip()


def load_file_text(file_path):
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_text(path)

    return path.read_text(encoding="utf-8", errors="ignore")


def ingest_text(source_name, text):
    text = (text or "").strip()

    if not text:
        return 0

    collection = get_collection()
    chunks = chunk_text(text)

    existing = collection.get(where={"source": source_name})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    ids = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        ids.append(f"{source_name}-{index}")
        documents.append(chunk)
        metadatas.append({"source": source_name, "chunk": index})

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    return len(documents)


def ingest_file(file_path):
    path = Path(file_path)
    text = load_file_text(path)
    return ingest_text(path.stem, text)


def ingest_docs_folder():
    total = 0

    for file_path in sorted(DOCS_DIR.glob("*.txt")):
        print(f"Processing: {file_path.name}")
        count = ingest_file(file_path)
        print(f"Stored {count} chunks")
        total += count

    return total


if __name__ == "__main__":
    stored = ingest_docs_folder()
    collection = get_collection()
    print(f"\nIngested {stored} chunks from {DOCS_DIR}")
    print("Total chunks in database:", collection.count())
