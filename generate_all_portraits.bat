@echo off
REM Convenience script to generate all portraits on Windows
REM Usage: generate_all_portraits.bat [api_type]
REM Example: generate_all_portraits.bat openai

SET API_TYPE=%1
IF "%API_TYPE%"=="" SET API_TYPE=openai

echo 🎨 Generating all portraits using %API_TYPE%...
echo.

REM Check if API key is set
IF "%API_TYPE%"=="openai" (
    IF "%OPENAI_API_KEY%"=="" (
        echo ❌ OPENAI_API_KEY not set!
        echo    Run: set OPENAI_API_KEY=sk-...
        exit /b 1
    )
)

IF "%API_TYPE%"=="stability" (
    IF "%STABILITY_API_KEY%"=="" (
        echo ❌ STABILITY_API_KEY not set!
        echo    Run: set STABILITY_API_KEY=sk-...
        exit /b 1
    )
)

IF "%API_TYPE%"=="replicate" (
    IF "%REPLICATE_API_KEY%"=="" (
        echo ❌ REPLICATE_API_KEY not set!
        echo    Run: set REPLICATE_API_KEY=r8_...
        exit /b 1
    )
)

REM Generate
python scripts\generate_portraits.py --api %API_TYPE% --category all

echo.
echo ✅ Done! Check the portraits\ directory
