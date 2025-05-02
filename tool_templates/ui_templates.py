"""
UI Templates for the pAIssive Income project.

This module provides templates for creating user interfaces for different types of applications.
It includes classes and functions for web applications, desktop applications, and mobile applications.

Dependencies:
- Flask (for web applications)
- React (for web and mobile applications)
- Electron (for desktop applications)
- PyQt5 (for desktop applications, alternative to Electron)
"""

import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Check for optional dependencies
try:
    import flask
    from flask import Flask, jsonify, redirect, render_template, request, url_for

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask not available. Web application templates will not work.")

try:
    from PyQt5 import QtCore, QtGui, QtWidgets

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    logger.warning(
        "PyQt5 not available. Desktop application templates (PyQt) will not work."
    )


class BaseUITemplate(ABC):
    """
    Base class for UI templates.
    """

    def __init__(
        self,
        app_name: str,
        description: str,
        version: str = "0.1.0",
        author: str = "",
        config_path: Optional[str] = None,
    ):
        """
        Initialize a UI template.

        Args:
            app_name: Name of the application
            description: Description of the application
            version: Version of the application
            author: Author of the application
            config_path: Optional path to a configuration file
        """
        self.app_name = app_name
        self.description = description
        self.version = version
        self.author = author
        self.created_at = datetime.now().isoformat()
        self.id = str(uuid.uuid4())
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from a JSON file or use default configuration.

        Args:
            config_path: Path to a JSON configuration file

        Returns:
            Configuration dictionary
        """
        default_config = {
            "theme": {
                "primary_color": "#4a6cf7",
                "secondary_color": "#f78c6c",
                "background_color": "#ffffff",
                "text_color": "#333333",
                "font_family": "Arial, sans-serif",
            },
            "layout": {"sidebar": True, "navbar": True, "footer": True},
            "features": {"dark_mode": True, "responsive": True, "animations": True},
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    user_config = json.load(f)
                    # Merge user config with default config
                    for key, value in user_config.items():
                        if key in default_config and isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                    return default_config
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
                return default_config
        return default_config

    @abstractmethod
    def create_app(self) -> Any:
        """
        Create and configure the application.

        Returns:
            Application instance
        """
        pass

    @abstractmethod
    def run(self, **kwargs) -> None:
        """
        Run the application.

        Args:
            **kwargs: Additional parameters for running the application
        """
        pass

    def export_template(self, output_path: str) -> None:
        """
        Export the template configuration to a JSON file.

        Args:
            output_path: Path to save the template configuration
        """
        template_config = {
            "id": self.id,
            "app_name": self.app_name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "created_at": self.created_at,
            "config": self.config,
            "template_type": self.__class__.__name__,
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(template_config, f, indent=2)

        logger.info(f"Template configuration exported to {output_path}")

    def __str__(self) -> str:
        """String representation of the UI template."""
        return f"{self.__class__.__name__}(app_name={self.app_name}, version={self.version})"


class WebAppTemplate(BaseUITemplate):
    """
    Template for web applications using Flask.
    """

    def __init__(
        self,
        app_name: str,
        description: str,
        version: str = "0.1.0",
        author: str = "",
        config_path: Optional[str] = None,
        template_folder: str = "templates",
        static_folder: str = "static",
    ):
        """
        Initialize a web application template.

        Args:
            app_name: Name of the application
            description: Description of the application
            version: Version of the application
            author: Author of the application
            config_path: Optional path to a configuration file
            template_folder: Folder for HTML templates
            static_folder: Folder for static files (CSS, JS, images)
        """
        super().__init__(app_name, description, version, author, config_path)

        if not FLASK_AVAILABLE:
            raise ImportError(
                "Flask is required for web applications. Install it with 'pip install flask'."
            )

        self.template_folder = template_folder
        self.static_folder = static_folder
        self.routes = []
        self.app = None

    def create_app(self) -> Flask:
        """
        Create and configure a Flask application.

        Returns:
            Flask application instance
        """
        app = Flask(
            self.app_name,
            template_folder=self.template_folder,
            static_folder=self.static_folder,
        )

        # Configure the app
        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_key_" + self.id)

        # Register default routes
        @app.route("/")
        def index():
            return render_template(
                "index.html", app_name=self.app_name, description=self.description
            )

        @app.route("/about")
        def about():
            return render_template(
                "about.html",
                app_name=self.app_name,
                description=self.description,
                version=self.version,
                author=self.author,
            )

        # Register custom routes
        for route in self.routes:
            app.add_url_rule(
                route["url"],
                endpoint=route.get("endpoint"),
                view_func=route["view_func"],
                methods=route.get("methods", ["GET"]),
            )

        self.app = app
        return app

    def add_route(
        self,
        url: str,
        view_func: Callable,
        endpoint: Optional[str] = None,
        methods: List[str] = None,
    ) -> None:
        """
        Add a route to the application.

        Args:
            url: URL pattern for the route
            view_func: View function to handle the route
            endpoint: Optional endpoint name
            methods: HTTP methods allowed for the route
        """
        if methods is None:
            methods = ["GET"]

        self.routes.append(
            {
                "url": url,
                "view_func": view_func,
                "endpoint": endpoint,
                "methods": methods,
            }
        )

        # If app is already created, add the route directly
        if self.app:
            self.app.add_url_rule(
                url, endpoint=endpoint, view_func=view_func, methods=methods
            )

    def run(
        self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False
    ) -> None:
        """
        Run the web application.

        Args:
            host: Host to run the application on
            port: Port to run the application on
            debug: Whether to run in debug mode
        """
        if not self.app:
            self.create_app()

        self.app.run(host=host, port=port, debug=debug)

    def generate_templates(self, output_dir: str) -> None:
        """
        Generate HTML templates for the web application.

        Args:
            output_dir: Directory to save the templates
        """
        os.makedirs(os.path.join(output_dir, self.template_folder), exist_ok=True)
        os.makedirs(os.path.join(output_dir, self.static_folder, "css"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, self.static_folder, "js"), exist_ok=True)

        # Create base template
        base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ app_name }}{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block head %}{% endblock %}
</head>
<body>
    <header>
        <nav>
            <div class="logo">{{ app_name }}</div>
            <ul>
                <li><a href="{{ url_for('index') }}">Home</a></li>
                <li><a href="{{ url_for('about') }}">About</a></li>
                {% block nav_items %}{% endblock %}
            </ul>
        </nav>
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; {{ now.year }} {{ author or app_name }}. All rights reserved.</p>
    </footer>
    
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""

        # Create index template
        index_template = """{% extends "base.html" %}

