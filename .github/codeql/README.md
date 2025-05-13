# CodeQL Configuration

This directory contains configuration files for GitHub's CodeQL analysis tool, which is part of GitHub Advanced Security.

## Files

- `codeql-javascript-config.yml`: Configuration for JavaScript/TypeScript analysis
- `codeql-python-config.yml`: Configuration for Python analysis
- `codeql-config-macos.yml`: Combined configuration for macOS platform
- `codeql-config-ubuntu.yml`: Combined configuration for Ubuntu platform
- `codeql-config-windows.yml`: Combined configuration for Windows platform
- `javascript-security-queries.qls`: Custom query suite for JavaScript/TypeScript security analysis
- `python-security-queries.qls`: Custom query suite for Python security analysis

## Workflow

The CodeQL analysis is configured in the `.github/workflows/codeql.yml` workflow file. Additionally, the `.github/workflows/consolidated-ci-cd.yml` workflow also includes CodeQL analysis for backward compatibility. These workflows:

1. Runs on push to main branches, pull requests to main branches, and on a weekly schedule (Monday at 4 AM UTC)
2. Performs separate analysis for JavaScript/TypeScript and Python
3. Uses the configuration files in this directory to customize the analysis
4. Caches CodeQL databases to speed up subsequent analyses
5. Installs dependencies for better analysis results
6. Uploads SARIF results as artifacts for later review

## Configuration Options

The configuration files include:

- **Paths**: Specify which files to include in the analysis
- **Paths-ignore**: Specify which files to exclude from the analysis
- **Queries**: Specify which query suites to run
- **Query filters**: Filter out specific queries or categories of queries
- **Database settings**: Configure database extraction parameters
- **Trap-for-errors**: Configure error handling during extraction

## Performance Optimizations

The CodeQL configuration includes several performance optimizations:

1. **Caching**: CodeQL databases are cached to speed up subsequent analyses
2. **Path exclusions**: Generated files, tests, and other non-essential code are excluded
3. **Query filtering**: Low-precision queries are excluded to reduce noise
4. **Concurrency limits**: Prevents multiple CodeQL analyses from running simultaneously
5. **Resource limits**: Sets limits on file size, lines of code, and AST nodes to analyze

## Security Focus

The custom query suites (`javascript-security-queries.qls` and `python-security-queries.qls`) focus on high-impact security vulnerabilities, including:

- Injection vulnerabilities (SQL, command, code, etc.)
- Cross-site scripting (XSS)
- Insecure cryptography
- Authentication and authorization issues
- Sensitive data exposure
- Server-side request forgery
- And many more

## Customizing

To customize the CodeQL analysis:

1. Modify the configuration files in this directory
2. Update the workflow file if needed
3. Test the changes by manually triggering the workflow
4. Review the SARIF results to ensure the changes are effective

## Troubleshooting

If you encounter issues with the CodeQL analysis:

1. Check the workflow logs for errors
2. Verify that the configuration files are valid YAML
3. Ensure that the query suites reference valid queries
4. Try running the analysis with fewer queries or path exclusions
5. Increase the timeout if the analysis is timing out

## References

- [CodeQL documentation](https://codeql.github.com/docs/)
- [GitHub Advanced Security documentation](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/configuring-code-scanning)
- [CodeQL query suites](https://codeql.github.com/codeql-query-help/)
- [CodeQL query language reference](https://codeql.github.com/docs/ql-language-reference/)
- [CodeQL standard libraries](https://codeql.github.com/docs/codeql-language-guides/)
