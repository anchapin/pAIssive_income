@echo off
echo Running GitHub Actions locally...

if "%1"=="" (
    echo Usage:
    echo   run_github_actions.bat security [--output-dir OUTPUT_DIR]
    echo   run_github_actions.bat lint [--file FILE_PATH]
    echo   run_github_actions.bat test [--path TEST_PATH]
    exit /b 0
)

set COMMAND=%1
shift

if /I "%COMMAND%"=="security" (
    echo Running security scan...
    python run_github_actions_locally.py security %*
) else if /I "%COMMAND%"=="lint" (
    echo Running linting...
    python run_github_actions_locally.py lint %*
) else if /I "%COMMAND%"=="test" (
    echo Running tests...
    python run_github_actions_locally.py test %*
) else (
    echo Unknown command: %COMMAND%
    echo Valid commands: security, lint, test
    exit /b 1
)

echo Done.
