@echo off
echo ============================================
echo   BIS Intelligence - Setup Script
echo ============================================
echo.

cd /d "%~dp0"

REM Check if .env exists
if not exist ".env" (
    echo [!] No .env file found.
    echo [*] Copying .env.example to .env ...
    copy .env.example .env
    echo [!] IMPORTANT: Open .env and add your GEMINI_API_KEY before continuing.
    echo     Get one free at: https://aistudio.google.com/apikey
    echo.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo [1/5] Installing Python dependencies ...
python -m pip install -r backend\requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)
echo      Done.
echo.

echo [2/5] Installing frontend dependencies ...
cd frontend
call npm install
cd ..
echo      Done.
echo.

echo [3/5] Building vector database (FAISS index) ...
python ai\rag.py build
if errorlevel 1 (
    echo [WARNING] Vector DB build failed. RAG fallback may not work.
    echo           Make sure GEMINI_API_KEY is set in .env
)
echo.

echo [4/5] Starting FastAPI backend on http://127.0.0.1:8000 ...
echo       Swagger docs: http://127.0.0.1:8000/docs
start cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo [5/5] Starting Next.js frontend on http://localhost:3000 ...
start cmd /k "cd frontend && npm run dev"

echo.
echo ============================================
echo   Both servers are starting!
echo ============================================
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:3000
echo   Swagger:  http://127.0.0.1:8000/docs
echo ============================================
echo.
pause
