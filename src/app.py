from pathlib import Path

import gradio as gr

from config import AVAILABLE_MODELS, DEFAULT_MODEL, N_RESULTS
from db import get_collection, reset_collection
from generate import stream_answer
from ingest import ingest_file, ingest_text
from retrieve import retrieve


def collection_status():
    count = get_collection().count()
    return f"**Knowledge base:** {count} chunk{'s' if count != 1 else ''} stored"


def add_to_knowledge_base(files, pasted_text):
    added = []

    if files:
        if not isinstance(files, list):
            files = [files]

        for file_path in files:
            if not file_path:
                continue
            path = Path(file_path)
            try:
                count = ingest_file(path)
                if count == 0:
                    added.append(f"`{path.name}` → no extractable text")
                else:
                    added.append(f"`{path.name}` → {count} chunks")
            except Exception as error:
                added.append(f"`{path.name}` failed: {error}")

    pasted_text = (pasted_text or "").strip()
    if pasted_text:
        count = ingest_text("pasted-text", pasted_text)
        added.append(f"`pasted-text` → {count} chunks")

    if not added:
        return "Add a PDF, a `.txt` file, or paste some text first.", collection_status()

    return "Added:\n\n" + "\n\n".join(f"- {item}" for item in added), collection_status()


def clear_knowledge_base():
    reset_collection()
    return "Knowledge base cleared.", collection_status()


def format_sources(hits):
    if not hits:
        return "_No sources retrieved._"

    lines = []
    for i, hit in enumerate(hits, start=1):
        source = hit["metadata"].get("source", "unknown")
        preview = " ".join(hit["document"].split())
        if len(preview) > 280:
            preview = preview[:277] + "..."
        lines.append(
            f"**{i}. {source}** · distance `{hit['distance']:.4f}`\n\n{preview}"
        )

    return "\n\n---\n\n".join(lines)


def ask(message, history, model, n_results):
    history = list(history or [])
    question = (message or "").strip()

    if not question:
        yield history, "_Ask a question first._"
        return

    history.append({"role": "user", "content": question})
    hits = retrieve(question, n_results=int(n_results))
    sources = format_sources(hits)

    if not hits:
        history.append(
            {
                "role": "assistant",
                "content": "Knowledge base is empty. Upload a PDF or paste text, then try again.",
            }
        )
        yield history, sources
        return

    history.append({"role": "assistant", "content": ""})
    yield history, sources

    try:
        for token in stream_answer(question, hits, model=model):
            history[-1]["content"] += token
            yield history, sources
    except Exception as error:
        history[-1]["content"] = (
            "Could not reach Ollama. Make sure it is running "
            f"(`ollama serve`) and the model `{model}` is pulled.\n\n`{error}`"
        )
        yield history, sources


with gr.Blocks(title="Mini RAG") as demo:
    gr.Markdown(
        """
# Mini RAG
Upload a PDF, paste text, then ask questions. Retrieval uses Chroma; answers come from a local Ollama model.
"""
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1. Feed data")
            files = gr.File(
                label="PDF or text files",
                file_count="multiple",
                file_types=[".pdf", ".txt"],
                type="filepath",
            )
            pasted = gr.Textbox(
                label="Or paste text",
                lines=10,
                placeholder="Paste notes, articles, or any text here...",
            )
            ingest_btn = gr.Button("Add to knowledge base", variant="primary")
            clear_btn = gr.Button("Clear knowledge base")
            ingest_log = gr.Markdown()
            status = gr.Markdown(value=collection_status())

        with gr.Column(scale=2):
            gr.Markdown("### 2. Ask")
            chatbot = gr.Chatbot(label="Chat", height=420, feedback_options=None)
            question = gr.Textbox(
                label="Question",
                placeholder="Ask anything about the documents you added...",
                submit_btn=True,
            )
            with gr.Row():
                model = gr.Dropdown(
                    choices=AVAILABLE_MODELS,
                    value=DEFAULT_MODEL,
                    label="Ollama model",
                )
                n_results = gr.Slider(
                    minimum=1,
                    maximum=8,
                    value=N_RESULTS,
                    step=1,
                    label="Chunks to retrieve",
                )
            gr.Markdown("### Retrieved sources")
            sources = gr.Markdown()

    ingest_btn.click(
        fn=add_to_knowledge_base,
        inputs=[files, pasted],
        outputs=[ingest_log, status],
    )
    clear_btn.click(
        fn=clear_knowledge_base,
        outputs=[ingest_log, status],
    )
    question.submit(
        fn=ask,
        inputs=[question, chatbot, model, n_results],
        outputs=[chatbot, sources],
    ).then(fn=lambda: "", outputs=question)


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
