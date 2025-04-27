# rag_agent.py

import logging
import os
import semantic_search
import uvicorn
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI


LOCAL_LLM_ENDPOINT = "http://localhost:11434/v1"
API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:4b")


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



client = AsyncOpenAI(
    base_url=LOCAL_LLM_ENDPOINT,
    api_key=API_KEY,
)


app = FastAPI(
    title="RAG Agent API",
    description="API for answering questions using Retrieval-Augmented Generation",
)



async def ask_llm(prompt: str, system_message: str = None, max_tokens: int = 200):
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    logger.info(f"Sending prompt to LLM (model: {LLM_MODEL}): {prompt}...")
    try:
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.2,  # Lower temperature for more deterministic results
        )
        content = response.choices[0].message.content.strip()
        logger.info(f"Received response from LLM: {content}...")
        return content
    except Exception as e:
        logger.error(f"Error interacting with LLM: {e}")
        raise HTTPException(status_code=503, detail=f"LLM service unavailable or error: {e}")




@app.get("/search/")
async def rag_query_endpoint(
        query: str,
        search_top_n: int = 3,
        search_fuzzy_threshold: int = 70
):
    """
    Performs RAG:
    1. Asks LLM to generate a search query from the user question.
    2. Performs semantic search using the generated query.
    3. Asks LLM to answer the user question based on search results.
    """
    user_question = query
    logger.info(f"Received RAG request for question: '{user_question}'")

    # === Step 1: Generate Search Query ===
    search_query_prompt = f"""Based on the following user question, generate a concise and effective search query suitable for retrieving relevant documents from a knowledge base containing text snippets. Focus on key entities and concepts. Do not add explanations, just output the query.

User Question: "{user_question}"

Search Query:"""

    try:
        generated_search_query = await ask_llm(search_query_prompt, max_tokens=50)
        # Sometimes models add quotes, remove them
        generated_search_query = generated_search_query.strip().strip('"')
        logger.info(f"Generated search query: '{generated_search_query}'")
        if not generated_search_query:
            logger.warning("LLM generated an empty search query. Using original question.")
            generated_search_query = user_question  # Fallback
    except Exception as e:
        logger.error(f"Failed to generate search query: {e}. Falling back to user question.")
        generated_search_query = user_question  # Fallback on error

    # === Step 2: Perform Semantic Search ===
    logger.info(
        f"Performing semantic search with query: '{generated_search_query}', top_n={search_top_n}, fuzzy_threshold={search_fuzzy_threshold}")
    try:
        search_results = semantic_search.search_documents(
            query=generated_search_query,
            top_n=search_top_n,
            fuzzy_threshold=search_fuzzy_threshold
        )
        logger.info(f"Found {len(search_results)} relevant documents.")
        if not search_results:
            logger.warning("Semantic search returned no results.")
            context_str = "No relevant documents found."
        else:
            # Format context for the final prompt
            context_snippets = [f"Document ID: {res['doc_id']}\nSnippet: {res['text_snippet']}" for res in
                                search_results]
            context_str = "\n\n---\n\n".join(context_snippets)
            logger.debug(f"Formatted context:\n{context_str}")

    except Exception as e:
        logger.error(f"Error during semantic search: {e}")
        raise HTTPException(status_code=500, detail=f"Error during semantic search: {e}")

    # === Step 3: Generate Final Answer based on Context ===
    final_answer_prompt = f"""Please answer the following user question based *only* on the provided context documents. Answer the question directly. If the context does not contain the answer, state that you cannot answer based on the provided information. Do not make up information. 

Context Documents:
---
{context_str}
---

User Question: "{user_question}"

Answer:"""

    try:
        final_answer = await ask_llm(final_answer_prompt, max_tokens=300)  # Allow longer answer
        logger.info(f"Generated final answer: '{final_answer}'")
    except Exception as e:
        logger.error(f"Failed to generate final answer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate final answer: {e}")

    return {
        "user_question": user_question,
        "generated_search_query": generated_search_query,
        "retrieved_context": search_results,  # Include retrieved snippets for inspection
        "final_answer": final_answer,
    }


@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG Agent API. Use the /rag_query/ endpoint."}


# --- Run the App (for local development) ---
if __name__ == "__main__":
    # Ensure the embeddings file exists before starting
    if not os.path.exists(semantic_search.EMBEDDINGS_FILE):
        logger.error(
            f"Embeddings file not found at {semantic_search.EMBEDDINGS_FILE}. Please run embedding_compute.py first.")
        exit(1)  # Exit if embeddings are missing

    logger.info(f"Starting RAG Agent API server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)