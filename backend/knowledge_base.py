import os
import re
import sys
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "BIS_Intelligence_Rohan_25_Products_VERIFIED_UPDATED.xlsx"

# Dynamically add the 'ai' directory to system path
AI_DIR = BASE_DIR / "ai"
if str(AI_DIR) not in sys.path:
    sys.path.insert(0, str(AI_DIR))

# Import ask_bis from Ujjwala's rag.py inside the ai folder
try:
    from rag import ask_bis
except ImportError:
    try:
        from ai.rag import ask_bis
    except ImportError:
        ask_bis = None
        print("[WARNING] Could not import 'ask_bis' from ai/rag.py. RAG fallback is disabled.")


def clean_text(text):
    if text is None or pd.isna(text):
        return ""
    # Fix common Windows-1252 / UTF-8 encoding artifacts
    cleaned = str(text).replace("â\x80\x93", "–").replace("â", "-").strip()
    return cleaned


def load_excel_knowledge_base():
    if not DATA_PATH.exists():
        print(f"[WARNING] File not found at {DATA_PATH}. Knowledge base initialized as empty.")
        return {}

    try:
        df = pd.read_excel(DATA_PATH)
        kb = {}

        for _, row in df.iterrows():
            product_val = row.get("Product")
            is_val = row.get("IS Number")

            if pd.isna(product_val) or not str(product_val).strip():
                continue

            product_name = clean_text(product_val)
            is_number = clean_text(is_val)

            def parse_list(val):
                if pd.isna(val) or val is None:
                    return []
                val_str = clean_text(val)
                if not val_str or val_str.lower() == "nan":
                    return []
                items = []
                for line in val_str.splitlines():
                    for item in line.split(";"):
                        cleaned = clean_text(item.strip(" •\t\r\n-"))
                        if cleaned and cleaned.lower() != "nan":
                            items.append(cleaned)
                return items

            cert_steps = []
            for i in range(1, 6):
                step_val = row.get(f"Certification Process — Step {i}")
                if pd.notna(step_val) and clean_text(step_val) and clean_text(step_val).lower() != "nan":
                    cert_steps.append(clean_text(step_val))

            if not cert_steps:
                cert_steps = [
                    "Factory & Lab Setup",
                    "Documentation Submission",
                    "Factory Audit & Sample Testing",
                    "Grant of License"
                ]

            entry = {
                "intent": "MANUFACTURING_GUIDANCE",
                "product": product_name,
                "standard_id": is_number,
                "standard_title": clean_text(row.get("Standard Title")),
                "direct_answer": f"For {product_name}, compulsory BIS certification under {is_number} applies.",
                "why_this_applies": clean_text(row.get("Scope / Applicability")) or "Mandatory compliance.",
                "requirements": parse_list(row.get("Current Requirements from Rohan")) or parse_list(row.get("Construction Requirements")),
                "safety_requirements": parse_list(row.get("Detailed Safety Requirements")) or parse_list(row.get("Current Safety from Rohan")),
                "testing": parse_list(row.get("Current Tests from Rohan")) or parse_list(row.get("Test Name")),
                "documents": parse_list(row.get("Required Documents / Inputs")),
                "certification": {
                    "scheme": clean_text(row.get("Certification Scheme / Route (VERIFIED)")) or "Scheme-I (ISI Mark)",
                    "steps": cert_steps
                },
                "compliance_roadmap": [
                    {"step": idx + 1, "title": step_name, "status": "completed" if idx == 0 else ("in_progress" if idx == 1 else "pending")}
                    for idx, step_name in enumerate(cert_steps)
                ],
                "related_standards": parse_list(row.get("Related Standards")),
                "official_source": {
                    "title": clean_text(row.get("Official Source Title")) or "BIS Manakonline Portal",
                    "url": clean_text(row.get("Official Source URL"))
                },
                "next_action": f"Review construction and testing limits under {is_number}.",
                "trust_status": clean_text(row.get("Verification Status")) or "VERIFIED_ONLY"
            }

            kb[product_name.lower()] = entry
            if is_number:
                kb[is_number.lower()] = entry

        print(f"[SUCCESS] Loaded {len(kb)} verified product keys into Knowledge Base.")
        return kb

    except Exception as e:
        print(f"[ERROR] Failed to load Excel knowledge base: {e}")
        return {}


KNOWLEDGE_BASE = load_excel_knowledge_base()


def _looks_conversational(question_lower: str) -> bool:
    """True when the question asks to explain/describe/proceed, routing it to RAG+Gemini."""
    hints = [
        "how do", "how to", "how can", "how should", "process", "explain",
        "export", "meaning", "what does", "steps", "step by", "apply for",
        "get certified", "certification process", "required", "tests",
        "testing", "compliance", "roadmap", "documents", "license", "scheme",
        "audit", "renew", "recommend", "what should i", "what do i", "guide",
        "help me", "overview",
    ]
    return any(hint in question_lower for hint in hints)


