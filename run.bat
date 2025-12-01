@echo off
setlocal

:: Configuration
set "PYTHON_CMD=python"
set "VENV_DIR=venv"
set "REQUIREMENTS_FILE=requirements.txt"
set "APP_SCRIPT=server.py"

echo Starting AURA System Setup...

:: 1. Check for Python
where %PYTHON_CMD% >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: %PYTHON_CMD% could not be found.
    echo Please install Python - preferably 3.12 - to proceed.
    pause
    exit /b 1
)

:: 2. Check/Create Virtual Environment
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv %VENV_DIR%
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
    
    :: Activate and Install Dependencies
    call "%VENV_DIR%\Scripts\activate.bat"
    echo Installing dependencies...
    python -m pip install --upgrade pip
    if exist "%REQUIREMENTS_FILE%" (
        pip install -r "%REQUIREMENTS_FILE%"
    ) else (
        echo Warning: %REQUIREMENTS_FILE% not found.
    )
) else (
    echo Virtual environment found.
    call "%VENV_DIR%\Scripts\activate.bat"
)

:: Always check for dependency updates
echo Checking for dependency updates...
if exist "%REQUIREMENTS_FILE%" (
    pip install -r "%REQUIREMENTS_FILE%"
)

:: 5. Run Application
echo Starting Application...
echo Dashboard will be available at: http://localhost:8000
echo Press Ctrl+C to stop.
python "%APP_SCRIPT%"

endlocal
