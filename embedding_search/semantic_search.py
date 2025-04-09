import json
import os
import sys
import numpy as np
from sentence_transformers import SentenceTransformer

def load_json(file_path):
    with open(file_path, 'r', encoding='utf8') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def get_ngrams(text, n=3):
    tokens = text.lower().split()
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

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
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )
    return dp[m][n]

def normalized_similarity(s1, s2):
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1, s2)
    return 1 - dist / max_len

def main():
    embeddings_file = "../embedding_search/embeddings.json"
    if not os.path.exists(embeddings_file):
        print("Embeddings file not found. Please run the update_embeddings.py script first.")
        sys.exit(1)

    data = load_json(embeddings_file)
    documents = data.get("documents", {})
    # Convert the stored index lists back to sets for faster look-ups.
    ngram_index = {ngram: set(doc_ids) for ngram, doc_ids in data.get("ngram_index", {}).items()}
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Set the threshold for approximate matching (adjustable as needed).
    approximate_threshold = 0.8

    while True:
        query = input("Enter your search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        query_embedding = model.encode(query)
        query_ngrams = set(get_ngrams(query, 3))
        candidate_scores = {}

        # For each n-gram in the query, first try exact matching.
        for q_ngram in query_ngrams:
            if q_ngram in ngram_index:
                for doc_id in ngram_index[q_ngram]:
                    candidate_scores[doc_id] = candidate_scores.get(doc_id, 0) + 1
            else:
                # Fall back to approximate matching when no exact match is found.
                for candidate_ngram, doc_ids in ngram_index.items():
                    sim = normalized_similarity(q_ngram, candidate_ngram)
                    if sim >= approximate_threshold:
                        for doc_id in doc_ids:
                            candidate_scores[doc_id] = candidate_scores.get(doc_id, 0) + 1

        # If some candidates were scored, use those; otherwise, fallback to all documents.
        if candidate_scores:
            candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
            top_candidates = [doc_id for doc_id, count in candidates[:100]]
        else:
            top_candidates = list(documents.keys())

        results = []
        for doc_id in top_candidates:
            doc_data = documents[doc_id]
            emb = np.array(doc_data["embedding"])
            sim = cosine_similarity(query_embedding, emb)
            ngram_match_ratio = candidate_scores.get(doc_id, 0) / len(query_ngrams) if query_ngrams else 0
            results.append((doc_id, sim, ngram_match_ratio, doc_data["text"]))

        # Sort the final results by semantic similarity.
        results = sorted(results, key=lambda x: x[1], reverse=True)
        top_n = 3
        print(f"\nTop {top_n} results:")
        for i, (doc_id, sim, ngram_ratio, text) in enumerate(results[:top_n], start=1):
            print(f"\nResult {i}:")
            print(f"Doc ID: {doc_id}")
            print(f"Semantic Similarity: {sim:.4f}")
            print(f"Text snippet: {text[:200]}...")
            print("-" * 40)

if __name__ == "__main__":
    main()
