# Python Syntax Error Fixer

This tool automatically fixes common syntax errors in Python files. It's designed to help clean up code and prevent GitHub Actions workflow failures due to syntax issues.

## Features

The script can automatically fix:

1. **Duplicate Lines**: Removes consecutive duplicate lines that often appear in files
2. **Indentation Issues**: Fixes common indentation problems
3. **Missing Colons**: Adds missing colons after class and function definitions
4. **Unmatched Parentheses**: Balances opening and closing parentheses
5. **Try-Except Blocks**: Fixes misplaced try-except blocks and redundant else blocks
6. **Other Syntax Issues**: Fixes various other common syntax problems

## Usage

### Basic Usage

To fix all Python files in the current directory and subdirectories:

```bash
# On Windows
fix_syntax_errors.bat

# On Unix/Linux
python fix_syntax_errors.py
```

### Specific Files or Directories

To fix specific files or directories:

```bash
# Fix a specific file
python fix_syntax_errors.py path/to/file.py

# Fix files matching a pattern
python fix_syntax_errors.py --files "ui/services/*.py" "tests/*.py"

# Fix files in a specific directory
python fix_syntax_errors.py path/to/directory
```

### Dry Run

To see what would be fixed without actually modifying any files:

```bash
python fix_syntax_errors.py --dry-run
```

## Examples

### Fix Specific Files

```bash
python fix_syntax_errors.py --files ui/services/developer_service.py ui/services/marketing_service.py
```

### Fix All Files in a Directory

```bash
python fix_syntax_errors.py ui/services
```

### Dry Run on All Files

```bash
python fix_syntax_errors.py --dry-run
```

## How It Works

1. The script scans Python files for syntax errors
2. It applies a series of fixes to common syntax problems
3. It verifies that the fixes resolved the syntax issues
4. It only modifies files that had syntax errors and were successfully fixed

## Limitations

- The script may not be able to fix all types of syntax errors
- Complex syntax issues might require manual intervention
- The script respects `.gitignore` patterns to avoid modifying ignored files

## Integration with GitHub Actions

You can add this script to your GitHub Actions workflow to automatically fix syntax errors before running tests:

```yaml
- name: Fix syntax errors
  run: python fix_syntax_errors.py
```

## Contributing

Feel free to contribute to this tool by adding more syntax error fixes or improving the existing ones.
