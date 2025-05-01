"""Service initialization module for dependency injection."""

import logging
from typing import Any, Dict, Optional, Type
from pathlib import Path
import os

from ai_models.model_manager import ModelManager
from ai_models.model_config import ModelConfig, IModelConfig
from agent_team import AgentTeam, IAgentTeam
from agent_team.team_config import TeamConfig
from dependency_container import DependencyContainer, register_service
from marketing.service import MarketingService
from monetization.service import MonetizationService
from niche_analysis.service import NicheAnalysisService

logger = logging.getLogger(__name__)

class CustomModelConfig(ModelConfig):
    @property
    def models_dir(self) -> str:
        return os.path.join(os.path.dirname(__file__), "models")
    
    @property
    def cache_dir(self) -> str:
        return os.path.join(os.path.dirname(__file__), "cache")
    
    @property
    def max_threads(self) -> int:
        return 4
        
    @property
    def auto_discover(self) -> bool:
        return True

def _init_configuration() -> None:
    config = CustomModelConfig()
    register_service("model_config", config)

def _init_ai_models() -> None:
    config = CustomModelConfig()
    model_manager = ModelManager(config)
    register_service("model_manager", model_manager)

def _init_agent_team() -> None:
    config_path = os.path.join(os.path.dirname(__file__), "agent_team", "config.json")
    team_config = TeamConfig(config_path)
    model_manager = ModelManager(CustomModelConfig())
    agent_team = AgentTeam(model_manager, team_config)
    register_service("agent_team", agent_team)

def _init_niche_analysis() -> None:
    niche_service = NicheAnalysisService()
    register_service("niche_analysis", niche_service)

def _init_marketing() -> None:
    marketing_service = MarketingService()
    register_service("marketing", marketing_service)

def _init_monetization() -> None:
    monetization_service = MonetizationService()
    register_service("monetization", monetization_service)

def initialize_services() -> None:
    """Initialize all application services."""
    _init_configuration()
    _init_ai_models()
    _init_agent_team()
    _init_niche_analysis()
    _init_marketing()
    _init_monetization()
