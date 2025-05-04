"""
"""
Service initialization for the pAIssive_income project.
Service initialization for the pAIssive_income project.


This module provides functions for initializing and configuring services
This module provides functions for initializing and configuring services
used by the project, including dependency injection setup.
used by the project, including dependency injection setup.
"""
"""




import logging
import logging
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


from agent_team import AgentProfile, AgentTeam, ResearchAgent
from agent_team import AgentProfile, AgentTeam, ResearchAgent
from ai_models.adapters import get_adapter_factory
from ai_models.adapters import get_adapter_factory
from ai_models.model_config import ModelConfig
from ai_models.model_config import ModelConfig
from ai_models.model_manager import ModelManager
from ai_models.model_manager import ModelManager
from dependency_container import DependencyContainer, get_container
from dependency_container import DependencyContainer, get_container
from interfaces.agent_interfaces import (IAgentProfile, IAgentTeam,
from interfaces.agent_interfaces import (IAgentProfile, IAgentTeam,
IResearchAgent)
IResearchAgent)
from interfaces.marketing_interfaces import IMarketingStrategy
from interfaces.marketing_interfaces import IMarketingStrategy
from interfaces.model_interfaces import IModelConfig, IModelManager
from interfaces.model_interfaces import IModelConfig, IModelManager
from interfaces.monetization_interfaces import IMonetizationCalculator
from interfaces.monetization_interfaces import IMonetizationCalculator
from interfaces.niche_interfaces import INicheAnalyzer
from interfaces.niche_interfaces import INicheAnalyzer
from marketing.strategy_generator import StrategyGenerator
from marketing.strategy_generator import StrategyGenerator
from monetization.calculator import MonetizationCalculator
from monetization.calculator import MonetizationCalculator
from niche_analysis.niche_analyzer import NicheAnalyzer
from niche_analysis.niche_analyzer import NicheAnalyzer
from ui.service_registry import register_ui_services
from ui.service_registry import register_ui_services


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




