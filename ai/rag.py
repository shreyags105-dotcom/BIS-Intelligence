import os
import pickle
from pathlib import Path

import pandas as pd
import numpy as np
import faiss

from google import genai
from google.genai import types
from dotenv import load_dotenv

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_DIR = PROJECT_ROOT / "ai"
DATA_DIR = PROJECT_ROOT / "data"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(AI_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Add it to the .env file in the project root or in ai/.env."
    )

client = genai.Client(api_key=api_key)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001").strip()

if SentenceTransformer is not None:
    _local_embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
else:
    _local_embedder = None

possible_excel_files = [
    DATA_DIR / "BIS.pdf.xlsx",
    DATA_DIR / "bis_data.xlsx",
    PROJECT_ROOT / "bis_data.xlsx",
    PROJECT_ROOT / "BIS.pdf.xlsx",
]
EXCEL_FILE = next((path for path in possible_excel_files if path.exists()), possible_excel_files[0])
INDEX_FILE = VECTOR_DB_DIR / "bis.index"
DATA_FILE = VECTOR_DB_DIR / "bis_data.pkl"


# ============================================================
# LOAD EXCEL DATA
# ============================================================

def load_bis_data():

    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"BIS Excel file not found at: {EXCEL_FILE}. "
            "Place the Excel file in the data folder or update the path."
        )

    df = pd.read_excel(EXCEL_FILE)

    # Remove unnecessary spaces from column names
    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # Replace empty values
    df = df.fillna("")

    return df


# ============================================================
# CREATE SEARCHABLE TEXT
# ============================================================

def create_search_text(row):

    return f"""
Product: {row['Products']}

Indian Standard: {row['IS NO.']}

Requirements:
{row['Requirements']}

Safety:
{row['Safety']}

Tests:
{row['Tests']}

Certification:
{row['Certification']}

Scheme:
{row['Scheme']}

BIS Service:
{row['BIS Service']}

Source:
{row['Source']}

Purpose:
{row['Purpose']}
"""


# ============================================================
# CREATE EMBEDDING
# ============================================================

def create_embedding(text):

    if EMBEDDING_MODEL:
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            if hasattr(response, "embeddings") and response.embeddings:
                embedding = response.embeddings[0].values
                return list(embedding)
            if isinstance(response, dict) and "embedding" in response:
                return response["embedding"]
            if hasattr(response, "embedding"):
                return list(response.embedding.values)
        except Exception as exc:
            print(f"[WARNING] Gemini embedding model unavailable ({EMBEDDING_MODEL}): {exc}. Falling back to local embeddings.")

    if _local_embedder is None:
        raise RuntimeError(
            "No valid embedding backend is available. "
            "Install sentence-transformers or provide a valid Gemini embeddings model."
        )

    embedding = _local_embedder.encode(text)
    return embedding.tolist()


# ============================================================
# BUILD VECTOR DATABASE
# ============================================================

def build_database():

    print("Loading BIS Excel data...")

    df = load_bis_data()

    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    texts = []

    embeddings = []

    print(f"Found {len(df)} BIS records.")

    for index, row in df.iterrows():

        text = create_search_text(row)

        texts.append(text)

        print(
            f"Creating embedding "
            f"{index + 1}/{len(df)}..."
        )

        embedding = create_embedding(text)

        embeddings.append(embedding)


    # Convert to numpy
    embeddings = np.array(
        embeddings,
        dtype="float32"
    )


    # ========================================================
    # FAISS
    # ========================================================

    dimension = embeddings.shape[1]

    faiss_index = faiss.IndexFlatL2(
        dimension
    )

    faiss_index.add(embeddings)


    # Save index
    faiss.write_index(
        faiss_index,
        str(INDEX_FILE)
    )


    # Save original data
    with open(DATA_FILE, "wb") as file:

        pickle.dump(
            {
                "data": df,
                "texts": texts
            },
            file
        )


    print()
    print("===================================")
    print("BIS VECTOR DATABASE CREATED")
    print("===================================")


# ============================================================
# LOAD VECTOR DATABASE
# ============================================================

def load_database():

    if not INDEX_FILE.exists() or not DATA_FILE.exists():

        print(
            "Vector database not found."
        )

        print(
            f"Run from the project root: python ai/rag.py build"
        )

        return None, None, None


    index = faiss.read_index(
        str(INDEX_FILE)
    )


    with open(DATA_FILE, "rb") as file:

        stored_data = pickle.load(file)


    return (
        index,
        stored_data["data"],
        stored_data["texts"]
    )


# ============================================================
# SEARCH BIS DATABASE
# ============================================================