{% block title %}{{ app_name }} - Home{% endblock %}

{% block content %}
<section class="hero">
    <h1>{{ app_name }}</h1>
    <p>{{ description }}</p>
    <button class="cta-button">Get Started</button>
</section>

<section class="features">
    <h2>Features</h2>
    <div class="feature-grid">
        <div class="feature-card">
            <h3>Feature 1</h3>
            <p>Description of feature 1</p>
        </div>
        <div class="feature-card">
            <h3>Feature 2</h3>
            <p>Description of feature 2</p>
        </div>
        <div class="feature-card">
            <h3>Feature 3</h3>
            <p>Description of feature 3</p>
        </div>
    </div>
</section>
{% endblock %}
"""

        # Create about template
        about_template = """{% extends "base.html" %}

{% block title %}{{ app_name }} - About{% endblock %}

{% block content %}
<section class="about">
    <h1>About {{ app_name }}</h1>
    <p>{{ description }}</p>
    <p>Version: {{ version }}</p>
    {% if author %}
    <p>Created by: {{ author }}</p>
    {% endif %}
</section>
{% endblock %}
"""

        # Create CSS file
        css_content = (
            """/* Base styles */
:root {
    --primary-color: """
            + self.config["theme"]["primary_color"]
            + """;
    --secondary-color: """
            + self.config["theme"]["secondary_color"]
            + """;
    --background-color: """
            + self.config["theme"]["background_color"]
            + """;
    --text-color: """
            + self.config["theme"]["text_color"]
            + """;
    --font-family: """
            + self.config["theme"]["font_family"]
            + """;
}

body {
    font-family: var(--font-family);
    margin: 0;
    padding: 0;
    background-color: var(--background-color);
    color: var(--text-color);
}

/* Header and navigation */
header {
    background-color: var(--primary-color);
    color: white;
    padding: 1rem;
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
}

nav ul {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
}

nav ul li {
    margin-left: 1rem;
}

nav ul li a {
    color: white;
    text-decoration: none;
}

nav ul li a:hover {
    text-decoration: underline;
}

/* Main content */
main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

/* Hero section */
.hero {
    text-align: center;
    padding: 3rem 0;
}

.hero h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.cta-button {
    background-color: var(--secondary-color);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 1rem;
}

.cta-button:hover {
    opacity: 0.9;
}

/* Features section */
.features {
    padding: 3rem 0;
}