def initialize_services(config: Optional[Dict[str, Any]] = None) -> DependencyContainer:
    def initialize_services(config: Optional[Dict[str, Any]] = None) -> DependencyContainer:
    """
    """
    Initialize all services and register them in the dependency container.
    Initialize all services and register them in the dependency container.


    Args:
    Args:
    config: Optional configuration dictionary
    config: Optional configuration dictionary


    Returns:
    Returns:
    Dependency container with registered services
    Dependency container with registered services
    """
    """
    container = get_container()
    container = get_container()


    # Register configuration
    # Register configuration
    _register_configuration(container, config)
    _register_configuration(container, config)


    # Register AI models
    # Register AI models
    _register_ai_models(container)
    _register_ai_models(container)


    # Register agent team
    # Register agent team
    _register_agent_team(container)
    _register_agent_team(container)


    # Register niche analysis
    # Register niche analysis
    _register_niche_analysis(container)
    _register_niche_analysis(container)


    # Register monetization
    # Register monetization
    _register_monetization(container)
    _register_monetization(container)


    # Register marketing
    # Register marketing
    _register_marketing(container)
    _register_marketing(container)


    # Register UI services
    # Register UI services
    register_ui_services()
    register_ui_services()


    logger.info("All services initialized and registered")
    logger.info("All services initialized and registered")
    return container
    return container




    def _register_configuration(
    def _register_configuration(
    container: DependencyContainer, config: Optional[Dict[str, Any]] = None
    container: DependencyContainer, config: Optional[Dict[str, Any]] = None
    ) -> None:
    ) -> None:
    """
    """
    Register configuration in the dependency container.
    Register configuration in the dependency container.


    Args:
    Args:
    container: Dependency container
    container: Dependency container
    config: Optional configuration dictionary
    config: Optional configuration dictionary
    """
    """
    # Register model configuration
    # Register model configuration
    if config and "model_config" in config:
    if config and "model_config" in config:
    model_config = ModelConfig(**config["model_config"])
    model_config = ModelConfig(**config["model_config"])
    else:
    else:
    model_config = ModelConfig.get_default()
    model_config = ModelConfig.get_default()


    container.register(IModelConfig, lambda: model_config, singleton=True)
    container.register(IModelConfig, lambda: model_config, singleton=True)
    logger.info("Registered model configuration")
    logger.info("Registered model configuration")




    def _register_ai_models(container: DependencyContainer) -> None:
    def _register_ai_models(container: DependencyContainer) -> None:
    """
    """
    Register AI model services in the dependency container.
    Register AI model services in the dependency container.


    Args:
    Args:
    container: Dependency container
    container: Dependency container
    """
    """
    # Register model manager
    # Register model manager
    container.register(
    container.register(
    IModelManager,
    IModelManager,
    lambda: ModelManager(config=container.resolve(IModelConfig)),
    lambda: ModelManager(config=container.resolve(IModelConfig)),
    singleton=True,
    singleton=True,
    )
    )


    # Register adapter factory
    # Register adapter factory
    adapter_factory = get_adapter_factory()
    adapter_factory = get_adapter_factory()
    container.register_instance("adapter_factory", adapter_factory)
    container.register_instance("adapter_factory", adapter_factory)


    logger.info("Registered AI model services")
    logger.info("Registered AI model services")




    def _register_agent_team(container: DependencyContainer) -> None:
    def _register_agent_team(container: DependencyContainer) -> None:
    """
    """
    Register agent team services in the dependency container.
    Register agent team services in the dependency container.


    Args:
    Args:
    container: Dependency container
    container: Dependency container
    """
    """
    # Register agent profile
    # Register agent profile
    container.register(
    container.register(
    IAgentProfile, lambda: AgentProfile(name="default"), singleton=True
    IAgentProfile, lambda: AgentProfile(name="default"), singleton=True
    )
    )


    # Register research agent
    # Register research agent
    container.register(
    container.register(
    IResearchAgent,
    IResearchAgent,
    lambda: ResearchAgent(
    lambda: ResearchAgent(
    profile=container.resolve(IAgentProfile),
    profile=container.resolve(IAgentProfile),
    model_manager=container.resolve(IModelManager),
    model_manager=container.resolve(IModelManager),
    ),
    ),
    singleton=True,
    singleton=True,
    )
    )


    # Register agent team
    # Register agent team
    container.register(
    container.register(
    IAgentTeam,
    IAgentTeam,
    lambda: AgentTeam(research_agent=container.resolve(IResearchAgent)),
    lambda: AgentTeam(research_agent=container.resolve(IResearchAgent)),
    singleton=True,
    singleton=True,
    )
    )


    logger.info("Registered agent team services")
    logger.info("Registered agent team services")




    def _register_niche_analysis(container: DependencyContainer) -> None:
    def _register_niche_analysis(container: DependencyContainer) -> None:
    """
    """
    Register niche analysis services in the dependency container.
    Register niche analysis services in the dependency container.


    Args:
    Args:
    container: Dependency container
    container: Dependency container
    """
    """
    # Register niche analyzer
    # Register niche analyzer
    container.register(
    container.register(
    INicheAnalyzer,
    INicheAnalyzer,
    lambda: NicheAnalyzer(agent_team=container.resolve(IAgentTeam)),
    lambda: NicheAnalyzer(agent_team=container.resolve(IAgentTeam)),
    singleton=True,
    singleton=True,
    )
    )


    logger.info("Registered niche analysis services")
    logger.info("Registered niche analysis services")




    def _register_monetization(container: DependencyContainer) -> None:
    def _register_monetization(container: DependencyContainer) -> None:
    """
    """
    Register monetization services in the dependency container.
    Register monetization services in the dependency container.


    Args:
    Args:
    container: Dependency container
    container: Dependency container
    """
    """
    # Register monetization calculator
    # Register monetization calculator
    container.register(
    container.register(
    IMonetizationCalculator, lambda: MonetizationCalculator(), singleton=True
    IMonetizationCalculator, lambda: MonetizationCalculator(), singleton=True
    )
    )


    logger.info("Registered monetization services")
    logger.info("Registered monetization services")




    def _register_marketing(container: DependencyContainer) -> None:
    def _register_marketing(container: DependencyContainer) -> None:
    """
    """
    Register marketing services in the dependency container.
    Register marketing services in the dependency container.


    Args:
    Args:
    container: Dependency container
    container: Dependency container
    """
    """
    # Register marketing strategy generator
    # Register marketing strategy generator
    container.register(
    container.register(
    IMarketingStrategy,
    IMarketingStrategy,
    lambda: StrategyGenerator(agent_team=container.resolve(IAgentTeam)),
    lambda: StrategyGenerator(agent_team=container.resolve(IAgentTeam)),
    singleton=True,
    singleton=True,
    )
    )


    logger.info("Registered marketing services")
    logger.info("Registered marketing services")