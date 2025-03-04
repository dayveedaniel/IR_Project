import json
import os
import sys
import numpy as np
from sentence_transformers import SentenceTransformer


def load_json(file_path):
    with open(file_path, 'r', encoding='utf8') as f:
        return json.load(f)


def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def main():
    embeddings_file = "../embedding_search/embeddings.json"

    if not os.path.exists(embeddings_file):
        print("Embeddings file not found. Please run the update_embeddings.py script first.")
        sys.exit(1)

    # Load the embeddings database.
    embeddings_db = load_json(embeddings_file)

    # Initialize the embedding model.
    model = SentenceTransformer('all-MiniLM-L6-v2')

    while True:
        query = input("Enter your search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        query_embedding = model.encode(query)

        # Compute similarity scores.
        results = []
        for doc_id, data in embeddings_db.items():
            emb = np.array(data["embedding"])
            sim = cosine_similarity(query_embedding, emb)
            results.append((doc_id, sim, data["text"]))

        # Sort results by descending similarity.
        results = sorted(results, key=lambda x: x[1], reverse=True)

        # Define how many top results to show.
        top_n = 3
        print(f"\nTop {top_n} results:")
        for i, (doc_id, sim, text) in enumerate(results[:top_n], start=1):
            print(f"\nResult {i}:")
            print(f"Doc ID: {doc_id}")
            print(f"Similarity: {sim:.4f}")
            # Show the first 200 characters of the text snippet.
            print(f"Text snippet: {text[:200]}...")
            print("-" * 40)


if __name__ == "__main__":
    main()
