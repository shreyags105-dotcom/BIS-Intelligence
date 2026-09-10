import os
import pickle
import re
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

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001").strip()

_client = None
_local_embedder = None
_covered_products = None


def _get_client():
    """Lazily create the Gemini client so imports never crash without an API key."""
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to the .env file in the project root or in ai/.env."
        )
    _client = genai.Client(api_key=api_key)
    return _client


def _get_local_embedder():
    """Lazily load the local embedding model (avoids big downloads at import time)."""
    global _local_embedder
    if _local_embedder is not None:
        return _local_embedder
    if SentenceTransformer is None:
        raise ImportError("sentence-transformers is not installed.")
    _local_embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _local_embedder

possible_excel_files = [
    DATA_DIR / "BIS_Intelligence_Rohan_25_Products_VERIFIED_UPDATED.xlsx",
    DATA_DIR / "BIS_Intelligence_25_Products_VERIFIED_UPDATED.xlsx",
    DATA_DIR / "BIS_Intelligence_25_Products_FILLED.xlsx",
    DATA_DIR / "BIS_Intelligence_VERIFIED.xlsx",
    DATA_DIR / "BIS_verified.xlsx",
    DATA_DIR / "bis_data.xlsx",
    DATA_DIR / "BIS.pdf.xlsx",
    Path(r"C:\Users\ujwal\Downloads\BIS_Intelligence_25_Products_VERIFIED_UPDATED.xlsx"),
    Path(r"C:\Users\ujwal\Downloads\BIS_Intelligence_25_Products_FILLED.xlsx"),
    Path(r"C:\Users\ujwal\Downloads\BIS_Intelligence_VERIFIED.xlsx"),
    PROJECT_ROOT / "bis_data.xlsx",
    PROJECT_ROOT / "BIS.pdf.xlsx",
]
EXCEL_FILE = next((path for path in possible_excel_files if path.exists()), possible_excel_files[0])
INDEX_FILE = VECTOR_DB_DIR / "bis.index"
DATA_FILE = VECTOR_DB_DIR / "bis_data.pkl"


# ============================================================
# NORMALIZE EXCEL DATA
# ============================================================

def normalize_columns(df):
    alias_map = {
        "product": "Products",
        "products": "Products",
        "product_name": "Products",
        "standard_no": "IS NO.",
        "standard_number": "IS NO.",
        "is_no": "IS NO.",
        "is_no_": "IS NO.",
        "is_number": "IS NO.",
        "indian_standard": "IS NO.",
        "requirements": "Requirements",
        "requirement": "Requirements",
        "current_requirements_from_rohan": "Requirements",
        "safety": "Safety",
        "current_safety_from_rohan": "Safety",
        "tests": "Tests",
        "test_method": "Tests",
        "test_methods": "Tests",
        "current_tests_from_rohan": "Tests",
        "certification": "Certification",
        "certification_applicability_verified": "Certification",
        "scheme": "Scheme",
        "certification_scheme_route_verified": "Scheme",
        "bis_service": "BIS Service",
        "bis_services": "BIS Service",
        "source": "Source",
        "purpose": "Purpose",
        "url": "URL",
        "official_source": "Source",
        "related_standards": "Related Standards",
        "scope": "Scope",
        "scope_applicability": "Scope",
        "status": "Status",
        "verification_date": "Verification Date",
        "certification_route": "Certification Route",
        "required_documents": "Required Documents",
        "laboratory_guidance": "Laboratory Guidance",
        "inspection_assessment": "Inspection/Assessment",
        "ongoing_compliance": "Ongoing Compliance",
        "clauses": "Clauses",
        "version": "Version",
        "standard_status_version": "Standard status/version",
        "construction": "Construction",
        "materials": "Materials",
        "manufacturing_process_information": "Manufacturing/process information",
        "performance": "Performance",
        "marking": "Marking",
        "product_type": "Products",
        "standard_name": "IS NO.",
        "standard": "IS NO.",
        "is_2347": "IS NO.",
    }

    renamed = {}
    for col in df.columns:
        raw_name = str(col).strip()
        normalized = raw_name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        normalized = normalized.replace("(", "").replace(")", "").replace(".", "")
        renamed[col] = alias_map.get(normalized, raw_name.strip())

    df = df.rename(columns=renamed)
    df.columns = [str(col).strip() for col in df.columns]
    df = df.fillna("")
    return df


# ============================================================
# LOAD EXCEL DATA
# ============================================================

