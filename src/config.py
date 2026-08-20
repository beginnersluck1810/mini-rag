from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
DB_DIR = ROOT / "data"

COLLECTION_NAME = "knowledge_base"

# Character chunks, not tokens. Overlap keeps sentences from being split
# across two embeddings with no shared context.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

N_RESULTS = 3
DEFAULT_MODEL = "gemma3:1b"
AVAILABLE_MODELS = ["gemma3:1b", "gemma4:26b"]
