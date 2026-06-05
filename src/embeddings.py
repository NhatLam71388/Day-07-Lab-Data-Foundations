from __future__ import annotations

import hashlib
import math
import re

LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_PROVIDER_ENV = "EMBEDDING_PROVIDER"


class MockEmbedder:
    """Deterministic embedding backend used by tests and default classroom runs."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim
        self._backend_name = "mock embeddings fallback"

    def __call__(self, text: str) -> list[float]:
        digest = hashlib.md5(text.encode()).hexdigest()
        seed = int(digest, 16)
        vector = []
        for _ in range(self.dim):
            seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
            vector.append((seed / 0xFFFFFFFF) * 2 - 1)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class LocalEmbedder:
    """Sentence Transformers-backed local embedder."""

    def __init__(self, model_name: str = LOCAL_EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._backend_name = model_name
        self.model = SentenceTransformer(model_name)

    def __call__(self, text: str) -> list[float]:
        embedding = self.model.encode(text, normalize_embeddings=True)
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return [float(value) for value in embedding]


class OpenAIEmbedder:
    """OpenAI embeddings API-backed embedder."""

    def __init__(self, model_name: str = OPENAI_EMBEDDING_MODEL) -> None:
        from openai import OpenAI

        self.model_name = model_name
        self._backend_name = model_name
        self.client = OpenAI()

    def __call__(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model_name, input=text)
        return [float(value) for value in response.data[0].embedding]


class TFIDFEmbedder:
    """
    TF-IDF bag-of-words embedder fit on a corpus of documents.

    Must be initialised with a list of texts (the corpus) so that IDF
    weights can be computed before any individual text is embedded.
    Produces L2-normalised vectors suitable for cosine similarity search.
    No external dependencies — pure Python.
    """

    _STOPWORDS = {
        'và','của','là','có','được','cho','trong','với','tại','từ','các',
        'theo','này','đó','khi','một','để','hoặc','không','thì','sau',
        'trên','về','bị','sẽ','đã','đến','nếu','mà','như','tôi','bạn',
        'học','sinh','viên','nhà','trường',
    }

    def __init__(self, corpus: list[str], max_vocab: int = 2000) -> None:
        df: dict[str, int] = {}
        n = len(corpus)
        for doc in corpus:
            for term in set(self._tokenize(doc)):
                df[term] = df.get(term, 0) + 1
        idf_raw = {t: math.log((n + 1) / (cnt + 1)) + 1 for t, cnt in df.items()}
        top_terms = sorted(idf_raw, key=lambda t: idf_raw[t], reverse=True)[:max_vocab]
        self.vocab: dict[str, int] = {t: i for i, t in enumerate(top_terms)}
        self.idf: list[float] = [idf_raw[t] for t in top_terms]
        self._backend_name = f"TF-IDF (vocab={len(self.vocab)}, corpus={n})"

    def _tokenize(self, text: str) -> list[str]:
        tokens = re.findall(
            r'[a-záàảãạăắặằẳẵâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]+',
            text.lower(),
        )
        return [t for t in tokens if t not in self._STOPWORDS and len(t) > 1]

    def __call__(self, text: str) -> list[float]:
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * len(self.vocab)
        tf: dict[str, float] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        max_tf = max(tf.values())
        vec = [0.0] * len(self.vocab)
        for term, idx in self.vocab.items():
            if term in tf:
                vec[idx] = (tf[term] / max_tf) * self.idf[idx]
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


class GoogleEmbedder:
    """Google Gemini embedding API (gemini-embedding-001) via google-genai SDK."""

    def __init__(self, api_key: str, model_name: str = "gemini-embedding-001") -> None:
        import time
        from google import genai
        self._client = genai.Client(api_key=api_key)
        self._time = time
        self.model_name = model_name
        self._backend_name = f"Google {model_name}"

    def __call__(self, text: str) -> list[float]:
        import re
        for attempt in range(5):
            try:
                result = self._client.models.embed_content(model=self.model_name, contents=text)
                vec = result.embeddings[0].values
                norm = math.sqrt(sum(v * v for v in vec)) or 1.0
                return [v / norm for v in vec]
            except Exception as e:
                msg = str(e)
                # Parse retry delay from error message if available
                match = re.search(r'retry[^\d]*(\d+(?:\.\d+)?)', msg, re.IGNORECASE)
                wait = float(match.group(1)) + 1 if match else (2 ** attempt) * 5
                if attempt < 4:
                    print(f"  [rate limit] waiting {wait:.0f}s...")
                    self._time.sleep(wait)
                else:
                    raise


_mock_embed = MockEmbedder()
