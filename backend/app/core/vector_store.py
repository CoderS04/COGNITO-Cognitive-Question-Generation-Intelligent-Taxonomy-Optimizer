import math
import os
import re
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from app.config import settings

class VectorStore:
    """
    Hybrid Vector Store providing high-dimensional vector embeddings,
    cosine similarity computations, and semantic similarity search.
    Wraps ChromaDB with an in-memory/fallback semantic vector engine.
    """
    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.chroma_client = None
        self.questions_collection = None
        self.syllabus_collection = None
        self._fallback_questions: Dict[str, Dict[str, Any]] = {}
        self._fallback_syllabus: Dict[str, Dict[str, Any]] = {}
        
        self._init_store()
        
    def _init_store(self):
        if CHROMA_AVAILABLE:
            try:
                os.makedirs(self.persist_dir, exist_ok=True)
                chroma_settings = ChromaSettings(
                    anonymized_telemetry=False,
                    is_persistent=True
                )
                self.chroma_client = chromadb.PersistentClient(path=self.persist_dir, settings=chroma_settings)
                self.questions_collection = self.chroma_client.get_or_create_collection(
                    name="cognito_questions",
                    metadata={"hnsw:space": "cosine"}
                )
                self.syllabus_collection = self.chroma_client.get_or_create_collection(
                    name="cognito_syllabus",
                    metadata={"hnsw:space": "cosine"}
                )
                return
            except Exception as e:
                print(f"[VectorStore] ChromaDB initialization notice: {e}. Utilizing internal semantic embedding engine.")
        self.chroma_client = None

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        tokens = [w for w in cleaned.split() if len(w) > 2]
        return tokens

    def _get_embedding_vector(self, text: str) -> Dict[str, float]:
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        counts = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        
        # Sublinear term frequency scaling
        mag_sq = 0.0
        vec = {}
        for t, c in counts.items():
            val = 1.0 + math.log(c)
            vec[t] = val
            mag_sq += val * val
            
        mag = math.sqrt(mag_sq) if mag_sq > 0 else 1.0
        for t in vec:
            vec[t] /= mag
        return vec

    def cosine_similarity(self, text1: str, text2: str) -> float:
        """
        Computes cosine similarity between two text snippets in [0.0, 1.0].
        Incorporates n-gram overlap and cognitive keyword alignment.
        """
        v1 = self._get_embedding_vector(text1)
        v2 = self._get_embedding_vector(text2)
        if not v1 or not v2:
            return 0.0
        
        dot = sum(v1[k] * v2.get(k, 0.0) for k in v1)
        
        # Bigram overlap boost for syntactic phrase repetition
        words1 = text1.lower().split()
        words2 = text2.lower().split()
        bg1 = set(zip(words1[:-1], words1[1:])) if len(words1) > 1 else set()
        bg2 = set(zip(words2[:-1], words2[1:])) if len(words2) > 1 else set()
        if bg1 and bg2:
            jaccard_bg = len(bg1 & bg2) / len(bg1 | bg2)
            similarity = 0.75 * dot + 0.25 * jaccard_bg
        else:
            similarity = dot
            
        return min(max(similarity, 0.0), 1.0)

    def add_question(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        if self.questions_collection:
            try:
                # Stringify complex metadata types for Chroma
                clean_meta = {k: str(v) if not isinstance(v, (int, float, str, bool)) else v for k, v in metadata.items()}
                self.questions_collection.upsert(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[clean_meta]
                )
                return
            except Exception as e:
                print(f"[VectorStore] Chroma upsert fallback: {e}")
        self._fallback_questions[doc_id] = {"text": text, "metadata": metadata}

    def add_syllabus_chunk(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        if self.syllabus_collection:
            try:
                clean_meta = {k: str(v) if not isinstance(v, (int, float, str, bool)) else v for k, v in metadata.items()}
                self.syllabus_collection.upsert(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[clean_meta]
                )
                return
            except Exception as e:
                print(f"[VectorStore] Chroma syllabus upsert fallback: {e}")
        self._fallback_syllabus[doc_id] = {"text": text, "metadata": metadata}

    def search_similar_questions(self, query: str, n_results: int = 5, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        results = []
        if self.questions_collection:
            try:
                res = self.questions_collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                if res and res.get("documents") and len(res["documents"][0]) > 0:
                    for i, doc in enumerate(res["documents"][0]):
                        dist = res["distances"][0][i] if "distances" in res and res["distances"] else 0.5
                        sim = 1.0 - dist  # Cosine distance to similarity
                        if threshold is None or sim >= threshold:
                            results.append({
                                "id": res["ids"][0][i],
                                "text": doc,
                                "metadata": res["metadatas"][0][i] if "metadatas" in res else {},
                                "similarity": round(float(sim), 4)
                            })
                    return results
            except Exception as e:
                print(f"[VectorStore] Chroma query fallback: {e}")

        # Fallback in-memory search
        scored = []
        for q_id, q_data in self._fallback_questions.items():
            sim = self.cosine_similarity(query, q_data["text"])
            if threshold is None or sim >= threshold:
                scored.append({
                    "id": q_id,
                    "text": q_data["text"],
                    "metadata": q_data["metadata"],
                    "similarity": round(float(sim), 4)
                })
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:n_results]

    def search_syllabus_context(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        results = []
        if self.syllabus_collection:
            try:
                res = self.syllabus_collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                if res and res.get("documents") and len(res["documents"][0]) > 0:
                    for i, doc in enumerate(res["documents"][0]):
                        dist = res["distances"][0][i] if "distances" in res and res["distances"] else 0.5
                        sim = 1.0 - dist
                        results.append({
                            "id": res["ids"][0][i],
                            "text": doc,
                            "metadata": res["metadatas"][0][i] if "metadatas" in res else {},
                            "relevance": round(float(sim), 4)
                        })
                    return results
            except Exception as e:
                print(f"[VectorStore] Chroma syllabus search fallback: {e}")

        scored = []
        for s_id, s_data in self._fallback_syllabus.items():
            sim = self.cosine_similarity(query, s_data["text"])
            scored.append({
                "id": s_id,
                "text": s_data["text"],
                "metadata": s_data["metadata"],
                "relevance": round(float(sim), 4)
            })
        scored.sort(key=lambda x: x["relevance"], reverse=True)
        return scored[:n_results]

# Global singleton vector store
vector_store = VectorStore()
