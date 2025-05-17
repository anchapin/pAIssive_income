# Fix trailing whitespace and end-of-file issues
$filesToFix = @(
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

foreach ($file in $filesToFix) {
    if (Test-Path $file) {
        # Read content, trim trailing whitespace, ensure ending newline
        $content = Get-Content -Raw $file
        $content = $content -replace '[ \t]+$', '' -replace '\r', ''
        if ($content -and -not $content.EndsWith("`n")) {
            $content = $content + "`n"
        }
        # Write content back to the file
        $content | Set-Content -NoNewline $file
        Write-Host "Fixed: $file"
    } else {
        Write-Host "File not found: $file"
    }
}
