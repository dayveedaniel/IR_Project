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
    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngram = " ".join(tokens[i:i+n])
        ngrams.append(ngram)
    return ngrams

def main():
    embeddings_file = "../embedding_search/embeddings.json"
    if not os.path.exists(embeddings_file):
        print("Embeddings file not found. Please run the update_embeddings.py script first.")
        sys.exit(1)
    data = load_json(embeddings_file)
    documents = data.get("documents", {})
    ngram_index = data.get("ngram_index", {})
    model = SentenceTransformer('all-MiniLM-L6-v2')
    while True:
        query = input("Enter your search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        query_embedding = model.encode(query)
        query_ngrams = get_ngrams(query, n=3)
        candidate_scores = {}
        for ngram in query_ngrams:
            if ngram in ngram_index:
                for doc_id in ngram_index[ngram]:
                    candidate_scores[doc_id] = candidate_scores.get(doc_id, 0) + 1
        if candidate_scores:
            candidates = list(candidate_scores.items())
            candidates.sort(key=lambda x: x[1], reverse=True)
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
