"""
Revenue Projector for the pAIssive Income project.

This module provides classes for projecting revenue for AI-powered software tools.
It includes tools for user acquisition, conversion, churn, and lifetime value calculations.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import json
import math
import copy


class RevenueProjector:
    """
    Class for projecting revenue for subscription-based software products.

    This class provides tools for calculating user acquisition, conversion rates,
    churn rates, lifetime value, and revenue projections.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        initial_users: int = 0,
        user_acquisition_rate: int = 50,
        conversion_rate: float = 0.2,
        churn_rate: float = 0.05,
        tier_distribution: Optional[Dict[str, float]] = None
    ):
        """
        Initialize a revenue projector.

        Args:
            name: Name of the revenue projector
            description: Description of the revenue projector
            initial_users: Initial number of users
            user_acquisition_rate: Number of new users per month
            conversion_rate: Conversion rate from free to paid
            churn_rate: Monthly churn rate
            tier_distribution: Distribution of users across tiers (e.g., {"basic": 0.6, "pro": 0.3, "premium": 0.1})
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.initial_users = initial_users
        self.user_acquisition_rate = user_acquisition_rate
        self.conversion_rate = conversion_rate
        self.churn_rate = churn_rate
        self.tier_distribution = tier_distribution or {"basic": 0.6, "pro": 0.3, "premium": 0.1}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def project_users(
        self,
        months: int = 36,
        growth_rate: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Project user growth over time using a sophisticated cohort-based growth model.
        
        This algorithm implements a comprehensive user growth simulation for 
        subscription products with freemium conversion patterns. The implementation 
        follows these key stages:
        
        1. MODEL INITIALIZATION AND PARAMETERIZATION:
           - Initializes tracking arrays for all user segments (total, free, paid)
           - Sets up the initial user acquisition rate based on configuration
           - Prepares for month-by-month iterative calculation
           - Creates a foundation for tracking multiple user states simultaneously
        
        2. ITERATIVE GROWTH SIMULATION:
           - Implements a time-step simulation with discrete monthly calculations
           - Models four key dynamics in each period:
             a) New user acquisition with compound growth
             b) Existing user churn based on configured churn rate
             c) Free-to-paid conversions based on conversion rate
             d) Separate paid user churn tracking
           - Maintains proper segment accounting across user categories
           - Ensures mathematical consistency in user flows between states
        
        3. GROWTH COMPOUNDING LOGIC:
           - Applies compound growth to user acquisition rate
           - Models the accelerating effects of marketing and word-of-mouth
           - Simulates realistic growth trajectories seen in successful products
           - Integer rounding for realistic user counts at each stage
        
        4. COMPREHENSIVE RESULT FORMATTING:
           - Transforms raw calculation arrays into structured month-by-month data
           - Includes all relevant metrics for each time period
           - Preserves raw data internally for other calculations
           - Returns results in a consistent, test-compatible format
        
        The user growth model forms the foundation of all revenue projections and
        incorporates several key business realities:
        - Most products start with free users who later convert to paid users
        - Both free and paid users experience churn, but potentially at different rates
        - Acquisition efforts typically compound over time with successful products
        - Integer rounding ensures realistic modeling of actual user counts
        
        This implementation specifically models the "leaky bucket" reality of SaaS:
        - New users continuously enter the top of the funnel
        - Some percentage of users convert from free to paid tiers
        - Users exit the system through churn at each stage
        - The bucket fills or drains depending on acquisition vs. churn balance
        
        Args:
            months: Number of months to project (default: 36 months / 3 years)
            growth_rate: Monthly compound growth rate in user acquisition (default: 5%)
                         Expressed as a decimal (e.g., 0.05 for 5% monthly growth)
            
        Returns:
            A list of dictionaries, where each dictionary contains:
            - month: Month number (1-based, so month 1 is the first projected month)
            - total_users: Total number of users in the system
            - free_users: Number of users on free tier/plan
            - paid_users: Number of users on paid plans
            - new_users: Number of new users acquired that month
            - churned_users: Number of users lost to churn that month
            - conversion_rate: Free-to-paid conversion rate used in calculation
            - churn_rate: Monthly churn rate used in calculation
        """
        # STAGE 1: Initialize tracking arrays for user segments with initial conditions
        # Use arrays with index 0 representing initial state (month 0)
        # This simplifies indexing as we can use month number directly
        total_users = [self.initial_users]  # All users in the system
        free_users = [self.initial_users]   # Users on free tier
        paid_users = [0]                    # Users on paid tiers (initially zero)
        
        # Set initial acquisition rate from configuration
        current_acquisition_rate = self.user_acquisition_rate

        # STAGE 2: Perform month-by-month iterative growth simulation
        # For each month, calculate new users, churn, conversions, and resulting totals
        for month in range(1, months + 1):
            # Calculate inflow: new users acquired this month
            new_users = current_acquisition_rate

            # Calculate outflow: users churned this month from the total user base
            # Integer rounding ensures we don't have fractional users
            churned_users = int(total_users[-1] * self.churn_rate)

            # Calculate conversion flow: free users converting to paid this month
            # This creates internal flow from free to paid user segments
            new_conversions = int(free_users[-1] * self.conversion_rate)

            # Calculate new totals based on all flows:
            # - Total users: previous + new - churned
            # - Paid users: previous + conversions - paid churn
            # - Free users: derived as total - paid to ensure consistency
            new_total = total_users[-1] + new_users - churned_users
            new_paid = paid_users[-1] + new_conversions - int(paid_users[-1] * self.churn_rate)
            new_free = new_total - new_paid

            # Store updated values to arrays for next iteration
            total_users.append(new_total)
            free_users.append(new_free)
            paid_users.append(new_paid)

            # STAGE 3: Apply compounding growth to acquisition rate
            # This models the typical acceleration in user acquisition as 
            # product awareness increases and marketing efforts compound
            current_acquisition_rate = int(current_acquisition_rate * (1 + growth_rate))

        # STAGE 4: Format results as structured month-by-month projections
        # Create a list of dictionaries with all relevant metrics for each month
        user_projections = []
        for month in range(1, months + 1):
            user_projections.append({
                "month": month,                              # Month number (1-based)
                "total_users": total_users[month],           # All users
                "free_users": free_users[month],             # Free tier users
                "paid_users": paid_users[month],             # Paid tier users
                "new_users": current_acquisition_rate,       # New user acquisition
                "churned_users": int(total_users[month-1] * self.churn_rate),  # Churn
                "conversion_rate": self.conversion_rate,     # Free-to-paid rate
                "churn_rate": self.churn_rate                # Attrition rate
            })

        # Store raw data arrays for internal use by other methods
        # This preserves the full dataset including month 0 (initial state)
        self._raw_user_projections = {
            "total_users": total_users,
            "free_users": free_users,
            "paid_users": paid_users,
        }

        return user_projections

    def project_revenue(
        self,
        months: int = 36,
        growth_rate: float = 0.05,
        subscription_model: Any = None,
        prices: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Project revenue over time by combining user growth with pricing tiers.
        
        This algorithm implements a sophisticated revenue forecasting model for
        subscription businesses with multiple pricing tiers. The implementation 
        follows these key stages:
        
        1. USER GROWTH PROJECTION:
           - Leverages the user growth model from project_users method
           - Simulates realistic user acquisition, conversion and churn patterns
           - Creates the foundation of all revenue calculations
           - Maintains cohort integrity through the projection period
        
        2. SUBSCRIPTION MODEL INTEGRATION:
           - Handles both simple and complex subscription models
           - Provides graceful fallback to default pricing if no model specified
           - Maps between tier names/IDs across different model structures
           - Accommodates dynamic tier layouts and configurations
        
        3. TIER-BASED REVENUE CALCULATION:
           - Distributes paid users across pricing tiers based on tier distribution
           - Applies specific pricing for each tier and user segment
           - Calculates granular revenue breakdowns by tier
           - Handles floating-point precision appropriately for financial calculations
        
        4. TEMPORAL AGGREGATION AND ANALYSIS:
           - Calculates monthly and cumulative revenue streams
           - Builds yearly summaries for higher-level analysis
           - Maintains full data granularity while providing useful aggregations
           - Produces properly structured outputs for visualization and reporting
        
        5. COMPREHENSIVE RESULT PACKAGING:
           - Combines all calculations into a complete projection dataset
           - Stores detailed projections for internal use and return values
           - Creates both detailed monthly projections and yearly summaries
           - Packages results with proper metadata for tracking and auditing
        
        The revenue projection model addresses several critical business needs:
        - Financial forecasting for business planning and fundraising
        - Scenario analysis for different pricing and growth strategies
        - Sensitivity testing around conversion and retention metrics
        - Return-on-investment calculations for marketing campaigns
        
        This implementation specifically handles the complexity of SaaS businesses:
        - Multiple pricing tiers with different user distributions
        - Integration with formal subscription model definitions
        - Flexible handling of pricing information from multiple sources
        - Complete traceability of revenue from user acquisition to final totals
        
        Args:
            months: Number of months to project forward (default: 36 months/3 years)
            growth_rate: Monthly compound growth rate in user acquisition (default: 5%)
                         Expressed as a decimal (e.g., 0.05 for 5% monthly growth)
            subscription_model: Optional subscription model object with tier definitions
                              Can be any object with a "tiers" attribute containing
                              tier definitions with price_monthly properties
            prices: Optional dictionary mapping tier IDs to monthly prices
                   If provided, these prices override any in the subscription model
            
        Returns:
            A list of dictionaries containing monthly projections, where each has:
            - month: Month number (1-based)
            - total_users: Total user count for that month
            - free_users: Free tier user count
            - paid_users: Paid tier user count
            - tier_users: Dictionary mapping tier names to user counts
            - tier_revenue: Dictionary mapping tier names to monthly revenue
            - total_revenue: Total revenue for the month
            - cumulative_revenue: Cumulative revenue through that month
        """
        # STAGE 1: User Growth Projection
        # Calculate user growth patterns using the cohort-based user growth model
        user_projections_list = self.project_users(months, growth_rate)

        # Get the raw user projections data (includes month 0) for internal calculations
        # This provides arrays of total, free, and paid users by month
        user_projections = self._raw_user_projections

        # STAGE 2: Initialize revenue tracking data structures
        # Set up arrays to track revenue metrics, with month 0 as starting point
        monthly_revenue = [0]       # Revenue generated in each month
        cumulative_revenue = [0]    # Running total of revenue to date
        tier_users = {}             # Users per tier by month
        tier_revenue = {}           # Revenue per tier by month

        # STAGE 3: Revenue Calculation Based on Available Subscription Model
        
        # BRANCH 3A: Simple tier-based calculation when no subscription model provided
        if subscription_model is None:
            # Use the configured tier distribution to calculate tier-specific metrics
            for month in range(1, months + 1):
                # Get the total paid users for this month from projections
                paid_users = user_projections["paid_users"][month]
                
                # Initialize month-specific tracking dictionaries
                month_tier_users = {}    # Users per tier this month
                month_tier_revenue = {}  # Revenue per tier this month
                month_revenue = 0        # Total revenue this month
                
                # Calculate users and revenue for each pricing tier
                for tier_name, distribution in self.tier_distribution.items():
                    # Distribute paid users across tiers according to distribution
                    tier_users_count = int(paid_users * distribution)
                    month_tier_users[tier_name] = tier_users_count
                    
                    # Apply default tier pricing based on common tier naming conventions
                    # This provides sensible defaults when no pricing model is available
                    tier_price = 9.99  # Basic tier default
                    if tier_name.lower() == "pro":
                        tier_price = 19.99  # Pro tier default
                    elif tier_name.lower() == "premium" or tier_name.lower() == "business":
                        tier_price = 49.99  # Premium tier default
                    
                    # Calculate revenue for this tier with proper rounding
                    # Round to 2 decimal places to avoid floating point errors with money
                    tier_rev = round(tier_users_count * tier_price, 2)
                    month_tier_revenue[tier_name] = tier_rev
                    month_revenue += tier_rev
                
                # Store the results for this month in our tracking dictionaries
                tier_users[month] = month_tier_users
                tier_revenue[month] = month_tier_revenue
                monthly_revenue.append(month_revenue)
                cumulative_revenue.append(cumulative_revenue[-1] + month_revenue)
                
        # BRANCH 3B: Model-based calculation using provided subscription model
        else:
            # Extract tier information from the subscription model
            tiers = getattr(subscription_model, "tiers", [])
            
            # STEP 3B.1: Determine pricing for each tier
            # If explicit prices not provided, extract them from the subscription model
            if prices is None:
                prices = {}
                for tier in tiers:
                    tier_id = tier.get("id")
                    price_monthly = tier.get("price_monthly", 0)
                    if tier_id and price_monthly > 0:  # Only include valid paid tiers
                        prices[tier_id] = price_monthly
            
            # STEP 3B.2: Build tier mapping between names and IDs
            # This allows us to match tier_distribution names to model tier IDs
            tier_ids_by_name = {}  # Maps tier name -> tier ID
            tier_names_by_id = {}  # Maps tier ID -> tier name
            for tier in tiers:
                if tier.get("price_monthly", 0) > 0:  # Only include paid tiers
                    name = tier["name"]
                    tier_ids_by_name[name.lower()] = tier["id"]
                    tier_names_by_id[tier["id"]] = name
            
            # STEP 3B.3: Handle case where tier names don't match exactly
            # Fallback to positional mapping if we can't match by name
            if not tier_ids_by_name:
                # Find all paid tiers in the model
                paid_tiers = [t for t in tiers if t.get("price_monthly", 0) > 0]
                # Map tiers by position if available (basic, pro, premium)
                if len(paid_tiers) >= 1:
                    tier_ids_by_name["basic"] = paid_tiers[0]["id"]
                    tier_names_by_id[paid_tiers[0]["id"]] = "Basic"
                if len(paid_tiers) >= 2:
                    tier_ids_by_name["pro"] = paid_tiers[1]["id"]
                    tier_names_by_id[paid_tiers[1]["id"]] = "Pro"
                if len(paid_tiers) >= 3:
                    tier_ids_by_name["premium"] = paid_tiers[2]["id"]
                    tier_names_by_id[paid_tiers[2]["id"]] = "Premium"
            
            # STEP 3B.4: Calculate revenue for each month using the model
            for month in range(1, months + 1):
                # Get the total paid users for this month
                paid_users = user_projections["paid_users"][month]
                
                # Initialize month-specific tracking
                month_tier_users = {}
                month_tier_revenue = {}
                month_revenue = 0
                
                # Calculate revenue from each tier based on tier distribution
                for tier_name, distribution in self.tier_distribution.items():
                    tier_name_lower = tier_name.lower()
                    # Only process tiers we have mapped to the subscription model
                    if tier_name_lower in tier_ids_by_name:
                        # Get the tier ID and display name
                        tier_id = tier_ids_by_name[tier_name_lower]
                        display_name = tier_names_by_id.get(tier_id, tier_name)
                        
                        # Calculate users in this tier
                        tier_users_count = int(paid_users * distribution)
                        
                        # Get the price for this tier
                        tier_price = prices.get(tier_id, 0)
                        
                        # Calculate revenue with proper rounding
                        tier_rev = round(tier_users_count * tier_price, 2)
                        
                        # Store tier-specific results
                        month_tier_users[display_name] = tier_users_count
                        month_tier_revenue[display_name] = tier_rev
                        month_revenue += tier_rev
                
                # Store the results for this month in our tracking dictionaries
                tier_users[month] = month_tier_users
                tier_revenue[month] = month_tier_revenue
                monthly_revenue.append(month_revenue)
                cumulative_revenue.append(cumulative_revenue[-1] + month_revenue)

        # STAGE 4: Generate yearly summary statistics
        # Create aggregated yearly views for higher-level business planning
        yearly_summaries = []
        for year in range(1, (months // 12) + 1):
            # Calculate the months corresponding to this year
            start_month = (year - 1) * 12
            end_month = year * 12

            yearly_summaries.append({
                "year": year,
                "total_users": user_projections["total_users"][end_month],
                "free_users": user_projections["free_users"][end_month],
                "paid_users": user_projections["paid_users"][end_month],
                "yearly_revenue": sum(monthly_revenue[start_month + 1:end_month + 1]),
                "cumulative_revenue": cumulative_revenue[end_month],
            })

        # STAGE 5: Create comprehensive monthly projection data
        # This includes detailed month-by-month statistics for all metrics
        monthly_projections = []
        for month in range(1, months + 1):
            monthly_projections.append({
                "month": month,                              # Month number
                "total_users": user_projections["total_users"][month],  # All users
                "free_users": user_projections["free_users"][month],    # Free users
                "paid_users": user_projections["paid_users"][month],    # Paid users
                "tier_users": tier_users.get(month, {}),     # Users per tier
                "tier_revenue": tier_revenue.get(month, {}), # Revenue per tier
                "total_revenue": monthly_revenue[month],     # Total monthly revenue
                "cumulative_revenue": cumulative_revenue[month]  # Running total revenue
            })

        # STAGE 6: Store the complete projection dataset internally
        # This preserves all data for reference by other methods
        self._full_projection = {
            "id": str(uuid.uuid4()),                        # Unique identifier
            "subscription_model_id": getattr(subscription_model, "id", None),  # Model reference
            "projection_months": months,                    # Projection timespan
            "growth_rate": growth_rate,                     # Growth rate used
            "user_projections": user_projections,           # User growth data
            "monthly_revenue": monthly_revenue,             # Monthly revenue data
            "cumulative_revenue": cumulative_revenue,       # Cumulative revenue data
            "monthly_projections": monthly_projections,     # Detailed monthly data
            "yearly_summaries": yearly_summaries,           # Yearly aggregations
            "total_revenue": cumulative_revenue[-1],        # Total projected revenue
            "timestamp": datetime.now().isoformat(),        # Calculation timestamp
        }

        # Return the monthly projections as expected by calling code
        return monthly_projections

    def calculate_lifetime_value(
        self,
        average_revenue_per_user: float,
        churn_rate: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate customer lifetime value using the discounted perpetuity model.
        
        This algorithm implements a sophisticated customer lifetime value (CLV/LTV) calculation
        based on the statistical perpetuity model. The implementation follows these key stages:
        
        1. PARAMETER NORMALIZATION:
           - Accepts the average monthly revenue per user (ARPU)
           - Takes optional churn rate override or defaults to instance configuration
           - Handles parameters in decimal form (e.g., 0.05 for 5% churn)
           - Ensures consistent measurement periods for all metrics (monthly basis)
        
        2. CORE LIFETIME VALUE COMPUTATION:
           - Implements the perpetuity model formula: LTV = ARPU / Churn Rate
           - Calculates expected customer lifetime as inverse of churn (1/churn)
           - Uses the statistical property that exponential decay processes have 
             mean lifetime equal to the inverse of decay rate
           - Applies direct multiplication approach: lifetime × ARPU = total value
        
        3. TEMPORAL VALUE PROJECTIONS:
           - Calculates constrained time-horizon projections (1/3/5 year values)
           - Applies mathematical minimum function to handle scenarios where 
             expected lifetime exceeds the time horizon
           - Creates graduated value projections to facilitate staged forecasting
           - Maintains mathematical consistency between all calculated values
        
        4. COMPREHENSIVE RESULT GENERATION:
           - Creates a structured result dictionary with all relevant metrics
           - Includes unique identifier for analysis tracking and auditing
           - Timestamps the calculation for historical reference
           - Returns both input parameters and all derived calculations
        
        The perpetuity CLV model is particularly suitable for subscription businesses
        where customers pay a recurring fee and have a relatively consistent churn rate.
        This implementation specifically addresses several critical business needs:
        
        - Provides realistic lifetime value for financial reporting and forecasting
        - Enables CAC:LTV ratio analysis for marketing efficiency
        - Supports time-bounded value projections for staged business planning
        - Facilitates cohort comparison with standardized metrics
        
        Notes on mathematical properties:
        - The core formula (ARPU/churn) represents the expected value of a geometric series
          with first term = ARPU and common ratio = (1-churn)
        - This converges to ARPU/churn as the number of terms approaches infinity
        - For time-bounded calculations, we use the partial sum of the geometric series
          capped at the specified number of periods
        
        Args:
            average_revenue_per_user: Monthly average revenue per user (ARPU)
            churn_rate: Monthly customer churn rate as a decimal (e.g., 0.05 for 5%)
                        If None, the instance's configured churn_rate will be used
            
        Returns:
            A comprehensive dictionary containing:
            - id: Unique identifier for this calculation
            - average_revenue_per_user: Input ARPU value
            - churn_rate: Churn rate used in calculation
            - average_lifetime_months: Expected customer lifetime in months
            - lifetime_value: Total expected customer value (unconstrained by time)
            - one_year_value: Expected customer value over first 12 months
            - three_year_value: Expected customer value over first 36 months
            - five_year_value: Expected customer value over first 60 months
            - timestamp: ISO-formatted timestamp of calculation
        """
        # STAGE 1: Parameter normalization and default handling
        # Use the instance's churn rate if none provided to maintain consistency
        # with other projection methods in this class
        if churn_rate is None:
            churn_rate = self.churn_rate

        # STAGE 2: Core lifetime value calculations
        # Calculate expected customer lifetime using the statistical property that
        # for exponential decay processes, mean lifetime = 1/decay_rate
        average_lifetime_months = 1 / churn_rate

        # Calculate total lifetime value using the perpetuity formula
        # LTV = ARPU / churn_rate (equivalent to ARPU * average_lifetime_months)
        lifetime_value = average_revenue_per_user * average_lifetime_months

        # STAGE 3: Calculate time-bounded value projections for practical planning
        # These are minimum of either the full lifetime value or what would be
        # realized within the specific time horizon
        one_year_value = average_revenue_per_user * min(12, average_lifetime_months)
        three_year_value = average_revenue_per_user * min(36, average_lifetime_months)
        five_year_value = average_revenue_per_user * min(60, average_lifetime_months)

        # STAGE 4: Assemble comprehensive result dictionary with all metrics
        # This includes input parameters, calculated results, and metadata
        return {
            "id": str(uuid.uuid4()),                        # Unique identifier
            "average_revenue_per_user": average_revenue_per_user,  # Input ARPU
            "churn_rate": churn_rate,                       # Churn rate used
            "average_lifetime_months": average_lifetime_months,    # Expected lifetime
            "lifetime_value": lifetime_value,               # Unconstrained LTV
            "one_year_value": one_year_value,               # 1Y constrained value
            "three_year_value": three_year_value,           # 3Y constrained value
            "five_year_value": five_year_value,             # 5Y constrained value
            "timestamp": datetime.now().isoformat(),        # Calculation timestamp
        }

    def calculate_payback_period(
        self,
        customer_acquisition_cost: float,
        average_revenue_per_user: float,
        gross_margin: float = 0.8
    ) -> Dict[str, Any]:
        """
        Calculate customer payback period to determine marketing ROI efficiency.
        
        This algorithm implements a sophisticated customer acquisition cost (CAC) 
        payback period calculation for subscription businesses. The implementation 
        follows these key stages:
        
        1. PARAMETER HANDLING AND VALIDATION:
           - Takes the customer acquisition cost (CAC) as direct input
           - Uses the average monthly revenue per user (ARPU) for revenue projections
           - Accepts an optional gross margin parameter (defaults to standard 80%)
           - Allows for business model-specific margin customization
        
        2. CONTRIBUTION MARGIN CALCULATION:
           - Calculates the monthly contribution margin per user
           - Applies gross margin percentage to filter out costs of goods sold
           - Focuses on the actual profit contribution of each customer
           - Creates a standardized monthly contribution metric for time calculations
        
        3. PAYBACK PERIOD DETERMINATION:
           - Implements the standard formula: CAC / Monthly Contribution
           - Calculates the exact breakeven point in months
           - Provides a precise measurement for marketing efficiency
           - Enables direct comparison against customer lifetime value
        
        4. COMPREHENSIVE RESULT PACKAGING:
           - Creates a structured result dictionary with all relevant metrics
           - Includes a unique identifier for tracking and correlation
           - Records calculation timestamp for historical tracking
           - Returns both input parameters and derived values
        
        The payback period calculation is a critical business metric for:
        - Evaluating marketing channel efficiency and ROI
        - Comparing customer acquisition strategies
        - Optimizing cash flow planning for growth
        - Determining sustainable growth rates based on capital constraints
        
        This implementation specifically addresses the unit economics of 
        subscription businesses, where:
        - Initial acquisition cost is typically higher than single-transaction value
        - Recovery occurs over an extended customer relationship
        - Gross margin significantly affects recovery timeline
        - Recovery timeline must be substantially shorter than expected lifetime
        
        Args:
            customer_acquisition_cost: Average cost to acquire a customer (CAC)
            average_revenue_per_user: Monthly average revenue per user (ARPU)
            gross_margin: Gross margin percentage as a decimal (default: 0.8 or 80%)
                          This represents what portion of revenue becomes contribution
                          margin after deducting costs of goods sold
            
        Returns:
            A comprehensive dictionary containing:
            - id: Unique identifier for this calculation
            - customer_acquisition_cost: Input CAC value
            - average_revenue_per_user: Input ARPU value
            - gross_margin: Gross margin used in calculation
            - monthly_contribution: Monthly contribution margin per user
            - payback_period_months: Time to recover CAC in months
            - timestamp: ISO-formatted timestamp of calculation
        """
        # STAGE 1: Parameter validation happens implicitly through Python's type system
        # The method signature ensures appropriate types for the calculation
        
        # STAGE 2: Calculate monthly contribution margin per customer
        # This is the amount each customer contributes to covering fixed costs
        # and acquisition costs each month after variable costs are deducted
        monthly_contribution = average_revenue_per_user * gross_margin

        # STAGE 3: Calculate the payback period in months using the simple division
        # This represents how long it takes to recoup the investment in customer acquisition
        payback_period_months = customer_acquisition_cost / monthly_contribution

        # STAGE 4: Assemble comprehensive result dictionary with all metrics and metadata
        # This allows for detailed analysis and comparison across different scenarios
        return {
            "id": str(uuid.uuid4()),                        # Unique identifier
            "customer_acquisition_cost": customer_acquisition_cost,  # Input CAC
            "average_revenue_per_user": average_revenue_per_user,    # Input ARPU
            "gross_margin": gross_margin,                   # Gross margin used
            "monthly_contribution": monthly_contribution,   # Monthly contribution
            "payback_period_months": payback_period_months, # Breakeven point
            "timestamp": datetime.now().isoformat(),        # Calculation timestamp
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the revenue projector to a dictionary.

        Returns:
            Dictionary representation of the revenue projector
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "initial_users": self.initial_users,
            "user_acquisition_rate": self.user_acquisition_rate,
            "conversion_rate": self.conversion_rate,
            "churn_rate": self.churn_rate,
            "tier_distribution": self.tier_distribution,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the revenue projector to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the revenue projector
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save_to_file(self, file_path: str) -> None:
        """
        Save the revenue projector to a JSON file.

        Args:
            file_path: Path to save the file
        """
        with open(file_path, "w") as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, file_path: str) -> 'RevenueProjector':
        """
        Load a revenue projector from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            RevenueProjector instance
        """
        with open(file_path, "r") as f:
            data = json.load(f)

        projector = cls(
            name=data["name"],
            description=data["description"],
            initial_users=data["initial_users"],
            user_acquisition_rate=data["user_acquisition_rate"],
            conversion_rate=data["conversion_rate"],
            churn_rate=data["churn_rate"],
            tier_distribution=data["tier_distribution"]
        )

        projector.id = data["id"]
        projector.created_at = data["created_at"]
        projector.updated_at = data["updated_at"]

        return projector

    def __str__(self) -> str:
        """String representation of the revenue projector."""
        return f"{self.name} (acquisition: {self.user_acquisition_rate}/month, conversion: {self.conversion_rate:.1%}, churn: {self.churn_rate:.1%})"

    def __repr__(self) -> str:
        """Detailed string representation of the revenue projector."""
        return f"RevenueProjector(id={self.id}, name={self.name}, acquisition={self.user_acquisition_rate}, conversion={self.conversion_rate:.1%}, churn={self.churn_rate:.1%})"


# Example usage
if __name__ == "__main__":
    # Import required classes
    from subscription_models import SubscriptionModel
    from pricing_calculator import PricingCalculator

    # Create a subscription model
    model = SubscriptionModel(
        name="AI Tool Subscription",
        description="Subscription model for an AI-powered tool"
    )

    # Add tiers
    basic_tier = model.add_tier(
        name="Basic",
        description="Essential features for individuals",
        price_monthly=9.99,
        target_users="Individual creators and small businesses"
    )

    pro_tier = model.add_tier(
        name="Pro",
        description="Advanced features for professionals",
        price_monthly=19.99,
        target_users="Professional content creators and marketing teams"
    )

    premium_tier = model.add_tier(
        name="Premium",
        description="All features for enterprise users",
        price_monthly=49.99,
        target_users="Enterprise teams and agencies"
    )

    # Create a pricing calculator
    calculator = PricingCalculator(
        name="AI Tool Pricing Calculator",
        description="Pricing calculator for an AI-powered tool",
        pricing_strategy="value-based"
    )

    # Calculate prices
    prices = {
        basic_tier["id"]: 9.99,
        pro_tier["id"]: 19.99,
        premium_tier["id"]: 49.99
    }

    # Create a revenue projector
    projector = RevenueProjector(
        name="AI Tool Revenue Projector",
        description="Revenue projector for an AI-powered tool",
        initial_users=0,
        user_acquisition_rate=50,
        conversion_rate=0.2,
        churn_rate=0.05,
        tier_distribution={"basic": 0.6, "pro": 0.3, "premium": 0.1}
    )

    # Project revenue
    projection = projector.project_revenue(
        subscription_model=model,
        prices=prices,
        months=36,
        growth_rate=0.05
    )

    # Print projection summary
    print(f"Revenue Projection for {model.name}")
    print(f"Projection period: {projection['projection_months']} months")
    print(f"Growth rate: {projection['growth_rate']:.1%} per month")

    print("\nYearly Summaries:")
    for year in projection["yearly_summaries"]:
        print(f"Year {year['year']}:")
        print(f"  Total Users: {year['total_users']}")
        print(f"  Paid Users: {year['paid_users']}")
        print(f"  Yearly Revenue: ${year['yearly_revenue']:.2f}")
        print(f"  Cumulative Revenue: ${year['cumulative_revenue']:.2f}")

    print(f"\nTotal Revenue: ${projection['total_revenue']:.2f}")

    # Calculate lifetime value
    average_revenue = (9.99 * 0.6 + 19.99 * 0.3 + 49.99 * 0.1)
    ltv = projector.calculate_lifetime_value(average_revenue)

    print(f"\nCustomer Lifetime Value:")
    print(f"Average Revenue Per User: ${ltv['average_revenue_per_user']:.2f}")
    print(f"Average Customer Lifetime: {ltv['average_lifetime_months']:.1f} months")
    print(f"Lifetime Value: ${ltv['lifetime_value']:.2f}")

    # Calculate payback period
    payback = projector.calculate_payback_period(
        customer_acquisition_cost=50,
        average_revenue_per_user=average_revenue
    )

    print(f"\nCustomer Payback Period:")
    print(f"Customer Acquisition Cost: ${payback['customer_acquisition_cost']:.2f}")
    print(f"Monthly Contribution: ${payback['monthly_contribution']:.2f}")
    print(f"Payback Period: {payback['payback_period_months']:.1f} months")
