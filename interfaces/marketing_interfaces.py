"""
Interfaces for the Marketing module.

This module provides interfaces for the marketing components to enable dependency injection
and improve testability and maintainability.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class IPersonaCreator(ABC):
    """Interface for persona creator."""
    
    @abstractmethod
    def create_persona(self, name: str, description: str, demographics: Dict[str, Any], pain_points: List[str], goals: List[str]) -> Dict[str, Any]:
        """
        Create a user persona.
        
        Args:
            name: Persona name
            description: Persona description
            demographics: Demographic information
            pain_points: List of pain points
            goals: List of goals
            
        Returns:
            User persona dictionary
        """
        pass
    
    @abstractmethod
    def analyze_persona(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a user persona.
        
        Args:
            persona: User persona dictionary
            
        Returns:
            Persona analysis dictionary
        """
        pass
    
    @abstractmethod
    def get_persona_categories(self) -> List[str]:
        """
        Get a list of persona categories.
        
        Returns:
            List of persona categories
        """
        pass


class IMarketingStrategy(ABC):
    """Interface for marketing strategy."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the strategy name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get the strategy description."""
        pass
    
    @property
    @abstractmethod
    def channel_type(self) -> str:
        """Get the channel type."""
        pass
    
    @abstractmethod
    def create_strategy(self, target_persona: Dict[str, Any], goals: List[str]) -> Dict[str, Any]:
        """
        Create a marketing strategy.
        
        Args:
            target_persona: Target user persona
            goals: List of marketing goals
            
        Returns:
            Marketing strategy dictionary
        """
        pass
    
    @abstractmethod
    def get_tactics(self) -> List[Dict[str, Any]]:
        """
        Get marketing tactics.
        
        Returns:
            List of marketing tactic dictionaries
        """
        pass
    
    @abstractmethod
    def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get marketing metrics.
        
        Returns:
            List of marketing metric dictionaries
        """
        pass
    
    @abstractmethod
    def get_full_strategy(self) -> Dict[str, Any]:
        """
        Get the full marketing strategy.
        
        Returns:
            Dictionary with complete strategy details
        """
        pass


class IContentTemplate(ABC):
    """Interface for content template."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Get the template ID."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the template name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get the template description."""
        pass
    
    @property
    @abstractmethod
    def content_type(self) -> str:
        """Get the content type."""
        pass
    
    @abstractmethod
    def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for the content.
        
        Returns:
            Dictionary with outline details
        """
        pass
    
    @abstractmethod
    def generate_content(self, topic: str = "", target_audience: str = "", tone: str = "", keywords: List[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate content based on the template.
        
        Args:
            topic: Topic of the content
            target_audience: Target audience for the content
            tone: Tone of the content
            keywords: Keywords for the content
            **kwargs: Additional keyword arguments
            
        Returns:
            Dictionary with generated content
        """
        pass
    
    @abstractmethod
    def add_section(self, name: str = "", description: str = "", content_type: str = "text", placeholder: str = "", required: bool = False, section_type: str = "", title: str = "", content: str = "") -> Dict[str, Any]:
        """
        Add a section to the content template.
        
        Args:
            name: Name of the section
            description: Description of the section
            content_type: Type of content
            placeholder: Placeholder text for the section
            required: Whether the section is required
            section_type: Type of section
            title: Title of the section
            content: Optional content for the section
            
        Returns:
            Dictionary with section details
        """
        pass
    
    @abstractmethod
    def get_seo_recommendations(self) -> Dict[str, Any]:
        """
        Get SEO recommendations for the content.
        
        Returns:
            Dictionary with SEO recommendations
        """
        pass
