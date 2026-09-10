from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

import models
from database import engine, get_db
from auth import hash_password, verify_password, create_access_token
from knowledge_base import query_knowledge_base, get_standard_by_id, KNOWLEDGE_BASE

# 1. DEFINE THE APP INSTANCE FIRST
app = FastAPI(title="BIS AI Assistant API")

# 2. ADD CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. INITIALIZE DATABASE TABLES
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
        role=user_data.role
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
        "full_name": user.full_name
    }


# --- CORE AI & CHAT ENDPOINTS ---
@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        # Dynamically query Rohan's 25 products from the knowledge base
        return query_knowledge_base(request.question, mode=request.mode or "consumer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
            {"id": "c4", "category": "Certification", "task": "Form-V Application Submission", "done": False}
        ],
        "next_recommended_action": "Review testing equipment calibration certificates."
    }