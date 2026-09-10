import os
import re
import sys
from pathlib import Path

<<<<<<< Updated upstream
import pandas as pd
=======
def sanitize(val):
    """Replaces None, empty strings, 'nan' text, or empty lists with clear fallback text."""
    if val is None or str(val).strip().lower() in ["nan", "none", ""]:
        return ["Standard BIS Guidelines Apply"]
    if isinstance(val, list):
        cleaned_list = [item for item in val if item and str(item).strip().lower() not in ["nan", "none", ""]]
        return cleaned_list if cleaned_list else ["Standard BIS Guidelines Apply"]
    return val
>>>>>>> Stashed changes

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "BIS_Intelligence_Rohan_25_Products_VERIFIED_UPDATED.xlsx"

AI_DIR = BASE_DIR / "ai"
if str(AI_DIR) not in sys.path:
    sys.path.insert(0, str(AI_DIR))

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
    cleaned = str(text).replace("â€“", "–").replace("â", "-").replace("Â", "").strip()
    return cleaned


def parse_list(val):
    if val is None or pd.isna(val):
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


def normalize_lookup(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def standard_base_key(value):
    text = str(value or "").lower()
    match = re.search(r"is\s*(\d+)", text)
    if match:
        return f"is{match.group(1)}"
    return normalize_lookup(text)


def response_aliases(data):
    source = data.get("official_source") or {}
    standard_id = str(data.get("standard_id") or "N/A")
    answer = data.get("direct_answer", "")
    testing = data.get("testing") or []
    if testing and answer and "required testing includes" not in answer.lower():
        answer = f"{answer} Required testing includes: {'; '.join(testing)}."

    return {
        "intent": data.get("intent", "MANUFACTURING_GUIDANCE"),
        "product": data.get("product", ""),
        "standard_id": standard_id,
        "standard_title": data.get("standard_title", ""),
        "direct_answer": answer,
        "why_this_applies": data.get("why_this_applies", ""),
        "requirements": data.get("requirements", []),
        "safety_requirements": data.get("safety_requirements", []),
        "testing": testing,
        "documents": data.get("documents", []),
        "certification": data.get("certification"),
        "compliance_roadmap": data.get("compliance_roadmap", []),
        "related_standards": data.get("related_standards", []),
        "official_source": source,
        "next_action": data.get("next_action", ""),
        "trust_status": data.get("trust_status", "VERIFIED_ONLY"),
        "answer": answer,
        "standard": standard_id,
        "source": source.get("title", "BIS Official Portal") if isinstance(source, dict) else source,
        "references": source.get("url", "") if isinstance(source, dict) else "",
        "id": re.sub(r"[^A-Za-z0-9]", "", standard_id),
    }


def load_excel_knowledge_base():
    if not DATA_PATH.exists():
        print(f"[WARNING] File not found at {DATA_PATH}. Knowledge base initialized as empty.")
        return {}

    try:
        df = pd.read_excel(DATA_PATH)
        kb = {}

        for _, row in df.iterrows():
            product_val = row.get("Product") or row.get("Products")
            is_val = row.get("IS Number") or row.get("IS NO.")

            if pd.isna(product_val) or not str(product_val).strip():
                continue

            product_name = clean_text(product_val)
            is_number = clean_text(is_val)

<<<<<<< Updated upstream
=======
            def parse_list(val):
                if pd.isna(val) or val is None:
                    return []
                val_str = clean_text(val)
                if not val_str or val_str.lower() in ["nan", "none", "not specified"]:
                    return []
                items = []
                for line in val_str.splitlines():
                    for item in line.split(";"):
                        cleaned = clean_text(item.strip(" •\t\r\n-"))
                        if cleaned and cleaned.lower() not in ["nan", "none", "not specified"]:
                            items.append(cleaned)
                return items

>>>>>>> Stashed changes
            cert_steps = []
            for i in range(1, 6):
                step_key = f"Certification Process — Step {i}"
                step_val = row.get(step_key)
                if pd.notna(step_val):
                    cleaned = clean_text(step_val)
                    if cleaned and cleaned.lower() != "nan":
                        cert_steps.append(cleaned)

            if not cert_steps:
                cert_steps = [
                    "Factory & Lab Setup",
                    "Documentation Submission",
                    "Factory Audit & Sample Testing",
                    "Grant of License",
                ]

            entry = {
                "intent": "MANUFACTURING_GUIDANCE",
                "product": product_name,
                "standard_id": is_number,
                "standard_title": clean_text(row.get("Standard Title")),
                "direct_answer": f"For {product_name}, compulsory BIS certification under {is_number} applies." if is_number else f"For {product_name}, BIS guidance is available in the verified knowledge base.",
                "why_this_applies": clean_text(row.get("Scope / Applicability")) or "Mandatory compliance.",
<<<<<<< Updated upstream
                "requirements": parse_list(row.get("Current Requirements from Rohan")) or parse_list(row.get("Construction Requirements")) or ["Review product requirements under the applicable standard."],
                "safety_requirements": parse_list(row.get("Detailed Safety Requirements")) or parse_list(row.get("Current Safety from Rohan")) or ["Safety requirements are included in the relevant BIS standard."],
                "testing": parse_list(row.get("Current Tests from Rohan")) or parse_list(row.get("Test Name")) or ["Product testing as required by the relevant BIS standard."],
                "documents": parse_list(row.get("Required Documents / Inputs")) or ["Application form", "Test reports", "Factory documents"],
=======
                "requirements": sanitize(parse_list(row.get("Current Requirements from Rohan")) or parse_list(row.get("Construction Requirements"))),
                "safety_requirements": sanitize(parse_list(row.get("Detailed Safety Requirements")) or parse_list(row.get("Current Safety from Rohan"))),
                "testing": sanitize(parse_list(row.get("Current Tests from Rohan")) or parse_list(row.get("Test Name"))),
                "documents": sanitize(parse_list(row.get("Required Documents / Inputs"))),
>>>>>>> Stashed changes
                "certification": {
                    "scheme": clean_text(row.get("Certification Scheme / Route (VERIFIED)")) or "Scheme-I (ISI Mark)",
                    "steps": cert_steps,
                },
                "compliance_roadmap": [
                    {"step": idx + 1, "title": step_name, "status": "completed" if idx == 0 else ("in_progress" if idx == 1 else "pending")}
                    for idx, step_name in enumerate(cert_steps)
                ],
                "related_standards": parse_list(row.get("Related Standards")),
                "official_source": {
                    "title": clean_text(row.get("Official Source Title")) or "BIS Manakonline Portal",
                    "url": clean_text(row.get("Official Source URL")) or "https://www.bis.gov.in",
                },
                "next_action": f"Review construction and testing limits under {is_number}." if is_number else "Review the applicable BIS guidance for this product.",
                "trust_status": clean_text(row.get("Verification Status")) or "VERIFIED_ONLY",
            }

            kb[product_name.lower()] = entry
            if is_number:
                kb[is_number.lower()] = entry
            if is_number:
                kb[normalize_lookup(is_number)] = entry

        print(f"[SUCCESS] Loaded {len(kb)} verified product keys into Knowledge Base.")
        return kb

    except Exception as e:
        print(f"[ERROR] Failed to load Excel knowledge base: {e}")
        return {}


KNOWLEDGE_BASE = load_excel_knowledge_base()


def _looks_conversational(question_lower: str) -> bool:
    hints = [
        "how do", "how to", "how can", "how should", "process", "explain",
        "meaning", "what does", "steps", "step by", "apply for", "get certified",
        "certification process", "required", "tests", "testing", "compliance",
        "roadmap", "documents", "license", "scheme", "audit", "renew",
        "recommend", "what should i", "what do i", "guide", "help me", "overview"
    ]
    return any(hint in question_lower for hint in hints)


def unsupported_response(message=None):
    default_message = (
        "I can assist with Indian Standards and BIS-related services. "
        "I do not have verified BIS information for this query."
    )
    return response_aliases({
        "intent": "UNSUPPORTED",
        "product": "",
        "standard_id": "N/A",
        "standard_title": "",
        "direct_answer": message or default_message,
        "why_this_applies": "",
        "requirements": [],
        "safety_requirements": [],
        "testing": [],
        "documents": [],
        "certification": None,
        "compliance_roadmap": [],
        "related_standards": [],
        "official_source": None,
        "next_action": "Ask about a BIS-covered product, certification, testing, or laboratory.",
        "trust_status": "UNVERIFIED",
    })


def query_knowledge_base(question: str, mode: str = "industry") -> dict:
    if not question:
        return unsupported_response()

    question_lower = str(question).lower()

<<<<<<< Updated upstream
    if any(term in question_lower for term in ("cricket", "football", "weather", "stock price", "today's score", "match winner")):
        return unsupported_response(
            "I can assist with Indian Standards and BIS-related services. I do not have verified BIS information for this query."
        )

    explicit_standard_match = re.search(r"\bis\s*\d+", question_lower)
    if explicit_standard_match:
        explicit_standard = explicit_standard_match.group(0)
        normalized_explicit = standard_base_key(explicit_standard)
        for item in KNOWLEDGE_BASE.values():
            standard_value = str(item.get("standard_id", ""))
            if standard_base_key(standard_value) == normalized_explicit:
                return response_aliases(item)
        return unsupported_response(
            "I do not have verified BIS information for that standard in the active knowledge base."
        )
=======
    has_explicit_standard = bool(re.search(r"\bis\s*\d", question_lower))
    if has_explicit_standard or not _looks_conversational(question_lower):

        # 1. Match against Rohan's 25-product Excel database
        generic_words = {
            "bureau", "indian", "standard", "standards", "bis", "is", "mark", "png",
            "safety", "test", "testing", "electric", "domestic", "product", "notice",
        }
        best_match = None
        best_score = 0
        question_norm = re.sub(r"[^a-z0-9]", "", question_lower)
>>>>>>> Stashed changes

    if "hallmark" in question_lower:
        return response_aliases({
            "intent": "HALLMARKING_GUIDANCE",
            "product": "Hallmarking",
            "standard_id": "N/A",
            "standard_title": "BIS Hallmarking Services",
            "direct_answer": "BIS hallmarking verifies the purity of precious-metal articles through authorised assaying and hallmarking centres.",
            "why_this_applies": "Hallmarking is a BIS consumer and certification service.",
            "requirements": ["Use a BIS-registered jeweller and authorised assaying and hallmarking centre."],
            "safety_requirements": [],
            "testing": ["Precious-metal purity assessment"],
            "documents": [],
            "certification": {"scheme": "BIS Hallmarking", "steps": ["Submit article", "Assay and hallmark", "Verify HUID"]},
            "compliance_roadmap": [],
            "related_standards": [],
            "official_source": {"title": "BIS Hallmarking Services", "url": "https://www.bis.gov.in/"},
            "next_action": "Verify the HUID and use the official BIS hallmarking service information.",
            "trust_status": "VERIFIED_ONLY",
        })

<<<<<<< Updated upstream
    if ("laborator" in question_lower or "testing lab" in question_lower or "testing laboratory" in question_lower):
        return response_aliases({
            "intent": "LABORATORY_GUIDANCE",
            "product": "BIS Testing Laboratory",
            "standard_id": "N/A",
            "standard_title": "BIS Recognized Laboratories",
            "direct_answer": "Use a BIS-recognized testing laboratory relevant to the product standard and retain the test report for certification.",
            "why_this_applies": "Product certification requires testing against the applicable Indian Standard.",
            "requirements": [],
            "safety_requirements": [],
            "testing": ["Testing by a relevant BIS-recognized laboratory"],
            "documents": ["Laboratory test report"],
            "certification": {"scheme": "Product Certification", "steps": ["Select laboratory", "Complete testing", "Retain report"]},
            "compliance_roadmap": [],
            "related_standards": [],
            "official_source": {"title": "BIS Laboratory Services", "url": "https://www.bis.gov.in/"},
            "next_action": "Identify a BIS-recognized laboratory for the applicable product standard.",
            "trust_status": "VERIFIED_ONLY",
        })
=======
            score = 0
            if std_id and std_id in question_lower:
                score = 1000
            elif std_id:
                std_norm = re.sub(r"[^a-z0-9]", "", std_id)
                if std_norm and (std_norm in question_norm or question_norm in std_norm):
                    score = 950
            elif product_key and product_key in question_lower:
                score = 500
            elif normalized_key and normalized_key in question_lower:
                score = 400
            else:
                if len(significant_words) >= 3:
                    score = 300 + len(significant_words)
                elif len(significant_words) == 2:
                    score = 200 + len(significant_words)
                elif len(non_generic) == 1 and all(len(w) >= 5 for w in non_generic):
                    score = 150
>>>>>>> Stashed changes

    if "certif" in question_lower:
        return response_aliases({
            "intent": "CERTIFICATION_GUIDANCE",
            "product": "Certification",
            "standard_id": "N/A",
            "standard_title": "BIS Certification Guidance",
            "direct_answer": "To obtain BIS certification, a manufacturer applies to BIS, submits the product for testing, and receives approval based on compliance with the relevant Indian Standard.",
            "why_this_applies": "Certification validates conformity to the relevant BIS standard.",
            "requirements": ["Application and documentation", "Testing evidence", "Compliance review"],
            "safety_requirements": [],
            "testing": ["Product testing as required by the standard"],
            "documents": ["Application form", "Factory details", "Test reports"],
            "certification": {"scheme": "BIS Product Certification", "steps": ["Apply", "Test", "Audit", "License"]},
            "compliance_roadmap": [],
            "related_standards": [],
            "official_source": {"title": "BIS Certification", "url": "https://www.bis.gov.in/"},
            "next_action": "Prepare the required documents and testing evidence for BIS certification.",
            "trust_status": "VERIFIED_ONLY",
        })

    compact_question = normalize_lookup(question_lower)
    best_match = None
    best_score = 0

    for product_key, data in KNOWLEDGE_BASE.items():
        std_id = str(data.get("standard_id", "")).lower()
        product_name = str(data.get("product", "")).lower()
        normalized_product = normalize_lookup(product_key)
        normalized_standard = normalize_lookup(std_id)
        score = 0

        if std_id and std_id in question_lower:
            score = 1000
        elif std_id:
            std_norm = normalize_lookup(std_id)
            if std_norm and (std_norm in compact_question or compact_question in std_norm):
                score = 950

        if product_name and product_name in question_lower:
            score = max(score, 500)
        if normalized_product and normalized_product in compact_question:
            score = max(score, 400)

        if product_key and product_key in question_lower:
            score = max(score, 300)

        words_in_question = set(re.findall(r"[a-z0-9]+", question_lower))
        product_words = set(re.findall(r"[a-z0-9]+", product_name))
        overlap = len(words_in_question & product_words)
        if overlap > 0:
            score = max(score, 200 + overlap)

        if score > best_score:
            best_score = score
            best_match = data

    if best_match:
        return response_aliases(best_match)

<<<<<<< Updated upstream
=======
    # 2. Fallback: Query Ujjwala's RAG AI engine
>>>>>>> Stashed changes
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
                "certification": {"scheme": "Standard BIS Certification Scheme", "steps": ["Submit Application", "Sample Testing", "Factory Inspection", "Grant of License"]},
                "compliance_roadmap": [
                    {"step": 1, "title": "Submit Application", "status": "completed"},
                    {"step": 2, "title": "Sample Testing", "status": "in_progress"},
                    {"step": 3, "title": "Factory Inspection", "status": "pending"},
                    {"step": 4, "title": "Grant of License", "status": "pending"},
                ],
                "related_standards": [],
                "official_source": {"title": primary_source.get("standard", "BIS Official Portal"), "url": primary_source.get("url") or "https://www.bis.gov.in"},
                "next_action": "Review compliance details generated by assistant.",
                "trust_status": "AI_GENERATED",
            }
        except Exception as e:
            print(f"[ERROR] RAG processing failed: {e}")

<<<<<<< Updated upstream
    return unsupported_response()
=======
    # 3. Default Unsupported Response
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
>>>>>>> Stashed changes


def get_standard_by_id(standard_id: str) -> dict:
    if not standard_id:
        return unsupported_response()

    lookup = str(standard_id).strip()
    lookup_key = standard_base_key(lookup)

    for item in KNOWLEDGE_BASE.values():
        item_standard = str(item.get("standard_id", ""))
        if standard_base_key(item_standard) == lookup_key:
            return response_aliases(item)

    direct = KNOWLEDGE_BASE.get(lookup.lower()) or KNOWLEDGE_BASE.get(normalize_lookup(lookup))
    if direct:
        return response_aliases(direct)

    return unsupported_response(f"I do not have verified BIS information for {standard_id}.")