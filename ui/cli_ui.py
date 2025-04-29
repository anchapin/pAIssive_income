"""
Command Line Interface for the pAIssive Income project.

This module provides a command line interface for interacting with the pAIssive Income framework.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)

class CommandLineInterface:
    """
    Command Line Interface for the pAIssive Income project.
    """
    
    def __init__(self, agent_team=None, model_manager=None, subscription_manager=None):
        """
        Initialize the Command Line Interface.
        
        Args:
            agent_team: Agent team instance
            model_manager: Model manager instance
            subscription_manager: Subscription manager instance
        """
        self.agent_team = agent_team
        self.model_manager = model_manager
        self.subscription_manager = subscription_manager
        
        # Initialize state
        self.current_niches = []
        self.current_solution = None
        self.current_monetization = None
        self.current_marketing_plan = None
        
        logger.info("CommandLineInterface initialized")
    
    def handle_command(self, command_str: str) -> str:
        """
        Handle a command.
        
        Args:
            command_str: Command string
            
        Returns:
            Response message
        """
        logger.info(f"Handling command: {command_str}")
        
        # Parse the command
        parts = command_str.strip().split()
        if not parts:
            return "No command specified"
        
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Process the command
        return self.process_command(command, args)
    
    def process_command(self, command: str, args: List[str]) -> str:
        """
        Process a command.
        
        Args:
            command: Command to process
            args: Command arguments
            
        Returns:
            Response message
        """
        logger.info(f"Processing command: {command} with args: {args}")
        
        # Handle different commands
        if command == "help":
            return self._handle_help()
        elif command == "analyze":
            return self._handle_analyze(args)
        elif command == "select":
            return self._handle_select(args)
        elif command == "develop":
            return self._handle_develop(args)
        elif command == "create":
            return self._handle_create(args)
        elif command == "export":
            return self._handle_export(args)
        else:
            return f"Unknown command: {command}"
    
    def _handle_help(self) -> str:
        """
        Handle the help command.
        
        Returns:
            Help message
        """
        return """
        Available commands:
        - help: Show this help message
        - analyze <market_segments...>: Analyze market segments to find niches
        - select niche <index>: Select a niche by index
        - develop solution: Develop a solution for the selected niche
        - create monetization: Create a monetization strategy for the solution
        - create marketing: Create a marketing plan
        - export plan: Export the complete plan
        """
    
    def _handle_analyze(self, args: List[str]) -> str:
        """
        Handle the analyze command.
        
        Args:
            args: Command arguments
            
        Returns:
            Response message
        """
        if not args:
            return "Please specify market segments to analyze"
        
        # Use the agent team to analyze the market segments
        self.current_niches = self.agent_team.run_niche_analysis(args)
        
        # Format the response
        response = f"Found {len(self.current_niches)} niches:\n"
        for i, niche in enumerate(self.current_niches):
            response += f"{i}: {niche['name']} (score: {niche.get('opportunity_score', 'N/A')})\n"
        
        return response
    
    def _handle_select(self, args: List[str]) -> str:
        """
        Handle the select command.
        
        Args:
            args: Command arguments
            
        Returns:
            Response message
        """
        if not args or len(args) < 2:
            return "Please specify what to select and its index"
        
        select_type = args[0]
        try:
            index = int(args[1])
        except ValueError:
            return f"Invalid index: {args[1]}"
        
        if select_type == "niche":
            if not self.current_niches:
                return "No niches available. Run 'analyze' first."
            
            if index < 0 or index >= len(self.current_niches):
                return f"Invalid niche index: {index}"
            
            # Select the niche
            selected_niche = self.current_niches[index]
            return f"Selected niche: {selected_niche['name']}"
        else:
            return f"Unknown selection type: {select_type}"
    
    def _handle_develop(self, args: List[str]) -> str:
        """
        Handle the develop command.
        
        Args:
            args: Command arguments
            
        Returns:
            Response message
        """
        if not args or args[0] != "solution":
            return "Please specify what to develop (e.g., 'develop solution')"
        
        if not self.current_niches:
            return "No niches available. Run 'analyze' first."
        
        # Use the agent team to develop a solution
        self.current_solution = self.agent_team.develop_solution(self.current_niches[0])
        
        # Format the response
        response = f"Developed solution: {self.current_solution['name']}\n"
        response += f"Description: {self.current_solution.get('description', 'N/A')}\n"
        response += "Features:\n"
        for feature in self.current_solution.get('features', []):
            response += f"- {feature['name']}\n"
        
        return response
    
    def _handle_create(self, args: List[str]) -> str:
        """
        Handle the create command.
        
        Args:
            args: Command arguments
            
        Returns:
            Response message
        """
        if not args:
            return "Please specify what to create"
        
        create_type = args[0]
        
        if create_type == "monetization":
            if not self.current_solution:
                return "No solution available. Run 'develop solution' first."
            
            # Use the agent team to create a monetization strategy
            self.current_monetization = self.agent_team.create_monetization_strategy(self.current_solution)
            
            # Format the response
            response = f"Created monetization strategy: {self.current_monetization['name']}\n"
            response += "Subscription tiers:\n"
            for tier in self.current_monetization.get('subscription_model', {}).get('tiers', []):
                response += f"- {tier['name']}: ${tier.get('price_monthly', 0)}/month\n"
            
            return response
        
        elif create_type == "marketing":
            if not self.current_solution:
                return "No solution available. Run 'develop solution' first."
            
            if not self.current_monetization:
                return "No monetization strategy available. Run 'create monetization' first."
            
            # Use the agent team to create a marketing plan
            self.current_marketing_plan = self.agent_team.create_marketing_plan(
                self.current_niches[0] if self.current_niches else None,
                self.current_solution,
                self.current_monetization
            )
            
            # Format the response
            response = f"Created marketing plan: {self.current_marketing_plan['name']}\n"
            response += f"Target audience: {self.current_marketing_plan.get('target_audience', 'N/A')}\n"
            response += "Channels:\n"
            for channel in self.current_marketing_plan.get('channels', []):
                response += f"- {channel}\n"
            
            return response
        
        else:
            return f"Unknown creation type: {create_type}"
    
    def _handle_export(self, args: List[str]) -> str:
        """
        Handle the export command.
        
        Args:
            args: Command arguments
            
        Returns:
            Response message
        """
        if not args or args[0] != "plan":
            return "Please specify what to export (e.g., 'export plan')"
        
        if not self.current_solution:
            return "No solution available. Run 'develop solution' first."
        
        if not self.current_monetization:
            return "No monetization strategy available. Run 'create monetization' first."
        
        if not self.current_marketing_plan:
            return "No marketing plan available. Run 'create marketing' first."
        
        # Create the plan
        plan = {
            'niche': self.current_niches[0] if self.current_niches else None,
            'solution': self.current_solution,
            'monetization': self.current_monetization,
            'marketing': self.current_marketing_plan
        }
        
        # Export the plan (mock implementation)
        return f"Exported plan to plan.json"
