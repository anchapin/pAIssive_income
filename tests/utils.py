"""
Utility functions for tests.
"""

import time


import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict


def create_test_file():
    (directory: str, filename: str, content: str) -> str:
    """
    Create a test file with the given content.

Args:
        directory: Directory to create the file in
        filename: Name of the file
        content: Content of the file

Returns:
        Path to the created file
    """
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)

with open(file_path, "w") as f:
        f.write(content)

            return file_path


def create_test_json_file(directory: str, filename: str, data: Dict[str, Any]) -> str:
    """
    Create a test JSON file with the given data.

Args:
        directory: Directory to create the file in
        filename: Name of the file
        data: Data to write to the file

Returns:
        Path to the created file
    """
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)

with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

            return file_path


def create_mock_niche(name: str = "Test Niche") -> Dict[str, Any]:
    """
    Create a mock niche for testing.

Args:
        name: Name of the niche

Returns:
        Mock niche dictionary
    """
                return {
        "id": str(uuid.uuid4()),
        "name": name,
        "market_segment": name.lower().replace(" ", "_"),
        "description": f"AI tools for {name.lower()}",
        "opportunity_score": 0.75,
        "market_data": {
            "market_size": "medium",
            "growth_rate": "high",
            "competition": "low",
            "barriers_to_entry": "medium",
            "technological_adoption": "medium",
            "potential_niches": [],
            "target_users": [],
        },
        "problems": [
            {
                "id": str(uuid.uuid4()),
                "name": "Problem 1",
                "description": "A test problem",
                "consequences": ["consequence 1", "consequence 2"],
                "severity": "medium",
            }
        ],
        "opportunity_analysis": {
            "score": 0.75,
            "factors": {
                "market_size": 0.7,
                "growth_rate": 0.8,
                "competition": 0.9,
                "problem_severity": 0.7,
                "solution_feasibility": 0.8,
                "monetization_potential": 0.7,
            },
            "recommendations": [
                "Focus on specific user pain points",
                "Develop a freemium model",
            ],
        },
        "created_at": datetime.now().isoformat(),
    }


def create_mock_subscription_model(
    name: str = "Test Subscription Model",
) -> Dict[str, Any]:
    """
    Create a mock subscription model for testing.

Args:
        name: Name of the subscription model

Returns:
        Mock subscription model dictionary
    """
                return {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": f"A test subscription model for {name}",
        "tiers": [
            {
                "id": str(uuid.uuid4()),
                "name": "Basic",
                "description": "Basic tier",
                "price_monthly": 9.99,
                "price_yearly": 99.99,
                "features": ["feature1", "feature2"],
                "limits": {"api_calls": 100, "exports": 10},
                "target_users": "Individual users",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Pro",
                "description": "Pro tier",
                "price_monthly": 19.99,
                "price_yearly": 199.99,
                "features": ["feature1", "feature2", "feature3"],
                "limits": {"api_calls": 500, "exports": 50},
                "target_users": "Professional users",
            },
        ],
        "features": [
            {
                "id": str(uuid.uuid4()),
                "name": "Feature 1",
                "description": "A test feature",
                "feature_type": "functional",
                "value_proposition": "Save time",
                "development_cost": "low",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Feature 2",
                "description": "Another test feature",
                "feature_type": "functional",
                "value_proposition": "Improve quality",
                "development_cost": "medium",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Feature 3",
                "description": "A premium test feature",
                "feature_type": "premium",
                "value_proposition": "Advanced capabilities",
                "development_cost": "high",
            },
        ],
        "billing_cycles": ["monthly", "yearly"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


def create_mock_model_info(name: str = "Test Model") -> Dict[str, Any]:
    """
    Create a mock model info for testing.

Args:
        name: Name of the model

Returns:
        Mock model info dictionary
    """
                return {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": f"A test model for {name}",
        "type": "huggingface",
        "path": f"/path/to/models/{name.lower().replace(' ', '_')}",
        "capabilities": ["text-generation", "embedding"],
        "metadata": {
            "model_size": "7B",
            "context_length": 2048,
            "quantization": None,
            "license": "MIT",
        },
        "performance": {
            "latency_ms": 100,
            "throughput": 10,
            "memory_usage_mb": 1000,
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }