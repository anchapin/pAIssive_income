@echo off
echo Running GitHub Actions locally...

REM Parse command-line arguments
set WORKFLOW=.github/workflows/simple-lint.yml
set JOB=lint
set FILE=
set PLATFORM=

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
shift
goto parse_args

:run
echo.
echo Running GitHub Actions with Act...
echo Workflow: %WORKFLOW%
echo Job: %JOB%
if not "%FILE%"=="" echo File: %FILE%
if not "%PLATFORM%"=="" echo Platform: %PLATFORM%
echo.

if "%FILE%"=="" (
    if "%PLATFORM%"=="" (
        python run_github_actions_locally.py --workflow %WORKFLOW% --job %JOB%
    ) else (
        python run_github_actions_locally.py --workflow %WORKFLOW% --job %JOB% --platform "%PLATFORM%"
    )
) else (
    if "%PLATFORM%"=="" (
        python run_github_actions_locally.py --workflow %WORKFLOW% --job %JOB% --file %FILE%
    ) else (
        python run_github_actions_locally.py --workflow %WORKFLOW% --job %JOB% --file %FILE% --platform "%PLATFORM%"
    )
)

echo.
echo Done!
