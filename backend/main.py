"""
BIS AI Assistant — Backend (v3)
Riya's module: Backend + BIS Service APIs.
 
NEW IN THIS VERSION: the BIS knowledge base is now loaded from Rohan's
spreadsheet in the shared `data/` folder, instead of being hardcoded here.
Whenever he updates that file and you restart the server, your backend
automatically picks up the latest data — no manual copy-pasting needed.
 
Run this file with:
    python -m uvicorn main:app --reload
 
Then test at:
    http://127.0.0.1:8000/docs
"""
 
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
 
# -----------------------------------------------------------------------
# 1) Create the app
# -----------------------------------------------------------------------
app = FastAPI(title="BIS AI Assistant - Backend")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
# -----------------------------------------------------------------------
# 2) Data shapes (Pydantic models)
# -----------------------------------------------------------------------
 
class ChatRequest(BaseModel):
    question: str
    mode: str = "consumer"  # "consumer" or "industry"
 
 
class ChatResponse(BaseModel):
    answer: str
    standard: str
    source: str
    references: str
    mode: str
 
 
class FeedbackRequest(BaseModel):
    question: str
    rating: int  # e.g. 1-5
 
 
# -----------------------------------------------------------------------
# 3) Load the BIS knowledge base from Rohan's file in data/
# -----------------------------------------------------------------------
# Expected file location (relative to this backend/ folder):
#     ../data/bis_data.xlsx
#
# Expected columns (matching what Rohan has been sending):
#     Products, IS NO., Requirements, Safety, Tests, Certification,
#     Scheme, BIS Service, Source, Purpose, URL
#
# If the file is missing, badly formatted, or a column is renamed,
# this falls back to a small built-in backup dataset so the server
# still starts and /chat still works — just with less coverage.
 
DATA_FILE_PATH = Path(__file__).parent.parent / "data" / "bis_data.xlsx"
 
# Small built-in backup — used ONLY if Rohan's file can't be loaded.
FALLBACK_BIS_DATA = {
    "IS2347": {
        "id": "IS2347",
        "product": "Pressure Cooker",
        "requirements": "Material thickness, Capacity, Gaskets, Pressure regulator function",
        "safety": "Safety plug, Burst pressure compliance, Thermal resistance",
        "testing": "Hydrostatic pressure test, air pressure test, Burst test, Safety device operating test",
        "certification": "ISI Mark",
        "scheme": "Scheme 1 (Marking scheme)",
        "bis_service": "CRS/ISI",
        "purpose": "Standardized domestic pressure cookers for safe cooking under pressure",
        "source": "BIS",
        "url": "https://www.bis.gov.in/revised-pm-is-2347/",
    },
}
 
 
def load_bis_data() -> dict:
    """
    Reads Rohan's spreadsheet from data/bis_data.xlsx and converts it into
    the dictionary format the rest of this file expects: { "IS2347": {...} }
    """
    if not DATA_FILE_PATH.exists():
        print(f"[WARNING] {DATA_FILE_PATH} not found — using fallback data. "
              f"Ask Rohan to add his file at data/bis_data.xlsx")
        return FALLBACK_BIS_DATA
 
    try:
        df = pd.read_excel(DATA_FILE_PATH)
        df.columns = [c.strip() for c in df.columns]  # clean up stray spaces in headers
 
        data = {}
        for _, row in df.iterrows():
            standard_id = str(row["IS NO."]).strip().replace(" ", "").upper()
            data[standard_id] = {
                "id": standard_id,
                "product": str(row["Products"]).strip(),
                "requirements": str(row["Requirements"]).strip(),
                "safety": str(row["Safety"]).strip(),
                "testing": str(row["Tests"]).strip(),
                "certification": str(row["Certification"]).strip(),
                "scheme": str(row["Scheme"]).strip(),
                "bis_service": str(row["BIS Service"]).strip(),
                "purpose": str(row["Purpose"]).strip(),
                "source": str(row["Source"]).strip(),
                "url": str(row["URL"]).strip(),
            }
 
        if not data:
            print("[WARNING] Data file loaded but contained no rows — using fallback data.")
            return FALLBACK_BIS_DATA
 
        print(f"[INFO] Loaded {len(data)} standards from {DATA_FILE_PATH}")
        return data
 
    except Exception as e:
        print(f"[WARNING] Failed to load {DATA_FILE_PATH}: {e} — using fallback data.")
        return FALLBACK_BIS_DATA
 
 
def build_keyword_map(data: dict) -> dict:
    """
    Builds a simple keyword -> standard-id lookup from product names,
    e.g. "pressure cooker" -> "IS2347". This stands in for Ujwala's real
    product-identification step until her AI pipeline is ready.
    """
    keywords = {}
    for standard_id, info in data.items():
        product_name = info["product"].lower()
        keywords[product_name] = standard_id
        for word in product_name.split():
            if len(word) > 3 and word not in ("with", "domestic", "electric"):
                keywords.setdefault(word, standard_id)
    return keywords
 
 
