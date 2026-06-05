from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # Step 1: Retrieve top-k relevant chunks from the store
        results = self.store.search(question, top_k=top_k)

        # Step 2: Build a prompt with the retrieved chunks as context
        if results:
            context_parts = [
                f"[{i + 1}] {r['content']}" for i, r in enumerate(results)
            ]
            context = "\n".join(context_parts)
        else:
            context = "No relevant context found."

        prompt = (
            f"You are a helpful assistant. Use the following context to answer the question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )

        # Step 3: Call the LLM function to generate an answer
        return self.llm_fn(prompt)
