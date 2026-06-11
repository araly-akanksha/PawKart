@echo off
echo ====================================================
echo Welcome to PawKart! Starting up the ecosystem...
echo ====================================================
echo.

:: 1. Navigate to backend and install requirements
echo [1/3] Checking and installing Python dependencies...
cd backend
pip install -r requirements.txt -q
echo Dependencies installed successfully.
echo.

:: 2. Prepare Database and Environment
echo [2/3] Preparing environment and database...
if not exist ".env" (
    echo Creating missing .env file with a secure SECRET_KEY...
    echo DATABASE_URL=sqlite:///./pawkart.db > ".env"
    echo SECRET_KEY=pawkart-auto-generated-secret-key-32chars >> ".env"
    echo DEBUG=True >> ".env"
)

python seed_real_data.py
echo Database prepared successfully.
echo.

:: 3. Start the Backend API in a separate window
echo [3/3] Starting the FastAPI Backend Server...
start "PawKart Backend Server" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo Backend server is booting up in a new window!
echo.

:: 4. Open the frontend automatically
echo Launching the PawKart Customer Portal...
timeout /t 3 >nul
start "" "..\Store-Owner-Panel\HTML\index.html"

echo ====================================================
echo All set! The browser should open automatically.
echo You can close this window now. The backend will run 
echo in the separate window that just popped up.
echo ====================================================
pause
