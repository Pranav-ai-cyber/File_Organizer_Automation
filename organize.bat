@echo off
REM ============================================================================
REM File Organizer - Quick Launch Script (Windows)
REM Usage: organize.bat [path] [options]
REM ============================================================================

setlocal enabledelayedexpansion

REM Colors (limited in batch)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

REM Print banner
echo %BLUE%
echo ================================================================
echo          File Organizer - Quick Launch Script
echo ================================================================
echo %NC%

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: Python is not installed or not in PATH%NC%
    echo Please install Python 3.7 or higher from python.org
    pause
    exit /b 1
)

REM Check if file_organizer.py exists
if not exist "%~dp0file_organizer.py" (
    echo %RED%Error: file_organizer.py not found%NC%
    echo Please run this script from the project directory
    pause
    exit /b 1
)

REM Interactive mode if no arguments
if "%~1"=="" (
    echo %YELLOW%Interactive Mode%NC%
    echo.
    
    REM Ask for path
    echo %BLUE%Enter the directory path to organize:%NC%
    set /p "TARGET_PATH=Path (e.g., C:\Users\%USERNAME%\Downloads): "
    
    if "!TARGET_PATH!"=="" (
        echo %RED%Error: No path provided%NC%
        pause
        exit /b 1
    )
    
    REM Check if path exists
    if not exist "!TARGET_PATH!" (
        echo %RED%Error: Directory does not exist: !TARGET_PATH!%NC%
        pause
        exit /b 1
    )
    
    REM Ask for dry run
    echo.
    echo %BLUE%Preview changes first (dry run)? [Y/n]:%NC%
    set /p "DRY_RUN=> "
    
    if /i not "!DRY_RUN!"=="n" (
        echo.
        echo %YELLOW%Running in DRY RUN mode...%NC%
        python "%~dp0file_organizer.py" -p "!TARGET_PATH!" --dry-run
        
        echo.
        echo %BLUE%Proceed with actual organization? [y/N]:%NC%
        set /p "PROCEED=> "
        
        if /i "!PROCEED!"=="y" (
            echo.
            echo %GREEN%Organizing files...%NC%
            python "%~dp0file_organizer.py" -p "!TARGET_PATH!"
        ) else (
            echo %YELLOW%Organization cancelled%NC%
            pause
            exit /b 0
        )
    ) else (
        echo.
        echo %GREEN%Organizing files...%NC%
        python "%~dp0file_organizer.py" -p "!TARGET_PATH!"
    )
    
) else (
    REM Command line mode
    if "%~1"=="--help" goto :show_help
    if "%~1"=="-h" goto :show_help
    
    REM Pass all arguments to Python script
    python "%~dp0file_organizer.py" %*
)

REM Check exit code
if errorlevel 1 (
    echo.
    echo %RED%Operation failed. Check the log file for details.%NC%
    pause
    exit /b 1
) else (
    echo.
    echo %GREEN%Operation completed successfully!%NC%
    pause
    exit /b 0
)

:show_help
echo Usage: organize.bat [OPTIONS]
echo.
echo Common commands:
echo   organize.bat                              - Interactive mode
echo   organize.bat C:\Users\%USERNAME%\Downloads         - Organize Downloads
echo   organize.bat C:\Users\%USERNAME%\Downloads --dry-run - Preview changes
echo   organize.bat C:\Users\%USERNAME%\Downloads -v      - Verbose mode
echo   organize.bat --help                       - Show this help
echo.
pause
exit /b 0