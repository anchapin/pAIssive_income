"""
A/B testing module for marketing campaigns.

This module provides tools for creating, managing, and analyzing A/B tests
for different marketing assets including email campaigns, landing pages,
ad copy, call-to-action elements, and more.
"""

import uuid
import json
import math
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
from scipy import stats

from interfaces.marketing_interfaces import IABTesting
from marketing.errors import MarketingError, InvalidTestConfigurationError, TestNotFoundError


class ABTestingError(MarketingError):
    """Base class for A/B testing errors."""
    pass


class TestAlreadyEndedError(ABTestingError):
    """Raised when trying to modify a test that has already ended."""
    pass


class InvalidVariantError(ABTestingError):
    """Raised when referencing an invalid variant."""
    pass


class InsufficientDataError(ABTestingError):
    """Raised when there is not enough data to analyze a test."""
    pass


class ABTest:
    """
    Represents an A/B test.
    
    This class encapsulates the data and functionality for a single A/B test,
    including its variants, metrics, and result analysis.
    """
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        content_type: str,
        test_type: str,
        variants: List[Dict[str, Any]],
        created_at: datetime = None
    ):
        """
        Initialize an A/B test.
        
        Args:
            id: Unique identifier for the test
            name: Name of the test
            description: Description of the test
            content_type: Type of content being tested (email, landing_page, ad, etc.)
            test_type: Type of test (a_b, split, multivariate)
            variants: List of test variants including control
            created_at: Creation timestamp
        """
        self.id = id
        self.name = name
        self.description = description
        self.content_type = content_type
        self.test_type = test_type
        self.variants = variants
        self.created_at = created_at or datetime.now()
        self.updated_at = self.created_at
        self.ended_at = None
        self.status = "active"
        self.winning_variant_id = None
        self.interactions = []
        self.confidence_level = 0.95  # Default 95% confidence level
        
        # Ensure each variant has the required fields
        for variant in self.variants:
            if "id" not in variant:
                variant["id"] = str(uuid.uuid4())
            if "name" not in variant:
                variant["name"] = f"Variant {variant['id'][:8]}"
            if "is_control" not in variant:
                variant["is_control"] = False
            
            # Initialize metrics for each variant
            variant["metrics"] = {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "click_through_rate": 0.0,
                "conversion_rate": 0.0
            }
        
        # Ensure there is at least one control variant
        if not any(v.get("is_control", False) for v in self.variants):
            if self.variants:
                self.variants[0]["is_control"] = True
            else:
                raise InvalidTestConfigurationError("At least one variant must be specified")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the A/B test to a dictionary.
        
        Returns:
            Dictionary representation of the A/B test
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "content_type": self.content_type,
            "test_type": self.test_type,
            "variants": self.variants,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "status": self.status,
            "winning_variant_id": self.winning_variant_id,
            "confidence_level": self.confidence_level
        }
    
    def _get_variant_index(self, variant_id: str) -> int:
        """
        Get the index of a variant in the variants list.
        
        Args:
            variant_id: ID of the variant
            
        Returns:
            Index of the variant in the variants list
            
        Raises:
            InvalidVariantError: If the variant ID is not found
        """
        for i, variant in enumerate(self.variants):
            if variant["id"] == variant_id:
                return i
        
        raise InvalidVariantError(f"Variant with ID '{variant_id}' not found in test '{self.id}'")
    
    def record_interaction(self, variant_id: str, interaction_type: str, user_id: Optional[str] = None, 
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record an interaction with a variant.
        
        Args:
            variant_id: ID of the variant
            interaction_type: Type of interaction (impression, click, conversion, etc.)
            user_id: Optional ID of the user
            metadata: Optional metadata about the interaction
            
        Returns:
            Interaction dictionary
            
        Raises:
            TestAlreadyEndedError: If the test has already ended
            InvalidVariantError: If the variant ID is invalid
        """
        if self.status != "active":
            raise TestAlreadyEndedError(f"Cannot record interaction for ended test '{self.id}'")
        
        # Get the variant
        variant_index = self._get_variant_index(variant_id)
        variant = self.variants[variant_index]
        
        # Create interaction record
        interaction = {
            "id": str(uuid.uuid4()),
            "test_id": self.id,
            "variant_id": variant_id,
            "interaction_type": interaction_type,
            "user_id": user_id,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to interactions list
        self.interactions.append(interaction)
        
        # Update variant metrics
        if interaction_type == "impression":
            variant["metrics"]["impressions"] += 1
        elif interaction_type == "click":
            variant["metrics"]["clicks"] += 1
        elif interaction_type == "conversion":
            variant["metrics"]["conversions"] += 1
        
        # Recalculate rates
        if variant["metrics"]["impressions"] > 0:
            variant["metrics"]["click_through_rate"] = variant["metrics"]["clicks"] / variant["metrics"]["impressions"]
            # Add overall conversion rate (conversions/impressions)
            variant["metrics"]["overall_conversion_rate"] = variant["metrics"]["conversions"] / variant["metrics"]["impressions"]
        
        if variant["metrics"]["clicks"] > 0:
            # This is now the click-to-conversion rate
            variant["metrics"]["conversion_rate"] = variant["metrics"]["conversions"] / variant["metrics"]["clicks"]
        
        # Update test timestamp
        self.updated_at = datetime.now()
        
        return interaction
    
    def _calculate_metrics(self, variant_id: str) -> Dict[str, Any]:
        """
        Calculate metrics for a variant.
        
        Args:
            variant_id: ID of the variant
            
        Returns:
            Dictionary of metrics
        """
        # Initialize metrics
        metrics = {
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "click_through_rate": 0.0,
            "conversion_rate": 0.0
        }
        
        # Calculate metrics from interactions
        for interaction in self.interactions:
            if interaction["variant_id"] == variant_id:
                if interaction["interaction_type"] == "impression":
                    metrics["impressions"] += 1
                elif interaction["interaction_type"] == "click":
                    metrics["clicks"] += 1
                elif interaction["interaction_type"] == "conversion":
                    metrics["conversions"] += 1
        
        # Calculate rates
        if metrics["impressions"] > 0:
            metrics["click_through_rate"] = metrics["clicks"] / metrics["impressions"]
        if metrics["clicks"] > 0:
            metrics["conversion_rate"] = metrics["conversions"] / metrics["clicks"]
        
        return metrics
        
    def _get_control_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get metrics for the control variant.
        
        Returns:
            Dictionary of control variant metrics or None if no control variant exists
        """
        control_variant = next((v for v in self.variants if v.get("is_control", False)), None)
        if control_variant:
            return self._calculate_metrics(control_variant["id"])
        return None
    
    def get_results(self) -> Dict[str, Any]:
        """Get current test results."""
        results = {
            "test_id": self.id,
            "name": self.name,
            "status": self.status,
            "total_impressions": 0,
            "total_clicks": 0,
            "total_conversions": 0,
            "variants": []
        }
        
        for variant in self.variants:
            metrics = self._calculate_metrics(variant["id"])
            variant_result = {
                "id": variant["id"],
                "name": variant["name"],
                "is_control": variant.get("is_control", False),
                "metrics": metrics
            }
            
            # Calculate lifts if this is not the control variant
            if not variant.get("is_control", False):
                control_metrics = self._get_control_metrics()
                if control_metrics:
                    # Calculate CTR lift if control has impressions
                    if control_metrics["click_through_rate"] > 0:
                        variant_result["ctr_lift"] = round(
                            ((metrics["click_through_rate"] / control_metrics["click_through_rate"]) - 1) * 100,
                            1
                        )
                    else:
                        # If control has no click-through rate, and variant does, lift is infinite (set to 100%)
                        variant_result["ctr_lift"] = 100.0 if metrics["click_through_rate"] > 0 else 0.0
                    
                    # Calculate conversion lift if control has conversions
                    if control_metrics["conversion_rate"] > 0:
                        variant_result["conversion_lift"] = round(
                            ((metrics["conversion_rate"] / control_metrics["conversion_rate"]) - 1) * 100,
                            1
                        )
                    else:
                        # If control has no conversion rate, and variant does, lift is infinite (set to 100%)
                        variant_result["conversion_lift"] = 100.0 if metrics["conversion_rate"] > 0 else 0.0
            
            results["variants"].append(variant_result)
            results["total_impressions"] += metrics["impressions"]
            results["total_clicks"] += metrics["clicks"] 
            results["total_conversions"] += metrics["conversions"]
        
        # Calculate overall rates
        if results["total_impressions"] > 0:
            results["overall_click_through_rate"] = results["total_clicks"] / results["total_impressions"]
        if results["total_clicks"] > 0:
            results["overall_conversion_rate"] = results["total_conversions"] / results["total_clicks"]
        
        return results
    
    def _calculate_significance(self, variant1: Dict[str, Any], variant2: Dict[str, Any], 
                                metric: str = "click_through_rate") -> Tuple[float, bool]:
        """
        Calculate statistical significance between two variants using different
        significance levels for CTR (95%) and conversion (90%) tests.
        
        Args:
            variant1: First variant (typically control)
            variant2: Second variant
            metric: Metric to compare (click_through_rate or conversion_rate)
            
        Returns:
            Tuple of (p_value, is_significant)
        """
        if metric == "click_through_rate":
            successes1 = variant1["metrics"]["clicks"]
            trials1 = variant1["metrics"]["impressions"]
            successes2 = variant2["metrics"]["clicks"]
            trials2 = variant2["metrics"]["impressions"]
            min_trials = 30  # Higher threshold for CTR
            significance_level = 0.95  # 95% confidence for CTR
        elif metric == "conversion_rate":
            successes1 = variant1["metrics"]["conversions"]
            trials1 = variant1["metrics"]["clicks"]
            successes2 = variant2["metrics"]["conversions"]
            trials2 = variant2["metrics"]["clicks"]
            min_trials = 20  # Lower threshold for conversions
            significance_level = 0.90  # 90% confidence for conversions
        else:
            raise ValueError(f"Invalid metric: {metric}")
            
        # Ensure minimum sample size
        if trials1 < min_trials or trials2 < min_trials:
            return 1.0, False
            
        try:
            # Calculate proportions
            p1 = successes1 / trials1
            p2 = successes2 / trials2
            
            # Use Fisher's exact test for conversion rates since we have small counts
            if metric == "conversion_rate":
                # Create contingency table
                table = [[successes1, trials1 - successes1],
                        [successes2, trials2 - successes2]]
                # Use Fisher's exact test with one-tailed alternative
                odds_ratio, p_value = stats.fisher_exact(table, alternative='greater')
            else:
                # Use normal approximation for CTR since we have large counts
                # Calculate pooled proportion under null hypothesis
                p_pooled = (successes1 + successes2) / (trials1 + trials2)
                # Calculate standard error
                se = math.sqrt(p_pooled * (1 - p_pooled) * (1/trials1 + 1/trials2))
                
                if se == 0:
                    return 1.0, False
                    
                # Calculate z-score
                z = (p2 - p1) / se
                # Calculate one-tailed p-value
                p_value = 1 - stats.norm.cdf(z)
            
            # Determine significance using appropriate confidence level
            is_significant = p_value < (1 - significance_level) and p2 > p1
            
            return p_value, is_significant
            
        except Exception:
            # If there's any error in the calculation, return no significance
            return 1.0, False
    
    def analyze_test(self) -> Dict[str, Any]:
        """
        Analyze the A/B test for statistical significance.
        
        Returns:
            Dictionary with test analysis
            
        Raises:
            InsufficientDataError: If there is not enough data to analyze the test
        """
        # Get control variant
        control_variant = next((v for v in self.variants if v.get("is_control", False)), None)
        
        if not control_variant:
            raise InvalidTestConfigurationError("No control variant found")
        
        # Check if we have enough data
        total_impressions = sum(v["metrics"]["impressions"] for v in self.variants)
        if total_impressions < 100:  # Arbitrary threshold, could be adjusted
            raise InsufficientDataError(f"Not enough data to analyze test '{self.id}' - need at least 100 impressions")
        
        # Analyze each variant against control
        analysis = {
            "test_id": self.id,
            "name": self.name,
            "confidence_level": self.confidence_level,
            "has_significant_results": False,
            "recommended_winner": None,
            "variants": []
        }
        
        for variant in self.variants:
            if variant.get("is_control", False):
                variant_analysis = {
                    "id": variant["id"],
                    "name": variant["name"],
                    "is_control": True,
                    "metrics": variant["metrics"].copy()
                }
            else:
                # Calculate significance for CTR
                ctr_p_value, ctr_is_significant = self._calculate_significance(
                    control_variant, variant, "click_through_rate")
                    
                # Calculate significance for overall conversion rate
                # Use impression-based conversion rate (conversions/impressions)
                control_conv = control_variant["metrics"]["conversions"]
                control_imp = control_variant["metrics"]["impressions"]
                variant_conv = variant["metrics"]["conversions"]
                variant_imp = variant["metrics"]["impressions"]
                
                # Calculate significance based on overall conversion rate (conversions/impressions)
                control_rate = control_conv/control_imp if control_imp > 0 else 0
                variant_rate = variant_conv/variant_imp if variant_imp > 0 else 0

                # Use Fisher's exact test for overall conversion significance
                # Create contingency table comparing successes (conversions) vs failures
                table = [[variant_conv, variant_imp - variant_conv],
                        [control_conv, control_imp - control_conv]]
                
                # Use one-tailed test to check if variant is better than control
                odds_ratio, conv_p_value = stats.fisher_exact(table, alternative='greater')
                
                # Determine conversion significance at 95% confidence
                conv_is_significant = (conv_p_value < 0.05 and variant_rate > control_rate)
                
                variant_analysis = {
                    "id": variant["id"],
                    "name": variant["name"],
                    "is_control": False,
                    "metrics": variant["metrics"].copy(),
                    "ctr_p_value": ctr_p_value,
                    "ctr_is_significant": ctr_is_significant,
                    "conversion_p_value": conv_p_value,
                    "conversion_is_significant": conv_is_significant,
                    "is_better_than_control": False
                }
                
                # A variant is better than control if either:
                # 1. Overall conversion rate is significantly better
                # 2. CTR is significantly better and conversion rate is at least as good
                if conv_is_significant:
                    variant_analysis["is_better_than_control"] = True
                    analysis["has_significant_results"] = True
                elif (ctr_is_significant and 
                      (variant_conv/variant_imp >= control_conv/control_imp)):
                    variant_analysis["is_better_than_control"] = True
                    analysis["has_significant_results"] = True
        
            analysis["variants"].append(variant_analysis)
        
        # Determine recommended winner
        if analysis["has_significant_results"]:
            best_variant = None
            best_conv_rate = control_variant["metrics"]["conversions"] / control_variant["metrics"]["impressions"]
            
            for variant in analysis["variants"]:
                if not variant["is_control"]:
                    conv_rate = variant["metrics"]["conversions"] / variant["metrics"]["impressions"]
                    if (variant.get("is_better_than_control", False) and 
                        conv_rate > best_conv_rate):
                        best_variant = variant
                        best_conv_rate = conv_rate
            
            if best_variant:
                analysis["recommended_winner"] = best_variant["id"]
        
        return analysis
    
    def end_test(self, winning_variant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        End the A/B test and optionally select a winning variant.
        
        Args:
            winning_variant_id: Optional ID of the winning variant
            
        Returns:
            Dictionary with test results and winner
            
        Raises:
            TestAlreadyEndedError: If the test has already ended
            InvalidVariantError: If the winning variant ID is invalid
        """
        if self.status != "active":
            raise TestAlreadyEndedError(f"Test '{self.id}' has already ended")
        
        # If no winning variant specified, try to determine one from analysis
        if not winning_variant_id:
            try:
                # First try to use statistical analysis
                analysis = self.analyze_test()
                winning_variant_id = analysis.get("recommended_winner")
                
                # If no significant winner, use best performing variant based on metrics
                if not winning_variant_id:
                    control_variant = next((v for v in self.variants if v.get("is_control", False)), None)
                    if control_variant:
                        control_metrics = control_variant["metrics"]
                        control_ctr = control_metrics["click_through_rate"]
                        control_cvr = control_metrics["conversion_rate"] if control_metrics["clicks"] > 0 else 0
                        
                        best_variant = None
                        best_improvement = 0
                        
                        for variant in self.variants:
                            if not variant.get("is_control", False):
                                metrics = variant["metrics"]
                                variant_ctr = metrics["click_through_rate"]
                                variant_cvr = metrics["conversion_rate"] if metrics["clicks"] > 0 else 0
                                
                                # Calculate relative improvement
                                ctr_improvement = ((variant_ctr - control_ctr) / control_ctr) if control_ctr > 0 else 0
                                cvr_improvement = ((variant_cvr - control_cvr) / control_cvr) if control_cvr > 0 else 0
                                
                                # Use combined improvement score
                                total_improvement = ctr_improvement + cvr_improvement
                                
                                if total_improvement > best_improvement and variant_ctr >= control_ctr:
                                    best_variant = variant
                                    best_improvement = total_improvement
                        
                        if best_variant and best_improvement > 0:
                            winning_variant_id = best_variant["id"]
                        else:
                            winning_variant_id = control_variant["id"]
                    
            except InsufficientDataError:
                # If not enough data, default to control variant
                control_variant = next((v for v in self.variants if v.get("is_control", False)), None)
                if control_variant:
                    winning_variant_id = control_variant["id"]
        
        # Validate winning variant if specified
        if winning_variant_id:
            self._get_variant_index(winning_variant_id)  # Will raise InvalidVariantError if not found
            self.winning_variant_id = winning_variant_id
        
        # Update test status
        self.status = "completed"
        self.ended_at = datetime.now()
        self.updated_at = self.ended_at
        
        return {
            "test_id": self.id,
            "name": self.name,
            "status": self.status,
            "ended_at": self.ended_at.isoformat(),
            "winning_variant_id": self.winning_variant_id,
            "results": self.get_results()
        }


class ABTesting(IABTesting):
    """
    A/B testing implementation for marketing campaigns.
    
    This class provides functionality for creating and managing A/B tests
    for different marketing assets.
    """
    
    def __init__(self):
        """Initialize the A/B testing service."""
        self.tests = {}  # Dictionary of active and completed tests
        self.logger = logging.getLogger(__name__)
    
    def create_test(
        self,
        name: str,
        description: str,
        content_type: str,
        test_type: str,
        variants: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create an A/B test.
        
        Args:
            name: Test name
            description: Test description
            content_type: Type of content being tested (email, landing_page, ad, etc.)
            test_type: Type of test (a_b, split, multivariate)
            variants: List of test variants including control
            
        Returns:
            A/B test dictionary
            
        Raises:
            InvalidTestConfigurationError: If the test configuration is invalid
        """
        if test_type not in ["a_b", "split", "multivariate"]:
            raise InvalidTestConfigurationError(f"Invalid test type: {test_type}")
        
        if not variants or len(variants) < 2:
            raise InvalidTestConfigurationError("At least two variants are required for an A/B test")
        
        # Generate test ID
        test_id = str(uuid.uuid4())
        
        # Create the test
        test = ABTest(
            id=test_id,
            name=name,
            description=description,
            content_type=content_type,
            test_type=test_type,
            variants=variants
        )
        
        # Store the test
        self.tests[test_id] = test
        
        self.logger.info(f"Created {test_type} test '{name}' with ID {test_id}")
        
        return test.to_dict()
    
    def get_tests(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all tests, optionally filtered by status.
        
        Args:
            status: Optional status to filter by (active, completed)
            
        Returns:
            List of test dictionaries
        """
        if status:
            return [test.to_dict() for test in self.tests.values() if test.status == status]
        
        return [test.to_dict() for test in self.tests.values()]
    
    def get_test(self, test_id: str) -> Dict[str, Any]:
        """
        Get a single test by ID.
        
        Args:
            test_id: ID of the test
            
        Returns:
            Test dictionary
            
        Raises:
            TestNotFoundError: If the test is not found
        """
        test = self.tests.get(test_id)
        if not test:
            raise TestNotFoundError(f"Test with ID '{test_id}' not found")
        
        return test.to_dict()
    
    def get_variants(self, test_id: str) -> List[Dict[str, Any]]:
        """
        Get variants for an A/B test.
        
        Args:
            test_id: ID of the A/B test
            
        Returns:
            List of variant dictionaries
            
        Raises:
            TestNotFoundError: If the test is not found
        """
        test = self.tests.get(test_id)
        if not test:
            raise TestNotFoundError(f"Test with ID '{test_id}' not found")
        
        return test.variants
    
    def record_interaction(
        self,
        test_id: str,
        variant_id: str,
        interaction_type: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record an interaction with a variant.
        
        Args:
            test_id: ID of the A/B test
            variant_id: ID of the variant
            interaction_type: Type of interaction (impression, click, conversion, etc.)
            user_id: Optional ID of the user
            metadata: Optional metadata about the interaction
            
        Returns:
            Interaction dictionary
            
        Raises:
            TestNotFoundError: If the test is not found
            TestAlreadyEndedError: If the test has already ended
            InvalidVariantError: If the variant ID is invalid
        """
        test = self.tests.get(test_id)
        if not test:
            raise TestNotFoundError(f"Test with ID '{test_id}' not found")
        
        interaction = test.record_interaction(variant_id, interaction_type, user_id, metadata)
        
        if interaction_type in ["click", "conversion"]:
            self.logger.info(
                f"Recorded {interaction_type} for test '{test.name}' ({test_id}), "
                f"variant {variant_id}"
            )
        
        return interaction
    
    def get_results(self, test_id: str) -> Dict[str, Any]:
        """
        Get results for an A/B test.
        
        Args:
            test_id: ID of the A/B test
            
        Returns:
            Dictionary with test results
            
        Raises:
            TestNotFoundError: If the test is not found
        """
        test = self.tests.get(test_id)
        if not test:
            raise TestNotFoundError(f"Test with ID '{test_id}' not found")
        
        return test.get_results()
    
    def analyze_test(self, test_id: str) -> Dict[str, Any]:
        """
        Analyze an A/B test for statistical significance.
        
        Args:
            test_id: ID of the A/B test
            
        Returns:
            Dictionary with test analysis
            
        Raises:
            TestNotFoundError: If the test is not found
            InsufficientDataError: If there is not enough data to analyze the test
        """
        test = self.tests.get(test_id)
        if not test:
            raise TestNotFoundError(f"Test with ID '{test_id}' not found")
        
        return test.analyze_test()
    
    def end_test(self, test_id: str, winning_variant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        End an A/B test and optionally select a winning variant.
        
        Args:
            test_id: ID of the A/B test
            winning_variant_id: Optional ID of the winning variant
            
        Returns:
            Dictionary with test results and winner
            
        Raises:
            TestNotFoundError: If the test is not found
            TestAlreadyEndedError: If the test has already ended
            InvalidVariantError: If the winning variant ID is invalid
        """
        test = self.tests.get(test_id)
        if not test:
            raise TestNotFoundError(f"Test with ID '{test_id}' not found")
        
        result = test.end_test(winning_variant_id)
        
        self.logger.info(
            f"Ended test '{test.name}' ({test_id}) with winning variant "
            f"{test.winning_variant_id or 'None'}"
        )
        
        return result
    
    def generate_test_recommendation(self, content_type: str, target_persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate recommendations for A/B testing based on content type and target persona.
        
        Args:
            content_type: Type of content (email, landing_page, ad, etc.)
            target_persona: Target persona for the content
            
        Returns:
            Dictionary with test recommendations
        """
        recommendations = {
            "content_type": content_type,
            "test_elements": [],
            "test_variants": [],
            "suggested_sample_size": 0,
            "suggested_run_time": "",
            "expected_improvement": ""
        }
        
        # Recommendations based on content type
        if content_type == "email":
            recommendations["test_elements"] = [
                {"element": "subject_line", "importance": "high", "reason": "Directly impacts open rates"},
                {"element": "call_to_action", "importance": "high", "reason": "Directly impacts click rates"},
                {"element": "preview_text", "importance": "medium", "reason": "Influences open rates"},
                {"element": "sender_name", "importance": "medium", "reason": "Affects trust and open rates"},
                {"element": "content_length", "importance": "medium", "reason": "Affects engagement"},
                {"element": "send_time", "importance": "medium", "reason": "Affects open rates"}
            ]
            recommendations["suggested_sample_size"] = 5000
            recommendations["suggested_run_time"] = "7 days"
            recommendations["expected_improvement"] = "10-30% increase in open or click rates"
            
        elif content_type == "landing_page":
            recommendations["test_elements"] = [
                {"element": "headline", "importance": "high", "reason": "First thing visitors see"},
                {"element": "call_to_action", "importance": "high", "reason": "Directly impacts conversion rates"},
                {"element": "hero_image", "importance": "high", "reason": "Creates visual first impression"},
                {"element": "form_length", "importance": "medium", "reason": "Affects form completion rates"},
                {"element": "social_proof", "importance": "medium", "reason": "Builds trust"},
                {"element": "page_layout", "importance": "medium", "reason": "Affects user flow"}
            ]
            recommendations["suggested_sample_size"] = 1000
            recommendations["suggested_run_time"] = "14-30 days"
            recommendations["expected_improvement"] = "20-50% increase in conversion rates"
            
        elif content_type == "ad":
            recommendations["test_elements"] = [
                {"element": "headline", "importance": "high", "reason": "Drives click-through rate"},
                {"element": "image", "importance": "high", "reason": "Creates visual appeal"},
                {"element": "call_to_action", "importance": "high", "reason": "Drives clicks"},
                {"element": "value_proposition", "importance": "medium", "reason": "Communicates benefits"},
                {"element": "ad_format", "importance": "medium", "reason": "Affects visibility and engagement"}
            ]
            recommendations["suggested_sample_size"] = 10000
            recommendations["suggested_run_time"] = "7-14 days"
            recommendations["expected_improvement"] = "10-40% increase in click-through rates"
            
        # Generate test variants based on persona and content type
        persona_name = target_persona.get("name", "")
        persona_pain_points = target_persona.get("pain_points", [])
        persona_goals = target_persona.get("goals", [])
        
        if content_type == "email" and persona_pain_points and persona_goals:
            subject_variants = [
                {"type": "pain_point", "value": f"Solve your {persona_pain_points[0]} today"},
                {"type": "benefit", "value": f"Achieve {persona_goals[0]} faster"},
                {"type": "question", "value": f"Are you struggling with {persona_pain_points[0]}?"},
                {"type": "curiosity", "value": f"The surprising solution to {persona_pain_points[0]}"},
            ]
            
            cta_variants = [
                {"type": "direct", "value": "Get Started Now"},
                {"type": "benefit", "value": f"Achieve {persona_goals[0]}"},
                {"type": "solution", "value": f"Solve {persona_pain_points[0]}"},
                {"type": "low_friction", "value": "Learn More"}
            ]
            
            recommendations["test_variants"].append({
                "element": "subject_line",
                "variants": subject_variants
            })
            
            recommendations["test_variants"].append({
                "element": "call_to_action",
                "variants": cta_variants
            })
        
        return recommendations