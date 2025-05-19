@echo off
REM Run pytest with the specified arguments

REM Create security-reports directory
mkdir security-reports 2>nul
echo Created security-reports directory

REM Run pytest with the specified arguments
python -m pytest %*
exit /b %ERRORLEVEL%
