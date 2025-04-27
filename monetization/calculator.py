"""
Monetization calculator for the Monetization module.

This module provides the MonetizationCalculator class that calculates monetization metrics.
"""

import os
import logging
import math
from typing import Dict, List, Any, Optional

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from interfaces.monetization_interfaces import IMonetizationCalculator
from monetization.errors import MonetizationError

# Set up logging
logger = logging.getLogger(__name__)


class MonetizationCalculator(IMonetizationCalculator):
    """
    Monetization calculator class.
    
    This class calculates monetization metrics for AI tools.
    """
    
    def __init__(self):
        """Initialize the monetization calculator."""
        logger.debug("Created monetization calculator")
    
    def calculate_subscription_revenue(self, tiers: List[Dict[str, Any]], user_counts: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate subscription revenue.
        
        Args:
            tiers: List of subscription tier dictionaries
            user_counts: Dictionary of user counts by tier
            
        Returns:
            Revenue dictionary
        """
        logger.info("Calculating subscription revenue")
        
        try:
            # Calculate revenue for each tier
            tier_revenue = {}
            total_revenue = 0
            total_users = 0
            
            for tier in tiers:
                tier_id = tier.get("id")
                tier_name = tier.get("name")
                price = tier.get("price", 0)
                
                if not tier_id:
                    logger.warning(f"Tier missing ID: {tier}")
                    continue
                
                # Get user count for this tier
                user_count = user_counts.get(tier_id, 0)
                total_users += user_count
                
                # Calculate revenue for this tier
                revenue = price * user_count
                total_revenue += revenue
                
                tier_revenue[tier_id] = {
                    "tier_name": tier_name,
                    "price": price,
                    "user_count": user_count,
                    "revenue": revenue
                }
            
            # Calculate average revenue per user
            arpu = total_revenue / total_users if total_users > 0 else 0
            
            result = {
                "total_revenue": total_revenue,
                "total_users": total_users,
                "arpu": arpu,
                "tier_revenue": tier_revenue
            }
            
            logger.info(f"Calculated subscription revenue: ${total_revenue:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating subscription revenue: {e}")
            raise MonetizationError("Error calculating subscription revenue", original_exception=e)
    
    def calculate_costs(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate costs for a solution.
        
        Args:
            solution: Solution dictionary
            
        Returns:
            Costs dictionary
        """
        logger.info("Calculating costs")
        
        try:
            # Extract cost factors from the solution
            infrastructure_cost = solution.get("infrastructure_cost", 0)
            development_cost = solution.get("development_cost", 0)
            marketing_cost = solution.get("marketing_cost", 0)
            support_cost = solution.get("support_cost", 0)
            
            # Calculate total costs
            total_fixed_costs = development_cost
            total_variable_costs = infrastructure_cost + marketing_cost + support_cost
            total_costs = total_fixed_costs + total_variable_costs
            
            result = {
                "fixed_costs": {
                    "development": development_cost,
                    "total": total_fixed_costs
                },
                "variable_costs": {
                    "infrastructure": infrastructure_cost,
                    "marketing": marketing_cost,
                    "support": support_cost,
                    "total": total_variable_costs
                },
                "total_costs": total_costs
            }
            
            logger.info(f"Calculated costs: ${total_costs:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating costs: {e}")
            raise MonetizationError("Error calculating costs", original_exception=e)
    
    def calculate_profit(self, revenue: Dict[str, Any], costs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate profit.
        
        Args:
            revenue: Revenue dictionary
            costs: Costs dictionary
            
        Returns:
            Profit dictionary
        """
        logger.info("Calculating profit")
        
        try:
            # Extract revenue and costs
            total_revenue = revenue.get("total_revenue", 0)
            total_costs = costs.get("total_costs", 0)
            
            # Calculate profit
            profit = total_revenue - total_costs
            profit_margin = (profit / total_revenue) * 100 if total_revenue > 0 else 0
            
            result = {
                "total_revenue": total_revenue,
                "total_costs": total_costs,
                "profit": profit,
                "profit_margin": profit_margin
            }
            
            logger.info(f"Calculated profit: ${profit:.2f} ({profit_margin:.2f}%)")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating profit: {e}")
            raise MonetizationError("Error calculating profit", original_exception=e)
    
    def project_growth(self, initial_users: int, growth_rate: float, months: int) -> Dict[str, Any]:
        """
        Project user growth.
        
        Args:
            initial_users: Initial number of users
            growth_rate: Monthly growth rate
            months: Number of months to project
            
        Returns:
            Growth projection dictionary
        """
        logger.info(f"Projecting growth for {months} months with {growth_rate:.2f}% monthly growth rate")
        
        try:
            # Calculate user growth for each month
            monthly_users = []
            current_users = initial_users
            
            for month in range(1, months + 1):
                # Calculate users for this month
                current_users = math.floor(current_users * (1 + growth_rate))
                
                monthly_users.append({
                    "month": month,
                    "users": current_users
                })
            
            # Calculate total growth
            total_growth = (current_users / initial_users - 1) * 100 if initial_users > 0 else 0
            
            result = {
                "initial_users": initial_users,
                "final_users": current_users,
                "growth_rate": growth_rate,
                "months": months,
                "total_growth": total_growth,
                "monthly_users": monthly_users
            }
            
            logger.info(f"Projected growth: {total_growth:.2f}% over {months} months")
            return result
            
        except Exception as e:
            logger.error(f"Error projecting growth: {e}")
            raise MonetizationError("Error projecting growth", original_exception=e)
