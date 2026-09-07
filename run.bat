@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo   🧹 Shared Household Chore Manager - Dev Server
echo ========================================================
echo.

where uv >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [INFO] Running server with uv...
    uv run python manage.py runserver %*
    goto end
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [INFO] Running server with Windows Python launcher (py)...
    py manage.py runserver %*
    goto end
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [INFO] Running server with python...
    python manage.py runserver %*
    goto end
)

echo [ERROR] Python or uv was not found in your PATH.
echo Please ensure Python or uv is installed and accessible.
pause

:end
endlocal
