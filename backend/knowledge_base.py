import os
import pandas as pd
from pathlib import Path

# Path to Rohan's 25 Products Excel file
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "BIS_Intelligence_Rohan_25_Products_VERIFIED_UPDATED.xlsx"

def load_excel_knowledge_base():
    """
    Parses Rohan's 25-product Excel dataset and structures it into
    the JSON contract expected by the frontend /chat endpoint.
    """
    if not DATA_PATH.exists():
        print(f"[WARNING] File not found at {DATA_PATH}. Knowledge base initialized as empty.")
        return {}

    try:
        # Load Excel sheet
        df = pd.read_excel(DATA_PATH)
        
        kb = {}

        for _, row in df.iterrows():
            product_name = str(row.get("Product", "")).strip()
            is_number = str(row.get("IS Number", "")).strip()

            if not product_name or pd.isna(row.get("Product")):
                continue

            # Keys for primary lookup
            key = product_name.lower()

            # Helper function to split text into clean list items
            def parse_list(val):
                if pd.isna(val) or not val:
                    return []
                val_str = str(val).strip()
                # Split by semicolon, newline, or bullet points
                items = [i.strip(" •\t\r\n-") for i.splitlines() for i in val_str.split(";")]
                return [i for i in items if i]

            # Build standard steps list from Rohan's step columns
            cert_steps = []
            for i in range(1, 6):
                step_val = row.get(f"Certification Process — Step {i}")
                if pd.notna(step_val) and str(step_val).strip():
                    cert_steps.append(str(step_val).strip())

            # Fallback if no specific steps listed
            if not cert_steps:
                cert_steps = [
                    "Factory & Lab Setup",
                    "Documentation Submission",
                    "Factory Audit & Sample Testing",
                    "Grant of License"
                ]

            # Map to expected API response payload
            kb[key] = {
                "intent": "MANUFACTURING_GUIDANCE",
                "product": product_name,
                "standard_id": is_number,
                "standard_title": str(row.get("Standard Title", "")),
                "direct_answer": f"For {product_name}, compulsory BIS certification under {is_number} applies ({row.get('Standard Status / Current Version', 'Active')}).",
                "why_this_applies": str(row.get("Scope / Applicability", "Mandatory compliance for Indian manufacturing and imports.")),
                "requirements": parse_list(row.get("Current Requirements from Rohan", "")) or parse_list(row.get("Construction Requirements", "")),
                "safety_requirements": parse_list(row.get("Detailed Safety Requirements", "")) or parse_list(row.get("Current Safety from Rohan", "")),
                "testing": parse_list(row.get("Current Tests from Rohan", "")) or parse_list(row.get("Test Name", "")),
                "documents": parse_list(row.get("Required Documents / Inputs", "")),
                "certification": {
                    "scheme": str(row.get("Certification Scheme / Route (VERIFIED)", "Scheme-I (ISI Mark)")),
                    "steps": cert_steps
                },
                "compliance_roadmap": [
                    {"step": idx + 1, "title": step_name, "status": "completed" if idx == 0 else ("in_progress" if idx == 1 else "pending")}
                    for idx, step_name in enumerate(cert_steps)
                ],
                "related_standards": parse_list(row.get("Related Standards", "")),
                "official_source": {
                    "title": str(row.get("Official Source Title", "BIS Manakonline Portal")),
                    "url": str(row.get("Official Source URL", ""))
                },
                "next_action": f"Review construction and testing limits under {is_number}.",
                "trust_status": str(row.get("Verification Status", "VERIFIED_ONLY"))
            }

        print(f"[SUCCESS] Successfully loaded {len(kb)} verified products into Knowledge Base.")
        return kb

    except Exception as e:
        print(f"[ERROR] Failed to load Excel knowledge base: {e}")
        return {}

# Load on startup
KNOWLEDGE_BASE = load_excel_knowledge_base()

def query_knowledge_base(question: str, mode: str = "industry") -> dict:
    """
    Lookup matching product or IS Number from Rohan's loaded dataset.
    """
    question_lower = question.lower()

    # Search by product name or IS Number
    for product_key, data in KNOWLEDGE_BASE.items():
        if product_key in question_lower or data["standard_id"].lower() in question_lower:
            return data

    # Fallback for out-of-scope products
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