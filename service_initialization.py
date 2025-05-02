"""Service initialization module for dependency injection."""

import logging
import os

from agent_team import AgentTeam
from agent_team.team_config import TeamConfig
from ai_models.model_config import ModelConfig
from ai_models.model_manager import ModelManager
from dependency_container import register_service
from marketing.service import MarketingService
from monetization.service import MonetizationService
from niche_analysis.service import NicheAnalysisService

logger = logging.getLogger(__name__)


class CustomModelConfig(ModelConfig):
    def __init__(self):
        super().__init__()
        self._models_dir = os.path.join(os.path.dirname(__file__), "models")
        self._cache_dir = os.path.join(os.path.dirname(__file__), "cache")
        self._max_threads = 4
        self._auto_discover = True

    @property
    def models_dir(self) -> str:
        return self._models_dir

    @models_dir.setter
    def models_dir(self, value: str) -> None:
        self._models_dir = value

    @property
    def cache_dir(self) -> str:
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, value: str) -> None:
        self._cache_dir = value

    @property
    def max_threads(self) -> int:
        return self._max_threads

    @max_threads.setter
    def max_threads(self, value: int) -> None:
        self._max_threads = value

    @property
    def auto_discover(self) -> bool:
        return self._auto_discover

    @auto_discover.setter
    def auto_discover(self, value: bool) -> None:
        self._auto_discover = value


def _register_configuration(container=None, config=None) -> None:
    """Register model configuration service."""
    config = CustomModelConfig()
    register_service("model_config", config)


def _register_ai_models(container=None) -> None:
    """Register AI model services."""
    config = CustomModelConfig()
    model_manager = ModelManager(config)
    register_service("model_manager", model_manager)


def _register_agent_team(container=None) -> None:
    """Register agent team services."""
    config_path = os.path.join(os.path.dirname(__file__), "agent_team", "config.json")
    team_config = TeamConfig(config_path)
    model_manager = ModelManager(CustomModelConfig())
    agent_team = AgentTeam(model_manager, team_config)
    register_service("agent_team", agent_team)


def _register_niche_analysis(container=None) -> None:
    """Register niche analysis services."""
    niche_service = NicheAnalysisService()
    register_service("niche_analysis", niche_service)


def _register_marketing(container=None) -> None:
    """Register marketing services."""
    marketing_service = MarketingService()
    register_service("marketing", marketing_service)


def _register_monetization(container=None) -> None:
    """Register monetization services."""
    monetization_service = MonetizationService()
    register_service("monetization", monetization_service)


def _register_ui_services(container=None) -> None:
    """Register UI services."""
    # This function is imported in tests but not implemented
    # Adding a placeholder implementation
    pass


def get_service(service_type):
    """Get a service from the container."""
    # This function is imported in tests but not implemented
    # Adding a placeholder implementation
    pass


def initialize_services() -> None:
    """Initialize all application services."""
    _register_configuration()
    _register_ai_models()
    _register_agent_team()
    _register_niche_analysis()
    _register_marketing()
    _register_monetization()
    _register_ui_services()

    # Return a placeholder for tests
    return None