def load_bis_data():
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"BIS Excel file not found at: {EXCEL_FILE}. "
            "Place the Excel file in the data folder or update the path."
        )

    try:
        excel_file = pd.ExcelFile(EXCEL_FILE)
    except ImportError as exc:
        raise ImportError(
            "Excel support is missing. Install it with: "
            "& '.\\.venv\\Scripts\\python.exe' -m pip install openpyxl"
        ) from exc

    frames = []
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        df = normalize_columns(df)
        if df.empty:
            continue
        frames.append(df)

    if not frames:
        raise ValueError(f"No valid BIS rows were found in {EXCEL_FILE}.")

    df = pd.concat(frames, ignore_index=True)

    required_columns = [
        "Products",
        "IS NO.",
        "Requirements",
        "Safety",
        "Tests",
        "Certification",
        "Scheme",
        "BIS Service",
        "Source",
        "Purpose",
        "URL",
    ]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    return df


# ============================================================
# CREATE SEARCHABLE TEXT
# ============================================================

def create_search_text(row):

    product = row.get("Products", "")
    standard = row.get("IS NO.", "")
    requirements = row.get("Requirements", "")
    safety = row.get("Safety", "")
    tests = row.get("Tests", "")
    certification = row.get("Certification", "")
    scheme = row.get("Scheme", "")
    service = row.get("BIS Service", "")
    source = row.get("Source", "")
    purpose = row.get("Purpose", "")
    url = row.get("URL", "")

    return f"""
Product: {product}

Indian Standard: {standard}

Requirements:
{requirements}

Safety:
{safety}

Tests:
{tests}

Certification:
{certification}

Scheme:
{scheme}

BIS Service:
{service}

Source:
{source}

Purpose:
{purpose}

URL:
{url}
"""


# ============================================================
# CREATE EMBEDDING
# ============================================================

def create_embedding(text, force_local=False):

    if EMBEDDING_MODEL and not force_local:
        try:
            response = _get_client().models.embed_content(
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

    try:
        embedder = _get_local_embedder()
    except (ImportError, Exception) as exc:
        raise RuntimeError(
            "No valid embedding backend is available. "
            "Install sentence-transformers or provide a valid Gemini embeddings model."
        ) from exc

    embedding = embedder.encode(text)
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
                "texts": texts,
                "embedding_dim": dimension,
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

    # Create query embedding, keeping its dimension compatible with the index.
    # Decide which backend matches the index dimension so it works whether the
    # index was built with local (384-d) or Gemini (3072-d) embeddings.
    try:
        local_dim = len(_get_local_embedder().encode("_")) if _get_local_embedder() is not None else None
    except Exception:
        local_dim = None

    query_embedding = None
    if index.d == local_dim:
        query_embedding = create_embedding(query, force_local=True)
    else:
        query_embedding = create_embedding(query)

    if len(query_embedding) != index.d:
        raise RuntimeError(
            f"Embedding dimension mismatch: index is {index.d}-dimensional but "
            f"the query embedding is {len(query_embedding)}-dimensional. "
            "Rebuild the vector index with the current embedding model: "
            "python ai/rag.py build"
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
                    row.get("Products", ""),

                "standard":
                    row.get("IS NO.", ""),

                "requirements":
                    row.get("Requirements", ""),

                "safety":
                    row.get("Safety", ""),

                "tests":
                    row.get("Tests", ""),

                "certification":
                    row.get("Certification", ""),

                "scheme":
                    row.get("Scheme", ""),

                "service":
                    row.get("BIS Service", ""),

                "source":
                    row.get("Source", ""),

                "purpose":
                    row.get("Purpose", ""),

                "url":
                    row.get("URL", ""),

                "distance":
                    float(distance)

            })


    return results


# ============================================================
# SAFE TEXT EXTRACTION
# ============================================================

def extract_text(response):
    if response is None:
        return ""

    if hasattr(response, "text") and response.text is not None:
        return str(response.text).strip()

    if isinstance(response, dict):
        text = response.get("text")
        if text is not None:
            return str(text).strip()

    candidates = getattr(response, "candidates", None)
    if candidates:
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            if content is None:
                continue
            parts = getattr(content, "parts", None)
            if not parts:
                continue
            for part in parts:
                value = getattr(part, "text", None)
                if value is not None:
                    return str(value).strip()

    return ""


# ============================================================
# BIS RELEVANCE CHECK
# ============================================================

