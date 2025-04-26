# pAIssive Income Framework UI

This directory contains the web interface for the pAIssive Income Framework, allowing users to interact with the framework's components through a user-friendly interface.

## Overview

The UI module provides a web-based interface for:

1. **Niche Analysis**: Identify profitable niches with high demand and low competition
2. **Solution Development**: Design and develop AI-powered solutions for specific niches
3. **Monetization Strategy**: Create effective monetization strategies with subscription models
4. **Marketing Campaign**: Develop targeted marketing campaigns to reach ideal customers

## Directory Structure

- `__init__.py`: Main module initialization and Flask application setup
- `app.py`: Entry point for running the web interface
- `routes.py`: URL routes and request handlers
- `services/`: Service classes for interacting with the framework components
- `templates/`: HTML templates for the web interface
- `static/`: Static files (CSS, JavaScript, images)
- `data/`: Data storage for the UI (JSON files)

## Services

The UI module includes the following services:

1. **AgentTeamService**: Interacts with the Agent Team module
2. **NicheAnalysisService**: Interacts with the Niche Analysis module
3. **DeveloperService**: Interacts with the Developer Agent module
4. **MonetizationService**: Interacts with the Monetization Agent module
5. **MarketingService**: Interacts with the Marketing Agent module

## Usage

To run the web interface:

```bash
python ui/app.py
```

Then open a web browser and navigate to `http://localhost:5000`.

## Dependencies

- Flask: Web framework
- Bootstrap: CSS framework (loaded from CDN)
- Font Awesome: Icon library (loaded from CDN)
- jQuery: JavaScript library (loaded from CDN)
- Chart.js (optional): For data visualization (loaded from CDN when needed)
- DataTables (optional): For enhanced tables (loaded from CDN when needed)

## Development

To extend the UI:

1. Add new routes in `routes.py`
2. Create new templates in the `templates/` directory
3. Add new services in the `services/` directory
4. Add new static files in the `static/` directory

## License

[MIT License](../LICENSE)
