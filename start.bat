@echo off
echo Starting BIS Intelligence ...
echo.

cd /d "%~dp0"

rem ---- Detect whether a port is already in use (helper) ----
set "BACKEND_UP=no"
set "FRONTEND_UP=no"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /r /c:":8000 .*LISTENING"') do set BACKEND_UP=yes
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /r /c:":3000 .*LISTENING"') do set FRONTEND_UP=yes

if "%BACKEND_UP%"=="no" (
    echo [1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...
    start cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"
    timeout /t 3 /nobreak >nul
) else (
    echo [1/2] Backend is already running on http://127.0.0.1:8000 - skipping.
)

if "%FRONTEND_UP%"=="no" (
    echo [2/2] Starting Next.js frontend on http://localhost:3000 ...
    start cmd /k "cd frontend && npm run dev"
) else (
    echo [2/2] Frontend is already running on http://localhost:3000 - skipping.
)

echo.
echo   Backend:  http://127.0.0.1:8000   (Swagger: http://127.0.0.1:8000/docs)
echo   Frontend: http://localhost:3000
echo.
echo NOTE: If the frontend shows port 3001, close the old window and run start.bat again.
echo.
pause