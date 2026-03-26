@echo off
echo ==================================================
echo Starting FinSight India with Python 3.11
echo ==================================================
echo.

:: 1. Try py launcher first
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] "py -3.11" was not found. Falling back to default "python".
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py -3.11
)

:: 2. Create the virtual environment if it doesn't exist
if not exist "venv\Scripts\python.exe" (
    echo [i] Creating new Python Virtual Environment...
    %PYTHON_CMD% -m venv venv
) else (
    echo [i] Virtual Environment found.
)

:: 3. Activate the environment
call venv\Scripts\activate.bat

:: 4. Ensure dependencies are installed
echo [i] Checking dependencies...
pip install -r requirements.txt --quiet

:: 5. Start the app using the python module directly
echo [i] Launching Dashboard...
python -m streamlit run ui\app.py