def is_bis_question(query):
    text = (query or "").lower().strip()
    if not text:
        return False

    if detect_product(text) is not None:
        return True

    if any(keyword in text for keyword in [
        "bis",
        "indian standard",
        "standard",
        "certification",
        "certify",
        "hallmark",
        "testing",
        "lab",
        "laboratory",
        "product compliance",
        "manufacture",
        "manufacturing",
        "quality",
        "safety requirements",
        "marking",
        "license",
    ]):
        return True

    try:
        response = _get_client().models.generate_content(
            model=MODEL_NAME,
            contents=(
                "You are a BIS domain classifier.\n\n"
                "Determine whether the user's question is related to BIS or Indian Standards.\n"
                "Return ONLY YES or NO.\n\n"
                f"Question: {query}"
            ),
            config=types.GenerateContentConfig(temperature=0, max_output_tokens=10),
        )

        result = extract_text(response).upper()
        return result == "YES"
    except Exception:
        return False

# ============================================================
# GENERATE BIS ANSWER
# ============================================================

def build_fallback_answer(query, results, product_name=None):
    if not results:
        return "I could not find verified BIS information for this query in the available knowledge base."

    first = results[0]
    product = first.get("product") or product_name or "the product"
    standard = first.get("standard") or "the relevant Indian Standard"
    requirements = first.get("requirements") or "No requirement details were found in the verified records."
    tests = first.get("tests") or "No testing details were found in the verified records."
    certification = first.get("certification") or "No certification guidance was found in the verified records."
    source = first.get("source") or "Verified BIS record"

    return (
        f"Based on the verified BIS records provided, here is the information regarding {product}:\n\n"
        f"* **Product:** {product}\n"
        f"* **Applicable Indian Standard:** {standard}\n"
        f"* **Requirements:** {requirements}\n"
        f"* **Testing:** {tests}\n"
        f"* **Certification:** {certification}\n"
        f"* **Source:** {source}"
    )


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

    try:
        response = _get_client().models.generate_content(
            model=MODEL_NAME,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=800,
                system_instruction=system_prompt,
            ),
        )
        answer = extract_text(response)
        if answer:
            return answer
    except Exception as exc:
        print(f"[WARNING] Gemini generate_content failed; using verified-data fallback. Details: {exc}")

    return build_fallback_answer(query, results)


# ============================================================
# INTENT AND PRODUCT DETECTION
# ============================================================

INTENT_PATTERNS = {
    "STANDARD_SEARCH": [
        "what standard applies",
        "which standard applies",
        "standard for",
        "what is the standard",
        "which standard",
        "what standard",
    ],
    "MANUFACTURING_GUIDANCE": [
        "how do i manufacture",
        "manufacture this",
        "how to manufacture",
        "make this product",
        "manufacturing",
        "how do i make",
    ],
    "TESTING": [
        "what tests",
        "tests are required",
        "testing required",
        "what test",
        "test methods",
    ],
    "CERTIFICATION": [
        "how do i get bis certification",
        "certification",
        "get certified",
        "bis certification",
        "certify",
    ],
    "HALLMARKING": [
        "hallmark",
        "hallmarking",
    ],
    "LABORATORY": [
        "laboratory",
        "testing laboratory",
        "test lab",
        "recognized lab",
    ],
    "DOCUMENTS": [
        "what documents",
        "documents do i need",
        "required documents",
        "paperwork",
        "documents",
    ],
    "COMPLIANCE": [
        "am i compliant",
        "compliance",
        "compliant",
        "check compliance",
    ],
    "NEXT_ACTION": [
        "what should i do next",
        "next action",
        "what do i do next",
        "next steps",
        "roadmap",
    ],
}

PRODUCT_KEYWORDS = {
    "Pressure Cooker": [
        "pressure cooker",
        "pressure cookers",
        "domestic pressure cooker",
        "cooker",
    ],
    "Helmet": [
        "helmet",
        "helmets",
    ],
    "Cement": [
        "cement",
    ],
    "LED Lamp": [
        "led lamp",
        "led lamps",
        "lamp",
    ],
    "LPG Gas Stove": [
        "lpg gas stove",
        "gas stove",
        "stove",
    ],
    "Electric Food Mixer": [
        "electric food mixer",
        "food mixer",
        "mixer",
    ],
    "Ceiling Fan": [
        "ceiling fan",
        "fan",
    ],
    "Laptop": [
        "laptop",
        "laptops",
    ],
    "Headphones": [
        "headphones",
        "headphone",
    ],
    "Packaged Drinking Water": [
        "packaged drinking water",
        "drinking water",
        "water bottle",
    ],
}


