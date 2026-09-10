from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import re

import models
from database import engine, get_db
from auth import hash_password, verify_password, create_access_token
from knowledge_base import query_knowledge_base, get_standard_by_id, KNOWLEDGE_BASE

app = FastAPI(title="BIS AI Assistant API", docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


# --- PYDANTIC SCHEMAS ---

class UserSignup(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "consumer"

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    full_name: str

class ChatRequest(BaseModel):
    question: str
    mode: Optional[str] = "consumer"

class ComplianceRequest(BaseModel):
    product_name: str
    standard_id: Optional[str] = "IS 2347"

class FeedbackRequest(BaseModel):
    question: str
    rating: int


# --- AUTH ENDPOINTS ---

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
    hashed_pwd = hash_password(user_data.password)
    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_pwd,
        role=user_data.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/auth/login", response_model=TokenResponse)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
    }


# --- CORE AI & CHAT ENDPOINTS ---

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        kb_result = query_knowledge_base(request.question, mode=request.mode or "consumer")

        # Map KB fields to what the frontend expects
        official_source = kb_result.get("official_source") or {}
        return {
            "direct_answer": kb_result.get("direct_answer", "No answer found."),
            "answer": kb_result.get("direct_answer", "No answer found."),
            "standard": kb_result.get("standard_id", "IS Standard"),
            "references": official_source.get("url", ""),
            "source": official_source.get("title", "BIS Official Portal"),
            "mode": request.mode or "consumer",
            "product": kb_result.get("product", ""),
            "intent": kb_result.get("intent", "UNKNOWN"),
            "requirements": kb_result.get("requirements", []),
            "testing": kb_result.get("testing", []),
            "certification": kb_result.get("certification", {}),
            "compliance_roadmap": kb_result.get("compliance_roadmap", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compliance-plan")
def generate_compliance_plan(request: ComplianceRequest):
    kb_item = get_standard_by_id(request.standard_id or request.product_name)
    if not kb_item or kb_item.get("intent") == "UNSUPPORTED":
        raise HTTPException(status_code=404, detail="Standard not found in knowledge base")
    return {
        "product": kb_item.get("product", request.product_name),
        "standard_id": kb_item.get("standard_id", request.standard_id),
        "overall_progress_percentage": 25,
        "checklist": [
            {"id": "c1", "category": "Requirements", "task": "Raw Material Verification", "done": True},
            {"id": "c2", "category": "Testing", "task": "Hydrostatic Pressure Test Equipment Calibration", "done": False},
            {"id": "c3", "category": "Documents", "task": "Factory Layout Plan Upload", "done": False},
            {"id": "c4", "category": "Certification", "task": "Form-V Application Submission", "done": False},
        ],
        "next_recommended_action": "Review testing equipment calibration certificates.",
    }


# --- STANDARDS INDEX (used by BisHome.jsx /standards endpoint) ---

@app.get("/standards")
def list_standards():
    standards = []
    seen = set()
    for key, data in KNOWLEDGE_BASE.items():
        std_id = data.get("standard_id", "")
        if std_id and std_id not in seen:
            seen.add(std_id)
            standards.append({
                "id": std_id,
                "product": data.get("product", ""),
                "purpose": data.get("why_this_applies", data.get("direct_answer", "")),
                "url": (data.get("official_source") or {}).get("url", ""),
            })
    return {"standards": standards}

@app.get("/standard/{standard_id}")
def get_standard(standard_id: str):
    data = get_standard_by_id(standard_id)
    if not data or data.get("intent") == "UNSUPPORTED":
        raise HTTPException(status_code=404, detail="Standard not found")
    cert = data.get("certification") or {}
    return {
        "id": re.sub(r"\s+", "", data.get("standard_id", standard_id)),
        "product": data.get("product", ""),
        "purpose": data.get("why_this_applies", ""),
        "requirements": data.get("direct_answer", ""),
        "testing": data.get("testing", []),
        "certification": cert.get("scheme", "BIS Certification"),
        "scheme": cert.get("scheme", "Scheme-I (ISI Mark)"),
        "url": (data.get("official_source") or {}).get("url", ""),
    }


# --- BIS SERVICE ENDPOINTS (used by BisHome.jsx service cards) ---

@app.get("/certification")
def get_certification_info():
    return {
        "what_is_it": (
            "BIS Product Certification (ISI Mark) is a mandatory certification scheme "
            "in India under the Bureau of Indian Standards Act, 2016. It ensures that "
            "products conform to relevant Indian Standards for safety, quality, and performance."
        ),
        "process": (
            "1. Application Submission\n"
            "2. Document Verification by BIS\n"
            "3. Factory Audit & Sample Testing\n"
            "4. Grant of License (ISI Mark)\n"
            "5. Ongoing Surveillance & Renewal"
        ),
        "source": "https://www.bis.gov.in",
    }

@app.get("/hallmarking")
def get_hallmarking_info():
    return {
        "what_is_it": (
            "BIS Hallmarking is the official recording of the purity/caratenage of precious "
            "metals (gold, silver) by BIS-recognized Assaying and Hallmarking Centres. "
            "Since April 2023, hallmarking of gold jewellery has been made mandatory in a "
            "phased manner across India."
        ),
        "process": (
            "1. Jeweller registers with BIS\n"
            "2. Articles sent to A&H Centre\n"
            "3. Assaying (purity testing)\n"
            "4. HUID (Hallmark Unique Identification) is assigned\n"
            "5. Hallmark stamped on the article"
        ),
        "consumer_guidance": (
            "Always buy BIS-hallmarked jewellery. Check for:\n"
            "- BIS logo\n"
            "- Purity grade (22K, 18K, etc.)\n"
            "- HUID number (verify on BIS Care app)\n"
            "- Jeweller's identification mark"
        ),
        "source": "https://www.bis.gov.in/hallmarking",
    }

@app.get("/labs")
def get_labs_info():
    return {
        "guidance": (
            "BIS maintains a list of recognized laboratories for testing products against "
            "relevant Indian Standards. These labs are accredited under ISO/IEC 17025 and "
            "are authorized to conduct testing for BIS certification purposes.\n\n"
            "Key points:\n"
            "- Only BIS-recognized labs can test products for certification\n"
            "- Labs must maintain ISO 17025 accreditation\n"
            "- Test reports from non-recognized labs are not accepted for BIS certification\n"
            "- BIS publishes and updates the list of recognized labs regularly"
        ),
        "source": "https://www.bis.gov.in/recognition-laboratories",
    }


# --- FEEDBACK (used by BisHome.jsx) ---

@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    print(f"[FEEDBACK] Question: {request.question} | Rating: {request.rating}/5")
    return {"message": "Feedback recorded", "rating": request.rating}
