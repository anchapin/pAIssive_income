"""
Tests for the statistical analysis framework used in marketing.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from scipy import stats

from marketing.errors import InsufficientDataError, InvalidTestConfigurationError
from marketing.statistical_framework import (
    ConfidenceIntervalCalculator,
    EffectSizeEstimator,
    MultipleTestingAdjuster,
    SequentialAnalyzer,
    StatisticalTestRunner,
)


class TestStatisticalFramework:
    """Test cases for statistical analysis framework."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_runner = StatisticalTestRunner()
        self.ci_calculator = ConfidenceIntervalCalculator()
        self.effect_estimator = EffectSizeEstimator()
        self.mt_adjuster = MultipleTestingAdjuster()
        self.sequential_analyzer = SequentialAnalyzer()

    def test_chi_square_test(self):
        """Test chi - square test implementation."""
        # Test data: 2x2 contingency table
        observed = np.array([[100, 50], [80, 70]])  # Clicks vs No - clicks for A / B

        # Run chi - square test
        result = self.test_runner.run_chi_square_test(observed)

        # Validate results
        assert "statistic" in result
        assert "p_value" in result
        assert "dof" in result
        assert result["dof"] == 1  # 2x2 table has 1 degree of freedom
        assert 0 <= result["p_value"] <= 1

        # Test assumptions validation
        with pytest.raises(InvalidTestConfigurationError):
            self.test_runner.run_chi_square_test(np.array([[1, 2]]))  # Invalid shape

    def test_fishers_exact_test(self):
        """Test Fisher's exact test for small samples."""
        # Test data: small sample 2x2 contingency table
        observed = np.array([[8, 2], [1, 5]])  # Small sample scenario

        # Run Fisher's exact test
        result = self.test_runner.run_fishers_exact_test(observed)

        # Validate results
        assert "odds_ratio" in result
        assert "p_value" in result
        assert 0 <= result["p_value"] <= 1

    def test_z_test_proportions(self):
        """Test z - test for proportions."""
        # Test data
        success_a = 150
        total_a = 1000
        success_b = 180
        total_b = 1000

        # Run z - test
        result = self.test_runner.run_z_test_proportions(success_a, total_a, success_b, 
            total_b)

        # Validate results
        assert "z_statistic" in result
        assert "p_value" in result
        assert "confidence_interval" in result
        assert len(result["confidence_interval"]) == 2
        assert result["confidence_interval"][0] < result["confidence_interval"][1]

    def test_confidence_intervals(self):
        """Test confidence interval calculations."""
        # Test data
        successes = 150
        total = 1000
        confidence_levels = [0.90, 0.95, 0.99]

        for level in confidence_levels:
            # Calculate CI
            ci = self.ci_calculator.calculate_proportion_ci(
                successes, total, confidence_level=level
            )

            # Validate CI
            assert len(ci) == 2
            assert 0 <= ci[0] <= ci[1] <= 1
            assert ci[1] - ci[0] > 0  # Positive width

    def test_effect_size_calculations(self):
        """Test effect size calculations."""
        # Test data for Cohen's h
        p1, p2 = 0.15, 0.20  # Two proportions

        # Calculate Cohen's h
        h = self.effect_estimator.cohens_h(p1, p2)

        # Validate effect size
        assert isinstance(h, float)
        assert h > 0  # Should be positive since p2 > p1

        # Test relative risk
        a_success, a_total = 150, 1000
        b_success, b_total = 180, 1000
        rr = self.effect_estimator.relative_risk(a_success, a_total, b_success, b_total)

        # Validate relative risk
        assert isinstance(rr, float)
        assert rr > 0

    def test_multiple_testing_adjustment(self):
        """Test multiple testing correction methods."""
        # Test data: multiple p - values
        p_values = np.array([0.01, 0.02, 0.03, 0.04, 0.05])

        # Test Bonferroni correction
        bonferroni = self.mt_adjuster.bonferroni_correction(p_values)
        assert len(bonferroni) == len(p_values)
        assert all(0 <= p <= 1 for p in bonferroni)
        assert all(b >= p for b, p in zip(bonferroni, p_values))

        # Test FDR correction
        fdr = self.mt_adjuster.fdr_correction(p_values)
        assert len(fdr) == len(p_values)
        assert all(0 <= p <= 1 for p in fdr)

    def test_sequential_analysis(self):
        """Test sequential analysis methods."""
        # Initialize sequential test
        test = self.sequential_analyzer.init_test(
            min_sample=100, max_sample=1000, effect_size=0.1, alpha=0.05, beta=0.2
        )

        # Add observations
        for _ in range(5):
            result = self.sequential_analyzer.update_analysis(
                test, successes_a=30, total_a=100, successes_b=35, total_b=100
            )

        # Validate sequential analysis
        assert "continue_sampling" in result
        assert "z_score" in result
        assert "crossed_boundary" in result
        assert isinstance(result["continue_sampling"], bool)

    def test_power_analysis(self):
        """Test power analysis calculations."""
        # Calculate required sample size
        sample_size = self.test_runner.calculate_sample_size(effect_size=0.2, alpha=0.05, 
            power=0.8)

        # Validate sample size calculation
        assert isinstance(sample_size, int)
        assert sample_size > 0

        # Calculate achieved power
        power = self.test_runner.calculate_power(effect_size=0.2, sample_size=1000, 
            alpha=0.05)

        # Validate power calculation
        assert 0 <= power <= 1

    def test_assumptions_checking(self):
        """Test statistical assumptions checking."""
        # Test data
        sample_size = 100
        success_count = 20

        # Check sample size assumption
        result = self.test_runner.check_sample_size_assumption(sample_size, 
            success_count)
        assert isinstance(result, bool)

        # Check normality assumption
        data = np.random.normal(0, 1, 1000)
        result = self.test_runner.check_normality_assumption(data)
        assert "is_normal" in result
        assert "test_statistic" in result
        assert "p_value" in result

    def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        # Test with insufficient data
        with pytest.raises(InsufficientDataError):
            self.test_runner.run_z_test_proportions(
                success_a=0, total_a=0, success_b=10, total_b=100
            )

        # Test with invalid proportions
        with pytest.raises(ValueError):
            self.effect_estimator.cohens_h(1.5, 0.5)  # Invalid proportion > 1

        # Test with invalid confidence level
        with pytest.raises(ValueError):
            self.ci_calculator.calculate_proportion_ci(
                successes=10, total=100, 
                    confidence_level=1.5  # Invalid confidence level > 1
            )

    def test_test_selection(self):
        """Test automatic test selection logic."""
        # Test data for different scenarios
        small_sample = {"successes": 5, "total": 50}
        large_sample = {"successes": 150, "total": 1000}

        # Test small sample scenario
        test_type = self.test_runner.select_appropriate_test(
            sample_a=small_sample, sample_b=small_sample
        )
        assert test_type == "fisher"  # Should select Fisher's exact test

        # Test large sample scenario
        test_type = self.test_runner.select_appropriate_test(
            sample_a=large_sample, sample_b=large_sample
        )
        assert test_type in ["chi_square", 
            "z_test"]  # Should select chi - square or z - test


if __name__ == "__main__":
    pytest.main([" - v", "test_statistical_framework.py"])
