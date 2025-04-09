import json
import os
import numpy as np
from fastapi import FastAPI, HTTPException
from sentence_transformers import SentenceTransformer

# --- Configuration and Model Loading ---

# Adjust this path if necessary.
EMBEDDINGS_FILE = "../embedding_search/embeddings.json"

if not os.path.exists(EMBEDDINGS_FILE):
    raise Exception("Embeddings file not found. Please run the update_embeddings script first.")

with open(EMBEDDINGS_FILE, 'r', encoding='utf8') as f:
    data = json.load(f)

# Load document embeddings and n-gram index (converted to sets for efficient look-ups)
documents = data.get("documents", {})
ngram_index = {ngram: set(doc_ids) for ngram, doc_ids in data.get("ngram_index", {}).items()}

# Load the SentenceTransformer model (this can take a bit of time)
model = SentenceTransformer('all-MiniLM-L6-v2')
approximate_threshold = 0.8  # threshold for approximate n-gram matching


# --- Helper Functions ---

def get_ngrams(text, n=3):
    tokens = text.lower().split()
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def levenshtein_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # deletion
                dp[i][j - 1] + 1,  # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )
    return dp[m][n]


def normalized_similarity(s1, s2):
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1, s2)
    return 1 - dist / max_len


def search_documents(query: str, n: int = 3, top_n: int = 3):
    """
    Search the document database based on the query.

    Parameters:
      query (str): The search string.
      n (int): The n-gram size to use. (default 3)
      top_n (int): The number of top results to return. (default 3)

    Returns:
      A list of dictionaries containing the doc_id, semantic similarity,
      n-gram match ratio, and a text snippet.
    """
    query_embedding = model.encode(query)
    query_ngrams = set(get_ngrams(query, n))
    candidate_scores = {}

    # First, try exact n-gram matching.
    for q_ngram in query_ngrams:
        if q_ngram in ngram_index:
            for doc_id in ngram_index[q_ngram]:
                candidate_scores[doc_id] = candidate_scores.get(doc_id, 0) + 1
        else:
            # Use approximate matching if no exact match is found.
            for candidate_ngram, doc_ids in ngram_index.items():
                sim = normalized_similarity(q_ngram, candidate_ngram)
                if sim >= approximate_threshold:
                    for doc_id in doc_ids:
                        candidate_scores[doc_id] = candidate_scores.get(doc_id, 0) + 1

    if candidate_scores:
        # Sort candidate document IDs by the number of matching n-grams (descending)
        candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        top_candidates = [doc_id for doc_id, count in candidates[:100]]
    else:
        # If no candidates were found via n-gram matching, consider all documents
        top_candidates = list(documents.keys())

    results = []
    for doc_id in top_candidates:
        doc_data = documents[doc_id]
        emb = np.array(doc_data["embedding"])
        sim = cosine_similarity(query_embedding, emb)
        ngram_match_ratio = candidate_scores.get(doc_id, 0) / len(query_ngrams) if query_ngrams else 0
        results.append({
            "doc_id": doc_id,
            "semantic_similarity": sim,
            "ngram_match_ratio": ngram_match_ratio,
            "text_snippet": doc_data["text"][:200]
        })

    # Sort the final results by semantic similarity in descending order.
    results = sorted(results, key=lambda x: x["semantic_similarity"], reverse=True)
    return results[:top_n]


# --- FastAPI Application ---

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Embedding Search API"}


@app.get("/search/")
def searchDB(query: str, n_grams: int = 3, top_n: int = 3):
    """
    API endpoint to search the document embeddings.

    Query parameters:
      - query (str): The search query.
      - n_grams (int): The n-gram size for indexing (default is 3).
      - top_n (int): Number of top results to return (default is 3).

    Returns:
      JSON response with a list of top search results.
    """
    try:
        results = search_documents(query, n_grams, top_n)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
