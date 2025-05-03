# pAIssive Income

A comprehensive framework for developing and monetizing niche AI agents to generate passive income through subscription-based software tools powered by local AI.

## Overview

This project provides a structured approach to creating specialized AI-powered software tools that solve specific problems for targeted user groups. By focusing on niche markets with specific needs, these tools can provide high value to users while generating recurring subscription revenue.

The framework uses a team of specialized AI agents that collaborate to identify profitable niches, develop solutions, create monetization strategies, and market the products to target users.

## Project Structure

- **Agent Team**: A team of specialized AI agents that collaborate on different aspects of the product development and monetization process.
- **Niche Analysis**: Tools and methodologies for identifying profitable niches and user pain points.
- **Tool Templates**: Development templates for creating AI-powered software solutions.
- **Monetization**: Subscription models and pricing strategies for maximizing recurring revenue.
- **Marketing**: Strategies for reaching target users and promoting the AI tools.
- **UI**: Web interface for interacting with the framework components.

## Agent Team

The project is built around a team of specialized AI agents:

1. **Research Agent**: Identifies market opportunities and user needs in specific niches.
2. **Developer Agent**: Creates AI-powered software solutions to address identified needs.
3. **Monetization Agent**: Designs subscription models and pricing strategies.
4. **Marketing Agent**: Develops strategies for reaching and engaging target users.
5. **Feedback Agent**: Gathers and analyzes user feedback for product improvement.

## Key Features

- **Niche Identification**: Sophisticated analysis tools to identify profitable niches with specific user problems that can be solved with AI.
- **Problem Analysis**: Detailed analysis of user problems and pain points to ensure solutions address real needs.
- **Solution Design**: Templates and frameworks for designing AI-powered software solutions.
- **Monetization Strategy**: Subscription models and pricing strategies optimized for recurring revenue.
- **Marketing Plan**: Comprehensive marketing strategies tailored to each niche and target user group.
- **Feedback Loop**: Tools for gathering and analyzing user feedback to continuously improve products.

## Example Niches

The framework has identified several promising niches for AI-powered tools:

1. **YouTube Script Generator**: AI tools to help YouTube creators write engaging scripts faster.
2. **Study Note Generator**: AI tools to help students create comprehensive study notes from lectures.
3. **Freelance Proposal Writer**: AI tools to help freelancers write compelling client proposals.
4. **Property Description Generator**: AI tools to help real estate agents write compelling property descriptions.
5. **Inventory Management for Small E-commerce**: AI tools to help small e-commerce businesses manage inventory efficiently.

## Getting Started

### Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/anchapin/pAIssive_income.git
   cd pAIssive_income
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Set up pre-commit hooks to ensure code quality:

   ```bash
   # On Windows
   setup_pre_commit.bat

   # On Unix/Linux
   python setup_pre_commit.py
   ```

   For more information about pre-commit hooks, see [Pre-commit Hooks Documentation](docs/pre-commit-hooks.md).

### Command Line Interface

1. Run the niche analysis tools to identify promising market opportunities:

   ```python
   python main.py
   ```

2. Review the generated project plan:

   ```bash
   cat project_plan.json
   ```

3. Use the agent team to develop a comprehensive strategy for your chosen niche:

   ```python
   from agent_team import AgentTeam

   team = AgentTeam("Your Project Name")
   niches = team.run_niche_analysis(["your", "target", "segments"])
   solution = team.develop_solution(niches[0]["id"])
   monetization = team.create_monetization_strategy()
   marketing = team.create_marketing_plan()
   ```

### Web Interface

#### Modern React UI (Recommended)

The framework now includes a modern React-based user interface with a Flask API backend.

1. Start both the React development server and Flask API server with a single command:

   ```python
   python ui/run_ui.py
   ```

   This script will:
   - Start the Flask API server on port 5000
   - Install React dependencies if needed
   - Start the React development server on port 3000
   - Open your web browser automatically

2. If the browser doesn't open automatically, navigate to `http://localhost:3000`

3. For development purposes, you can also run the components separately:

   ```bash
   # Start just the Flask API server
   python ui/api_server.py

   # Start just the React development server (from the react_frontend directory)
   cd ui/react_frontend
   npm install  # Only needed the first time
   npm start
   ```

#### Legacy Web Interface

The original web interface is still available:

1. Start the legacy web interface:

   ```python
   python run_ui.py --legacy
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Use the web interface to:
   - Analyze niches
   - Develop solutions
   - Create monetization strategies
   - Plan marketing campaigns

### Next Steps

1. Implement the AI tool using the provided templates in the `tool_templates` directory.

2. Deploy your monetization strategy based on the subscription models in the `monetization` directory.

3. Execute the marketing plan using strategies from the `marketing` directory.

4. Gather feedback and iterate on your product using the Feedback Agent.

## Example Output

Running the main script generates a complete project plan including:

- Niche analysis with opportunity scores
- Detailed user problem analysis
- Solution design with features and architecture
- Monetization strategy with subscription tiers and revenue projections
- Marketing plan with user personas and channel strategies

## Requirements

- Python 3.8+
- Node.js 14.0+ (for modern UI)
- Dependencies listed in each module's README

## Documentation

The project includes comprehensive API documentation that can be built from source:

1. Navigate to the docs_source directory:

   ```bash
   cd docs_source
   ```

2. Generate the API documentation from source code:

   ```bash
   python generate_api_docs.py
   ```

3. Build the HTML documentation:

   ```bash
   make html
   ```

   On Windows, use:

   ```bash
   make.bat html
   ```

4. The generated documentation will be available in `docs_source/build/html/`

You can view the documentation by opening `docs_source/build/html/index.html` in your web browser.

## License

[MIT License](LICENSE)
