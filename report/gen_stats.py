import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.chunking import ChunkingStrategyComparator, compute_similarity
from src.embeddings import MockEmbedder
from src.store import EmbeddingStore
from src.models import Document
from src.agent import KnowledgeBaseAgent

text1 = (
    "Artificial intelligence is transforming industries around the world. "
    "Machine learning enables computer systems to learn from data and improve their performance without being explicitly programmed. "
    "Deep learning uses neural networks with many layers to process complex patterns. "
    "Natural language processing allows machines to understand and generate human language. "
    "Computer vision enables machines to interpret and analyze visual information from the world."
)

text2 = (
    "Python is a high-level, general-purpose programming language. "
    "It is known for its simple and readable syntax, making it a popular choice for beginners. "
    "Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming. "
    "It has a large standard library and an active community. "
    "Python is widely used in web development, data science, artificial intelligence, and automation."
)

comp = ChunkingStrategyComparator()

print("=== Document 1: AI Overview ===")
r1 = comp.compare(text1, chunk_size=200)
for name, stats in r1.items():
    print(f"  {name}: count={stats['count']}, avg_length={stats['avg_length']}")

print()
print("=== Document 2: Python Overview ===")
r2 = comp.compare(text2, chunk_size=200)
for name, stats in r2.items():
    print(f"  {name}: count={stats['count']}, avg_length={stats['avg_length']}")

print()
print("=== Similarity Predictions ===")
embed = MockEmbedder()

pairs = [
    ("I love machine learning", "I enjoy deep learning", "high"),
    ("The cat sat on the mat", "Quantum physics is complex", "low"),
    ("Python is a programming language", "Python is used for coding", "high"),
    ("The weather is sunny today", "I like to eat pizza", "low"),
    ("Vector databases store embeddings", "Vector stores hold embedding data", "high"),
]

for a, b, pred in pairs:
    va = embed(a)
    vb = embed(b)
    score = compute_similarity(va, vb)
    print(f"  pred={pred}, actual={score:.4f} | '{a}' vs '{b}'")

print()
print("=== RAG Benchmark ===")
store = EmbeddingStore(collection_name="demo", embedding_fn=MockEmbedder())
docs = [
    Document("d1", "Python is a high-level programming language known for its simple syntax.", {"topic": "python"}),
    Document("d2", "Machine learning is a branch of AI that learns patterns from data.", {"topic": "ml"}),
    Document("d3", "Vector databases index embeddings for fast similarity search.", {"topic": "vectordb"}),
    Document("d4", "Deep learning uses multi-layer neural networks for complex tasks.", {"topic": "dl"}),
    Document("d5", "Natural language processing enables machines to understand human text.", {"topic": "nlp"}),
]
store.add_documents(docs)
agent = KnowledgeBaseAgent(store=store, llm_fn=lambda prompt: "Answer based on retrieved context.")

queries = [
    ("What is Python?", "Python is a high-level programming language"),
    ("How does machine learning work?", "ML learns patterns from data"),
    ("What is a vector database?", "Vector databases index embeddings"),
    ("What is deep learning?", "Deep learning uses neural networks"),
    ("What is NLP?", "NLP enables machines to understand text"),
]

for i, (q, gold) in enumerate(queries, 1):
    results = store.search(q, top_k=3)
    top1 = results[0] if results else {}
    score = top1.get("score", 0)
    content_preview = top1.get("content", "")[:60] if top1 else ""
    relevant = "Yes" if gold.lower().split()[0] in (top1.get("content", "").lower()) else "Maybe"
    print(f"  Q{i}: score={score:.4f}, chunk='{content_preview}...', relevant={relevant}")
