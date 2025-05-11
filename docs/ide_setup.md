# IDE Setup for pAIssive Income Project

This guide provides instructions for setting up various IDEs and editors to work with the pAIssive Income project, with a focus on using Ruff as the primary code formatter.

## VS Code

### Required Extensions

1. **Ruff Extension**: Install the [Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) for VS Code.
2. **Python Extension**: Install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) for VS Code.

### Configuration

The project includes a `.vscode/settings.json` file with the following configuration:

```json
{
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    
    // Linting and formatting settings
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    
    // Disable Black formatter
    "python.formatting.blackEnabled": false,
    
    // Enable Ruff as the primary formatter and linter
    "python.formatting.provider": "none",
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": true,
            "source.organizeImports.ruff": true
        }
    },
    
    // Ruff extension settings
    "ruff.format.args": [],
    "ruff.lint.run": "onSave",
    
    // Editor settings for consistent formatting
    "editor.rulers": [88],
    "editor.renderWhitespace": "all",
    "editor.insertSpaces": true,
    "editor.tabSize": 4,
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true
}
```

This configuration:
- Disables Black formatting
- Sets Ruff as the default formatter
- Enables format on save
- Configures Ruff to fix issues and organize imports on save
- Sets up editor guidelines for consistent formatting

## PyCharm

### Required Plugins

1. **Ruff Plugin**: Install the [Ruff plugin](https://plugins.jetbrains.com/plugin/20574-ruff) for PyCharm.

### Configuration

The project includes a `.idea/ruff.xml` file with the following configuration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="RuffConfigService">
    <option name="projectRuffExecutablePath" value="$PROJECT_DIR$/.venv/bin/ruff" />
    <option name="useRuffFormat" value="true" />
    <option name="runRuffOnSave" value="true" />
    <option name="runRuffOnReformatCode" value="true" />
  </component>
</project>
```

Additionally, you should configure PyCharm as follows:

1. Go to **Settings** > **Tools** > **Ruff**
2. Check "Use Ruff format instead of Black"
3. Check "Run Ruff on save"
4. Check "Run Ruff on Reformat Code action"

### Disabling Black

1. Go to **Settings** > **Tools** > **Black**
2. Uncheck "Enable Black"

## Other Editors

The project includes an `.editorconfig` file that provides basic formatting settings for most editors:

```ini
# EditorConfig helps maintain consistent coding styles across different editors
# https://editorconfig.org/

root = true

[*]
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
charset = utf-8

[*.{py,pyi}]
indent_style = space
indent_size = 4
max_line_length = 88

[*.{json,yml,yaml,toml}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

For editors that support EditorConfig, these settings will be applied automatically. For other editors, you'll need to configure them manually to match these settings.

## Manual Configuration for Other Editors

### Sublime Text

1. Install the [Ruff package](https://packagecontrol.io/packages/Ruff) via Package Control
2. Configure Ruff as the default formatter:
   - Go to **Preferences** > **Package Settings** > **Ruff** > **Settings**
   - Add the following configuration:
     ```json
     {
       "format_on_save": true,
       "lint_on_save": true
     }
     ```

### Vim/Neovim

1. Install a Ruff plugin like [ruff.vim](https://github.com/charliermarsh/ruff.vim) or use a language server like [coc-ruff](https://github.com/yaegassy/coc-ruff)
2. Configure your `.vimrc` or `init.vim` to use Ruff for formatting:
   ```vim
   " For vim-plug
   Plug 'charliermarsh/ruff.vim'
   
   " Configure format on save
   let g:ruff_format_on_save = 1
   ```

## Troubleshooting

If you encounter issues with formatting:

1. Make sure you have Ruff installed in your environment:
   ```bash
   pip install ruff
   ```

2. Verify that your IDE is using the correct Python interpreter with Ruff installed

3. Check that the Ruff configuration in `ruff.toml` is being properly loaded

4. Try running Ruff manually to see if there are any errors:
   ```bash
   ruff format path/to/file.py
   ```

For persistent issues, please open an issue in the GitHub repository.
