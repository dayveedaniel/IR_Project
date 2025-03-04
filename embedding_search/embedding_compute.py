import json
import os
import time
import shutil
from sentence_transformers import SentenceTransformer


def extract_texts(data):
    texts = {}
    # data is a list of dictionaries, each with one article title as key
    for article in data:
        for title, content in article.items():
            def traverse(subcontent, path):
                if isinstance(subcontent, dict):
                    for key, val in subcontent.items():
                        if key == "main_content" and isinstance(val, str):
                            # Create a unique doc_id by combining title and section path.
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


def main():
    data_file = "../data_mining/data.json"
    embeddings_file = "../embedding_search/embeddings.json"
    backup_file_path = "../embedding_search/embeddings_backup.json"

    with open(data_file, 'r', encoding='utf8') as f:
        data = json.load(f)

    # Extract text blocks with unique identifiers.
    texts = extract_texts(data)  # dict: doc_id -> text

    # Load existing embeddings (if any)
    if os.path.exists(embeddings_file):
        with open(embeddings_file, 'r', encoding='utf8') as f:
            embeddings_db = json.load(f)
        # Create a backup of current embeddings.
        backup_file(embeddings_file, backup_file_path)
    else:
        embeddings_db = {}

    # Remove embeddings that are not in the current scraped data.
    embeddings_db = {doc_id: emb for doc_id, emb in embeddings_db.items() if doc_id in texts}

    # Initialize the embedding model.
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Find texts that are new and need embeddings.
    new_texts = {doc_id: text for doc_id, text in texts.items() if doc_id not in embeddings_db}
    total_new = len(new_texts)
    print(f"Found {total_new} new text blocks to embed.")

    new_count = 0
    start_time = time.time()

    for doc_id, text in new_texts.items():
        # Generate embedding.
        embedding = model.encode(text).tolist()  # convert numpy array to list for JSON serialization
        embeddings_db[doc_id] = {
            "embedding": embedding,
            "text": text
        }
        new_count += 1

        # Estimate remaining time.
        elapsed = time.time() - start_time
        avg_time = elapsed / new_count
        remaining = total_new - new_count
        est_time_left = remaining * avg_time
        print(
            f"({new_count}/{total_new}). Estimated time left: {est_time_left:.2f} seconds. Generated for {doc_id} ")

        # Save progress every 50 new embeddings.
        if new_count % 500 == 0:
            save_json(embeddings_db, embeddings_file)
            print(f"Progress saved after {new_count} new embeddings.")

    # Save any remaining embeddings.
    save_json(embeddings_db, embeddings_file)
    print("All embeddings updated and saved.")


if __name__ == "__main__":
    main()
