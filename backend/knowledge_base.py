import os
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "BIS_Intelligence_Rohan_25_Products_VERIFIED_UPDATED.xlsx"

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

def query_knowledge_base(question: str, mode: str = "industry") -> dict:
    if not question:
        question = ""
    question_lower = str(question).lower()

    for product_key, data in KNOWLEDGE_BASE.items():
        std_id = str(data.get("standard_id", "")).lower()
        if (product_key and product_key in question_lower) or (std_id and std_id in question_lower):
            return data

    return {
        "intent": "UNSUPPORTED",
        "product": "",
        "standard_id": "",
        "standard_title": "",
        "direct_answer": "No verified BIS standard record was found for this specific query in the active database.",
        "why_this_applies": "",
        "requirements": [],
        "safety_requirements": [],
        "testing": [],
        "documents": [],
        "certification": None,
        "compliance_roadmap": [],
        "related_standards": [],
        "official_source": None,
        "next_action": "Please search for one of the 25 covered products (e.g., Helmet, Toys, Pressure Cooker, Stainless Steel Water Bottle).",
        "trust_status": "UNVERIFIED"
    }

def get_standard_by_id(standard_id: str) -> dict:
    return query_knowledge_base(standard_id)