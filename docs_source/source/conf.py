# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pAIssive_income'
copyright = '2025, Alex Chapin'
author = 'Alex Chapin'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # Automatically generate API documentation
    'sphinx.ext.viewcode',  # Add links to highlighted source code
    'sphinx.ext.napoleon',  # Support for NumPy and Google style docstrings
    'sphinx.ext.intersphinx',  # Link to other project's documentation
    'sphinx.ext.githubpages',  # Generate .nojekyll file for GitHub Pages
    'sphinx.ext.todo',  # Support for todo items
    'sphinx.ext.coverage',  # Check documentation coverage
]

# Napoleon settings
napoleon_google_docstring = True  # Enable Google style docstrings
napoleon_numpy_docstring = False  # Disable NumPy style docstrings
napoleon_include_init_with_doc = True  # Include __init__ method documentation
napoleon_include_private_with_doc = True  # Include _private methods if they have docstrings
napoleon_include_special_with_doc = True  # Include __special__ methods if they have docstrings
napoleon_use_admonition_for_examples = True  # Use admonition for examples
napoleon_use_admonition_for_notes = True  # Use admonition for notes
napoleon_use_admonition_for_references = True  # Use admonition for references
napoleon_use_ivar = True  # Use :ivar: for instance variables
napoleon_use_param = True  # Use :param: for function/method parameters
napoleon_use_rtype = True  # Use :rtype: for return type

# Auto-doc settings
autodoc_member_order = 'bysource'  # Order members as they are in the source code
autodoc_default_options = {
    'members': True,  # Include module/class members
    'undoc-members': True,  # Include members without docstrings
    'show-inheritance': True,  # Show base classes
    'special-members': '__init__',  # Include __special__ methods
    'exclude-members': '__weakref__',  # Exclude __weakref__ attribute
}

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'  # Use the Read The Docs theme
html_static_path = ['_static']

# -- Options for intersphinx -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable', None),
}
