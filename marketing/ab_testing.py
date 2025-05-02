"""
A/B testing module for marketing campaigns.

This module provides tools for creating, managing, and analyzing A/B tests
for different marketing assets including email campaigns, landing pages,
ad copy, call-to-action elements, and more.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from scipy import stats

from interfaces.marketing_interfaces import IABTesting
from marketing.errors import (
    MarketingError,
    InvalidTestConfigurationError,
    TestNotFoundError,
)


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
        created_at: datetime = None,
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
        self.created_at = created_at or datetime.utcnow()
        self.ended_at = None

        # Validate variants
        if len(variants) < 2:
            raise InvalidTestConfigurationError("Test must have at least 2 variants")
        if not any(v.get("is_control") for v in variants):
            raise InvalidTestConfigurationError("Test must have a control variant")
        if sum(1 for v in variants if v.get("is_control")) > 1:
            raise InvalidTestConfigurationError("Test can only have one control variant")

        # Initialize metrics for each variant
        for variant in self.variants:
            variant.setdefault("metrics", {
                "impressions": 0,
                "interactions": 0,
                "conversions": 0,
                "revenue": 0.0
            })
            variant.setdefault("user_ids", set())

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
            "variants": [
                {
                    **v,
                    "user_ids": list(v["user_ids"]),
                    "metrics": v["metrics"]
                }
                for v in self.variants
            ],
            "created_at": self.created_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "results": self.analyze_test() if self.ended_at else None
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

        raise InvalidVariantError(
            f"Variant with ID '{variant_id}' not found in test '{self.id}'"
        )

    def record_interaction(
        self,
        variant_id: str,
        interaction_type: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
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
        if self.ended_at:
            raise TestAlreadyEndedError("Cannot record interactions for ended test")

        variant_idx = self._get_variant_index(variant_id)
        variant = self.variants[variant_idx]

        # Update metrics based on interaction type
        if interaction_type == "impression":
            variant["metrics"]["impressions"] += 1
        elif interaction_type == "interaction":
            variant["metrics"]["interactions"] += 1
        elif interaction_type == "conversion":
            variant["metrics"]["conversions"] += 1
            if metadata and "revenue" in metadata:
                variant["metrics"]["revenue"] += float(metadata["revenue"])

        # Track user if provided
        if user_id:
            variant["user_ids"].add(user_id)

        return self._calculate_metrics(variant_id)

    def _calculate_metrics(self, variant_id: str) -> Dict[str, Any]:
        """
        Calculate metrics for a variant.

        Args:
            variant_id: ID of the variant

        Returns:
            Dictionary of metrics
        """
        variant_idx = self._get_variant_index(variant_id)
        variant = self.variants[variant_idx]
        metrics = variant["metrics"]

        result = {
            "id": variant["id"],
            "name": variant["name"],
            "is_control": variant.get("is_control", False),
            "impressions": metrics["impressions"],
            "interactions": metrics["interactions"],
            "conversions": metrics["conversions"],
            "revenue": metrics["revenue"],
            "unique_users": len(variant["user_ids"])
        }

        # Calculate rates
        if metrics["impressions"] > 0:
            result["interaction_rate"] = metrics["interactions"] / metrics["impressions"]
            result["conversion_rate"] = metrics["conversions"] / metrics["impressions"]
            result["revenue_per_impression"] = metrics["revenue"] / metrics["impressions"]
        else:
            result["interaction_rate"] = 0
            result["conversion_rate"] = 0
            result["revenue_per_impression"] = 0

        if metrics["interactions"] > 0:
            result["conversion_per_interaction"] = metrics["conversions"] / metrics["interactions"]
            result["revenue_per_interaction"] = metrics["revenue"] / metrics["interactions"]
        else:
            result["conversion_per_interaction"] = 0
            result["revenue_per_interaction"] = 0

        if metrics["conversions"] > 0:
            result["revenue_per_conversion"] = metrics["revenue"] / metrics["conversions"]
        else:
            result["revenue_per_conversion"] = 0

        return result

    def _get_control_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get metrics for the control variant.

        Returns:
            Dictionary of control variant metrics or None if no control variant exists
        """
        for variant in self.variants:
            if variant.get("is_control"):
                return self._calculate_metrics(variant["id"])
        return None

    def _get_best_performing_variant_by_ctr(
        self, variants: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Find the variant with the best click-through rate (CTR).

        Args:
            variants: List of variants to compare

        Returns:
            ID of the variant with the best CTR, or None if no valid variants

        Raises:
            ZeroDivisionError: If a variant has impressions but no clicks
        """
        max_ctr = -1
        best_variant = None

        for variant in variants:
            metrics = variant["metrics"]
            if metrics["impressions"] > 0:
                ctr = metrics["interactions"] / metrics["impressions"]
                if ctr > max_ctr:
                    max_ctr = ctr
                    best_variant = variant["id"]

        return best_variant

    def get_results(self) -> Dict[str, Any]:
        """Get current test results."""
        results = {
            "test_id": self.id,
            "name": self.name,
            "status": self.status,
            "total_impressions": 0,
            "total_clicks": 0,
            "total_conversions": 0,
            "variants": [],
        }

        for variant in self.variants:
            metrics = self._calculate_metrics(variant["id"])
            variant_result = {
                "id": variant["id"],
                "name": variant["name"],
                "is_control": variant.get("is_control", False),
                "metrics": metrics,
            }

            # Calculate lifts if this is not the control variant
            if not variant.get("is_control", False):
                control_metrics = self._get_control_metrics()
                if control_metrics:
                    # Calculate CTR lift if control has impressions
                    if control_metrics["click_through_rate"] > 0:
                        variant_result["ctr_lift"] = round(
                            (
                                (
                                    metrics["click_through_rate"]
                                    / control_metrics["click_through_rate"]
                                )
                                - 1
                            )
                            * 100,
                            1,
                        )
                    else:
                        # If control has no click-through rate, and variant does, lift is infinite (set to 100%)
                        variant_result["ctr_lift"] = (
                            100.0 if metrics["click_through_rate"] > 0 else 0.0
                        )

                    # Calculate conversion lift if control has conversions
                    if control_metrics["conversion_rate"] > 0:
                        variant_result["conversion_lift"] = round(
                            (
                                (
                                    metrics["conversion_rate"]
                                    / control_metrics["conversion_rate"]
                                )
                                - 1
                            )
                            * 100,
                            1,
                        )
                    else:
                        # If control has no conversion rate, and variant does, lift is infinite (set to 100%)
                        variant_result["conversion_lift"] = (
                            100.0 if metrics["conversion_rate"] > 0 else 0.0
                        )

            results["variants"].append(variant_result)
            results["total_impressions"] += metrics["impressions"]
            results["total_clicks"] += metrics["clicks"]
            results["total_conversions"] += metrics["conversions"]

        # Calculate overall rates
        if results["total_impressions"] > 0:
            results["overall_click_through_rate"] = (
                results["total_clicks"] / results["total_impressions"]
            )
        if results["total_clicks"] > 0:
            results["overall_conversion_rate"] = (
                results["total_conversions"] / results["total_clicks"]
            )

        return results

    def _calculate_significance(
        self,
        variant1: Dict[str, Any],
        variant2: Dict[str, Any],
        metric: str = "conversion_rate"
    ) -> Tuple[float, bool]:
        """
        Calculate statistical significance between two variants.

        Args:
            variant1: First variant (typically control)
            variant2: Second variant
            metric: Metric to compare (click_through_rate or conversion_rate)

        Returns:
            Tuple of (p_value, is_significant)
        """
        # Get conversion and impression counts
        variant1_imp = variant1["metrics"]["impressions"]
        variant1_conv = variant1["metrics"]["conversions"]
        variant2_imp = variant2["metrics"]["impressions"]
        variant2_conv = variant2["metrics"]["conversions"]

        # Skip if not enough data
        min_sample = 100  # Minimum sample size per variant
        if variant1_imp < min_sample or variant2_imp < min_sample:
            return 1.0, False  # Not significant if not enough data

        # Create contingency table for Fisher's exact test
        table = [
            [variant1_conv, variant1_imp - variant1_conv],
            [variant2_conv, variant2_imp - variant2_conv]
        ]

        # Use one-tailed Fisher's exact test
        odds_ratio, p_value = stats.fisher_exact(table, alternative="greater")

        # Test is significant if p < 0.05 and variant1 rate > variant2 rate
        is_significant = p_value < 0.05 and (
            variant1_conv/variant1_imp > variant2_conv/variant2_imp
        )

        return p_value, is_significant

    def analyze_test(self) -> Dict[str, Any]:
        """
        Analyze the A/B test for statistical significance.

        Returns:
            Dictionary with test analysis

        Raises:
            InsufficientDataError: If there is not enough data to analyze the test
        """
        if not self.ended_at:
            raise ABTestingError("Cannot analyze test that hasn't ended")

        control_metrics = self._get_control_metrics()
        if not control_metrics:
            raise InvalidTestConfigurationError("No control variant found")

        results = {
            "control": control_metrics,
            "variants": [],
            "winner": None,
            "ended_at": self.ended_at.isoformat(),
            "duration": (self.ended_at - self.created_at).total_seconds(),
            "total_users": len(set().union(*(v["user_ids"] for v in self.variants))),
            "statistical_power": None  # Calculated below if possible
        }

        # Analyze each non-control variant
        for variant in self.variants:
            if variant.get("is_control"):
                continue

            variant_metrics = self._calculate_metrics(variant["id"])
            
            # Calculate significance vs control
            p_value, is_significant = self._calculate_significance(
                variant, 
                next(v for v in self.variants if v.get("is_control"))
            )

            variant_result = {
                **variant_metrics,
                "p_value": p_value,
                "is_significant": is_significant,
                "lift": {
                    "interaction_rate": (
                        variant_metrics["interaction_rate"] / control_metrics["interaction_rate"] - 1
                        if control_metrics["interaction_rate"] > 0 else 0
                    ),
                    "conversion_rate": (
                        variant_metrics["conversion_rate"] / control_metrics["conversion_rate"] - 1
                        if control_metrics["conversion_rate"] > 0 else 0
                    ),
                    "revenue_per_impression": (
                        variant_metrics["revenue_per_impression"] / control_metrics["revenue_per_impression"] - 1
                        if control_metrics["revenue_per_impression"] > 0 else 0
                    )
                }
            }

            results["variants"].append(variant_result)

            # Update winner if this variant is significant and has highest conversion rate
            if (
                is_significant and
                (results["winner"] is None or
                 variant_metrics["conversion_rate"] > results["variants"][results["winner"]]["conversion_rate"])
            ):
                results["winner"] = len(results["variants"]) - 1

        # Calculate test-wide metrics
        total_impressions = sum(v["metrics"]["impressions"] for v in self.variants)
        if total_impressions >= 100:  # Minimum sample size for power calculation
            # Calculate observed effect size
            control_rate = control_metrics["conversion_rate"]
            variant_rates = [v["conversion_rate"] for v in results["variants"]]
            max_effect_size = max(abs(r - control_rate) for r in variant_rates)

            # Calculate statistical power
            if max_effect_size > 0:
                power = stats.power_analysis.power_analysis_two_sample(
                    effect_size=max_effect_size,
                    nobs1=control_metrics["impressions"],
                    ratio=len(self.variants) - 1,  # Number of variant groups
                    alpha=0.05
                )
                results["statistical_power"] = power

        return results

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
                # First try statistical analysis
                analysis = self.analyze_test()
                winning_variant_id = analysis.get("recommended_winner")

                # If no statistically significant winner, pick best performing variant
                if not winning_variant_id:
                    winning_variant_id = self._get_best_performing_variant_by_ctr(
                        self.variants
                    )

            except (InsufficientDataError, ZeroDivisionError):
                # If not enough data or error in calculation, default to control variant
                control_variant = next(
                    (v for v in self.variants if v.get("is_control", False)), None
                )
                if control_variant:
                    winning_variant_id = control_variant["id"]

        # Validate winning variant if specified
        if winning_variant_id:
            self._get_variant_index(
                winning_variant_id
            )  # Will raise InvalidVariantError if not found
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
            "results": self.get_results(),
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
        variants: List[Dict[str, Any]],
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
            raise InvalidTestConfigurationError(
                "At least two variants are required for an A/B test"
            )

        # Generate test ID
        test_id = str(uuid.uuid4())

        # Create the test
        test = ABTest(
            id=test_id,
            name=name,
            description=description,
            content_type=content_type,
            test_type=test_type,
            variants=variants,
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
            return [
                test.to_dict() for test in self.tests.values() if test.status == status
            ]

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
        metadata: Optional[Dict[str, Any]] = None,
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

        interaction = test.record_interaction(
            variant_id, interaction_type, user_id, metadata
        )

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

    def end_test(
        self, test_id: str, winning_variant_id: Optional[str] = None
    ) -> Dict[str, Any]:
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

    def generate_test_recommendation(
        self, content_type: str, target_persona: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            "expected_improvement": "",
        }

        # Recommendations based on content type
        if content_type == "email":
            recommendations["test_elements"] = [
                {
                    "element": "subject_line",
                    "importance": "high",
                    "reason": "Directly impacts open rates",
                },
                {
                    "element": "call_to_action",
                    "importance": "high",
                    "reason": "Directly impacts click rates",
                },
                {
                    "element": "preview_text",
                    "importance": "medium",
                    "reason": "Influences open rates",
                },
                {
                    "element": "sender_name",
                    "importance": "medium",
                    "reason": "Affects trust and open rates",
                },
                {
                    "element": "content_length",
                    "importance": "medium",
                    "reason": "Affects engagement",
                },
                {
                    "element": "send_time",
                    "importance": "medium",
                    "reason": "Affects open rates",
                },
            ]
            recommendations["suggested_sample_size"] = 5000
            recommendations["suggested_run_time"] = "7 days"
            recommendations["expected_improvement"] = (
                "10-30% increase in open or click rates"
            )

        elif content_type == "landing_page":
            recommendations["test_elements"] = [
                {
                    "element": "headline",
                    "importance": "high",
                    "reason": "First thing visitors see",
                },
                {
                    "element": "call_to_action",
                    "importance": "high",
                    "reason": "Directly impacts conversion rates",
                },
                {
                    "element": "hero_image",
                    "importance": "high",
                    "reason": "Creates visual first impression",
                },
                {
                    "element": "form_length",
                    "importance": "medium",
                    "reason": "Affects form completion rates",
                },
                {
                    "element": "social_proof",
                    "importance": "medium",
                    "reason": "Builds trust",
                },
                {
                    "element": "page_layout",
                    "importance": "medium",
                    "reason": "Affects user flow",
                },
            ]
            recommendations["suggested_sample_size"] = 1000
            recommendations["suggested_run_time"] = "14-30 days"
            recommendations["expected_improvement"] = (
                "20-50% increase in conversion rates"
            )

        elif content_type == "ad":
            recommendations["test_elements"] = [
                {
                    "element": "headline",
                    "importance": "high",
                    "reason": "Drives click-through rate",
                },
                {
                    "element": "image",
                    "importance": "high",
                    "reason": "Creates visual appeal",
                },
                {
                    "element": "call_to_action",
                    "importance": "high",
                    "reason": "Drives clicks",
                },
                {
                    "element": "value_proposition",
                    "importance": "medium",
                    "reason": "Communicates benefits",
                },
                {
                    "element": "ad_format",
                    "importance": "medium",
                    "reason": "Affects visibility and engagement",
                },
            ]
            recommendations["suggested_sample_size"] = 10000
            recommendations["suggested_run_time"] = "7-14 days"
            recommendations["expected_improvement"] = (
                "10-40% increase in click-through rates"
            )

        # Generate test variants based on persona and content type
        persona_name = target_persona.get("name", "")
        persona_pain_points = target_persona.get("pain_points", [])
        persona_goals = target_persona.get("goals", [])

        if content_type == "email" and persona_pain_points and persona_goals:
            subject_variants = [
                {
                    "type": "pain_point",
                    "value": f"Solve your {persona_pain_points[0]} today",
                },
                {"type": "benefit", "value": f"Achieve {persona_goals[0]} faster"},
                {
                    "type": "question",
                    "value": f"Are you struggling with {persona_pain_points[0]}?",
                },
                {
                    "type": "curiosity",
                    "value": f"The surprising solution to {persona_pain_points[0]}",
                },
            ]

            cta_variants = [
                {"type": "direct", "value": "Get Started Now"},
                {"type": "benefit", "value": f"Achieve {persona_goals[0]}"},
                {"type": "solution", "value": f"Solve {persona_pain_points[0]}"},
                {"type": "low_friction", "value": "Learn More"},
            ]

            recommendations["test_variants"].append(
                {"element": "subject_line", "variants": subject_variants}
            )

            recommendations["test_variants"].append(
                {"element": "call_to_action", "variants": cta_variants}
            )

        return recommendations
