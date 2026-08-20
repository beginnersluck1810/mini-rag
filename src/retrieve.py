from config import N_RESULTS
from db import get_collection


def retrieve(question, n_results=N_RESULTS):
    collection = get_collection()

    if collection.count() == 0:
        return []

    n_results = min(n_results, collection.count())

    results = collection.query(
        query_texts=[question],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]
    ids = results["ids"][0]

    for index, document in enumerate(documents):
        hits.append(
            {
                "id": ids[index],
                "document": document,
                "distance": distances[index],
                "metadata": metadatas[index] or {},
            }
        )

    return hits


def format_context(hits):
    parts = []

    for i, hit in enumerate(hits, start=1):
        source = hit["metadata"].get("source", "unknown")
        parts.append(f"[Source {i}: {source}]\n{hit['document']}")

    return "\n\n".join(parts)


if __name__ == "__main__":
    while True:
        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        hits = retrieve(question)

        print("\n--- Retrieved Context ---")

        if not hits:
            print("Knowledge base is empty. Run ingest.py first.")
            continue

        for i, hit in enumerate(hits, start=1):
            print(f"\nChunk {i}")
            print(f"Source: {hit['metadata'].get('source', 'unknown')}")
            print(f"Distance: {hit['distance']:.4f}")
            print(hit["document"])
