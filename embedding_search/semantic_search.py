import json
import os
import numpy as np
from fastapi import FastAPI, HTTPException
from sentence_transformers import SentenceTransformer
from rapidfuzz import process, fuzz
from typing import List

EMBEDDINGS_FILE = "../embedding_search/embeddings.json"
if not os.path.exists(EMBEDDINGS_FILE):
    raise Exception("Embeddings file not found. Please run the embeddings script first.")

with open(EMBEDDINGS_FILE, 'r', encoding='utf8') as f:
    data = json.load(f)

documents = data.get("documents", {})
ngram_index_data = data.get("ngram_index", {})

ngram_index = {ng: set(doc_ids) for ng, doc_ids in ngram_index_data.items()}
ngram_keys = list(ngram_index.keys())


model = SentenceTransformer('all-MiniLM-L6-v2')




def get_ngrams(text: str, n: int = 3) -> List[str]:
    tokens = text.lower().split()
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def get_approximate_matches(query_ng: str, threshold: int = 80) -> List[str]:

    matches = process.extract(query_ng, ngram_keys, scorer=fuzz.ratio, score_cutoff=threshold)
    return [match[0] for match in matches]


def search_documents(query: str, n: int = 3, top_n: int = 3, fuzzy_threshold: int = 50):


    query_embedding = model.encode(query)
    query_ngrams = set(get_ngrams(query, n))
    candidate_scores = {}

    for q_ng in query_ngrams:
        if q_ng in ngram_index:
            # Found an exact match.
            for doc_id in ngram_index[q_ng]:
                candidate_scores[doc_id] = candidate_scores.get(doc_id, 0) + 1
        else:
            # Use RapidFuzz for approximate matching on this n-gram.
            approx_matches = get_approximate_matches(q_ng, threshold=fuzzy_threshold)
            for approx_ng in approx_matches:
                for doc_id in ngram_index.get(approx_ng, []):
                    candidate_scores[doc_id] = candidate_scores.get(doc_id, 0) + 1

    # If no candidates are found via n-grams, fall back to all documents.
    candidate_ids = list(candidate_scores.keys()) if candidate_scores else list(documents.keys())

    results = []
    for doc_id in candidate_ids:
        doc = documents[doc_id]
        emb = np.array(doc["embedding"])
        sem_sim = cosine_similarity(query_embedding, emb)
        # Ratio of matched n-grams acts as a local match indicator.
        ngram_match_ratio = candidate_scores.get(doc_id, 0) / len(query_ngrams) if query_ngrams else 0
        results.append({
            "doc_id": doc_id,
            "semantic_similarity": sem_sim,
            "ngram_match_ratio": ngram_match_ratio,
            "text_snippet": doc["text"]
        })

    # Sort primarily by semantic similarity.
    results = sorted(results, key=lambda x: x["semantic_similarity"], reverse=True)
    return results[:top_n]


# --- FastAPI Application ---

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG Semantic Search API"}


@app.get("/search/")
def search_api(query: str, n: int = 3, top_n: int = 3, fuzzy_threshold: int = 80):
    """
    API endpoint to search documents.

    Query parameters:
      - query: search text.
      - n: n-gram size (default 3).
      - top_n: number of results (default 3).
      - fuzzy_threshold: minimum fuzzy score (0-100, default 80).
    """
    try:
        results = search_documents(query, n, top_n, fuzzy_threshold)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
