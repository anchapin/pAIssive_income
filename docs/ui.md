# UI Module

The UI module provides a web interface for interacting with the pAIssive Income framework, allowing users to analyze niches, develop solutions, create monetization strategies, and plan marketing campaigns.

## Overview

The UI module is built with Flask and provides a user-friendly interface for accessing the framework's functionality. It includes:

1. **Web Interface**: A responsive web interface for desktop and mobile devices
2. **Services**: Service classes for interacting with the framework components
3. **Routes**: URL routes and request handlers
4. **Templates**: HTML templates for rendering pages
5. **Static Files**: CSS, JavaScript, and images for styling and interactivity

## Directory Structure

The UI module is organized into the following directories:

- `__init__.py`: Main module initialization and Flask application setup
- `app.py`: Entry point for running the web interface
- `routes.py`: URL routes and request handlers
- `services/`: Service classes for interacting with the framework components
- `templates/`: HTML templates for the web interface
- `static/`: Static files (CSS, JavaScript, images)
- `data/`: Data storage for the UI (JSON files)

## Routes

The UI module provides the following routes:

### Main Routes

- `/`: Home page with an overview of the framework
- `/dashboard`: Dashboard with an overview of projects
- `/about`: About page with information about the framework

### Niche Analysis Routes

- `/niche-analysis`: Niche analysis page for selecting market segments
- `/niche-analysis/run`: Route for running niche analysis on selected market segments
- `/niche-analysis/results`: Page for displaying niche analysis results

### Developer Routes

- `/developer`: Developer page for selecting niches to develop solutions for
- `/developer/solution`: Route for developing a solution for a selected niche
- `/developer/results`: Page for displaying solution development results

### Monetization Routes

- `/monetization`: Monetization page for selecting solutions to create monetization strategies for
- `/monetization/strategy`: Route for creating a monetization strategy for a selected solution
- `/monetization/results`: Page for displaying monetization strategy results

### Marketing Routes

- `/marketing`: Marketing page for selecting solutions to create marketing campaigns for
- `/marketing/campaign`: Route for creating a marketing campaign for a selected solution
- `/marketing/results`: Page for displaying marketing campaign results

### API Routes

- `/api/niches`: API endpoint for getting niches
- `/api/solutions`: API endpoint for getting solutions
- `/api/monetization-strategies`: API endpoint for getting monetization strategies
- `/api/marketing-campaigns`: API endpoint for getting marketing campaigns

## Services

The UI module includes several service classes for interacting with the framework components:

### AgentTeamService

The `AgentTeamService` class provides methods for interacting with the Agent Team module:

```python
from ui.services import AgentTeamService

# Create an agent team service
service = AgentTeamService()

# Get all projects
projects = service.get_projects()

# Create a new project
project = service.create_project("My Project", "A project for developing an AI tool")

# Get a project by ID
project = service.get_project("project-id")

# Update a project
service.update_project("project-id", name="New Name", description="New description")

# Delete a project
service.delete_project("project-id")
```

### NicheAnalysisService

The `NicheAnalysisService` class provides methods for interacting with the Niche Analysis module:

```python
from ui.services import NicheAnalysisService

# Create a niche analysis service
service = NicheAnalysisService()

# Get all market segments
segments = service.get_market_segments()

# Analyze niches
niches = service.analyze_niches(["e-commerce", "content creation"])

# Get all niches
niches = service.get_niches()

# Get a niche by ID
niche = service.get_niche("niche-id")
```

### DeveloperService

The `DeveloperService` class provides methods for interacting with the Developer Agent:

```python
from ui.services import DeveloperService

# Create a developer service
service = DeveloperService()

# Develop a solution
solution = service.develop_solution("niche-id")

# Get all solutions
solutions = service.get_solutions()

# Get a solution by ID
solution = service.get_solution("solution-id")
```

### MonetizationService

The `MonetizationService` class provides methods for interacting with the Monetization module:

```python
from ui.services import MonetizationService

# Create a monetization service
service = MonetizationService()

# Create a monetization strategy
strategy = service.create_strategy("solution-id")

# Get all strategies
strategies = service.get_strategies()

# Get a strategy by ID
strategy = service.get_strategy("strategy-id")
```

### MarketingService

The `MarketingService` class provides methods for interacting with the Marketing module:

```python
from ui.services import MarketingService

# Create a marketing service
service = MarketingService()

# Create a marketing campaign
campaign = service.create_campaign("solution-id", "strategy-id")

# Get all campaigns
campaigns = service.get_campaigns()

# Get a campaign by ID
campaign = service.get_campaign("campaign-id")
```

## Templates

The UI module includes several HTML templates for rendering pages:

### Base Template

The `base.html` template provides the base structure for all pages, including:

- Header with navigation
- Sidebar with links to different sections
- Main content area
- Footer with copyright information

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}pAIssive Income Framework{% endblock %}</title>
    # UI Tailwind CSS Integration Guide

## Overview

