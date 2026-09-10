<<<<<<< Updated upstream
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
=======
import re
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
>>>>>>> Stashed changes
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import create_access_token, hash_password, verify_password
from database import engine, get_db
from knowledge_base import KNOWLEDGE_BASE, get_standard_by_id, query_knowledge_base
import models

app = FastAPI(
    title="BIS AI Assistant API",
    description="Backend API for BIS Product Certification & Intelligence Assistant",
    docs_url="/docs",
    redoc_url="/redoc"
)

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

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED, tags=["Authentication"])
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


@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
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


# --- HELPER FUNCTIONS ---

def clean_query(user_input: str) -> str:
    """Strips common conversational filler words to extract core product keywords."""
    if not user_input:
        return ""
    stop_words = {
        "how", "do", "i", "certify", "is", "there", "a", "an", "for", 
        "what", "the", "mark", "bis", "standard", "quality", "certification", 
        "process", "requirements", "compliance", "give", "me", "tell", "about"
    }
    # Clean non-alphanumeric characters except spaces
    cleaned = re.sub(r"[^\w\s]", "", user_input.lower())
    words = cleaned.split()
    filtered = [w for w in words if w not in stop_words]
    
    # Return cleaned string if words remain, otherwise return original input
    return " ".join(filtered) if filtered else user_input


# --- CHAT & COMPLIANCE ENDPOINTS ---

@app.post("/chat", tags=["Assistant"])
def chat_endpoint(request: ChatRequest):
    try:
        raw_question = request.question.strip() if request.question else ""
        cleaned_q = clean_query(raw_question)
        
        # Query Knowledge Base using both cleaned input and fallback to raw input
        kb_result = query_knowledge_base(cleaned_q or raw_question, mode=request.mode or "consumer")

        # Fallback query attempt with original text if unsupported
        if kb_result.get("intent") == "UNSUPPORTED" and cleaned_q != raw_question:
            kb_result = query_knowledge_base(raw_question, mode=request.mode or "consumer")

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
            "safety_requirements": kb_result.get("safety_requirements", []),
            "testing": kb_result.get("testing", []),
            "documents": kb_result.get("documents", []),
            "certification": kb_result.get("certification", {}),
            "compliance_roadmap": kb_result.get("compliance_roadmap", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

<<<<<<< Updated upstream
@app.get("/standards")
def list_standards():
    standards = []
    seen = set()
    for item in KNOWLEDGE_BASE.values():
        key = item.get("standard_id")
        if not key or key in seen:
            continue
        seen.add(key)
        standards.append({
            "id": key,
            "product": item.get("product", ""),
            "purpose": item.get("standard_title", ""),
            "source": (item.get("official_source") or {}).get("url", ""),
        })
    return {"standards": standards}

@app.get("/standard/{standard_id:path}")
def standard_lookup(standard_id: str):
    item = get_standard_by_id(standard_id)
    if item.get("intent") == "UNSUPPORTED":
        raise HTTPException(status_code=404, detail="Standard not found in knowledge base")
    return item

@app.get("/certification")
def certification_service():
    return {"service": "BIS Product Certification", "steps": ["Prepare documents", "Complete testing", "Submit application", "Factory assessment", "Grant of licence"]}

@app.get("/hallmarking")
def hallmarking_service():
    return {"service": "BIS Hallmarking", "guidance": "Use registered jewellers and authorised assaying and hallmarking centres."}

@app.get("/labs")
def laboratory_service():
    return {"service": "BIS Recognized Laboratories", "guidance": "Select a laboratory relevant to the applicable Indian Standard."}

@app.post("/documents/analyze")
async def analyze_document(file: UploadFile = File(...)):
    allowed_types = {".pdf": "PDF", ".doc": "Word", ".docx": "Word", ".xls": "Excel", ".xlsx": "Excel"}
    suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    file_type = allowed_types.get(suffix)
    if not file_type:
        raise HTTPException(status_code=415, detail="Supported document types are PDF, Excel, and Word")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded document is empty")
    return {
        "filename": file.filename,
        "file_type": file_type,
        "analyzed": True,
        "matched_standard": "IS 2347:2023",
        "issues": [],
        "results": "Document received and analyzed for BIS compliance indicators.",
        "understandable": True,
    }

@app.post("/compliance-plan")
=======

@app.post("/compliance-plan", tags=["Compliance"])
>>>>>>> Stashed changes
def generate_compliance_plan(request: ComplianceRequest):
    query_target = request.standard_id or request.product_name
    kb_item = get_standard_by_id(query_target)
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


# --- STANDARDS INDEX ---

@app.get("/standards", tags=["Standards"])
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


@app.get("/standard/{standard_id}", tags=["Standards"])
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


# --- BIS SERVICE INFORMATIONAL ENDPOINTS ---

@app.get("/certification", tags=["Information"])
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


@app.get("/hallmarking", tags=["Information"])
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


@app.get("/labs", tags=["Information"])
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


# --- FEEDBACK ENDPOINT ---

@app.post("/feedback", tags=["Feedback"])
def submit_feedback(request: FeedbackRequest):
    print(f"[FEEDBACK] Question: {request.question} | Rating: {request.rating}/5")
    return {"message": "Feedback recorded successfully", "rating": request.rating}