def search_bis(query, top_k=3):

    index, df, texts = load_database()

    if index is None:

        return []


    # Create query embedding
    query_embedding = create_embedding(
        query
    )


    query_vector = np.array(
        [query_embedding],
        dtype="float32"
    )


    # Search
    distances, indices = index.search(
        query_vector,
        top_k
    )


    results = []


    for distance, idx in zip(
        distances[0],
        indices[0]
    ):

        if idx < len(df):

            row = df.iloc[idx]

            results.append({

                "product":
                    row["Products"],

                "standard":
                    row["IS NO."],

                "requirements":
                    row["Requirements"],

                "safety":
                    row["Safety"],

                "tests":
                    row["Tests"],

                "certification":
                    row["Certification"],

                "scheme":
                    row["Scheme"],

                "service":
                    row["BIS Service"],

                "source":
                    row["Source"],

                "purpose":
                    row["Purpose"],

                "url":
                    row["URL"],

                "distance":
                    float(distance)

            })


    return results


# ============================================================
# BIS RELEVANCE CHECK
# ============================================================

def is_bis_question(query):

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=(
            "You are a BIS domain classifier.\n\n"
            "Determine whether the user's question is related to BIS or Indian Standards.\n"
            "Return ONLY YES or NO.\n\n"
            f"Question: {query}"
        ),
        config=types.GenerateContentConfig(temperature=0, max_output_tokens=10),
    )

    result = response.text.strip().upper()
    return result == "YES"

# ============================================================
# GENERATE BIS ANSWER
# ============================================================

def generate_answer(query, results):

    if not results:

        return (
            "I could not find verified BIS "
            "information for this query."
        )


    # --------------------------------------------------------
    # Create context
    # --------------------------------------------------------

    context = ""


    for i, result in enumerate(results):

        context += f"""

===== BIS RECORD {i + 1} =====

Product:
{result['product']}

Indian Standard:
{result['standard']}

Purpose:
{result['purpose']}

Requirements:
{result['requirements']}

Safety:
{result['safety']}

Tests:
{result['tests']}

Certification:
{result['certification']}

Scheme:
{result['scheme']}

BIS Service:
{result['service']}

Source:
{result['source']}

URL:
{result['url']}

"""


    # --------------------------------------------------------
    # SYSTEM PROMPT
    # --------------------------------------------------------

    system_prompt = """

You are a BIS-focused Intelligent Assistant.

Your job is to assist industries and consumers
with Indian Standards and BIS services.

STRICT GROUNDING RULES:

1. Use ONLY the verified BIS records provided
   in the context.

2. NEVER invent:

   - Indian Standard numbers
   - BIS schemes
   - Certification requirements
   - Testing requirements
   - Safety requirements
   - Laboratory information
   - Fees
   - BIS procedures

3. If the information is not available
   in the context, clearly say:

   "I could not find verified BIS information
   for this query in the available knowledge base."

4. Never present assumptions as official BIS information.

5. Always mention the relevant source.

6. For product recommendation questions,
   identify:

   Product
   Applicable Indian Standard
   Requirements
   Safety
   Tests
   Certification Guidance
   BIS Scheme
   Source

7. If multiple products or standards are retrieved,
   choose the one that best matches the user's
   product description.

8. Do not use outside/general knowledge.

9. Keep answers clear and useful for both
   consumers and industries.

"""


    # --------------------------------------------------------
    # USER PROMPT
    # --------------------------------------------------------

    user_prompt = f"""

USER QUESTION:

{query}


VERIFIED BIS KNOWLEDGE:

{context}


Answer the user using ONLY the verified
BIS knowledge above.

"""


    # --------------------------------------------------------
    # LLM
    # --------------------------------------------------------

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=800,
            system_instruction=system_prompt,
        ),
    )

    return response.text


# ============================================================
# COMPLETE RAG PIPELINE
# ============================================================

def ask_bis(query):

    # --------------------------------------------------------
    # STEP 1: Domain check
    # --------------------------------------------------------

    if not is_bis_question(query):

        return {

            "answer":
                "I can assist with Indian Standards "
                "and BIS-related services. I don't have "
                "verified BIS information for this query.",

            "results": []

        }


    # --------------------------------------------------------
    # STEP 2: Search BIS knowledge
    # --------------------------------------------------------

    results = search_bis(
        query,
        top_k=3
    )


    # --------------------------------------------------------
    # STEP 3: Generate answer
    # --------------------------------------------------------

    answer = generate_answer(
        query,
        results
    )


    return {

        "answer": answer,

        "results": results

    }


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) > 1:

        command = sys.argv[1]

        if command == "build":

            build_database()

        else:

            print(
                "Use: python rag.py build"
            )

    else:

        print(
            "Use: python rag.py build"
        )