The UI now uses [Tailwind CSS](https://tailwindcss.com/) for modern, utility-first styling. Legacy styles from `style.css` are merged into the Tailwind build output for a seamless transition.

## Key Integration Details

- **Tailwind Installation:**  
  Tailwind and its dependencies are managed via `pnpm` and configured through `tailwind.config.js` at the project root and in `ui/`.
- **Build Output:**  
  Run `pnpm tailwind:build` to generate `ui/static/css/tailwind.output.css`, which includes both Tailwind utilities and your legacy styles from `style.css`.
- **Template Usage:**  
  Only `tailwind.output.css` needs to be referenced in your templates:
  ```html
  <link rel="stylesheet" href="{{ url_for('static', filename='css/tailwind.output.css') }}">
  ```
- **Legacy CSS Merge:**  
  The Tailwind input file (`ui/static/css/tailwind.css`) imports `style.css` so custom styles are included in the build.
- **.gitignore:**  
  The build output is git-ignored to keep the repository clean.
- **CI/CD Pipeline:**  
  The GitHub Actions workflow automatically builds Tailwind CSS before running tests and deployment.

## Example

See `ui/templates/tailwind_example.html` for a minimal template using Tailwind classes.

## For Contributors

- Update `tailwind.config.js` if you add new templates or JS files with Tailwind classes.
- Edit `ui/static/css/tailwind.css` to add custom CSS or further customize Tailwind.
- Refer to `ui/README.md` for more detailed onboarding instructions.

```css
/* Variables */
:root {
    --primary-color: #4e73df;
    --secondary-color: #858796;
    --success-color: #1cc88a;
    --info-color: #36b9cc;
    --warning-color: #f6c23e;
    --danger-color: #e74a3b;
    --light-color: #f8f9fc;
    --dark-color: #5a5c69;
    --background-color: #f8f9fc;
    --text-color: #333;
    --font-family: 'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Global styles */
body {
    font-family: var(--font-family);
    background-color: var(--background-color);
    color: var(--text-color);
}

/* Sidebar styles */
#sidebar {
    min-width: 250px;
    max-width: 250px;
    background: var(--primary-color);
    color: #fff;
    transition: all 0.3s;
}

#sidebar.active {
    margin-left: -250px;
}

#sidebar .sidebar-header {
    padding: 20px;
    background: rgba(0, 0, 0, 0.1);
}

#sidebar ul.components {
    padding: 20px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

#sidebar ul li a {
    padding: 10px;
    font-size: 1.1em;
    display: block;
    color: #fff;
    text-decoration: none;
}

#sidebar ul li a:hover {
    color: var(--primary-color);
    background: #fff;
}

#sidebar ul li.active > a {
    color: #fff;
    background: rgba(0, 0, 0, 0.2);
}

/* Content styles */
#content {
    width: 100%;
    padding: 20px;
    min-height: 100vh;
    transition: all 0.3s;
}

.content-header {
    margin-bottom: 20px;
}

.content-body {
    background: #fff;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

/* Card styles */
.card {
    background: #fff;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.card-header {
    background: var(--light-color);
    padding: 15px 20px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    font-weight: bold;
}

.card-body {
    padding: 20px;
}

/* Form styles */
.form-group {
    margin-bottom: 20px;
}

.form-control {
    display: block;
    width: 100%;
    padding: 10px;
    font-size: 1rem;
    line-height: 1.5;
    color: var(--text-color);
    background-color: #fff;
    border: 1px solid #ced4da;
    border-radius: 5px;
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.btn {
    display: inline-block;
    font-weight: 400;
    text-align: center;
    white-space: nowrap;
    vertical-align: middle;
    user-select: none;
    border: 1px solid transparent;
    padding: 10px 20px;
    font-size: 1rem;
    line-height: 1.5;
    border-radius: 5px;
    transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    cursor: pointer;
}

.btn-primary {
    color: #fff;
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}

.btn-primary:hover {
    background-color: #2e59d9;
    border-color: #2653d4;
}
```

### JavaScript

The `static/js/main.js` file provides interactivity for the UI:

```javascript
/**
 * pAIssive Income Framework UI
 * Main JavaScript file for the web interface
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');

            sidebar.classList.toggle('active');
            content.classList.toggle('active');
        });
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    if (forms.length > 0) {
        Array.from(forms).forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }

                form.classList.add('was-validated');
            }, false);
        });
    }

    // Opportunity score color coding
    const opportunityScores = document.querySelectorAll('.opportunity-score .score');
    opportunityScores.forEach(function(score) {
        const value = parseFloat(score.textContent);
        if (value >= 0.8) {
            score.style.color = '#28a745'; // Success/green
        } else if (value >= 0.6) {
            score.style.color = '#17a2b8'; // Info/blue
        } else if (value >= 0.4) {
            score.style.color = '#ffc107'; // Warning/yellow
        } else {
            score.style.color = '#dc3545'; // Danger/red
        }
    });

    // Initialize any charts
    initializeCharts();

    // Initialize any data tables
    initializeDataTables();

    console.log('pAIssive Income Framework UI initialized');
});

// Function to initialize charts
function initializeCharts() {
    const chartElements = document.querySelectorAll('.chart');
    if (chartElements.length === 0) return;

    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded. Charts will not be initialized.');
        return;
    }

    chartElements.forEach(function(element) {
        const ctx = element.getContext('2d');
        const chartType = element.dataset.chartType || 'bar';
        const chartData = JSON.parse(element.dataset.chartData || '{}');
        const chartOptions = JSON.parse(element.dataset.chartOptions || '{}');

        new Chart(ctx, {
            type: chartType,
            data: chartData,
            options: chartOptions
        });
    });
}

// Function to initialize data tables
function initializeDataTables() {
    const tableElements = document.querySelectorAll('.datatable');
    if (tableElements.length === 0) return;

    // Check if DataTables is loaded
    if (typeof $.fn.DataTable === 'undefined') {
        console.warn('DataTables is not loaded. Tables will not be initialized.');
        return;
    }

    tableElements.forEach(function(element) {
        $(element).DataTable({
            responsive: true
        });
    });
}
```

## Running the UI

To run the UI, use the `run_ui.py` script:

```bash
python run_ui.py
```

This will start a web server at [http://localhost:5000](http://localhost:5000) where you can access the UI.

### Dependencies

The UI module uses Flask 3.1.1 as its web framework. This version includes the following improvements over previous versions:

- Fixed signing key selection order when key rotation is enabled via `SECRET_KEY_FALLBACKS`
- Fixed type hint for `cli_runner.invoke`
- Improved `flask --help` command to load the app and plugins first to ensure all commands are shown
- Enhanced typing support for views that return `AsyncIterable` (for compatibility with Quart)

For a complete list of changes, see the [Flask 3.1.1 changelog](https://flask.palletsprojects.com/en/stable/changes/#version-3-1-1).

## Extending the UI

To extend the UI with new functionality:

1. Add new routes in `routes.py`
2. Create new templates in the `templates/` directory
3. Add new services in the `services/` directory
4. Add new static files in the `static/` directory

For example, to add a new page for user settings:

1. Add a new route in `routes.py`:

```python
@app.route('/settings')
def settings():
    """Render the settings page."""
    return render_template('settings.html', title='Settings')
```

2. Create a new template in `templates/settings.html`:

```html
{% extends "base.html" %}

{% block title %}pAIssive Income Framework - Settings{% endblock %}

{% block page_title %}Settings{% endblock %}

{% block content %}
<div class="settings-container">
    <div class="card">
        <div class="card-header">
            User Settings
        </div>
        <div class="card-body">
            <form method="post" action="{{ url_for('update_settings') }}">
                <div class="form-group">
                    <label for="name">Name</label>
                    <input type="text" class="form-control" id="name" name="name" value="{{ user.name }}">
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" class="form-control" id="email" name="email" value="{{ user.email }}">
                </div>
                <button type="submit" class="btn btn-primary">Save Settings</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

3. Add a new service in `services/user_service.py`:

```python
"""
User service for the pAIssive Income UI.

This module provides services for managing user settings.
"""

import os
import json
import logging
from datetime import datetime
import uuid

# Set up logging
logger = logging.getLogger(__name__)

class UserService:
    """
    Service for managing user settings.
    """

    def __init__(self):
        """Initialize the UserService."""
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        self.users_file = os.path.join(self.data_dir, 'users.json')
        self._load_users()

    def _load_users(self):
        """Load users from the data file."""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            except Exception as e:
                logger.error(f"Error loading users: {e}")
                self.users = {}
        else:
            self.users = {}

    def _save_users(self):
        """Save users to the data file."""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving users: {e}")

    def get_user(self, user_id):
        """Get a user by ID."""
        return self.users.get(user_id)

    def update_user(self, user_id, name=None, email=None):
        """Update a user's settings."""
        if user_id not in self.users:
            self.users[user_id] = {
                'id': user_id,
                'created_at': datetime.now().isoformat()
            }

        if name is not None:
            self.users[user_id]['name'] = name

        if email is not None:
            self.users[user_id]['email'] = email

        self.users[user_id]['updated_at'] = datetime.now().isoformat()

        self._save_users()

        return self.users[user_id]
```

4. Update `routes.py` with a route for updating settings:

```python
@app.route('/settings/update', methods=['POST'])
def update_settings():
    """Update user settings."""
    # Get user ID from session
    user_id = session.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id

    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')

    # Update user settings
    user_service = UserService()
    user = user_service.update_user(user_id, name=name, email=email)

    # Flash a success message
    flash('Settings updated successfully', 'success')

    return redirect(url_for('settings'))
```

5. Add a link to the settings page in `base.html`:

```html
<li {% if request.path == '/settings' %}class="active"{% endif %}>
    <a href="{{ url_for('settings') }}"><i class="fas fa-cog"></i> Settings</a>
</li>
```
