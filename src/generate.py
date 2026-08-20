from ollama import chat

from config import DEFAULT_MODEL
from retrieve import format_context, retrieve

SYSTEM_PROMPT = """You are a helpful RAG assistant.
Answer the user's question using only the provided context.
If the context does not contain the answer, say you don't know.
Be concise. Quote the source name when it helps."""


def build_messages(question, hits):
    context = format_context(hits)
    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer based only on the context above."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def stream_answer(question, hits, model=DEFAULT_MODEL):
    for chunk in chat(
        model=model,
        messages=build_messages(question, hits),
        stream=True,
    ):
        token = chunk.message.content
        if token:
            yield token


def answer_question(question, n_results=3, model=DEFAULT_MODEL):
    hits = retrieve(question, n_results=n_results)

    if not hits:
        return "Knowledge base is empty. Upload a PDF or paste text first.", hits

    pieces = []
    for token in stream_answer(question, hits, model=model):
        pieces.append(token)

    return "".join(pieces), hits


if __name__ == "__main__":
    while True:
        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        reply, hits = answer_question(question)

        print("\n--- Retrieved Context ---")
        if hits:
            for i, hit in enumerate(hits, start=1):
                print(f"\nChunk {i} ({hit['metadata'].get('source', 'unknown')})")
                print(f"Distance: {hit['distance']:.4f}")
                print(hit["document"])
        else:
            print("No chunks found.")

        print("\n--- Answer ---")
        print(reply)