def detect_intent(query):
    text = (query or "").lower().strip()
    if not text:
        return "UNKNOWN"

    for intent, patterns in INTENT_PATTERNS.items():
        if any(pattern in text for pattern in patterns):
            return intent

    if "standard" in text:
        return "STANDARD_SEARCH"
    if "manufactur" in text:
        return "MANUFACTURING_GUIDANCE"
    if "test" in text:
        return "TESTING"
    if "certif" in text:
        return "CERTIFICATION"
    if "hallmark" in text:
        return "HALLMARKING"
    if "laborator" in text or " lab" in text:
        return "LABORATORY"
    if "document" in text:
        return "DOCUMENTS"
    if "compliant" in text or "compliance" in text:
        return "COMPLIANCE"
    if "next" in text or "roadmap" in text:
        return "NEXT_ACTION"

    return "UNKNOWN"


def detect_product(query):
    text = (query or "").lower().strip()
    for product, patterns in PRODUCT_KEYWORDS.items():
        if any(pattern in text for pattern in patterns):
            return product
    return None


SERVICE_GUIDANCE = {
    "CERTIFICATION": (
        "BIS certification is the process through which the Bureau of Indian Standards grants "
        "a licence (typically under the ISI-mark scheme) to manufacture a product that conforms "
        "to a relevant Indian Standard. The general route includes: (1) identification of the "
        "applicable Indian Standard and the certification scheme for your product, "
        "(2) establishment of a qualified factory with an in-house or recognized test facility, "
        "(3) submission of the application with technical documentation to BIS, "
        "(4) factory audit and sample testing by BIS, and (5) grant of the licence if found conforming. "
        "Tell me the specific product you manufacture so I can give you the exact standard and steps."
    ),
    "HALLMARKING": (
        "BIS hallmarking is the official certification by the Bureau of Indian Standards of the "
        "purity and fineness of gold and silver jewellery sold in India. It assures consumers "
        "that the metal conforms to the applicable Indian Standard, verified against the BIS "
        "Hallmarking scheme, which includes a HUID number on each certified article. "
        "If you would like details for a specific jewellery product or registration as a "
        "jeweller, ask me about your product so I can guide you."
    ),
    "LABORATORY": (
        "To find a relevant BIS testing laboratory, you should consult BIS-recognized testing "
        "laboratories that are empanelled for the specific Indian Standard of your product. "
        "BIS lists its recognized laboratories on the official BIS portal, and your samples "
        "must be tested in a laboratory recognized for that standard and scheme before licence "
        "grant. Tell me your product so I can point you to the correct testing guidance."
    ),
}


def build_ai_explainer(product_name, result):
    if not result:
        return "No verified BIS record was available for this product in the current dataset."

    product_label = result.get("product") or product_name or "this product"
    standard_label = result.get("standard") or "the relevant Indian Standard"
    return (
        f"The evidence shows that {product_label} is associated with {standard_label}. "
        "This explanation is based on the retrieved BIS records and not on general assumptions."
    )


def build_standard_comparison(results):
    if not results:
        return "No comparison was possible because no verified BIS records were retrieved."

    valid = [r for r in results if r.get("standard") or r.get("product")]
    if not valid:
        return "No comparison was possible because no verified BIS records were retrieved."

    standards = ", ".join(sorted({str(r.get("standard", "")) for r in valid if r.get("standard")})) or "No standard listed"
    products = ", ".join(sorted({str(r.get("product", "")) for r in valid if r.get("product")})) or "No product listed"
    return f"Relevant records retrieved for {products}. Ranked standards: {standards}."


def build_follow_up_questions(product_name=None, intent=None):
    if product_name:
        return [
            f"Would you like the manufacturing checklist for {product_name}?",
            "Do you want the testing requirements and certification steps next?",
            "Would you like a compliance roadmap for this product?",
        ]

    if intent == "CERTIFICATION":
        return [
            "Which product are you certifying?",
            "Do you want the standard, documents, or certification steps first?",
        ]

    return [
        "Which product are you asking about?",
        "Do you need the standard, testing, or certification guidance?",
    ]


def calculate_confidence(results, product_name=None, intent=None):
    score = 0.35
    if product_name:
        score += 0.20
    if intent:
        score += 0.10
    if results:
        score += min(0.30, len(results) * 0.10)
    return round(min(1.0, max(score, 0.0)), 2)


