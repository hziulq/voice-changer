@echo off
setlocal

echo [1/5] Checking Python...
python --version
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found. Install from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2/5] Checking Docker...
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker Desktop is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

cd /d "%~dp0"
echo [3/5] Working directory: %CD%

if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b 1
    )
)

echo [4/5] Installing dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] pip install failed. See errors above.
    pause
    exit /b 1
)

echo [5/5] Starting Python API on port 8000...
start "" http://localhost:8080/voice-changer

.venv\Scripts\python.exe -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000
if %ERRORLEVEL% neq 0 (
    echo [ERROR] uvicorn failed to start. See errors above.
    pause
)

endlocal
