@echo off
REM Script to fix security scan issues
REM Usage: fix_security_scan.bat [scan_results_file]

echo Running security scan fix script...

if "%1"=="" (
    echo No scan results file provided, running with default options
    python fix_security_scan_issues.py --update-config --add-comments --verbose
) else (
    echo Using scan results from %1
    python fix_security_scan_issues.py --scan-results "%1" --update-config --add-comments --verbose
)

echo.
echo Done!
echo.
echo Next steps:
echo 1. Review the changes made to the files
echo 2. Review the updated .gitleaks.toml file
echo 3. Run the security scan again to verify the issues are fixed
echo.
