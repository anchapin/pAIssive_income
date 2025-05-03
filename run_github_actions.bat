@echo off
echo Running GitHub Actions locally...

REM Parse command-line arguments
set WORKFLOW=.github/workflows/local-testing.yml
set JOB=
set FILE=
set PLATFORM=ubuntu-latest
set TEST_PATH=tests/
set LINT_ONLY=
set TEST_ONLY=

:parse_args
if "%~1"=="" goto run
if /i "%~1"=="--workflow" (
    set WORKFLOW=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--job" (
    set JOB=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--file" (
    set FILE=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--platform" (
    set PLATFORM=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--test-path" (
    set TEST_PATH=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--lint-only" (
    set LINT_ONLY=--lint-only
    shift
    goto parse_args
)
if /i "%~1"=="--test-only" (
    set TEST_ONLY=--test-only
    shift
    goto parse_args
)
shift
goto parse_args

:run
echo.
echo Running GitHub Actions with Act...
echo Workflow: %WORKFLOW%
if not "%JOB%"=="" echo Job: %JOB%
if not "%FILE%"=="" echo File: %FILE%
if not "%PLATFORM%"=="" echo Platform: %PLATFORM%
if not "%TEST_PATH%"=="" echo Test Path: %TEST_PATH%
if not "%LINT_ONLY%"=="" echo Lint Only: Yes
if not "%TEST_ONLY%"=="" echo Test Only: Yes
echo.

REM Build the command with all available parameters
set CMD=python run_github_actions_locally.py --workflow %WORKFLOW%

if not "%JOB%"=="" set CMD=%CMD% --job %JOB%
if not "%PLATFORM%"=="" set CMD=%CMD% --platform "%PLATFORM%"
if not "%FILE%"=="" set CMD=%CMD% --file "%FILE%"
if not "%TEST_PATH%"=="" set CMD=%CMD% --test-path "%TEST_PATH%"
if not "%LINT_ONLY%"=="" set CMD=%CMD% %LINT_ONLY%
if not "%TEST_ONLY%"=="" set CMD=%CMD% %TEST_ONLY%

echo Command: %CMD%
%CMD%

echo.
echo Done!
