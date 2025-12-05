"""
RAG (Retrieval Augmented Generation) system for service retrieval
"""
import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, RAG_TOP_K, RAG_SIMILARITY_THRESHOLD, RAG_MIN_SIMILARITY
from services.database import SERVICES_DB


class RAGSystem:
    def __init__(self):
        print("📚 Loading embeddings...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.kb = []
        self.embeddings = None
        self._build_kb()
        print(f"✅ RAG ready: {len(self.kb)} documents")
    
    def _build_kb(self):
        """Build knowledge base from services database"""
        for sid, svc in SERVICES_DB.items():
            text = f"Service: {svc['name_fr']} / {svc['name_ar']}. Description: {svc['description']}"
            self.kb.append({"text": text, "id": sid, "svc": svc})
        
        texts = [x["text"] for x in self.kb]
        self.embeddings = self.embedder.encode(texts, convert_to_numpy=True)
    
    def _keyword_match(self, query_lower: str):
        """Fallback keyword matching for robust search"""
        scores = {}
        for entry in self.kb:
            sid = entry["id"]
            svc = entry["svc"]
            kws = [k.lower() for k in svc.get("keywords", [])]
            count = sum(1 for kw in kws if kw in query_lower)
            scores[sid] = count
        
        best_sid = max(scores, key=lambda k: scores[k])
        if scores[best_sid] > 0:
            for entry in self.kb:
                if entry["id"] == best_sid:
                    return [entry]
        return []
    
    def search(self, query: str, top_k: int = RAG_TOP_K):
        """
        Search for relevant services using embeddings and keyword matching
        
        Args:
            query: User query
            top_k: Number of results to return
            
        Returns:
            List of relevant service entries
        """
        # Embedding similarity search
        q_emb = self.embedder.encode([query], convert_to_numpy=True)[0]
        sims = np.dot(self.embeddings, q_emb) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q_emb) + 1e-10
        )
        
        # Find top indices and their scores
        top_idx = np.argsort(sims)[-top_k:][::-1]
        top_results = [{"entry": self.kb[i], "score": float(sims[i])} for i in top_idx]
        
        # If best score is strong, return those entries
        if top_results and top_results[0]["score"] >= RAG_SIMILARITY_THRESHOLD:
            return [r["entry"] for r in top_results if r["score"] > 0.15]
        
        # Otherwise try keyword matching
        qlow = query.lower()
        kw_results = self._keyword_match(qlow)
        if kw_results:
            return kw_results
        
        # Fallback: return best entries even if low score
        return [r["entry"] for r in top_results if r["score"] > RAG_MIN_SIMILARITY]