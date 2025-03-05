import json
import os
import time
import shutil
from sentence_transformers import SentenceTransformer

def extract_texts(data):
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
    tokens = text.lower().split()
    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngram = " ".join(tokens[i:i+n])
        ngrams.append(ngram)
    return ngrams

def build_ngram_index(documents, n=3):
    index = {}
    for doc_id, data in documents.items():
        text = data["text"]
        ngrams = get_ngrams(text, n)
        for ngram in ngrams:
            if ngram in index:
                if doc_id not in index[ngram]:
                    index[ngram].append(doc_id)
            else:
                index[ngram] = [doc_id]
    return index

def main():
    data_file = "../data_mining/data.json"
    embeddings_file = "../embedding_search/embeddings.json"
    backup_file_path = "../embedding_search/embeddings_backup.json"
    with open(data_file, 'r', encoding='utf8') as f:
        data = json.load(f)
    texts = extract_texts(data)
    if os.path.exists(embeddings_file):
        loaded = load_json(embeddings_file)
        documents = loaded.get("documents", {})
        backup_file(embeddings_file, backup_file_path)
    else:
        documents = {}
    documents = {doc_id: info for doc_id, info in documents.items() if doc_id in texts}
    model = SentenceTransformer('all-MiniLM-L6-v2')
    new_texts = {doc_id: text for doc_id, text in texts.items() if doc_id not in documents}
    total_new = len(new_texts)
    print(f"Found {total_new} new text blocks to embed.")
    new_count = 0
    start_time = time.time()
    for doc_id, text in new_texts.items():
        embedding = model.encode(text).tolist()
        documents[doc_id] = {"embedding": embedding, "text": text}
        new_count += 1
        elapsed = time.time() - start_time
        avg_time = elapsed / new_count
        remaining = total_new - new_count
        est_time_left = remaining * avg_time
        print(f"Generated embedding for {doc_id} ({new_count}/{total_new}). Estimated time left: {est_time_left:.2f} seconds.")
        if new_count % 5000 == 0:
            temp_data = {"documents": documents}
            temp_data["ngram_index"] = build_ngram_index(documents)
            save_json(temp_data, embeddings_file)
            print(f"Progress saved after {new_count} new embeddings.")
    final_data = {"documents": documents}
    final_data["ngram_index"] = build_ngram_index(documents)
    save_json(final_data, embeddings_file)
    print("All embeddings updated and saved.")

if __name__ == "__main__":
    main()