.features h2 {
    text-align: center;
    margin-bottom: 2rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.feature-card {
    background-color: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
    color: var(--primary-color);
    margin-top: 0;
}

/* About page */
.about {
    max-width: 800px;
    margin: 0 auto;
}

/* Footer */
footer {
    background-color: #f5f5f5;
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}

/* Responsive design */
@media (max-width: 768px) {
    nav {
        flex-direction: column;
    }
    
    nav ul {
        margin-top: 1rem;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
    }
}
"""
        )

        # Create JavaScript file
        js_content = """// Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Get the CTA button
    const ctaButton = document.querySelector('.cta-button');
    
    // Add click event listener if the button exists
    if (ctaButton) {
        ctaButton.addEventListener('click', function() {
            alert('Welcome to ' + document.title + '!');
        });
    }
    
    // Initialize any components or features
    initializeApp();
});

function initializeApp() {
    console.log('Application initialized');
    // Add your initialization code here
}
"""

        # Write files
        with open(
            os.path.join(output_dir, self.template_folder, "base.html"), "w"
        ) as f:
            f.write(base_template)

        with open(
            os.path.join(output_dir, self.template_folder, "index.html"), "w"
        ) as f:
            f.write(index_template)

        with open(
            os.path.join(output_dir, self.template_folder, "about.html"), "w"
        ) as f:
            f.write(about_template)

        with open(
            os.path.join(output_dir, self.static_folder, "css", "style.css"), "w"
        ) as f:
            f.write(css_content)

        with open(
            os.path.join(output_dir, self.static_folder, "js", "main.js"), "w"
        ) as f:
            f.write(js_content)

        logger.info(f"Web application templates generated in {output_dir}")


class DesktopAppTemplate(BaseUITemplate):
    """
    Template for desktop applications using PyQt5.
    """

    def __init__(
        self,
        app_name: str,
        description: str,
        version: str = "0.1.0",
        author: str = "",
        config_path: Optional[str] = None,
        window_width: int = 800,
        window_height: int = 600,
    ):
        """
        Initialize a desktop application template.

        Args:
            app_name: Name of the application
            description: Description of the application
            version: Version of the application
            author: Author of the application
            config_path: Optional path to a configuration file
            window_width: Width of the main window
            window_height: Height of the main window
        """
        super().__init__(app_name, description, version, author, config_path)

        if not PYQT_AVAILABLE:
            raise ImportError(
                "PyQt5 is required for desktop applications. Install it with 'pip install PyQt5'."
            )

        self.window_width = window_width
        self.window_height = window_height
        self.app = None
        self.main_window = None

    def create_app(self) -> QtWidgets.QApplication:
        """
        Create and configure a PyQt application.

        Returns:
            QApplication instance
        """
        app = QtWidgets.QApplication([])
        app.setApplicationName(self.app_name)
        app.setApplicationVersion(self.version)

        # Create main window
        main_window = QtWidgets.QMainWindow()
        main_window.setWindowTitle(self.app_name)
        main_window.resize(self.window_width, self.window_height)

        # Create central widget
        central_widget = QtWidgets.QWidget()
        main_window.setCentralWidget(central_widget)

        # Create layout
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Add a label with the app description
        description_label = QtWidgets.QLabel(self.description)
        description_label.setAlignment(QtCore.Qt.AlignCenter)
        description_label.setStyleSheet("font-size: 16px; margin: 20px;")
        layout.addWidget(description_label)

        # Add a button
        button = QtWidgets.QPushButton("Get Started")
        button.setStyleSheet(
            f"background-color: {self.config['theme']['primary_color']}; color: white; padding: 10px; font-size: 14px;"
        )
        button.clicked.connect(
            lambda: QtWidgets.QMessageBox.information(
                main_window, "Welcome", f"Welcome to {self.app_name}!"
            )
        )
        layout.addWidget(button, alignment=QtCore.Qt.AlignCenter)

        # Create menu bar
        menu_bar = main_window.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Exit action
        exit_action = QtWidgets.QAction("Exit", main_window)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(app.quit)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menu_bar.addMenu("Help")

        # About action
        about_action = QtWidgets.QAction("About", main_window)
        about_action.triggered.connect(
            lambda: QtWidgets.QMessageBox.about(
                main_window,
                f"About {self.app_name}",
                f"{self.app_name} v{self.version}\n\n{self.description}\n\nCreated by: {self.author or 'Unknown'}",
            )
        )
        help_menu.addAction(about_action)

        self.app = app
        self.main_window = main_window

        return app

    def run(self) -> None:
        """
        Run the desktop application.
        """
        if not self.app:
            self.create_app()

        self.main_window.show()
        self.app.exec_()

    def generate_template(self, output_path: str) -> None:
        """
        Generate a Python script for the desktop application.

        Args:
            output_path: Path to save the Python script
        """
        template = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
{self.app_name} - {self.description}
Version: {self.version}
Author: {self.author}
\"\"\"

import sys
from PyQt5 import QtWidgets, QtCore, QtGui

class MainWindow(QtWidgets.QMainWindow):
    \"\"\"
    Main window for the {self.app_name} application.
    \"\"\"
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("{self.app_name}")
        self.resize({self.window_width}, {self.window_height})
        
        # Create central widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create layout
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        
        # Initialize UI components
        self.init_ui()
        
        # Create menus
        self.create_menus()
    
    def init_ui(self):
        \"\"\"Initialize UI components.\"\"\"
        # Add a label with the app description
        description_label = QtWidgets.QLabel("{self.description}")
        description_label.setAlignment(QtCore.Qt.AlignCenter)
        description_label.setStyleSheet("font-size: 16px; margin: 20px;")
        self.layout.addWidget(description_label)
        
        # Add a button
        button = QtWidgets.QPushButton("Get Started")
        button.setStyleSheet("background-color: {self.config['theme']['primary_color']}; color: white; padding: 10px; font-size: 14px;")
        button.clicked.connect(self.on_button_click)
        self.layout.addWidget(button, alignment=QtCore.Qt.AlignCenter)
    
    def create_menus(self):
        \"\"\"Create application menus.\"\"\"
        # Create menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        # Exit action
        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        # About action
        about_action = QtWidgets.QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def on_button_click(self):
        \"\"\"Handle button click event.\"\"\"
        QtWidgets.QMessageBox.information(self, "Welcome", "Welcome to {self.app_name}!")
    
    def show_about_dialog(self):
        \"\"\"Show about dialog.\"\"\"
        QtWidgets.QMessageBox.about(
            self,
            f"About {self.app_name}",
            f"{self.app_name} v{self.version}\\n\\n{self.description}\\n\\nCreated by: {self.author or 'Unknown'}"
        )


def main():
    \"\"\"Main function to run the application.\"\"\"
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("{self.app_name}")
    app.setApplicationVersion("{self.version}")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
"""

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(template)

        logger.info(f"Desktop application template generated at {output_path}")


