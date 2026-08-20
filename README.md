# Mini RAG

A small Retrieval-Augmented Generation app: feed a PDF or pasted text, retrieve relevant chunks from Chroma, and answer with a local Ollama model.

## How it works

```text
PDF / pasted text
        │
        ▼
  extract + chunk (overlap)
        │
        ▼
 Chroma embeddings (local ONNX)
        │
        ▼
 query → nearest chunks
        │
        ▼
 Ollama (Gemma) answers from that context
```

1. **Ingest** splits text into overlapping character chunks so related sentences stay together, then stores them in Chroma. Chroma embeds each chunk automatically.
2. **Retrieve** embeds the question the same way and returns the closest chunks (smaller distance = closer match).
3. **Generate** sends those chunks to Ollama as context and asks the model to answer only from that context.
4. **UI** (`src/app.py`) is a Gradio page for upload/paste + chat.

The early `chroma_test.py` / `chroma_test1.py` scripts were experiments: store a document, inspect embeddings, and check that similar questions retrieve the right chunk.

## Setup

Ollama should already be running, with a model pulled:

```bash
ollama serve
ollama pull gemma3:1b
```

Then:

```bash
cd mini-rag
source venv/bin/activate
pip install -r requirements.txt
python src/app.py
```

Open the local URL Gradio prints (usually http://127.0.0.1:7860).

## CLI (same pipeline, no UI)

```bash
python src/ingest.py      # load docs/*.txt into Chroma
python src/retrieve.py    # print nearest chunks only
python src/generate.py    # retrieve + answer with Ollama
```

`gemma3:1b` is the default (fast). Switch to `gemma4:26b` in the UI for a stronger answer, at the cost of speed.
