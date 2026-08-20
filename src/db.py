import chromadb

from config import COLLECTION_NAME, DB_DIR

_client = None


def get_client():
    global _client
    if _client is None:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(DB_DIR))
    return _client


def get_collection():
    return get_client().get_or_create_collection(name=COLLECTION_NAME)


def reset_collection():
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    return get_collection()
