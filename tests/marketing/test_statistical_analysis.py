"""
Tests for the statistical analysis framework used in A/B testing.
"""

import pytest
import numpy as np
from scipy import stats
from math import sqrt
from unittest.mock import MagicMock, patch

from marketing.ab_testing.statistical_analysis import (
    StatisticalAnalyzer,
    SignificanceTest,
    EffectSizeCalculator,
    PowerAnalysis
)
from marketing.ab_testing.errors import InsufficientDataError, InvalidTestConfigurationError


class TestStatisticalAnalysis:
    """Test cases for statistical analysis framework."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = StatisticalAnalyzer()
        self.effect_size_calc = EffectSizeCalculator()
        self.power_analyzer = PowerAnalysis()

    def test_chi_square_test(self):
        """Test chi-square test for conversion rate comparison."""
        # Test data
        control_data = {"impressions": 1000, "conversions": 100}  # 10% conversion
        variant_data = {"impressions": 1000, "conversions": 150}  # 15% conversion

        # Run chi-square test
        result = self.analyzer.run_chi_square_test(
            control_data["impressions"],
            control_data["conversions"],
            variant_data["impressions"],
            variant_data["conversions"]
        )

        # Validate test results
        assert "chi_square_statistic" in result
        assert "p_value" in result
        assert "degrees_of_freedom" in result
        assert result["degrees_of_freedom"] == 1
        assert 0 <= result["p_value"] <= 1
        assert result["chi_square_statistic"] > 0

    def test_fishers_exact_test(self):
        """Test Fisher's exact test for small sample sizes."""
        # Small sample test data
        control_data = {"impressions": 50, "conversions": 5}
        variant_data = {"impressions": 50, "conversions": 15}

        # Run Fisher's exact test
        result = self.analyzer.run_fishers_exact_test(
            control_data["impressions"],
            control_data["conversions"],
            variant_data["impressions"],
            variant_data["conversions"]
        )

        # Validate test results
        assert "odds_ratio" in result
        assert "p_value" in result
        assert 0 <= result["p_value"] <= 1

    def test_z_test_proportions(self):
        """Test z-test for comparing proportions."""
        # Test data
        control_data = {"impressions": 2000, "conversions": 200}  # 10% conversion
        variant_data = {"impressions": 2000, "conversions": 260}  # 13% conversion

        # Run z-test
        result = self.analyzer.run_z_test_proportions(
            control_data["impressions"],
            control_data["conversions"],
            variant_data["impressions"],
            variant_data["conversions"]
        )

        # Validate test results
        assert "z_statistic" in result
        assert "p_value" in result
        assert "confidence_interval" in result
        assert len(result["confidence_interval"]) == 2
        assert 0 <= result["p_value"] <= 1

    def test_effect_size_calculation(self):
        """Test effect size calculations."""
        # Test data for Cohen's h (for proportions)
        p1 = 0.10  # 10% conversion rate
        p2 = 0.15  # 15% conversion rate

        # Calculate Cohen's h
        effect_size = self.effect_size_calc.cohens_h(p1, p2)

        # Validate effect size
        assert isinstance(effect_size, float)
        assert effect_size > 0  # Should be positive since p2 > p1

        # Test relative risk
        control_data = {"impressions": 1000, "conversions": 100}
        variant_data = {"impressions": 1000, "conversions": 150}

        relative_risk = self.effect_size_calc.relative_risk(
            control_data["impressions"],
            control_data["conversions"],
            variant_data["impressions"],
            variant_data["conversions"]
        )

        # Validate relative risk
        assert isinstance(relative_risk, float)
        assert relative_risk > 1  # Should be > 1 since variant has higher conversion

    def test_confidence_intervals(self):
        """Test confidence interval calculations."""
        # Test data
        control_data = {"impressions": 1000, "conversions": 100}
        variant_data = {"impressions": 1000, "conversions": 150}

        # Calculate confidence intervals
        control_ci = self.analyzer.calculate_proportion_ci(
            control_data["conversions"],
            control_data["impressions"],
            confidence_level=0.95
        )
        variant_ci = self.analyzer.calculate_proportion_ci(
            variant_data["conversions"],
            variant_data["impressions"],
            confidence_level=0.95
        )

        # Validate confidence intervals
        assert len(control_ci) == 2
        assert len(variant_ci) == 2
        assert control_ci[0] < control_ci[1]
        assert variant_ci[0] < variant_ci[1]
        assert 0 <= control_ci[0] <= control_ci[1] <= 1
        assert 0 <= variant_ci[0] <= variant_ci[1] <= 1

    def test_power_analysis(self):
        """Test statistical power analysis."""
        # Test parameters
        effect_size = 0.3  # Medium effect size
        alpha = 0.05  # Significance level
        power = 0.8  # Desired power

        # Calculate required sample size
        sample_size = self.power_analyzer.calculate_sample_size(
            effect_size=effect_size,
            alpha=alpha,
            power=power
        )

        # Validate sample size calculation
        assert isinstance(sample_size, int)
        assert sample_size > 0

        # Calculate achieved power
        achieved_power = self.power_analyzer.calculate_achieved_power(
            sample_size=1000,
            effect_size=effect_size,
            alpha=alpha
        )

        # Validate achieved power
        assert isinstance(achieved_power, float)
        assert 0 <= achieved_power <= 1

    def test_multiple_comparison_correction(self):
        """Test multiple comparison correction methods."""
        # Test data: p-values from multiple tests
        p_values = [0.02, 0.04, 0.01, 0.03, 0.005]

        # Apply Bonferroni correction
        corrected_p_values = self.analyzer.bonferroni_correction(p_values)

        # Validate corrected p-values
        assert len(corrected_p_values) == len(p_values)
        assert all(0 <= p <= 1 for p in corrected_p_values)
        assert all(corrected_p >= original_p 
                  for corrected_p, original_p in zip(corrected_p_values, p_values))

        # Apply FDR correction
        fdr_corrected = self.analyzer.fdr_correction(p_values)

        # Validate FDR correction
        assert len(fdr_corrected) == len(p_values)
        assert all(0 <= p <= 1 for p in fdr_corrected)

    def test_sequential_analysis(self):
        """Test sequential analysis methods."""
        # Initialize sequential test
        sequential_test = self.analyzer.init_sequential_test(
            min_sample_size=100,
            max_sample_size=1000,
            alpha=0.05
        )

        # Test data points
        control_data = {"impressions": 500, "conversions": 50}
        variant_data = {"impressions": 500, "conversions": 75}

        # Run sequential analysis
        result = self.analyzer.analyze_sequential_data(
            sequential_test,
            control_data["impressions"],
            control_data["conversions"],
            variant_data["impressions"],
            variant_data["conversions"]
        )

        # Validate sequential analysis results
        assert "continue_sampling" in result
        assert "crossed_boundary" in result
        assert "current_z_score" in result
        assert isinstance(result["continue_sampling"], bool)

    def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        # Test with invalid sample sizes
        with pytest.raises(InvalidTestConfigurationError):
            self.analyzer.run_chi_square_test(0, 0, 100, 10)

        # Test with invalid conversion counts
        with pytest.raises(InvalidTestConfigurationError):
            self.analyzer.run_chi_square_test(100, -1, 100, 10)

        # Test with conversions > impressions
        with pytest.raises(InvalidTestConfigurationError):
            self.analyzer.run_chi_square_test(100, 101, 100, 10)

    def test_small_sample_handling(self):
        """Test handling of small sample sizes."""
        # Test automatic switch to Fisher's exact test
        result = self.analyzer.analyze_conversion_data(
            control_impressions=20,
            control_conversions=2,
            variant_impressions=20,
            variant_conversions=6
        )

        # Validate that Fisher's exact test was used
        assert result["test_method"] == "fisher"
        assert "odds_ratio" in result
        assert "p_value" in result

    def test_type_i_ii_error_analysis(self):
        """Test Type I and Type II error rate analysis."""
        # Calculate Type I error rate (alpha)
        alpha = self.power_analyzer.calculate_type_i_error_rate(
            sample_size=1000,
            effect_size=0.0  # Null hypothesis is true
        )

        # Validate Type I error rate
        assert isinstance(alpha, float)
        assert 0 <= alpha <= 1

        # Calculate Type II error rate (beta)
        beta = self.power_analyzer.calculate_type_ii_error_rate(
            sample_size=1000,
            effect_size=0.3  # Alternative hypothesis is true
        )

        # Validate Type II error rate
        assert isinstance(beta, float)
        assert 0 <= beta <= 1
        assert (1 - beta) > 0  # Power should be positive


if __name__ == "__main__":
    pytest.main(["-v", "test_statistical_analysis.py"])