def query_knowledge_base(question: str, mode: str = "industry") -> dict:
    if not question:
        question = ""
    question_lower = str(question).lower()
    question_words = set("".join(c if c.isalnum() else " " for c in question_lower).split())

    # Mixed-mode routing:
    #  - Explicit IS-number lookups (e.g. "IS 2347") and bare product names
    #    get the fast, verified Excel answer.
    #  - Conversational / industry questions get the richer RAG + Gemini answer,
    #    still grounded on the same Excel data.
    has_explicit_standard = bool(re.search(r"\bis\s*\d", question_lower))
    if has_explicit_standard or not _looks_conversational(question_lower):

        # 1. Match against Rohan's 25-product Excel database (score all, pick best)
        generic_words = {
            "bureau", "indian", "standard", "standards", "bis", "is", "mark", "png",
            "safety", "test", "testing", "electric", "domestic", "product", "notice",
        }
        best_match = None
        best_score = 0
        question_norm = re.sub(r"[^a-z0-9]", "", question_lower)

        for product_key, data in KNOWLEDGE_BASE.items():
            std_id = str(data.get("standard_id", "")).lower()
            normalized_key = "".join(c if c.isalnum() else " " for c in product_key).strip()
            key_words = set(normalized_key.split())
            significant_words = key_words & question_words
            non_generic = significant_words - generic_words

            score = 0
            # Exact IS number present in the question
            if std_id and std_id in question_lower:
                score = 1000
            # Normalized IS-number match, e.g. "IS2347" vs "IS 2347:2023" or bare "2347"
            elif std_id:
                std_norm = re.sub(r"[^a-z0-9]", "", std_id)
                if std_norm and (std_norm in question_norm or question_norm in std_norm):
                    score = 950
            # Whole product key appears in the question
            elif product_key and product_key in question_lower:
                score = 500
            # Key is a fragment/paraphrase inside the question
            elif normalized_key and normalized_key in question_lower:
                score = 400
            else:
                # Token overlap: 2+ shared words is the strongest weak signal
                if len(significant_words) >= 3:
                    score = 300 + len(significant_words)
                elif len(significant_words) == 2:
                    score = 200 + len(significant_words)
                elif len(non_generic) == 1 and all(len(w) >= 5 for w in non_generic):
                    # A single distinctive word, e.g. "cement", "helmet", "laptop"
                    score = 150

            if score > best_score:
                best_score = score
                best_match = data

        if best_match:
            return best_match

        if has_explicit_standard:
            cited = re.search(r"\bis\s*\d[\d\s]*", question_lower)
            cited_text = cited.group(0).strip() if cited else "that standard"
            return {
                "intent": "UNSUPPORTED",
                "product": "",
                "standard_id": "N/A",
                "standard_title": "",
                "direct_answer": (
                    f"I do not have verified BIS information for {cited_text} in the available "
                    "knowledge base. Please double-check the standard number or ask about a "
                    "product that is covered by a verified BIS standard."
                ),
                "why_this_applies": "",
                "requirements": [],
                "safety_requirements": [],
                "testing": [],
                "documents": [],
                "certification": None,
                "compliance_roadmap": [],
                "related_standards": [],
                "official_source": None,
                "next_action": "Ask about a covered product or verify the standard number.",
                "trust_status": "UNVERIFIED",
            }

    # 2. Fallback: Query Ujjwala's RAG AI engine (ai/rag.py)
    if ask_bis:
        try:
            rag_response = ask_bis(question)
            answer_text = rag_response.get("answer", "No direct answer generated.")
            results = rag_response.get("results", [])

            primary_source = results[0] if results else {}

            return {
                "intent": "MANUFACTURING_GUIDANCE",
                "product": primary_source.get("product", "BIS General Standard Query"),
                "standard_id": primary_source.get("standard", "BIS Standard"),
                "standard_title": primary_source.get("product", ""),
                "direct_answer": answer_text,
                "why_this_applies": "Retrieved via BIS RAG AI Knowledge Engine.",
                "requirements": [answer_text],
                "safety_requirements": [],
                "testing": [],
                "documents": ["Application form", "Test reports"],
                "certification": {
                    "scheme": "Standard BIS Certification Scheme",
                    "steps": [
                        "Submit Application",
                        "Sample Testing",
                        "Factory Inspection",
                        "Grant of License"
                    ]
                },
                "compliance_roadmap": [
                    {"step": 1, "title": "Submit Application", "status": "completed"},
                    {"step": 2, "title": "Sample Testing", "status": "in_progress"},
                    {"step": 3, "title": "Factory Inspection", "status": "pending"},
                    {"step": 4, "title": "Grant of License", "status": "pending"}
                ],
                "related_standards": [],
                "official_source": {
                    "title": primary_source.get("standard", "BIS Official Portal"),
                    "url": primary_source.get("url") or "https://www.bis.gov.in"
                },
                "next_action": "Review compliance details generated by assistant.",
                "trust_status": "AI_GENERATED"
            }
        except Exception as e:
            print(f"[ERROR] RAG processing failed: {e}")

    # 3. Default Unsupported Response if RAG is unavailable or fails
    return {
        "intent": "UNSUPPORTED",
        "product": "",
        "standard_id": "",
        "standard_title": "",
        "direct_answer": "No verified BIS standard record was found for this specific query.",
        "why_this_applies": "",
        "requirements": [],
        "safety_requirements": [],
        "testing": [],
        "documents": [],
        "certification": None,
        "compliance_roadmap": [],
        "related_standards": [],
        "official_source": None,
        "next_action": "Please search for a covered product.",
        "trust_status": "UNVERIFIED"
    }


def get_standard_by_id(standard_id: str) -> dict:
    return query_knowledge_base(standard_id)