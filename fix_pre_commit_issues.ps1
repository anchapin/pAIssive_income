# Fix trailing whitespace and end-of-file issues
 = @(
    'docs/getting-started.md',
    'docs/faq.md',
    'docs/README.md',
    'dev_tools/build_docs.sh',
    'dev_tools/quick_lint.sh',
    'dev_tools/type_check.sh',
    'dev_tools/deps_audit.sh',
    'docs/documentation-guide.md',
    'dev_tools/security_audit.sh',
    'dev_tools/__init__.py',
    'dev_tools/health_check.py'
)

foreach ( in ) {
    if (Test-Path ) {
        # Read content, trim trailing whitespace, ensure ending newline
         = Get-Content -Raw
         =  -replace '[ \t]+$', '' -replace '\r', ''
        if ( -and -not .EndsWith(\

\)) {
             =  + \
\
        }
        # Write content back to the file
         | Set-Content -NoNewline
        Write-Host \Fixed:
\
    } else {
        Write-Host \File
not
found:
\
    }
}