BIS_DATA = load_bis_data()
PRODUCT_KEYWORDS = build_keyword_map(BIS_DATA)
 
 
# -----------------------------------------------------------------------
# 4) Placeholder for Ujwala's AI module
# -----------------------------------------------------------------------
# THIS IS THE FUNCTION TO REPLACE ONCE HER REAL AI/RAG PIPELINE IS READY.


def get_ai_answer_MOCK(question: str, mode: str) -> dict:
    question_lower = question.lower()

    if any(term in question_lower for term in ["hallmark", "hallmarking"]):
        return {
            "answer": (
                "BIS hallmarking is the process of certifying the purity of gold and silver jewelry. "
                "Consumers should look for the BIS hallmark, HUID number, and the jeweller's registration details. "
                "Official BIS information on hallmarking is available through the BIS hallmarking scheme."
            ),
            "standard": "N/A",
            "source": "Bureau of Indian Standards (BIS)",
            "references": "https://www.bis.gov.in/hallmarking/",
        }

    if any(term in question_lower for term in ["laboratory", "lab", "testing laboratory", "testing lab"]):
        return {
            "answer": (
                "For product testing and certification, manufacturers should use BIS-recognized or accredited testing laboratories. "
                "You can identify relevant testing facilities through the official BIS laboratory directory and the specific product certification guidance."
            ),
            "standard": "N/A",
            "source": "Bureau of Indian Standards (BIS)",
            "references": "https://www.bis.gov.in/",
        }

    if any(term in question_lower for term in ["certification", "certify", "isi mark"]):
        return {
            "answer": (
                "To obtain BIS certification, a manufacturer typically applies to BIS, submits the product for testing, and then receives approval based on compliance with the relevant Indian Standard. "
                "The certification outcome is usually the BIS/ISI mark for the product, subject to compliance and scheme requirements."
            ),
            "standard": "N/A",
            "source": "Bureau of Indian Standards (BIS)",
            "references": "https://www.bis.gov.in/",
        }

    matched_id = None
    for keyword, standard_id in PRODUCT_KEYWORDS.items():
        if keyword in question_lower:
            matched_id = standard_id
            break

    if matched_id:
        data = BIS_DATA[matched_id]
        answer = (
            f"For {data['product']}, the applicable standard is {data['id']}. "
            f"Requirements: {data['requirements']}. "
            f"Safety: {data['safety']}. "
            f"Testing: {data['testing']}. "
            f"Certification: {data['certification']} under {data['scheme']}."
        )
        return {
            "answer": answer,
            "standard": data["id"],
            "source": data["source"],
            "references": data["url"],
        }

    return {
        "answer": (
            "I can assist with Indian Standards and BIS-related services. "
            "I do not have verified BIS information for this query."
        ),
        "standard": "N/A",
        "source": "N/A",
        "references": "N/A",
    }
 
 
# -----------------------------------------------------------------------
# 5) Endpoints
# -----------------------------------------------------------------------
 
@app.get("/")
def root():
    """Health check — also reports how many standards are currently loaded."""
    return {
        "status": "BIS Assistant backend is running",
        "standards_loaded": len(BIS_DATA),
    }
 
 
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    question = request.question.strip()
    result = get_ai_answer_MOCK(question, request.mode)
 
    return ChatResponse(
        answer=result["answer"],
        standard=result["standard"],
        source=result["source"],
        references=result["references"],
        mode=request.mode,
    )
 
 
@app.get("/standards")
def list_standards():
    return {
        "standards": [
            {"id": v["id"], "product": v["product"], "purpose": v["purpose"]}
            for v in BIS_DATA.values()
        ]
    }
 
 
@app.get("/standard/{standard_id}")
def get_standard(standard_id: str):
    data = BIS_DATA.get(standard_id.upper())
    if not data:
        raise HTTPException(status_code=404, detail=f"Standard '{standard_id}' not found")
    return data
 
 
@app.get("/certification")
def certification_info():
    return {
        "what_is_it": "BIS certification (ISI mark) confirms a product meets the relevant Indian Standard.",
        "process": "Apply to BIS, submit product for testing at a recognized lab, receive license upon compliance.",
        "source": "Bureau of Indian Standards (BIS) — Certification Scheme",
    }
 
 
@app.get("/hallmarking")
def hallmarking_info():
    return {
        "what_is_it": "BIS hallmarking certifies the purity of gold/silver jewelry sold in India.",
        "consumer_guidance": "Look for the BIS hallmark, HUID number, and jeweler's registration before purchase.",
        "source": "Bureau of Indian Standards (BIS) — Hallmarking Scheme",
    }
 
 
@app.get("/labs")
def labs_info():
    return {
        "guidance": "BIS-recognized testing laboratories can be located via the official BIS laboratory directory.",
        "source": "Bureau of Indian Standards (BIS) — Recognized Laboratories",
    }
 
 
@app.post("/feedback")
def feedback_endpoint(request: FeedbackRequest):
    return {"status": "received", "question": request.question, "rating": request.rating}
 