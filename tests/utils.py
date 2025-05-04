"""
"""
Utility functions for tests.
Utility functions for tests.
"""
"""


import json
import json
import os
import os
import time
import time
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict
from typing import Any, Dict




def create_test_file():
    def create_test_file():
    (directory: str, filename: str, content: str) -> str:
    (directory: str, filename: str, content: str) -> str:
    """
    """
    Create a test file with the given content.
    Create a test file with the given content.


    Args:
    Args:
    directory: Directory to create the file in
    directory: Directory to create the file in
    filename: Name of the file
    filename: Name of the file
    content: Content of the file
    content: Content of the file


    Returns:
    Returns:
    Path to the created file
    Path to the created file
    """
    """
    os.makedirs(directory, exist_ok=True)
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    file_path = os.path.join(directory, filename)


    with open(file_path, "w") as f:
    with open(file_path, "w") as f:
    f.write(content)
    f.write(content)


    return file_path
    return file_path




    def create_test_json_file(directory: str, filename: str, data: Dict[str, Any]) -> str:
    def create_test_json_file(directory: str, filename: str, data: Dict[str, Any]) -> str:
    """
    """
    Create a test JSON file with the given data.
    Create a test JSON file with the given data.


    Args:
    Args:
    directory: Directory to create the file in
    directory: Directory to create the file in
    filename: Name of the file
    filename: Name of the file
    data: Data to write to the file
    data: Data to write to the file


    Returns:
    Returns:
    Path to the created file
    Path to the created file
    """
    """
    os.makedirs(directory, exist_ok=True)
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    file_path = os.path.join(directory, filename)


    with open(file_path, "w") as f:
    with open(file_path, "w") as f:
    json.dump(data, f, indent=2)
    json.dump(data, f, indent=2)


    return file_path
    return file_path




    def create_mock_niche(name: str = "Test Niche") -> Dict[str, Any]:
    def create_mock_niche(name: str = "Test Niche") -> Dict[str, Any]:
    """
    """
    Create a mock niche for testing.
    Create a mock niche for testing.


    Args:
    Args:
    name: Name of the niche
    name: Name of the niche


    Returns:
    Returns:
    Mock niche dictionary
    Mock niche dictionary
    """
    """
    return {
    return {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": name,
    "name": name,
    "market_segment": name.lower().replace(" ", "_"),
    "market_segment": name.lower().replace(" ", "_"),
    "description": f"AI tools for {name.lower()}",
    "description": f"AI tools for {name.lower()}",
    "opportunity_score": 0.75,
    "opportunity_score": 0.75,
    "market_data": {
    "market_data": {
    "market_size": "medium",
    "market_size": "medium",
    "growth_rate": "high",
    "growth_rate": "high",
    "competition": "low",
    "competition": "low",
    "barriers_to_entry": "medium",
    "barriers_to_entry": "medium",
    "technological_adoption": "medium",
    "technological_adoption": "medium",
    "potential_niches": [],
    "potential_niches": [],
    "target_users": [],
    "target_users": [],
    },
    },
    "problems": [
    "problems": [
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Problem 1",
    "name": "Problem 1",
    "description": "A test problem",
    "description": "A test problem",
    "consequences": ["consequence 1", "consequence 2"],
    "consequences": ["consequence 1", "consequence 2"],
    "severity": "medium",
    "severity": "medium",
    }
    }
    ],
    ],
    "opportunity_analysis": {
    "opportunity_analysis": {
    "score": 0.75,
    "score": 0.75,
    "factors": {
    "factors": {
    "market_size": 0.7,
    "market_size": 0.7,
    "growth_rate": 0.8,
    "growth_rate": 0.8,
    "competition": 0.9,
    "competition": 0.9,
    "problem_severity": 0.7,
    "problem_severity": 0.7,
    "solution_feasibility": 0.8,
    "solution_feasibility": 0.8,
    "monetization_potential": 0.7,
    "monetization_potential": 0.7,
    },
    },
    "recommendations": [
    "recommendations": [
    "Focus on specific user pain points",
    "Focus on specific user pain points",
    "Develop a freemium model",
    "Develop a freemium model",
    ],
    ],
    },
    },
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }




    def create_mock_subscription_model(
    def create_mock_subscription_model(
    name: str = "Test Subscription Model",
    name: str = "Test Subscription Model",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a mock subscription model for testing.
    Create a mock subscription model for testing.


    Args:
    Args:
    name: Name of the subscription model
    name: Name of the subscription model


    Returns:
    Returns:
    Mock subscription model dictionary
    Mock subscription model dictionary
    """
    """
    return {
    return {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": name,
    "name": name,
    "description": f"A test subscription model for {name}",
    "description": f"A test subscription model for {name}",
    "tiers": [
    "tiers": [
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Basic",
    "name": "Basic",
    "description": "Basic tier",
    "description": "Basic tier",
    "price_monthly": 9.99,
    "price_monthly": 9.99,
    "price_yearly": 99.99,
    "price_yearly": 99.99,
    "features": ["feature1", "feature2"],
    "features": ["feature1", "feature2"],
    "limits": {"api_calls": 100, "exports": 10},
    "limits": {"api_calls": 100, "exports": 10},
    "target_users": "Individual users",
    "target_users": "Individual users",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Pro",
    "name": "Pro",
    "description": "Pro tier",
    "description": "Pro tier",
    "price_monthly": 19.99,
    "price_monthly": 19.99,
    "price_yearly": 199.99,
    "price_yearly": 199.99,
    "features": ["feature1", "feature2", "feature3"],
    "features": ["feature1", "feature2", "feature3"],
    "limits": {"api_calls": 500, "exports": 50},
    "limits": {"api_calls": 500, "exports": 50},
    "target_users": "Professional users",
    "target_users": "Professional users",
    },
    },
    ],
    ],
    "features": [
    "features": [
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Feature 1",
    "name": "Feature 1",
    "description": "A test feature",
    "description": "A test feature",
    "feature_type": "functional",
    "feature_type": "functional",
    "value_proposition": "Save time",
    "value_proposition": "Save time",
    "development_cost": "low",
    "development_cost": "low",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Feature 2",
    "name": "Feature 2",
    "description": "Another test feature",
    "description": "Another test feature",
    "feature_type": "functional",
    "feature_type": "functional",
    "value_proposition": "Improve quality",
    "value_proposition": "Improve quality",
    "development_cost": "medium",
    "development_cost": "medium",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Feature 3",
    "name": "Feature 3",
    "description": "A premium test feature",
    "description": "A premium test feature",
    "feature_type": "premium",
    "feature_type": "premium",
    "value_proposition": "Advanced capabilities",
    "value_proposition": "Advanced capabilities",
    "development_cost": "high",
    "development_cost": "high",
    },
    },
    ],
    ],
    "billing_cycles": ["monthly", "yearly"],
    "billing_cycles": ["monthly", "yearly"],
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    }
    }




    def create_mock_model_info(name: str = "Test Model") -> Dict[str, Any]:
    def create_mock_model_info(name: str = "Test Model") -> Dict[str, Any]:
    """
    """
    Create a mock model info for testing.
    Create a mock model info for testing.


    Args:
    Args:
    name: Name of the model
    name: Name of the model


    Returns:
    Returns:
    Mock model info dictionary
    Mock model info dictionary
    """
    """
    return {
    return {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": name,
    "name": name,
    "description": f"A test model for {name}",
    "description": f"A test model for {name}",
    "type": "huggingface",
    "type": "huggingface",
    "path": f"/path/to/models/{name.lower().replace(' ', '_')}",
    "path": f"/path/to/models/{name.lower().replace(' ', '_')}",
    "capabilities": ["text-generation", "embedding"],
    "capabilities": ["text-generation", "embedding"],
    "metadata": {
    "metadata": {
    "model_size": "7B",
    "model_size": "7B",
    "context_length": 2048,
    "context_length": 2048,
    "quantization": None,
    "quantization": None,
    "license": "MIT",
    "license": "MIT",
    },
    },
    "performance": {
    "performance": {
    "latency_ms": 100,
    "latency_ms": 100,
    "throughput": 10,
    "throughput": 10,
    "memory_usage_mb": 1000,
    "memory_usage_mb": 1000,
    },
    },
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    }
    }