def build_structured_sections(results, product_name=None, intent=None):
    sections = {
        "direct_answer": "",
        "why_this_applies": "",
        "requirements": "",
        "testing": "",
        "documents": "",
        "certification": "",
        "compliance_roadmap": "",
        "next_action": "",
        "sources": [],
        "ai_explainer": "",
        "comparison": "",
        "follow_up_questions": [],
        "trust_status": "VERIFIED_BIS_DATA",
        "confidence": 0.0,
    }

    if not results:
        sections["trust_status"] = "UNVERIFIED"
        sections["follow_up_questions"] = build_follow_up_questions(product_name=product_name, intent=intent)
        sections["confidence"] = calculate_confidence([], product_name=product_name, intent=intent)
        return sections

    first = results[0]
    sections["direct_answer"] = (
        f"The most relevant verified BIS record appears to be {first.get('standard', '')} for {first.get('product', product_name or 'this product')}."
    )
    sections["why_this_applies"] = (
        f"This recommendation matches the product and standard information in the verified BIS dataset for {first.get('product', product_name or 'the product')}."
    )
    sections["requirements"] = first.get("requirements", "") or "No requirement details were found in the verified records."
    sections["testing"] = first.get("tests", "") or "No testing details were found in the verified records."
    sections["documents"] = first.get("documents", "") or "No document list was found in the verified records."
    sections["certification"] = first.get("certification", "") or "No certification guidance was found in the verified records."
    sections["compliance_roadmap"] = (
        "1. Confirm the product and standard.\n2. Review requirements and testing.\n3. Prepare required documents.\n4. Follow BIS certification route."
    )
    sections["next_action"] = (
        "Review the applicable standard, testing requirements, and certification guidance before proceeding with manufacturing or compliance filing."
    )
    sections["ai_explainer"] = build_ai_explainer(product_name, first)
    sections["comparison"] = build_standard_comparison(results)
    sections["follow_up_questions"] = build_follow_up_questions(product_name=product_name, intent=intent)
    sections["confidence"] = calculate_confidence(results, product_name=product_name, intent=intent)
    sections["sources"] = [
        {
            "standard": result.get("standard", ""),
            "product": result.get("product", ""),
            "source": result.get("source", ""),
            "url": result.get("url", "")
        }
        for result in results
    ]

    return sections


def build_local_answer(results, product_name=None):
    """Compose a plain-language answer from retrieved records without calling any LLM."""
    if not results:
        return "I could not find verified BIS information for this query in the available knowledge base."

    first = results[0]
    lines = []
    lines.append(f"**{first.get('product', product_name or 'This product')}** — {first.get('standard', 'BIS Standard')}")
    if first.get("requirements"):
        lines.append(f"**Requirements:** {first.get('requirements')}")
    if first.get("safety"):
        lines.append(f"**Safety:** {first.get('safety')}")
    if first.get("tests"):
        lines.append(f"**Tests:** {first.get('tests')}")
    if first.get("certification"):
        lines.append(f"**Certification:** {first.get('certification')}")
    if first.get("source"):
        lines.append(f"**Source:** {first.get('source')}")
    return "\n\n".join(lines)


# ============================================================
# COMPLETE RAG PIPELINE
# ============================================================

def get_covered_products():
    """Return the set of product names that have verified data in this system."""
    global _covered_products
    if _covered_products is None:
        names = set(PRODUCT_KEYWORDS)
        try:
            df = load_bis_data()
            names.update(
                str(x).strip()
                for x in df["Products"].tolist()
                if x is not None and str(x).strip()
            )
        except Exception:
            pass
        _covered_products = names
    return _covered_products


def extract_product_candidate(query):
    """Guess a product-like noun phrase so we can say 'no verified data' for products
    that are NOT in the verified knowledge base without ever hallucinating a standard."""
    text = re.sub(r"\s+", " ", (query or "").strip()).strip()
    if not text:
        return None

    patterns = [
        r"\bis there a\s+(?:bis\s+)?standard\s+for\s+([a-z0-9 ,&'-]{2,40}?)(?=[,.;:!?]|$)",
        r"\b(?:standard|standards)\s+for\s+([a-z0-9 ,&'-]{2,40}?)(?=[,.;:!?]|$)",
        r"\b(?:certify|certifying|manufacture|manufacturing|making|make|sell|export|import|produce|producing)\s+([a-z0-9 ,&'-]{2,40}?)(?=[,.;:!?]|\s+which\b|\s+that\b|\s+and\b|\s+for\b|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = re.sub(r"\s+", " ", match.group(1)).strip().strip(" ,'-")
            if candidate and len(candidate) >= 3:
                return candidate

    # A short bare-phrase query with no service cue is likely just a product name.
    if len(text.split()) <= 4 and not re.search(
        r"(hallmark|laboratory|laboratory|help|call|hello|hi|thank|options|list)", text, re.IGNORECASE
    ):
        return text.strip().strip("?")
    return None


def ask_bis(query):

    if not query or not str(query).strip():
        return {
            "answer": "Please ask a BIS-related question.",
            "results": [],
            "intent": "UNKNOWN",
            "product": None,
            "needs_clarification": True,
            "confidence": 0.0,
            "follow_up_questions": build_follow_up_questions(),
            "sections": build_structured_sections([], intent="UNKNOWN"),
        }

    # --------------------------------------------------------
    # STEP 1: Domain check
    # --------------------------------------------------------
    detected_product = detect_product(query)
    detected_intent = detect_intent(query)

    if not is_bis_question(query):
        return {
            "answer":
                "I can assist with Indian Standards and BIS-related services. I don't have verified BIS information for this query.",
            "results": [],
            "intent": detected_intent or "OUT_OF_SCOPE",
            "product": detected_product,
            "needs_clarification": False,
            "confidence": 0.0,
            "follow_up_questions": build_follow_up_questions(product_name=detected_product, intent=detected_intent),
            "sections": build_structured_sections([], product_name=detected_product, intent=detected_intent),
        }

    # --------------------------------------------------------
    # STEP 2: Ask for clarification when product is missing
    # --------------------------------------------------------
    candidate = extract_product_candidate(query)
    if candidate and re.match(r"^(?:my|your|the|this|that|a|an|some)\s+(?:product|item|goods?|things?)\b", candidate, re.IGNORECASE):
        candidate = None

    if candidate:
        candidate_lower = candidate.lower()
        matched_covered = None
        for covered_name in get_covered_products():
            covered_lower = covered_name.lower()
            if covered_lower in candidate_lower or candidate_lower in covered_lower:
                matched_covered = covered_name
                break

        if matched_covered:
            detected_product = matched_covered
        else:
            guidance = SERVICE_GUIDANCE.get(detected_intent)
            not_found_text = (
                "I don't have verified BIS information for "
                f"'{candidate}' in the knowledge base yet. My data is limited to "
                "25 verified BIS products (for example: pressure cooker, cement, "
                "LED lamps, ceiling fans, helmets, LPG gas stoves, laptops, "
                "headphones, and packaged drinking water). I will not guess a "
                "standard for products I have no verified data for."
            )
            answer = not_found_text + ("\n\n" + guidance if guidance else "")
            return {
                "answer": answer,
                "results": [],
                "intent": "UNCOVERED_PRODUCT" if detected_intent in ("UNKNOWN", None) else detected_intent,
                "product": candidate,
                "needs_clarification": False,
                "confidence": 0.2,
                "sections": build_structured_sections([]),
            }

    if detected_product is None:
        guidance = SERVICE_GUIDANCE.get(detected_intent)
        if guidance:
            return {
                "answer": guidance,
                "results": [],
                "intent": detected_intent,
                "product": None,
                "needs_clarification": True,
                "confidence": 0.35,
                "sections": build_structured_sections([]),
            }
        return {
            "answer": (
                "I can help, but I need the product name first. For example: "
                "pressure cooker, helmet, cement, or LED lamp."
            ),
            "results": [],
            "intent": detected_intent,
            "product": None,
            "needs_clarification": True,
            "confidence": 0.35,
            "follow_up_questions": build_follow_up_questions(intent=detected_intent),
            "sections": build_structured_sections([], intent=detected_intent),
        }

    # --------------------------------------------------------
    # STEP 3: Search BIS knowledge
    # --------------------------------------------------------
    results = search_bis(
        query,
        top_k=3
    )

    # --------------------------------------------------------
    # STEP 4: Generate answer
    # --------------------------------------------------------
    try:
        answer = generate_answer(query, results)
    except Exception:
        # No API key / LLM offline: compose a grounded answer from retrieved records
        answer = build_local_answer(results, product_name=detected_product)

    structured = build_structured_sections(results, product_name=detected_product, intent=detected_intent)

    return {
        "answer": answer,
        "results": results,
        "intent": detected_intent,
        "product": detected_product,
        "needs_clarification": False,
        "confidence": structured["confidence"],
        "follow_up_questions": structured["follow_up_questions"],
        "sections": structured,
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