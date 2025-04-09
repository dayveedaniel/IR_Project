import json
import os
import time
import shutil
from sentence_transformers import SentenceTransformer

def extract_texts(data):
    """
    Recursively extract text blocks from your hierarchical JSON corpus.
    Every leaf that is under the key "main_content" is extracted and given
    a unique document id based on its hierarchy.
    """
    texts = {}
    for article in data:
        for title, content in article.items():
            def traverse(subcontent, path):
                if isinstance(subcontent, dict):
                    for key, val in subcontent.items():
                        if key == "main_content" and isinstance(val, str):
                            doc_id = "||".join([title] + path + [key])
                            texts[doc_id] = val
                        elif isinstance(val, dict):
                            traverse(val, path + [key])
                        elif isinstance(val, list):
                            for item in val:
                                if isinstance(item, dict):
                                    traverse(item, path)
            traverse(content, [])
    return texts

def load_json(file_path):
    with open(file_path, 'r', encoding='utf8') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup_file(src, backup_path):
    try:
        shutil.copy(src, backup_path)
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"Error creating backup: {e}")

def get_ngrams(text, n=3):
    """
    Splits text into n-grams (using a simple whitespace tokenizer).
    You could later extend this (e.g. with regex, removing punctuation, etc.).
    """
    tokens = text.lower().split()
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def build_ngram_index(documents, n=3):
    """
    Build an index that maps each n-gram to a list of document IDs where it appears.
    """
    index = {}
    for doc_id, doc in documents.items():
        text = doc["text"]
        ngrams = get_ngrams(text, n)
        for ng in ngrams:
            if ng not in index:
                index[ng] = []
            if doc_id not in index[ng]:
                index[ng].append(doc_id)
    return index

def main():
    data_file = "../data_mining/data.json"
    embeddings_file = "../embedding_search/embeddings.json"
    backup_file_path = "../embedding_search/embeddings_backup.json"

    print("Loading corpus data...")
    with open(data_file, 'r', encoding='utf8') as f:
        data = json.load(f)

    texts = extract_texts(data)
    print(f"Extracted {len(texts)} text blocks from corpus.")

    # Load existing embeddings if available.
    if os.path.exists(embeddings_file):
        existing = load_json(embeddings_file)
        documents = existing.get("documents", {})
        backup_file(embeddings_file, backup_file_path)
    else:
        documents = {}

    # Remove documents that no longer exist in the current texts.
    documents = {doc_id: doc for doc_id, doc in documents.items() if doc_id in texts}

    # Identify new texts that need embeddings.
    new_texts = {doc_id: text for doc_id, text in texts.items() if doc_id not in documents}
    total_new = len(new_texts)
    print(f"Found {total_new} new text blocks requiring embeddings.")

    model = SentenceTransformer('all-MiniLM-L6-v2')
    start_time = time.time()
    count = 0
    for doc_id, text in new_texts.items():
        embedding = model.encode(text).tolist()
        documents[doc_id] = {"embedding": embedding, "text": text}
        count += 1
        if count % 1000 == 0:
            elapsed = time.time() - start_time
            print(f"Processed {count}/{total_new} texts, elapsed {elapsed:.2f} sec")

    # Build the n-gram index (using n=3 by default).
    ngram_index = build_ngram_index(documents, n=3)
    output_data = {
        "documents": documents,
        "ngram_index": ngram_index  # stored as lists (JSON serializable)
    }
    save_json(output_data, embeddings_file)
    print(f"Embeddings and index saved to {embeddings_file}")

if __name__ == "__main__":
    main()
