"""
Monetization calculator for the Monetization module.

This module provides the MonetizationCalculator class that calculates monetization metrics.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
import math
from typing import Any, Dict, List

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

    def calculate_subscription_revenue(
        self, tiers: List[Dict[str, Any]], user_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Calculate subscription revenue across multiple pricing tiers.

        This algorithm performs a comprehensive revenue calculation by analyzing each
        subscription tier and its associated user base. The calculation workflow follows
        a multi - stage process:

        1. INITIALIZATION:
           - Create structures for tracking tier - specific revenue details
           - Initialize accumulators for user counts and revenue totals

        2. TIER - BY - TIER ANALYSIS:
           - For each pricing tier, extract key attributes (ID, name, price)
           - Look up the corresponding user count for that tier
           - Calculate tier - specific revenue (price × user count)
           - Aggregate metrics into the running totals
           - Store tier - specific details for reporting

        3. DERIVATION OF KEY METRICS:
           - Calculate Average Revenue Per User (ARPU) as total revenue / total users
           - Handle edge case when total users is zero to prevent division by zero

        4. COMPREHENSIVE RESULT GENERATION:
           - Create a structured report containing tier - specific breakdowns
           - Include aggregate metrics like total revenue, total users, and ARPU
           - Provide detailed logging for debugging and tracking

        5. ERROR HANDLING AND SAFETY:
           - Validate tier data integrity (e.g., check for missing tier IDs)
           - \
               Use a try - except pattern to catch and properly report any calculation errors
           - \
               Transform unexpected errors into domain - specific MonetizationError objects

        The algorithm is designed to handle multiple subscription models including:
        - Freemium models (with free and paid tiers)
        - Multi - tiered subscription models (basic, pro, premium)
        - Enterprise pricing models

        Args:
            tiers: List of subscription tier dictionaries, each containing:
                  - id: Unique identifier for the tier
                  - name: Display name of the tier
                  - price: Monetary cost of the tier (per user / month)
            user_counts: Dictionary mapping tier IDs to the number of users in that tier

        Returns:
            Revenue dictionary containing:
            - total_revenue: Sum of revenue across all tiers
            - total_users: Sum of users across all tiers
            - arpu: Average Revenue Per User (total_revenue / total_users)
            - tier_revenue: Dictionary of tier - specific revenue details

        Raises:
            MonetizationError: If an error occurs during revenue calculation
        """
        logger.info("Calculating subscription revenue")

        try:
            # STAGE 1: Initialize tracking structures and accumulators
            # tier_revenue stores detailed breakdown for each tier
            # total_revenue and total_users track aggregate metrics
            tier_revenue = {}
            total_revenue = 0
            total_users = 0

            # STAGE 2: Process each tier to calculate tier - specific and aggregate metrics
            for tier in tiers:
                # Extract essential tier attributes
                tier_id = tier.get("id")
                tier_name = tier.get("name")
                price = tier.get("price", 0)  # Default to 0 if price not specified

                # Data validation - skip tiers with missing IDs
                if not tier_id:
                    logger.warning(f"Tier missing ID: {tier}")
                    continue

                # Retrieve user count for this tier (default to 0 if not specified)
                user_count = user_counts.get(tier_id, 0)

                # Add to total user count (including free tier users)
                total_users += user_count

                # Calculate revenue contribution for this specific tier
                # For free tiers, this will be $0 as price = 0
                revenue = price * user_count

                # Add to total revenue across all tiers
                total_revenue += revenue

                # Store detailed revenue information for this tier
                tier_revenue[tier_id] = {
                    "tier_name": tier_name,  # Human - readable name
                    "price": price,  # Price per user
                    "user_count": user_count,  # Number of users
                    "revenue": revenue,  # Total revenue from this tier
                }

            # STAGE 3: Calculate derived metrics - Average Revenue Per User (ARPU)
            # Handle division by zero case when there are no users
            arpu = total_revenue / total_users if total_users > 0 else 0

            # STAGE 4: Construct the comprehensive result object with all metrics
            result = {
                "total_revenue": total_revenue,  # Sum of all tier revenues
                "total_users": total_users,  # Sum of all tier user counts
                "arpu": arpu,  # Average Revenue Per User
                "tier_revenue": tier_revenue,  # Detailed breakdown by tier
            }

            # Log the successful calculation for monitoring
            logger.info(f"Calculated subscription revenue: ${total_revenue:.2f}")

            return result

        except Exception as e:
            # STAGE 5: Handle and properly transform any unexpected errors
            logger.error(f"Error calculating subscription revenue: {e}")
            raise MonetizationError("Error calculating subscription revenue", 
                original_exception=e)

    def calculate_costs(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive cost breakdown for a business solution.

        This algorithm implements a systematic cost analysis framework that processes
        solution parameters to produce a structured cost breakdown. The implementation
        follows these key stages:

        1. DATA EXTRACTION AND NORMALIZATION:
           - Extracts key cost components from the solution dictionary
           - Applies defaults (zero) for missing cost values
           - Ensures consistent data types for calculation
           - Logs the calculation attempt for auditing

        2. COST CATEGORIZATION AND AGGREGATION:
           - Categorizes costs into fixed versus variable components
           - Classifies development costs as fixed (one - time) expenses
           - Classifies infrastructure, marketing, 
               and support as variable (ongoing) expenses
           - Calculates subtotals for each cost category
           - Determines the total overall cost

        3. HIERARCHICAL RESULT COMPOSITION:
           - Creates a nested structure reflecting cost categories
           - Maintains individual cost components for granular analysis
           - Provides category subtotals for intermediate reporting
           - Includes total costs for high - level decision making
           - Logs the successful calculation with the final cost figure

        4. ERROR HANDLING AND SAFETY:
           - Implements defensive programming with exception handling
           - \
               Transforms generic exceptions into domain - specific MonetizationError objects
           - Includes detailed error logging for troubleshooting

        The algorithm supports multiple cost analysis scenarios including:
        - Minimum viable product (MVP) cost estimation
        - Ongoing operational cost forecasting
        - Break - even analysis when combined with revenue projections
        - Fixed vs. variable cost ratio analysis for scaling planning

        Args:
            solution: Solution dictionary containing cost parameters:
                     - infrastructure_cost: Ongoing infrastructure and hosting costs
                     - development_cost: One - time development and implementation costs
                     - marketing_cost: Ongoing marketing and customer acquisition costs
                     - support_cost: Ongoing customer support and maintenance costs

        Returns:
            A hierarchical costs dictionary containing:
            - fixed_costs: Dictionary of one - time costs:
              - development: Development cost value
              - total: Total fixed costs
            - variable_costs: Dictionary of ongoing costs:
              - infrastructure: Infrastructure cost value
              - marketing: Marketing cost value
              - support: Support cost value
              - total: Total variable costs
            - total_costs: Sum of all fixed and variable costs

        Raises:
            MonetizationError: If an error occurs during cost calculation
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
                    "total": total_fixed_costs,
                },
                "variable_costs": {
                    "infrastructure": infrastructure_cost,
                    "marketing": marketing_cost,
                    "support": support_cost,
                    "total": total_variable_costs,
                },
                "total_costs": total_costs,
            }

            logger.info(f"Calculated costs: ${total_costs:.2f}")
            return result

        except Exception as e:
            logger.error(f"Error calculating costs: {e}")
            raise MonetizationError("Error calculating costs", original_exception=e)

    def calculate_profit(self, revenue: Dict[str, Any], costs: Dict[str, 
        Any]) -> Dict[str, Any]:
        """
        Calculate profit and profitability metrics by comparing revenue against costs.

        This algorithm implements a comprehensive profitability analysis system that processes
        revenue and \
            cost data to produce key business performance indicators. The implementation
        follows these key stages:

        1. DATA EXTRACTION AND VALIDATION:
           - Extracts total revenue from the revenue dictionary
           - Extracts total costs from the costs dictionary
           - Performs silent validation with defaults to handle missing data
           - Logs the calculation attempt for auditing and debugging

        2. CORE PROFITABILITY CALCULATIONS:
           - Computes absolute profit as the difference between revenue and costs
           - Derives profit margin as a percentage of revenue
           - Implements safe division logic to handle edge cases (zero revenue)
           - Maintains numerical precision throughout calculations

        3. COMPREHENSIVE RESULT COMPOSITION:
           - \
               Creates a structured profitability report with both raw values and derived metrics
           - Maintains data lineage by including source values (revenue and costs)
           - Formats profit margin as a percentage for business reporting
           - Provides context through detailed logging

        4. ERROR HANDLING AND SAFETY:
           - Implements defensive programming with try - except pattern
           - \
               Transforms generic exceptions into domain - specific MonetizationError objects
           - Includes detailed error logging with original exception context

        The algorithm provides critical financial intelligence for business decision - making:
        - Absolute profit indicates short - term financial health
        - Profit margin enables comparison across different business scales
        - Tracking these metrics over time reveals business efficiency trends
        - Combined with growth projections, they support strategic planning

        Args:
            revenue: Revenue dictionary containing at minimum:
                    - total_revenue: The aggregate revenue amount
            costs: Costs dictionary containing at minimum:
                  - total_costs: The aggregate cost amount

        Returns:
            A profitability dictionary containing:
            - total_revenue: The input total revenue value
            - total_costs: The input total costs value
            - profit: The calculated absolute profit (revenue - costs)
            - \
                profit_margin: The calculated relative profit (profit / revenue) as a percentage

        Raises:
            MonetizationError: If an error occurs during profit calculation
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
                "profit_margin": profit_margin,
            }

            logger.info(f"Calculated profit: ${profit:.2f} ({profit_margin:.2f}%)")
            return result

        except Exception as e:
            logger.error(f"Error calculating profit: {e}")
            raise MonetizationError("Error calculating profit", original_exception=e)

    def project_growth(self, initial_users: int, growth_rate: float, 
        months: int) -> Dict[str, Any]:
        """
        Project user growth over time using a compound growth model.

        This algorithm implements a time - \
            series growth projection system that forecasts user
        growth over a specified period. The implementation follows these key stages:

        1. INITIALIZATION AND PARAMETER VALIDATION:
           - Takes the starting user count, growth rate, and projection timeframe
           - Logs the operation for tracking and auditing purposes
           - Validates that the projection period is reasonable

        2. TIME - SERIES GROWTH CALCULATION:
           - Implements a discrete compound growth formula: Users(t + \
               1) = Users(t) * (1 + growth_rate)
           - Applies a mathematical floor function to maintain whole user counts
           - Produces month - by - month projections in a sequential manner
           - Creates a structured time series with both time indices and user counts

        3. AGGREGATION AND DERIVED METRICS:
           - Calculates the total percentage growth over the entire period
           - Implements a safe division check to handle edge case of zero initial users
           - \
               Combines initial parameters and calculated results into a comprehensive output

        4. ERROR HANDLING AND LOGGING:
           - Implements a defensive try - except pattern for robustness
           - \
               Transforms generic exceptions into domain - specific MonetizationError objects
           - Provides detailed error logging to facilitate troubleshooting
           - Ensures successful projections are logged with summary metrics

        The compound growth model is particularly suitable for early - \
            stage user acquisition
        where growth tends to follow an exponential rather than linear pattern. The algorithm
        ensures integrity by:

        - Maintaining integer user counts (no fractional users)
        - Providing a complete historical projection (not just final numbers)
        - Calculating relative growth metrics regardless of absolute scale
        - Properly handling edge cases like zero initial users

        Args:
            initial_users: Starting user base at month 0
            growth_rate: Monthly compound growth rate as a decimal (e.g., 
                0.05 for 5% growth)
            months: Number of months to project forward

        Returns:
            A comprehensive growth projection dictionary containing:
            - initial_users: The starting user count
            - final_users: The projected user count after the specified months
            - growth_rate: The monthly growth rate used in calculations
            - months: The projection timeframe in months
            - total_growth: The percentage increase from initial to final users
            - monthly_users: A time series of monthly user counts with month indices

        Raises:
            MonetizationError: If an error occurs during the projection calculation
        """
        logger.info(
            f"Projecting growth for {months} months with {growth_rate:.2f}% monthly" \
             + "growth rate"
        )

        try:
            # STAGE 1: Prepare the growth model and initialize tracking structures
            # monthly_users will hold the time series data for each projection month
            # current_users tracks the running user count as we step through time
            monthly_users = []
            current_users = initial_users

            # STAGE 2: Generate month - by - month projections using compound growth formula
            # For each future month, calculate the new user count and store in time series
            for month in range(1, months + 1):
                # Apply compound growth formula with integer conversion
                # This ensures we maintain whole user counts (no fractional users)
                current_users = math.floor(current_users * (1 + growth_rate))

                # Record this month's projection in the time series
                # Include both the time index and calculated user count
                monthly_users.append(
                    {
                        "month": month,  # Time index (1 - based for readability)
                        "users": current_users,  # Projected user count at this time
                    }
                )

            # STAGE 3: Calculate aggregate metrics across the entire projection period
            # Determine total percentage growth from start to end (handling zero case)
            total_growth = (current_users / initial_users - \
                1) * 100 if initial_users > 0 else 0

            # STAGE 4: Compile the comprehensive projection results
            # Combine input parameters, calculated series, and derived metrics
            result = {
                "initial_users": initial_users,  # Starting user count
                "final_users": current_users,  
                    # Ending user count after projection period
                "growth_rate": growth_rate,  # Monthly growth rate used
                "months": months,  # Total projection period
                "total_growth": total_growth,  # Percentage growth over entire period
                "monthly_users": monthly_users,  # Complete time series of projections
            }

            # Log successful projection completion with summary metrics
            logger.info(f"Projected growth: {total_growth:.2f}% over {months} months")
            return result

        except Exception as e:
            # STAGE 5: Handle and transform any calculation errors
            # Convert generic exceptions to domain - specific error types with context
            logger.error(f"Error projecting growth: {e}")
            raise MonetizationError("Error projecting growth", original_exception=e)
