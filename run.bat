@echo off
setlocal enabledelayedexpansion

set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

if "%1"=="" goto help
if "%1"=="install" goto install
if "%1"=="backend" goto backend
if "%1"=="client1" goto client1
if "%1"=="client2" goto client2
if "%1"=="test" goto test
if "%1"=="init-db" goto init_db
goto help

:install
    echo Installing dependencies...
    if not exist venv\ (
        echo Creating virtual environment...
        python -m venv venv
    )
    call venv\Scripts\activate
    pip install --upgrade pip
    pip install -r backend\requirements-dev.txt
    pip install -r clients\client1\requirements.txt
    pip install -r clients\client2\requirements.txt
    pre-commit install
    echo Done.
    goto end

:backend
    if not exist venv\ ( echo Run 'run.bat install' first & goto end )
    call venv\Scripts\activate
    cd backend
    uvicorn app.main:app --reload --port 8000
    goto end

:client1
    if not exist venv\ ( echo Run 'run.bat install' first & goto end )
    call venv\Scripts\activate
    cd clients\client1
    python main.py
    goto end

:client2
    if not exist venv\ ( echo Run 'run.bat install' first & goto end )
    call venv\Scripts\activate
    cd clients\client2
    python main.py
    goto end

:test
    if not exist venv\ ( echo Run 'run.bat install' first & goto end )
    call venv\Scripts\activate
    cd backend
    pytest
    goto end

:init_db
    echo Creating data directory...
    if not exist data\ mkdir data
    echo SQLite database will be created on first run
    goto end

:help
    echo Usage: run.bat [command]
    echo.
    echo Commands:
    echo   install      - Create venv and install all dependencies
    echo   init-db      - Create data directory for SQLite
    echo   backend      - Start FastAPI server on port 8000
    echo   client1      - Start Client1 (Designer)
    echo   client2      - Start Client2 (Calculator)
    echo   test         - Run all tests
    goto end

:end
    pause