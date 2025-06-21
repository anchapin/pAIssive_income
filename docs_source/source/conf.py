"""conf - Sphinx configuration for pAIssive Income documentation."""

# -- Project information -----------------------------------------------------
project = "pAIssive Income"
copyright = "2025"
author = "AI Assistant & Contributors"

# -- General configuration ---------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
autosummary_generate = True

# -- Options for HTML output -------------------------------------------------
# (Feel free to set html_theme if desired; default is fine for now)

# -- Intersphinx mapping -----------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
