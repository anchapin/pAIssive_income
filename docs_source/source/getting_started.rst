.. _getting_started:

Getting Started
=============

This guide will help you get started with pAIssive_income.

Installation
-----------

You can install pAIssive_income using pip:

.. code-block: bash

   uv pip install -e .

Requirements
-----------

- Python 3.8+
- Dependencies listed in requirements.txt

Configuration
-----------

Before using pAIssive_income, you need to configure it for your environment:

1. Create a `config.yaml` file in your project directory or specify a custom path with `--config`.
2. Set up your API keys for various services (OpenAI, Hugging Face, etc.).

.. code-block: yaml

   # Example config.yaml
   api_keys:
     openai: "your-openai-api-key"
     huggingface: "your-huggingface-api-key"

   models:
     default: "gpt-3.5-turbo"

Basic Usage
---------

Here's a simple example of using pAIssive_income to analyze a niche:

.. code-block: python

   from pAIssive_income import niche_analysis

   # Initialize the niche analyzer
   analyzer = niche_analysis.OpportunityAnalyzer()

   # Analyze a potential niche
   results = analyzer.analyze_niche("AI productivity tools for freelancers")

   # Print the opportunity score
   print(f"Opportunity score: {results.opportunity_score}")

   # Generate solution ideas
   solutions = niche_analysis.solution_generator.generate_solutions(results)
   for solution in solutions:
       print(f"- {solution.name}: {solution.description}")

Next Steps
---------

- Check out the :ref:`examples` for more complex use cases
- Explore the :ref:`api` documentation to learn about all available features
- Read the :ref:`overview` to understand the system architecture
