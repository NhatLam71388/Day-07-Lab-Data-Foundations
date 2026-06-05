from __future__ import annotations

import uuid
from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb

            client = chromadb.EphemeralClient()
            # UUID suffix ensures each store instance starts with a fresh collection
            unique_name = f"{collection_name}_{uuid.uuid4().hex}"
            self._collection = client.get_or_create_collection(
                unique_name,
                metadata={"hnsw:space": "cosine"},
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        embedding = self._embedding_fn(doc.content)
        meta = dict(doc.metadata)
        meta["doc_id"] = doc.id
        return {"id": doc.id, "content": doc.content, "embedding": embedding, "metadata": meta}

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        query_vec = self._embedding_fn(query)
        scored = [
            {**r, "score": _dot(query_vec, r["embedding"])}
            for r in records
        ]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return [{"content": r["content"], "score": r["score"], "metadata": r["metadata"]} for r in scored[:top_k]]

    def add_documents(self, docs: list[Document]) -> None:
        if self._use_chroma:
            ids, documents, embeddings, metadatas = [], [], [], []
            for doc in docs:
                ids.append(f"{doc.id}_{self._next_index}")
                self._next_index += 1
                documents.append(doc.content)
                embeddings.append(self._embedding_fn(doc.content))
                metadatas.append({**doc.metadata, "doc_id": doc.id})
            self._collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        else:
            for doc in docs:
                self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self._use_chroma:
            count = self._collection.count()
            if count == 0:
                return []
            results = self._collection.query(
                query_embeddings=[self._embedding_fn(query)],
                n_results=min(top_k, count),
            )
            return [
                {"content": doc, "score": 1 - dist, "metadata": meta}
                for doc, dist, meta in zip(
                    results["documents"][0],
                    results["distances"][0],
                    results["metadatas"][0],
                )
            ]
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        if self._use_chroma:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        if self._use_chroma:
            count = self._collection.count()
            if count == 0:
                return []
            kwargs = {
                "query_embeddings": [self._embedding_fn(query)],
                "n_results": min(top_k, count),
            }
            if metadata_filter:
                kwargs["where"] = metadata_filter
            results = self._collection.query(**kwargs)
            return [
                {"content": doc, "score": 1 - dist, "metadata": meta}
                for doc, dist, meta in zip(
                    results["documents"][0],
                    results["distances"][0],
                    results["metadatas"][0],
                )
            ]
        if not metadata_filter:
            return self._search_records(query, self._store, top_k)
        filtered = [
            r for r in self._store
            if all(r["metadata"].get(k) == v for k, v in metadata_filter.items())
        ]
        return self._search_records(query, filtered, top_k)

    def delete_document(self, doc_id: str) -> bool:
        if self._use_chroma:
            existing = self._collection.get(where={"doc_id": doc_id})
            if not existing["ids"]:
                return False
            self._collection.delete(where={"doc_id": doc_id})
            return True
        before = len(self._store)
        self._store = [r for r in self._store if r["metadata"].get("doc_id") != doc_id]
        return len(self._store) < before