class UITemplateFactory:
    """
    Factory class for creating UI templates.
    """

    @staticmethod
    def create(
        template_type: str, app_name: str, description: str, **kwargs
    ) -> BaseUITemplate:
        """
        Create a UI template.

        Args:
            template_type: Type of template (web, desktop)
            app_name: Name of the application
            description: Description of the application
            **kwargs: Additional parameters for template initialization

        Returns:
            UI template instance
        """
        if template_type.lower() == "web":
            return WebAppTemplate(app_name, description, **kwargs)
        elif template_type.lower() == "desktop":
            return DesktopAppTemplate(app_name, description, **kwargs)
        else:
            raise ValueError(f"Unknown template type: {template_type}")


# Example usage
if __name__ == "__main__":
    # Example 1: Web application template
    if FLASK_AVAILABLE:
        try:
            web_app = UITemplateFactory.create(
                template_type="web",
                app_name="My Web App",
                description="A web application for managing tasks",
                version="1.0.0",
                author="John Doe",
            )

            # Generate templates
            web_app.generate_templates("./web_app_example")

            # Export template configuration
            web_app.export_template("./web_app_example/template_config.json")

            print("Web application template created successfully!")
            print(f"Template ID: {web_app.id}")
            print(f"App Name: {web_app.app_name}")
            print(f"Description: {web_app.description}")
            print(f"Version: {web_app.version}")
            print(f"Author: {web_app.author}")
            print()

            # Uncomment to run the web application
            # web_app.run(debug=True)
        except Exception as e:
            print(f"Error creating web application template: {e}")

    # Example 2: Desktop application template
    if PYQT_AVAILABLE:
        try:
            desktop_app = UITemplateFactory.create(
                template_type="desktop",
                app_name="My Desktop App",
                description="A desktop application for managing tasks",
                version="1.0.0",
                author="Jane Doe",
                window_width=1024,
                window_height=768,
            )

            # Generate template
            desktop_app.generate_template("./desktop_app_example/app.py")

            # Export template configuration
            desktop_app.export_template("./desktop_app_example/template_config.json")

            print("Desktop application template created successfully!")
            print(f"Template ID: {desktop_app.id}")
            print(f"App Name: {desktop_app.app_name}")
            print(f"Description: {desktop_app.description}")
            print(f"Version: {desktop_app.version}")
            print(f"Author: {desktop_app.author}")
            print()

            # Uncomment to run the desktop application
            # desktop_app.run()
        except Exception as e:
            print(f"Error creating desktop application template: {e}")
