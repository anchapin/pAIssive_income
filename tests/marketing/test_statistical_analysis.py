"""
Tests for the statistical analysis module.

This module tests the statistical analysis framework used in marketing analytics
and A / B testing.
"""

import numpy as np
import pytest

from marketing.statistical_analysis import (
    InsufficientDataError,
    InvalidParameterError,
    StatisticalAnalysis,
    StatisticalAnalysisError,
)


class TestStatisticalAnalysis:
    """Tests for the StatisticalAnalysis class."""

    def test_init(self):
        """Test initialization of StatisticalAnalysis."""
        # Test with default parameters
        stats_analysis = StatisticalAnalysis()
        assert stats_analysis.default_alpha == 0.05

        # Test with custom parameters
        stats_analysis = StatisticalAnalysis(default_alpha=0.01)
        assert stats_analysis.default_alpha == 0.01

    def test_validate_data(self):
        """Test data validation method."""
        stats_analysis = StatisticalAnalysis()

        # Test valid data
        assert stats_analysis.validate_data(5, int) is True
        assert stats_analysis.validate_data(5.0, float) is True
        assert stats_analysis.validate_data([1, 2, 3], list) is True
        assert stats_analysis.validate_data(None, int, allow_none=True) is True

        # Test invalid data
        with pytest.raises(InvalidParameterError):
            stats_analysis.validate_data(None, int)

        with pytest.raises(InvalidParameterError):
            stats_analysis.validate_data("string", int)

        with pytest.raises(InvalidParameterError):
            stats_analysis.validate_data(5, int, min_value=10)

        with pytest.raises(InvalidParameterError):
            stats_analysis.validate_data(15, int, max_value=10)

        with pytest.raises(InvalidParameterError):
            stats_analysis.validate_data([], list, min_length=1)

    def test_check_sufficient_data(self):
        """Test sufficient data check."""
        stats_analysis = StatisticalAnalysis()

        # Test sufficient data
        data = list(range(30))
        assert stats_analysis.check_sufficient_data(data) is True

        # Test insufficient data
        data = list(range(10))
        with pytest.raises(InsufficientDataError):
            stats_analysis.check_sufficient_data(data)

        # Test with custom minimum
        data = list(range(20))
        assert stats_analysis.check_sufficient_data(data, min_samples=20) is True
        with pytest.raises(InsufficientDataError):
            stats_analysis.check_sufficient_data(data, min_samples=21)

    def test_mean_and_std(self):
        """Test mean and standard deviation calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test with simple data
        data = [1, 2, 3, 4, 5]
        mean, std = stats_analysis.mean_and_std(data)
        assert mean == 3.0
        assert std == pytest.approx(1.5811, abs=1e - 4)

        # Test with numpy array
        data = np.array([1, 2, 3, 4, 5])
        mean, std = stats_analysis.mean_and_std(data)
        assert mean == 3.0
        assert std == pytest.approx(1.5811, abs=1e - 4)

        # Test with empty list
        with pytest.raises(InvalidParameterError):
            stats_analysis.mean_and_std([])

    def test_median_and_iqr(self):
        """Test median and IQR calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test with odd number of elements
        data = [1, 2, 3, 4, 5]
        median, iqr = stats_analysis.median_and_iqr(data)
        assert median == 3.0
        assert iqr == 2.0  # Q3 (4) - Q1 (2) = 2 using NumPy's default percentile method

        # Test with even number of elements
        data = [1, 2, 3, 4, 5, 6]
        median, iqr = stats_analysis.median_and_iqr(data)
        assert median == 3.5
        assert iqr == 2.5  # Q3 (4.5) - \
            Q1 (2) = 2.5 using NumPy's default percentile method

        # Test with empty list
        with pytest.raises(InvalidParameterError):
            stats_analysis.median_and_iqr([])

    def test_summary_statistics(self):
        """Test summary statistics calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test with simple data
        data = [1, 2, 3, 4, 5]
        stats = stats_analysis.summary_statistics(data)

        assert stats["count"] == 5
        assert stats["mean"] == 3.0
        assert stats["median"] == 3.0
        assert stats["std"] == pytest.approx(1.5811, abs=1e - 4)
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["q1"] == 2.0  # Using NumPy's default percentile method
        assert stats["q3"] == 4.0  # Using NumPy's default percentile method
        assert stats["iqr"] == 2.0  # Q3 (4) - Q1 (2) = 2

        # Test with empty list
        with pytest.raises(InvalidParameterError):
            stats_analysis.summary_statistics([])

    def test_chi_square_test(self):
        """Test chi - square test."""
        stats_analysis = StatisticalAnalysis()

        # Test 2x2 contingency table
        observed = [[10, 20], [30, 40]]
        result = stats_analysis.chi_square_test(observed)

        # Check result structure
        assert "chi2" in result
        assert "p_value" in result
        assert "dof" in result
        assert "expected" in result
        assert "residuals" in result
        assert "is_significant" in result
        assert "test_name" in result
        assert "alpha" in result

        # Check specific values
        assert result["dof"] == 1
        assert result["test_name"] == "chi_square"

        # Test 1D array with expected values
        observed = np.array([10, 20, 30, 40])
        expected = np.array([25, 25, 25, 25])
        result = stats_analysis.chi_square_test(observed, expected)

        assert result["dof"] == 3
        assert result["chi2"] == pytest.approx(20.0, abs=1e - 10)

        # Test with insufficient data
        with pytest.raises(InsufficientDataError):
            stats_analysis.chi_square_test([[1, 2], [3, 4]])

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.chi_square_test(np.array([1, 2, 
                3]))  # 1D array without expected values

    def test_fishers_exact_test(self):
        """Test Fisher's exact test."""
        stats_analysis = StatisticalAnalysis()

        # Test 2x2 contingency table
        table = [[12, 5], [29, 2]]
        result = stats_analysis.fishers_exact_test(table)

        # Check result structure
        assert "odds_ratio" in result
        assert "p_value" in result
        assert "is_significant" in result
        assert "test_name" in result
        assert "alternative" in result
        assert "alpha" in result
        assert "table" in result

        # Check specific values
        assert result["test_name"] == "fishers_exact"
        assert result["alternative"] == "two - sided"

        # Test with different alternative hypotheses
        result_less = stats_analysis.fishers_exact_test(table, alternative="less")
        result_greater = stats_analysis.fishers_exact_test(table, alternative="greater")

        assert result_less["alternative"] == "less"
        assert result_greater["alternative"] == "greater"

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.fishers_exact_test([[1, 2, 3], [4, 5, 6]])  # Not a 2x2 table

        with pytest.raises(InvalidParameterError):
            stats_analysis.fishers_exact_test([[1, 2], [3, 4]], alternative="invalid")

    def test_z_test_proportions(self):
        """Test z - test for proportions."""
        stats_analysis = StatisticalAnalysis()

        # Test two - sample test
        result = stats_analysis.z_test_proportions(count1=40, nobs1=100, count2=30, 
            nobs2=100)

        # Check result structure
        assert "z_score" in result
        assert "p_value" in result
        assert "proportion1" in result
        assert "proportion2" in result
        assert "difference" in result
        assert "pooled_proportion" in result
        assert "standard_error" in result
        assert "is_significant" in result
        assert "test_name" in result
        assert "alternative" in result
        assert "alpha" in result
        assert "count1" in result
        assert "nobs1" in result
        assert "count2" in result
        assert "nobs2" in result
        assert "test_type" in result

        # Check specific values
        assert result["proportion1"] == 0.4
        assert result["proportion2"] == 0.3
        assert result["difference"] == pytest.approx(0.1, abs=1e - 10)
        assert result["test_name"] == "z_test_proportions"
        assert result["test_type"] == "two - sample"

        # Test one - sample test
        result = stats_analysis.z_test_proportions(count1=40, nobs1=100, value=0.3)

        assert "proportion1" in result
        assert "proportion2" in result
        assert result["proportion1"] == 0.4
        assert result["proportion2"] == 0.3
        assert result["test_type"] == "one - sample"

        # Test with different alternative hypotheses
        result_less = stats_analysis.z_test_proportions(
            count1=40, nobs1=100, count2=50, nobs2=100, alternative="less"
        )
        result_greater = stats_analysis.z_test_proportions(
            count1=40, nobs1=100, count2=30, nobs2=100, alternative="greater"
        )

        assert result_less["alternative"] == "less"
        assert result_greater["alternative"] == "greater"

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.z_test_proportions(
                count1=40, nobs1=100
            )  # Missing second sample or value

        with pytest.raises(InvalidParameterError):
            stats_analysis.z_test_proportions(count1=40, nobs1=100, 
                value=1.5)  # Value > 1.0

    def test_confidence_interval_mean(self):
        """Test confidence interval for mean."""
        stats_analysis = StatisticalAnalysis()

        # Test with simple data
        data = [1, 2, 3, 4, 5]
        result = stats_analysis.confidence_interval_mean(data)

        # Check result structure
        assert "mean" in result
        assert "lower_bound" in result
        assert "upper_bound" in result
        assert "confidence_level" in result
        assert "standard_error" in result
        assert "margin_of_error" in result
        assert "degrees_of_freedom" in result
        assert "sample_size" in result
        assert "standard_deviation" in result
        assert "t_value" in result

        # Check specific values
        assert result["mean"] == 3.0
        assert result["confidence_level"] == 0.95
        assert result["degrees_of_freedom"] == 4
        assert result["sample_size"] == 5

        # Test with different confidence levels
        result_90 = stats_analysis.confidence_interval_mean(data, confidence_level=0.90)
        result_99 = stats_analysis.confidence_interval_mean(data, confidence_level=0.99)

        # Higher confidence level should result in wider interval
        assert (
            result_90["margin_of_error"] < result["margin_of_error"] < result_99["margin_of_error"]
        )

        # Test with insufficient data
        with pytest.raises(InsufficientDataError):
            stats_analysis.confidence_interval_mean([1])

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.confidence_interval_mean(data, confidence_level=1.5)

    def test_confidence_interval_proportion(self):
        """Test confidence interval for proportion."""
        stats_analysis = StatisticalAnalysis()

        # Test with normal approximation method
        result = stats_analysis.confidence_interval_proportion(count=40, nobs=100)

        # Check result structure
        assert "proportion" in result
        assert "lower_bound" in result
        assert "upper_bound" in result
        assert "confidence_level" in result
        assert "method" in result
        assert "standard_error" in result
        assert "margin_of_error" in result
        assert "count" in result
        assert "nobs" in result
        assert "z_value" in result

        # Check specific values
        assert result["proportion"] == 0.4
        assert result["confidence_level"] == 0.95
        assert result["method"] == "normal"

        # Test with different methods
        result_wilson = stats_analysis.confidence_interval_proportion(
            count=40, nobs=100, method="wilson"
        )
        result_agresti = stats_analysis.confidence_interval_proportion(
            count=40, nobs=100, method="agresti - coull"
        )
        result_exact = stats_analysis.confidence_interval_proportion(
            count=40, nobs=100, method="exact"
        )

        assert result_wilson["method"] == "wilson"
        assert result_agresti["method"] == "agresti - coull"
        assert result_exact["method"] == "exact"

        # Test with different confidence levels
        result_90 = stats_analysis.confidence_interval_proportion(
            count=40, nobs=100, confidence_level=0.90
        )
        result_99 = stats_analysis.confidence_interval_proportion(
            count=40, nobs=100, confidence_level=0.99
        )

        # Higher confidence level should result in wider interval
        assert (result_99["upper_bound"] - result_99["lower_bound"]) > (
            result["upper_bound"] - result["lower_bound"]
        )
        assert (result["upper_bound"] - result["lower_bound"]) > (
            result_90["upper_bound"] - result_90["lower_bound"]
        )

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.confidence_interval_proportion(count=40, nobs=100, 
                method="invalid")

        with pytest.raises(InvalidParameterError):
            stats_analysis.confidence_interval_proportion(count=40, nobs=100, 
                confidence_level=1.5)

    def test_confidence_interval_difference_proportions(self):
        """Test confidence interval for difference between proportions."""
        stats_analysis = StatisticalAnalysis()

        # Test with normal approximation method
        result = stats_analysis.confidence_interval_difference_proportions(
            count1=40, nobs1=100, count2=30, nobs2=100
        )

        # Check result structure
        assert "proportion1" in result
        assert "proportion2" in result
        assert "difference" in result
        assert "lower_bound" in result
        assert "upper_bound" in result
        assert "confidence_level" in result
        assert "method" in result
        assert "standard_error" in result
        assert "margin_of_error" in result
        assert "count1" in result
        assert "nobs1" in result
        assert "count2" in result
        assert "nobs2" in result
        assert "z_value" in result

        # Check specific values
        assert result["proportion1"] == 0.4
        assert result["proportion2"] == 0.3
        assert result["difference"] == pytest.approx(0.1, abs=1e - 10)
        assert result["confidence_level"] == 0.95
        assert result["method"] == "normal"

        # Test with Agresti - Caffo method
        result_agresti = stats_analysis.confidence_interval_difference_proportions(
            count1=40, nobs1=100, count2=30, nobs2=100, method="agresti - caffo"
        )

        assert result_agresti["method"] == "agresti - caffo"
        assert "adjusted_proportion1" in result_agresti
        assert "adjusted_proportion2" in result_agresti
        assert "adjusted_difference" in result_agresti

        # Test with different confidence levels
        result_90 = stats_analysis.confidence_interval_difference_proportions(
            count1=40, nobs1=100, count2=30, nobs2=100, confidence_level=0.90
        )
        result_99 = stats_analysis.confidence_interval_difference_proportions(
            count1=40, nobs1=100, count2=30, nobs2=100, confidence_level=0.99
        )

        # Higher confidence level should result in wider interval
        assert (result_99["upper_bound"] - result_99["lower_bound"]) > (
            result["upper_bound"] - result["lower_bound"]
        )
        assert (result["upper_bound"] - result["lower_bound"]) > (
            result_90["upper_bound"] - result_90["lower_bound"]
        )

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.confidence_interval_difference_proportions(
                count1=40, nobs1=100, count2=30, nobs2=100, method="invalid"
            )

        with pytest.raises(InvalidParameterError):
            stats_analysis.confidence_interval_difference_proportions(
                count1=40, nobs1=100, count2=30, nobs2=100, confidence_level=1.5
            )

    def test_cohens_d(self):
        """Test Cohen's d effect size calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test with simple data
        group1 = [1, 2, 3, 4, 5]
        group2 = [2, 3, 4, 5, 6]
        result = stats_analysis.cohens_d(group1, group2)

        # Check result structure
        assert "effect_size" in result
        assert "interpretation" in result
        assert "mean1" in result
        assert "mean2" in result
        assert "std1" in result
        assert "std2" in result
        assert "pooled_std" in result
        assert "n1" in result
        assert "n2" in result
        assert "correction_applied" in result

        # Check specific values
        assert result["mean1"] == 3.0
        assert result["mean2"] == 4.0
        assert result["n1"] == 5
        assert result["n2"] == 5
        assert result["correction_applied"] is False
        assert result["effect_size"] == pytest.approx(
            -0.632, abs=1e - 3
        )  # Actual value is around -0.632
        assert result["interpretation"] == "medium"  # 0.5 < |d| < 0.8 is medium

        # Test with Hedges' correction
        result_corrected = stats_analysis.cohens_d(group1, group2, correction=True)
        assert result_corrected["correction_applied"] is True
        assert abs(result_corrected["effect_size"]) < abs(
            result["effect_size"]
        )  # Correction reduces magnitude

        # Test with different effect sizes
        small_effect = stats_analysis.cohens_d([1, 2, 3, 4, 5], [1.5, 2.5, 3.5, 4.5, 
            5.5])
        medium_effect = stats_analysis.cohens_d([1, 2, 3, 4, 5], [2, 3, 4, 5, 6])
        large_effect = stats_analysis.cohens_d([1, 2, 3, 4, 5], [4, 5, 6, 7, 8])

        assert small_effect["interpretation"] in ["small", "medium"]  # Around 0.5
        assert medium_effect["interpretation"] in ["medium", "large"]  # Around 1.0
        assert large_effect["interpretation"] == "large"  # > 0.8

        # Test with insufficient data
        with pytest.raises(InsufficientDataError):
            stats_analysis.cohens_d([1], [2, 3])

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.cohens_d("not a list", [1, 2, 3])

    def test_odds_ratio(self):
        """Test odds ratio calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test with 2x2 contingency table
        table = [
            [30, 70],
            [10, 90],
        ]  # [[exposed cases, exposed non - cases], [unexposed cases, 
            unexposed non - cases]]
        result = stats_analysis.odds_ratio(table)

        # Check result structure
        assert "odds_ratio" in result
        assert "log_odds_ratio" in result
        assert "se_log_odds_ratio" in result
        assert "ci_lower" in result
        assert "ci_upper" in result
        assert "ci_level" in result
        assert "interpretation" in result
        assert "table" in result

        # Check specific values
        assert result["odds_ratio"] == pytest.approx(3.857, 
            abs=1e - 3)  # (30 * 90) / (70 * 10) = 3.857
        assert result["ci_level"] == 0.95
        assert "positive association" in result["interpretation"]

        # Test with different confidence levels
        result_90 = stats_analysis.odds_ratio(table, ci_level=0.90)
        result_99 = stats_analysis.odds_ratio(table, ci_level=0.99)

        assert result_90["ci_level"] == 0.90
        assert result_99["ci_level"] == 0.99

        # Higher confidence level should result in wider interval
        assert (result_99["ci_upper"] - result_99["ci_lower"]) > (
            result["ci_upper"] - result["ci_lower"]
        )
        assert (result["ci_upper"] - result["ci_lower"]) > (
            result_90["ci_upper"] - result_90["ci_lower"]
        )

        # Test with zero cells (should apply Haldane correction)
        table_zero = [[30, 0], [10, 90]]
        result_zero = stats_analysis.odds_ratio(table_zero)
        assert result_zero["odds_ratio"] > 0  # Should not be infinity

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.odds_ratio([[1, 2, 3], [4, 5, 6]])  # Not a 2x2 table

        with pytest.raises(InvalidParameterError):
            stats_analysis.odds_ratio(table, ci_level=1.5)  # Invalid confidence level

    def test_relative_risk(self):
        """Test relative risk calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test with 2x2 contingency table
        table = [
            [30, 70],
            [10, 90],
        ]  # [[exposed cases, exposed non - cases], [unexposed cases, 
            unexposed non - cases]]
        result = stats_analysis.relative_risk(table)

        # Check result structure
        assert "relative_risk" in result
        assert "log_relative_risk" in result
        assert "se_log_relative_risk" in result
        assert "ci_lower" in result
        assert "ci_upper" in result
        assert "ci_level" in result
        assert "risk_exposed" in result
        assert "risk_unexposed" in result
        assert "interpretation" in result
        assert "table" in result

        # Check specific values
        assert result["risk_exposed"] == pytest.approx(30 / 100, 
            abs=1e - 10)  # 30 / (30 + 70) = 0.3
        assert result["risk_unexposed"] == pytest.approx(10 / 100, 
            abs=1e - 10)  # 10 / (10 + 90) = 0.1
        assert result["relative_risk"] == pytest.approx(3.0, 
            abs=1e - 10)  # 0.3 / 0.1 = 3.0
        assert result["ci_level"] == 0.95
        assert "increased risk" in result["interpretation"]

        # Test with different confidence levels
        result_90 = stats_analysis.relative_risk(table, ci_level=0.90)
        result_99 = stats_analysis.relative_risk(table, ci_level=0.99)

        assert result_90["ci_level"] == 0.90
        assert result_99["ci_level"] == 0.99

        # Higher confidence level should result in wider interval
        assert (result_99["ci_upper"] - result_99["ci_lower"]) > (
            result["ci_upper"] - result["ci_lower"]
        )
        assert (result["ci_upper"] - result["ci_lower"]) > (
            result_90["ci_upper"] - result_90["ci_lower"]
        )

        # Test with zero risk in unexposed group (should apply correction)
        table_zero = [[30, 70], [0, 100]]
        result_zero = stats_analysis.relative_risk(table_zero)
        assert result_zero["relative_risk"] > 0  # Should not be infinity

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.relative_risk([[1, 2, 3], [4, 5, 6]])  # Not a 2x2 table

        with pytest.raises(InvalidParameterError):
            stats_analysis.relative_risk(table, 
                ci_level=1.5)  # Invalid confidence level

        with pytest.raises(InvalidParameterError):
            stats_analysis.relative_risk([[0, 0], [10, 90]])  # No exposed subjects

    def test_number_needed_to_treat(self):
        """Test Number Needed to Treat (NNT) calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test with 2x2 contingency table
        table = [
            [20, 80],
            [40, 60],
        ]  # [[treatment cases, treatment non - cases], [control cases, 
            control non - cases]]
        result = stats_analysis.number_needed_to_treat(table)

        # Check result structure
        assert "nnt" in result
        assert "arr" in result
        assert "risk_treatment" in result
        assert "risk_control" in result
        assert "ci_lower" in result
        assert "ci_upper" in result
        assert "ci_level" in result
        assert "interpretation" in result
        assert "table" in result

        # Check specific values
        assert result["risk_treatment"] == pytest.approx(20 / 100, 
            abs=1e - 10)  # 20 / (20 + 80) = 0.2
        assert result["risk_control"] == pytest.approx(40 / 100, 
            abs=1e - 10)  # 40 / (40 + 60) = 0.4
        assert result["arr"] == pytest.approx(0.2, abs=1e - 10)  # 0.4 - 0.2 = 0.2
        assert result["nnt"] == pytest.approx(5.0, abs=1e - 10)  # 1 / 0.2 = 5
        assert result["ci_level"] == 0.95
        assert "beneficial" in result["interpretation"]

        # Test with different confidence levels
        result_90 = stats_analysis.number_needed_to_treat(table, ci_level=0.90)
        result_99 = stats_analysis.number_needed_to_treat(table, ci_level=0.99)

        assert result_90["ci_level"] == 0.90
        assert result_99["ci_level"] == 0.99

        # Test with harmful effect (negative ARR)
        table_harmful = [[40, 60], [20, 80]]  # Reversed from beneficial example
        result_harmful = stats_analysis.number_needed_to_treat(table_harmful)
        assert result_harmful["arr"] < 0
        assert "harmful" in result_harmful["interpretation"]

        # Test with no effect (ARR = 0)
        table_no_effect = [[30, 70], [30, 70]]
        result_no_effect = stats_analysis.number_needed_to_treat(table_no_effect)
        assert result_no_effect["arr"] == 0
        assert result_no_effect["nnt"] == float("inf")
        assert "no effect" in result_no_effect["interpretation"]

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.number_needed_to_treat([[1, 2, 3], [4, 5, 
                6]])  # Not a 2x2 table

        with pytest.raises(InvalidParameterError):
            stats_analysis.number_needed_to_treat(table, 
                ci_level=1.5)  # Invalid confidence level

        with pytest.raises(InvalidParameterError):
            stats_analysis.number_needed_to_treat([[0, 0], [40, 
                60]])  # No treatment subjects

    # -------------------------------------------------------------------------
    # Power Analysis Tests
    # -------------------------------------------------------------------------

    def test_sample_size_for_proportion_test(self):
        """Test sample size calculation for proportion test."""
        stats_analysis = StatisticalAnalysis()

        # Test with default parameters
        result = stats_analysis.sample_size_for_proportion_test(effect_size=0.1)

        # Check result structure
        assert "sample_size" in result
        assert "effect_size" in result
        assert "alpha" in result
        assert "power" in result
        assert "alternative" in result
        assert "p_null" in result
        assert "p_alt" in result
        assert "test_type" in result

        # Check specific values
        assert result["effect_size"] == 0.1
        assert result["alpha"] == 0.05
        assert result["power"] == 0.8
        assert result["alternative"] == "two - sided"
        assert result["p_null"] == 0.5
        assert result["p_alt"] == 0.6
        assert result["test_type"] == "proportion"
        assert isinstance(result["sample_size"], int)
        assert result["sample_size"] > 0

        # Test with custom parameters
        result_custom = stats_analysis.sample_size_for_proportion_test(
            effect_size=0.2, alpha=0.01, power=0.9, alternative="one - sided", 
                p_null=0.3
        )

        assert result_custom["effect_size"] == 0.2
        assert result_custom["alpha"] == 0.01
        assert result_custom["power"] == 0.9
        assert result_custom["alternative"] == "one - sided"
        assert result_custom["p_null"] == 0.3
        assert result_custom["p_alt"] == 0.5

        # Larger effect size should require smaller sample size
        result_large_effect = \
            stats_analysis.sample_size_for_proportion_test(effect_size=0.2)
        assert result_large_effect["sample_size"] < result["sample_size"]

        # Higher power should require larger sample size
        result_high_power = stats_analysis.sample_size_for_proportion_test(
            effect_size=0.1, power=0.9
        )
        assert result_high_power["sample_size"] > result["sample_size"]

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_proportion_test(
                effect_size=0)  # Effect size must be > 0

        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_proportion_test(
                effect_size=0.1, alpha=0
            )  # Alpha must be > 0

        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_proportion_test(
                effect_size=0.1, power=0
            )  # Power must be > 0

        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_proportion_test(
                effect_size=0.1, alternative="invalid"
            )  # Invalid alternative

        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_proportion_test(
                effect_size=0.8, p_null=0.5
            )  # p_alt would be > 1

    def test_sample_size_for_mean_test(self):
        """Test sample size calculation for mean test."""
        stats_analysis = StatisticalAnalysis()

        # Test with default parameters
        result = stats_analysis.sample_size_for_mean_test(effect_size=0.5, std_dev=1.0)

        # Check result structure
        assert "sample_size" in result
        assert "effect_size" in result
        assert "std_dev" in result
        assert "standardized_effect_size" in result
        assert "alpha" in result
        assert "power" in result
        assert "alternative" in result
        assert "test_type" in result

        # Check specific values
        assert result["effect_size"] == 0.5
        assert result["std_dev"] == 1.0
        assert result["standardized_effect_size"] == 0.5  # effect_size / std_dev
        assert result["alpha"] == 0.05
        assert result["power"] == 0.8
        assert result["alternative"] == "two - sided"
        assert result["test_type"] == "mean"
        assert isinstance(result["sample_size"], int)
        assert result["sample_size"] > 0

        # Test with custom parameters
        result_custom = stats_analysis.sample_size_for_mean_test(
            effect_size=1.0, std_dev=2.0, alpha=0.01, power=0.9, 
                alternative="one - sided"
        )

        assert result_custom["effect_size"] == 1.0
        assert result_custom["std_dev"] == 2.0
        assert result_custom["standardized_effect_size"] == 0.5  # 1.0 / 2.0
        assert result_custom["alpha"] == 0.01
        assert result_custom["power"] == 0.9
        assert result_custom["alternative"] == "one - sided"

        # Larger effect size should require smaller sample size
        result_large_effect = stats_analysis.sample_size_for_mean_test(effect_size=1.0, 
            std_dev=1.0)
        assert result_large_effect["sample_size"] < result["sample_size"]

        # Higher power should require larger sample size
        result_high_power = stats_analysis.sample_size_for_mean_test(
            effect_size=0.5, std_dev=1.0, power=0.9
        )
        assert result_high_power["sample_size"] > result["sample_size"]

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_mean_test(
                effect_size=0, std_dev=1.0
            )  # Effect size must be > 0

        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_mean_test(
                effect_size=0.5, std_dev=0
            )  # Std dev must be > 0

        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_mean_test(
                effect_size=0.5, std_dev=1.0, alpha=0
            )  # Alpha must be > 0

        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_mean_test(
                effect_size=0.5, std_dev=1.0, alternative="invalid"
            )  # Invalid alternative

    def test_sample_size_for_correlation(self):
        """Test sample size calculation for correlation test."""
        stats_analysis = StatisticalAnalysis()

        # Test with default parameters
        result = stats_analysis.sample_size_for_correlation(effect_size=0.3)

        # Check result structure
        assert "sample_size" in result
        assert "effect_size" in result
        assert "alpha" in result
        assert "power" in result
        assert "alternative" in result
        assert "test_type" in result

        # Check specific values
        assert result["effect_size"] == 0.3
        assert result["alpha"] == 0.05
        assert result["power"] == 0.8
        assert result["alternative"] == "two - sided"
        assert result["test_type"] == "correlation"
        assert isinstance(result["sample_size"], int)
        assert result["sample_size"] > 0

        # Test with custom parameters
        result_custom = stats_analysis.sample_size_for_correlation(
            effect_size=0.5, alpha=0.01, power=0.9, alternative="one - sided"
        )

        assert result_custom["effect_size"] == 0.5
        assert result_custom["alpha"] == 0.01
        assert result_custom["power"] == 0.9
        assert result_custom["alternative"] == "one - sided"

        # Larger effect size should require smaller sample size
        result_large_effect = \
            stats_analysis.sample_size_for_correlation(effect_size=0.5)
        assert result_large_effect["sample_size"] < result["sample_size"]

        # Higher power should require larger sample size
        result_high_power = stats_analysis.sample_size_for_correlation(effect_size=0.3, 
            power=0.9)
        assert result_high_power["sample_size"] > result["sample_size"]

        # Test with negative correlation (should use absolute value)
        result_negative = stats_analysis.sample_size_for_correlation(effect_size=-0.3)
        assert result_negative["sample_size"] == result["sample_size"]

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_correlation(
                effect_size=0)  # Effect size must be != 0

        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_correlation(
                effect_size=1.5)  # Effect size must be <= 1

        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_correlation(
                effect_size=0.3, alpha=0
            )  # Alpha must be > 0

        with pytest.raises(InvalidParameterError):
            stats_analysis.sample_size_for_correlation(
                effect_size=0.3, alternative="invalid"
            )  # Invalid alternative

    def test_minimum_detectable_effect_size(self):
        """Test minimum detectable effect size calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test for proportion test
        result_prop = stats_analysis.minimum_detectable_effect_size(
            sample_size=100, test_type="proportion"
        )

        # Check result structure
        assert "effect_size" in result_prop
        assert "sample_size" in result_prop
        assert "alpha" in result_prop
        assert "power" in result_prop
        assert "test_type" in result_prop
        assert "alternative" in result_prop
        assert "p_null" in result_prop

        # Check specific values
        assert result_prop["sample_size"] == 100
        assert result_prop["alpha"] == 0.05
        assert result_prop["power"] == 0.8
        assert result_prop["test_type"] == "proportion"
        assert result_prop["alternative"] == "two - sided"
        assert result_prop["p_null"] == 0.5
        assert result_prop["effect_size"] > 0

        # Test for mean test
        result_mean = stats_analysis.minimum_detectable_effect_size(
            sample_size=100, test_type="mean", std_dev=1.0
        )

        assert "effect_size" in result_mean
        assert "std_dev" in result_mean
        assert result_mean["test_type"] == "mean"
        assert result_mean["std_dev"] == 1.0
        assert result_mean["effect_size"] > 0

        # Test for correlation test
        result_corr = stats_analysis.minimum_detectable_effect_size(
            sample_size=100, test_type="correlation"
        )

        assert "effect_size" in result_corr
        assert result_corr["test_type"] == "correlation"
        assert 0 < result_corr["effect_size"] < 1

        # Larger sample size should allow detecting smaller effect sizes
        result_large_sample = stats_analysis.minimum_detectable_effect_size(
            sample_size=400, test_type="proportion"
        )
        assert result_large_sample["effect_size"] < result_prop["effect_size"]

        # Higher power should require larger effect size
        result_high_power = stats_analysis.minimum_detectable_effect_size(
            sample_size=100, test_type="proportion", power=0.9
        )
        assert result_high_power["effect_size"] > result_prop["effect_size"]

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.minimum_detectable_effect_size(
                sample_size=1)  # Sample size must be >= 2

        with pytest.raises(InvalidParameterError):
            stats_analysis.minimum_detectable_effect_size(
                sample_size=100, test_type="invalid"
            )  # Invalid test type

        with pytest.raises(InvalidParameterError):
            stats_analysis.minimum_detectable_effect_size(
                sample_size=100, test_type="mean"
            )  # Missing std_dev

    def test_power_analysis(self):
        """Test power analysis calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test for proportion test
        result_prop = stats_analysis.power_analysis(
            test_type="proportion", effect_size=0.1, sample_size=400
        )

        # Check result structure
        assert "power" in result_prop
        assert "effect_size" in result_prop
        assert "sample_size" in result_prop
        assert "alpha" in result_prop
        assert "test_type" in result_prop
        assert "alternative" in result_prop
        assert "p_null" in result_prop
        assert "p_alt" in result_prop

        # Check specific values
        assert result_prop["effect_size"] == 0.1
        assert result_prop["sample_size"] == 400
        assert result_prop["alpha"] == 0.05
        assert result_prop["test_type"] == "proportion"
        assert result_prop["alternative"] == "two - sided"
        assert result_prop["p_null"] == 0.5
        assert result_prop["p_alt"] == 0.6
        assert 0 <= result_prop["power"] <= 1

        # Test for mean test
        result_mean = stats_analysis.power_analysis(
            test_type="mean", effect_size=0.5, sample_size=100, std_dev=1.0
        )

        assert "power" in result_mean
        assert "std_dev" in result_mean
        assert "standardized_effect_size" in result_mean
        assert result_mean["test_type"] == "mean"
        assert result_mean["std_dev"] == 1.0
        assert result_mean["standardized_effect_size"] == 0.5
        assert 0 <= result_mean["power"] <= 1

        # Test for correlation test
        result_corr = stats_analysis.power_analysis(
            test_type="correlation", effect_size=0.3, sample_size=100
        )

        assert "power" in result_corr
        assert result_corr["test_type"] == "correlation"
        assert result_corr["effect_size"] == 0.3
        assert 0 <= result_corr["power"] <= 1

        # Larger effect size should increase power
        result_large_effect = stats_analysis.power_analysis(
            test_type="proportion", effect_size=0.2, sample_size=400
        )
        assert result_large_effect["power"] > result_prop["power"]

        # Larger sample size should increase power
        result_large_sample = stats_analysis.power_analysis(
            test_type="proportion", effect_size=0.1, sample_size=800
        )
        assert result_large_sample["power"] > result_prop["power"]

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.power_analysis(
                test_type="invalid", effect_size=0.1, sample_size=100
            )  # Invalid test type

        with pytest.raises(InvalidParameterError):
            stats_analysis.power_analysis(
                test_type="mean", effect_size=0.5, sample_size=100
            )  # Missing std_dev

    def test_type_error_rates(self):
        """Test Type I and Type II error rate calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test for proportion test
        result_prop = stats_analysis.type_error_rates(
            test_type="proportion", effect_size=0.1, sample_size=400
        )

        # Check result structure
        assert "type_i_error" in result_prop
        assert "type_ii_error" in result_prop
        assert "power" in result_prop
        assert "effect_size" in result_prop
        assert "sample_size" in result_prop
        assert "test_type" in result_prop
        assert "alternative" in result_prop
        assert "p_null" in result_prop
        assert "p_alt" in result_prop

        # Check specific values
        assert result_prop["type_i_error"] == 0.05
        assert result_prop["power"] + result_prop["type_ii_error"] == pytest.approx(1.0, 
            abs=1e - 10)
        assert result_prop["effect_size"] == 0.1
        assert result_prop["sample_size"] == 400
        assert result_prop["test_type"] == "proportion"
        assert result_prop["alternative"] == "two - sided"
        assert result_prop["p_null"] == 0.5
        assert result_prop["p_alt"] == 0.6

        # Test for mean test
        result_mean = stats_analysis.type_error_rates(
            test_type="mean", effect_size=0.5, sample_size=100, std_dev=1.0
        )

        assert "type_i_error" in result_mean
        assert "type_ii_error" in result_mean
        assert "power" in result_mean
        assert "std_dev" in result_mean
        assert "standardized_effect_size" in result_mean
        assert result_mean["type_i_error"] == 0.05
        assert result_mean["power"] + result_mean["type_ii_error"] == pytest.approx(1.0, 
            abs=1e - 10)
        assert result_mean["test_type"] == "mean"

        # Test for correlation test
        result_corr = stats_analysis.type_error_rates(
            test_type="correlation", effect_size=0.3, sample_size=100
        )

        assert "type_i_error" in result_corr
        assert "type_ii_error" in result_corr
        assert "power" in result_corr
        assert result_corr["type_i_error"] == 0.05
        assert result_corr["power"] + result_corr["type_ii_error"] == pytest.approx(1.0, 
            abs=1e - 10)
        assert result_corr["test_type"] == "correlation"

        # Larger effect size should decrease Type II error
        result_large_effect = stats_analysis.type_error_rates(
            test_type="proportion", effect_size=0.2, sample_size=400
        )
        assert result_large_effect["type_ii_error"] < result_prop["type_ii_error"]

        # Larger sample size should decrease Type II error
        result_large_sample = stats_analysis.type_error_rates(
            test_type="proportion", effect_size=0.1, sample_size=800
        )
        assert result_large_sample["type_ii_error"] < result_prop["type_ii_error"]

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.type_error_rates(
                test_type="invalid", effect_size=0.1, sample_size=100
            )  # Invalid test type

        with pytest.raises(InvalidParameterError):
            stats_analysis.type_error_rates(
                test_type="mean", effect_size=0.5, sample_size=100
            )  # Missing std_dev

    # -------------------------------------------------------------------------
    # Multiple Comparison Corrections Tests
    # -------------------------------------------------------------------------

    def test_bonferroni_correction(self):
        """Test Bonferroni correction for multiple comparisons."""
        stats_analysis = StatisticalAnalysis()

        # Test with a set of p - values
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        result = stats_analysis.bonferroni_correction(p_values)

        # Check result structure
        assert "original_p_values" in result
        assert "adjusted_p_values" in result
        assert "significant" in result
        assert "alpha" in result
        assert "n_tests" in result
        assert "correction_method" in result

        # Check specific values
        assert result["n_tests"] == 5
        assert result["correction_method"] == "bonferroni"
        assert len(result["adjusted_p_values"]) == 5

        # Check that adjusted p - values are correctly calculated
        expected_adjusted = [0.05, 0.10, 0.15, 0.20, 0.25]  # p * n_tests
        for i in range(5):
            assert result["adjusted_p_values"][i] == pytest.approx(expected_adjusted[i], 
                abs=1e - 10)

        # Check significance after correction
        # With default alpha=0.05, none of the adjusted p - values (0.05, 0.10, 0.15, 0.20, 0.25) are significant
        assert result["significant"] == [False, False, False, False, False]

        # Test with p - values that exceed 1.0 after correction
        p_values = [0.3, 0.4, 0.5]
        result = stats_analysis.bonferroni_correction(p_values)

        # Adjusted p - values should be capped at 1.0
        assert all(p <= 1.0 for p in result["adjusted_p_values"])

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.bonferroni_correction([])  # Empty list

        with pytest.raises(InvalidParameterError):
            stats_analysis.bonferroni_correction([0.1, 1.1, 
                0.3])  # Invalid p - value > 1

        with pytest.raises(InvalidParameterError):
            stats_analysis.bonferroni_correction([0.1, -0.1, 
                0.3])  # Invalid p - value < 0

    def test_holm_bonferroni_correction(self):
        """Test Holm - Bonferroni correction for multiple comparisons."""
        stats_analysis = StatisticalAnalysis()

        # Test with a set of p - values
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        result = stats_analysis.holm_bonferroni_correction(p_values)

        # Check result structure
        assert "original_p_values" in result
        assert "adjusted_p_values" in result
        assert "significant" in result
        assert "alpha" in result
        assert "n_tests" in result
        assert "correction_method" in result

        # Check specific values
        assert result["n_tests"] == 5
        assert result["correction_method"] == "holm - bonferroni"
        assert len(result["adjusted_p_values"]) == 5

        # Check that adjusted p - values are correctly calculated
        # For Holm - Bonferroni, the smallest p - value is multiplied by n, the second by (n - 1), etc.
        # The expected values are calculated as p * (n - rank + 1) with monotonicity enforcement
        expected_adjusted = [0.05, 0.08, 0.09, 0.09, 0.09]
        for i in range(5):
            assert result["adjusted_p_values"][i] == pytest.approx(expected_adjusted[i], 
                abs=1e - 10)

        # Test with p - values in different order
        p_values = [0.05, 0.04, 0.03, 0.02, 0.01]
        result = stats_analysis.holm_bonferroni_correction(p_values)

        # The adjusted p - values should be the same as before, but in different order
        expected_adjusted = [0.05, 0.08, 0.09, 0.09, 
            0.09]  # p * (n - rank + 1) with monotonicity
        for i in range(5):
            assert result["adjusted_p_values"][4 - i] == pytest.approx(
                expected_adjusted[i], abs=1e - 10
            )

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.holm_bonferroni_correction([])  # Empty list

        with pytest.raises(InvalidParameterError):
            stats_analysis.holm_bonferroni_correction([0.1, 1.1, 
                0.3])  # Invalid p - value > 1

    def test_benjamini_hochberg_correction(self):
        """Test Benjamini - Hochberg correction for multiple comparisons."""
        stats_analysis = StatisticalAnalysis()

        # Test with a set of p - values
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        result = stats_analysis.benjamini_hochberg_correction(p_values)

        # Check result structure
        assert "original_p_values" in result
        assert "adjusted_p_values" in result
        assert "significant" in result
        assert "alpha" in result
        assert "n_tests" in result
        assert "correction_method" in result

        # Check specific values
        assert result["n_tests"] == 5
        assert result["correction_method"] == "benjamini - hochberg"
        assert len(result["adjusted_p_values"]) == 5

        # Check that adjusted p - values are correctly calculated
        # For Benjamini - Hochberg, p - value is multiplied by n / rank
        expected_adjusted = [0.05, 0.05, 0.05, 0.05, 0.05]  # p * n / rank
        for i in range(5):
            assert result["adjusted_p_values"][i] == pytest.approx(expected_adjusted[i], 
                abs=1e - 10)

        # Test with p - values that would exceed 1.0 after correction
        p_values = [0.3, 0.4, 0.5]
        result = stats_analysis.benjamini_hochberg_correction(p_values)

        # Adjusted p - values should be capped at 1.0
        assert all(p <= 1.0 for p in result["adjusted_p_values"])

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.benjamini_hochberg_correction([])  # Empty list

        with pytest.raises(InvalidParameterError):
            stats_analysis.benjamini_hochberg_correction([0.1, 1.1, 
                0.3])  # Invalid p - value > 1

    def test_benjamini_yekutieli_correction(self):
        """Test Benjamini - Yekutieli correction for multiple comparisons."""
        stats_analysis = StatisticalAnalysis()

        # Test with a set of p - values
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        result = stats_analysis.benjamini_yekutieli_correction(p_values)

        # Check result structure
        assert "original_p_values" in result
        assert "adjusted_p_values" in result
        assert "significant" in result
        assert "alpha" in result
        assert "n_tests" in result
        assert "correction_factor" in result
        assert "correction_method" in result

        # Check specific values
        assert result["n_tests"] == 5
        assert result["correction_method"] == "benjamini - yekutieli"
        assert len(result["adjusted_p_values"]) == 5

        # Check that correction factor is correctly calculated
        # Correction factor is sum of 1 / i for i from 1 to n
        expected_factor = 1 + 1 / 2 + 1 / 3 + 1 / 4 + 1 / 5
        assert result["correction_factor"] == pytest.approx(expected_factor, 
            abs=1e - 10)

        # Test with p - values that would exceed 1.0 after correction
        p_values = [0.3, 0.4, 0.5]
        result = stats_analysis.benjamini_yekutieli_correction(p_values)

        # Adjusted p - values should be capped at 1.0
        assert all(p <= 1.0 for p in result["adjusted_p_values"])

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.benjamini_yekutieli_correction([])  # Empty list

        with pytest.raises(InvalidParameterError):
            stats_analysis.benjamini_yekutieli_correction([0.1, 1.1, 
                0.3])  # Invalid p - value > 1

    def test_sidak_correction(self):
        """Test Šidák correction for multiple comparisons."""
        stats_analysis = StatisticalAnalysis()

        # Test with a set of p - values
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        result = stats_analysis.sidak_correction(p_values)

        # Check result structure
        assert "original_p_values" in result
        assert "adjusted_p_values" in result
        assert "significant" in result
        assert "alpha" in result
        assert "n_tests" in result
        assert "correction_method" in result

        # Check specific values
        assert result["n_tests"] == 5
        assert result["correction_method"] == "sidak"
        assert len(result["adjusted_p_values"]) == 5

        # Check that adjusted p - values are correctly calculated
        # For Šidák, adjusted p - value is 1 - (1 - p)^n
        for i, p in enumerate(p_values):
            expected = 1.0 - (1.0 - p) ** 5
            assert result["adjusted_p_values"][i] == pytest.approx(expected, 
                abs=1e - 10)

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.sidak_correction([])  # Empty list

        with pytest.raises(InvalidParameterError):
            stats_analysis.sidak_correction([0.1, 1.1, 0.3])  # Invalid p - value > 1

    def test_adjust_alpha(self):
        """Test alpha adjustment for multiple comparisons."""
        stats_analysis = StatisticalAnalysis()

        # Test Bonferroni adjustment
        result = stats_analysis.adjust_alpha(alpha=0.05, n_tests=5, method="bonferroni")

        # Check result structure
        assert "original_alpha" in result
        assert "adjusted_alpha" in result
        assert "n_tests" in result
        assert "adjustment_method" in result

        # Check specific values
        assert result["original_alpha"] == 0.05
        assert result["n_tests"] == 5
        assert result["adjustment_method"] == "bonferroni"
        assert result["adjusted_alpha"] == pytest.approx(0.01, abs=1e - 10)  # 0.05 / 5

        # Test Šidák adjustment
        result = stats_analysis.adjust_alpha(alpha=0.05, n_tests=5, method="sidak")

        # Check specific values
        assert result["adjustment_method"] == "sidak"
        assert result["adjusted_alpha"] == pytest.approx(1.0 - (1.0 - 0.05) ** 5, 
            abs=1e - 10)

        # Test no adjustment
        result = stats_analysis.adjust_alpha(alpha=0.05, n_tests=5, method="none")

        # Check specific values
        assert result["adjustment_method"] == "none"
        assert result["adjusted_alpha"] == 0.05  # No change

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.adjust_alpha(alpha=1.5, n_tests=5)  # Invalid alpha > 1

        with pytest.raises(InvalidParameterError):
            stats_analysis.adjust_alpha(alpha=0.05, n_tests=0)  # Invalid n_tests < 1

        with pytest.raises(InvalidParameterError):
            stats_analysis.adjust_alpha(alpha=0.05, n_tests=5, 
                method="invalid")  # Invalid method

    # -------------------------------------------------------------------------
    # Sequential Analysis Tests
    # -------------------------------------------------------------------------

    def test_obrien_fleming_boundary(self):
        """Test O'Brien - Fleming boundary calculation for sequential testing."""
        stats_analysis = StatisticalAnalysis()

        # Test with default parameters
        result = stats_analysis.obrien_fleming_boundary(num_looks=3)

        # Check result structure
        assert "boundaries" in result
        assert "cumulative_alpha" in result
        assert "z_boundaries" in result
        assert "information_fractions" in result
        assert "num_looks" in result
        assert "alpha" in result
        assert "method" in result

        # Check specific values
        assert result["num_looks"] == 3
        assert result["alpha"] == 0.05
        assert result["method"] == "obrien_fleming"
        assert len(result["boundaries"]) == 3
        assert len(result["cumulative_alpha"]) == 3
        assert len(result["z_boundaries"]) == 3
        assert len(result["information_fractions"]) == 3

        # Check that information fractions are correctly calculated
        expected_fractions = [1 / 3, 2 / 3, 3 / 3]
        for i in range(3):
            assert result["information_fractions"][i] == pytest.approx(
                expected_fractions[i], abs=1e - 10
            )

        # Check that boundaries are decreasing (easier to reject as trial progresses)
        assert result["z_boundaries"][0] > result["z_boundaries"][1] > result["z_boundaries"][2]

        # Test with custom parameters
        result_custom = stats_analysis.obrien_fleming_boundary(num_looks=4, alpha=0.01)

        assert result_custom["num_looks"] == 4
        assert result_custom["alpha"] == 0.01
        assert len(result_custom["boundaries"]) == 4

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.obrien_fleming_boundary(num_looks=0)  # Invalid num_looks

        with pytest.raises(InvalidParameterError):
            stats_analysis.obrien_fleming_boundary(num_looks=3, 
                alpha=0)  # Invalid alpha

    def test_pocock_boundary(self):
        """Test Pocock boundary calculation for sequential testing."""
        stats_analysis = StatisticalAnalysis()

        # Test with default parameters
        result = stats_analysis.pocock_boundary(num_looks=3)

        # Check result structure
        assert "boundaries" in result
        assert "cumulative_alpha" in result
        assert "z_boundaries" in result
        assert "information_fractions" in result
        assert "num_looks" in result
        assert "alpha" in result
        assert "method" in result

        # Check specific values
        assert result["num_looks"] == 3
        assert result["alpha"] == 0.05
        assert result["method"] == "pocock"
        assert len(result["boundaries"]) == 3
        assert len(result["cumulative_alpha"]) == 3
        assert len(result["z_boundaries"]) == 3
        assert len(result["information_fractions"]) == 3

        # Check that information fractions are correctly calculated
        expected_fractions = [1 / 3, 2 / 3, 3 / 3]
        for i in range(3):
            assert result["information_fractions"][i] == pytest.approx(
                expected_fractions[i], abs=1e - 10
            )

        # Check that z - boundaries are constant across all looks
        assert result["z_boundaries"][0] == pytest.approx(result["z_boundaries"][1], 
            abs=1e - 10)
        assert result["z_boundaries"][1] == pytest.approx(result["z_boundaries"][2], 
            abs=1e - 10)

        # Test with custom parameters
        result_custom = stats_analysis.pocock_boundary(num_looks=4, alpha=0.01)

        assert result_custom["num_looks"] == 4
        assert result_custom["alpha"] == 0.01
        assert len(result_custom["boundaries"]) == 4

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.pocock_boundary(num_looks=0)  # Invalid num_looks

        with pytest.raises(InvalidParameterError):
            stats_analysis.pocock_boundary(num_looks=3, alpha=0)  # Invalid alpha

    def test_alpha_spending_function(self):
        """Test alpha spending function for sequential testing."""
        stats_analysis = StatisticalAnalysis()

        # Test with default parameters
        info_fractions = [0.25, 0.5, 0.75, 1.0]
        result = \
            stats_analysis.alpha_spending_function(information_fractions=info_fractions)

        # Check result structure
        assert "alpha_spent" in result
        assert "cumulative_alpha" in result
        assert "information_fractions" in result
        assert "num_looks" in result
        assert "alpha" in result
        assert "method" in result

        # Check specific values
        assert result["num_looks"] == 4
        assert result["alpha"] == 0.05
        assert result["method"] == "obrien_fleming"
        assert len(result["alpha_spent"]) == 4
        assert len(result["cumulative_alpha"]) == 4
        assert len(result["information_fractions"]) == 4

        # Check that information fractions are correctly stored
        for i in range(4):
            assert result["information_fractions"][i] == pytest.approx(info_fractions[i], 
                abs=1e - 10)

        # Check that cumulative alpha is monotonically increasing
        for i in range(1, 4):
            assert result["cumulative_alpha"][i] >= result["cumulative_alpha"][i - 1]

        # Check that final cumulative alpha equals total alpha
        assert result["cumulative_alpha"][-1] == pytest.approx(0.05, abs=1e - 10)

        # Test with different methods
        methods = ["pocock", "hwang_shih_decosta", "linear"]
        for method in methods:
            result = stats_analysis.alpha_spending_function(
                information_fractions=info_fractions, method=method
            )
            assert result["method"] == method
            assert result["cumulative_alpha"][-1] == pytest.approx(0.05, abs=1e - 10)

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.alpha_spending_function(
                information_fractions=[])  # Empty list

        with pytest.raises(InvalidParameterError):
            stats_analysis.alpha_spending_function(
                information_fractions=[0.5, 0.3, 0.7]
            )  # Not ascending

        with pytest.raises(InvalidParameterError):
            stats_analysis.alpha_spending_function(
                information_fractions=[0.5, 1.2]
            )  # Invalid fraction > 1

        with pytest.raises(InvalidParameterError):
            stats_analysis.alpha_spending_function(
                information_fractions=[0.5, 0.7], method="invalid"
            )  # Invalid method

    def test_sequential_test_analysis(self):
        """Test sequential test analysis."""
        stats_analysis = StatisticalAnalysis()

        # Test with default parameters
        z_scores = [1.5, 2.0, 2.5]
        result = stats_analysis.sequential_test_analysis(z_scores=z_scores)

        # Check result structure
        assert "z_scores" in result
        assert "boundaries" in result
        assert "crossed" in result
        assert "adjusted_p_values" in result
        assert "information_fractions" in result
        assert "num_looks" in result
        assert "alpha" in result
        assert "method" in result
        assert "stop_early" in result
        assert "first_significant_look" in result

        # Check specific values
        assert result["num_looks"] == 3
        assert result["alpha"] == 0.05
        assert result["method"] == "obrien_fleming"
        assert len(result["z_scores"]) == 3
        assert len(result["boundaries"]) == 3
        assert len(result["crossed"]) == 3
        assert len(result["adjusted_p_values"]) == 3
        assert len(result["information_fractions"]) == 3

        # Check that information fractions are correctly calculated
        expected_fractions = [1 / 3, 2 / 3, 3 / 3]
        for i in range(3):
            assert result["information_fractions"][i] == pytest.approx(
                expected_fractions[i], abs=1e - 10
            )

        # Test with custom parameters
        info_fractions = [0.25, 0.5, 0.75, 1.0]
        z_scores = [1.0, 1.5, 2.0, 2.5]
        result_custom = stats_analysis.sequential_test_analysis(
            z_scores=z_scores, information_fractions=info_fractions, alpha=0.01, 
                method="pocock"
        )

        assert result_custom["num_looks"] == 4
        assert result_custom["alpha"] == 0.01
        assert result_custom["method"] == "pocock"
        assert len(result_custom["z_scores"]) == 4

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.sequential_test_analysis(z_scores=[])  # Empty list

        with pytest.raises(InvalidParameterError):
            stats_analysis.sequential_test_analysis(
                z_scores=[1.0, 2.0], information_fractions=[0.5]
            )  # Length mismatch

        with pytest.raises(InvalidParameterError):
            stats_analysis.sequential_test_analysis(
                z_scores=[1.0, 2.0], method="invalid"
            )  # Invalid method

    def test_conditional_power(self):
        """Test conditional power calculation for sequential testing."""
        stats_analysis = StatisticalAnalysis()

        # Test with default parameters
        result = stats_analysis.conditional_power(current_z=1.5, 
            information_fraction=0.5)

        # Check result structure
        assert "conditional_power" in result
        assert "current_z" in result
        assert "information_fraction" in result
        assert "target_effect" in result
        assert "observed_effect" in result
        assert "alpha" in result
        assert "z_critical" in result

        # Check specific values
        assert result["current_z"] == 1.5
        assert result["information_fraction"] == 0.5
        assert result["alpha"] == 0.05
        assert 0 <= result["conditional_power"] <= 1

        # Test with custom parameters
        result_custom = stats_analysis.conditional_power(
            current_z=2.0, information_fraction=0.25, target_effect=0.5, alpha=0.01
        )

        assert result_custom["current_z"] == 2.0
        assert result_custom["information_fraction"] == 0.25
        assert result_custom["target_effect"] == 0.5
        assert result_custom["alpha"] == 0.01

        # Test with observed effect
        result_observed = stats_analysis.conditional_power(
            current_z=1.0, information_fraction=0.5, observed_effect=0.3
        )

        assert result_observed["current_z"] == 1.0
        assert result_observed["information_fraction"] == 0.5
        assert result_observed["observed_effect"] == 0.3

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.conditional_power(
                current_z=1.0, information_fraction=1.5
            )  # Invalid fraction > 1

        with pytest.raises(InvalidParameterError):
            stats_analysis.conditional_power(
                current_z=1.0, information_fraction=0.5, alpha=0
            )  # Invalid alpha

    def test_futility_boundary(self):
        """Test futility boundary calculation for sequential testing."""
        stats_analysis = StatisticalAnalysis()

        # Test with default parameters
        info_fractions = [0.25, 0.5, 0.75, 1.0]
        result = stats_analysis.futility_boundary(information_fractions=info_fractions)

        # Check result structure
        assert "futility_boundaries" in result
        assert "information_fractions" in result
        assert "num_looks" in result
        assert "beta" in result
        assert "method" in result

        # Check specific values
        assert result["num_looks"] == 4
        assert result["beta"] == 0.2
        assert result["method"] == "obrien_fleming"
        assert len(result["futility_boundaries"]) == 4
        assert len(result["information_fractions"]) == 4

        # Check that information fractions are correctly stored
        for i in range(4):
            assert result["information_fractions"][i] == pytest.approx(info_fractions[i], 
                abs=1e - 10)

        # Check that final futility boundary is -inf (no stopping for futility at final analysis)
        assert result["futility_boundaries"][-1] == float(" - inf")

        # Test with Pocock method
        result_pocock = stats_analysis.futility_boundary(
            information_fractions=info_fractions, method="pocock"
        )

        assert result_pocock["method"] == "pocock"
        assert result_pocock["futility_boundaries"][-1] == float(" - inf")

        # Test with custom parameters
        result_custom = stats_analysis.futility_boundary(
            information_fractions=info_fractions, beta=0.1
        )

        assert result_custom["beta"] == 0.1

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.futility_boundary(information_fractions=[])  # Empty list

        with pytest.raises(InvalidParameterError):
            stats_analysis.futility_boundary(information_fractions=[0.5, 0.3, 
                0.7])  # Not ascending

        with pytest.raises(InvalidParameterError):
            stats_analysis.futility_boundary(
                information_fractions=[0.5, 1.2]
            )  # Invalid fraction > 1

        with pytest.raises(InvalidParameterError):
            stats_analysis.futility_boundary(
                information_fractions=[0.5, 0.7], method="invalid"
            )  # Invalid method

    def test_optional_stopping_correction(self):
        """Test correction for optional stopping in sequential testing."""
        stats_analysis = StatisticalAnalysis()

        # Test with default parameters
        result = stats_analysis.optional_stopping_correction(p_value=0.04, num_looks=5)

        # Check result structure
        assert "original_p_value" in result
        assert "adjusted_p_value" in result
        assert "num_looks" in result
        assert "method" in result

        # Check specific values
        assert result["original_p_value"] == 0.04
        assert result["num_looks"] == 5
        assert result["method"] == "bonferroni"
        assert result["adjusted_p_value"] == pytest.approx(0.04 * 5, abs=1e - 10)

        # Test with different methods
        result_sidak = stats_analysis.optional_stopping_correction(
            p_value=0.04, num_looks=5, method="sidak"
        )

        assert result_sidak["method"] == "sidak"
        assert result_sidak["adjusted_p_value"] == pytest.approx(1.0 - (1.0 - 0.04) ** 5, 
            abs=1e - 10)

        result_sequential = stats_analysis.optional_stopping_correction(
            p_value=0.04, num_looks=5, method="sequential"
        )

        assert result_sequential["method"] == "sequential"
        assert "z_score" in result_sequential
        assert "adjusted_z_score" in result_sequential

        # Test with p - value that would exceed 1.0 after correction
        result_large_p = stats_analysis.optional_stopping_correction(p_value=0.3, 
            num_looks=5)
        assert result_large_p["adjusted_p_value"] <= 1.0

        # Test with invalid input
        with pytest.raises(InvalidParameterError):
            stats_analysis.optional_stopping_correction(
                p_value=1.5, num_looks=5
            )  # Invalid p - value > 1

        with pytest.raises(InvalidParameterError):
            stats_analysis.optional_stopping_correction(
                p_value=0.04, num_looks=0
            )  # Invalid num_looks

        with pytest.raises(InvalidParameterError):
            stats_analysis.optional_stopping_correction(
                p_value=0.04, num_looks=5, method="invalid"
            )  # Invalid method

    def test_log_likelihood_ratio_test(self):
        """Test log - likelihood ratio test for nested model comparison."""
        stats_analysis = StatisticalAnalysis()

        # Test with simple models
        # Model 1 (simpler model) with 2 parameters
        model1_loglik = -100.0
        df1 = 2

        # Model 2 (more complex model) with 4 parameters
        model2_loglik = -95.0
        df2 = 4

        result = stats_analysis.log_likelihood_ratio_test(model1_loglik, model2_loglik, 
            df1, df2)

        # Check result structure
        assert "test_statistic" in result
        assert "p_value" in result
        assert "df_diff" in result
        assert "df1" in result
        assert "df2" in result
        assert "loglik1" in result
        assert "loglik2" in result
        assert "is_significant" in result
        assert "model_selection" in result
        assert "test_name" in result
        assert "alpha" in result

        # Check specific values
        assert result["test_statistic"] == pytest.approx(10.0, 
            abs=1e - 10)  # 2 * ((-95) - (-100))
        assert result["df_diff"] == 2  # 4 - 2
        assert result["test_name"] == "log_likelihood_ratio"

        # Check model selection criteria
        assert "aic1" in result["model_selection"]
        assert "aic2" in result["model_selection"]
        assert "bic1" in result["model_selection"]
        assert "bic2" in result["model_selection"]
        assert "aic_preferred" in result["model_selection"]
        assert "bic_preferred" in result["model_selection"]

        # Test with non - significant difference
        # Model 1 (simpler model) with 2 parameters
        model1_loglik = -100.0
        df1 = 2

        # Model 2 (more complex model) with 4 parameters but only slightly better fit
        model2_loglik = -99.0
        df2 = 4

        result_nonsig = stats_analysis.log_likelihood_ratio_test(
            model1_loglik, model2_loglik, df1, df2
        )

        # The difference should not be significant
        assert result_nonsig["test_statistic"] == pytest.approx(
            2.0, abs=1e - 10
        )  # 2 * ((-99) - (-100))
        # Check that p - value is greater than alpha for non - significance
        assert result_nonsig["p_value"] > stats_analysis.default_alpha

        # Test with invalid inputs
        with pytest.raises(InvalidParameterError):
            stats_analysis.log_likelihood_ratio_test("not a float", model2_loglik, df1, 
                df2)

        with pytest.raises(InvalidParameterError):
            stats_analysis.log_likelihood_ratio_test(
                model1_loglik, model2_loglik, 0, df2
            )  # df1 must be >= 1

        with pytest.raises(InvalidParameterError):
            stats_analysis.log_likelihood_ratio_test(
                model1_loglik, model2_loglik, df1, df1
            )  # df2 must be > df1

    def test_model_selection_criteria(self):
        """Test model selection criteria calculation."""
        stats_analysis = StatisticalAnalysis()

        # Test with simple model
        loglik = -100.0
        df = 3
        sample_size = 100

        result = stats_analysis.model_selection_criteria(loglik, df, sample_size)

        # Check result structure
        assert "aic" in result
        assert "bic" in result
        assert "aicc" in result
        assert "hqic" in result
        assert "loglik" in result
        assert "df" in result
        assert "sample_size" in result

        # Check specific values
        assert result["aic"] == pytest.approx(206.0, abs=1e - 10)  # -2 * (-100) + 2 * 3
        assert result["bic"] == pytest.approx(213.8155, 
            abs=1e - 4)  # -2 * (-100) + 3 * ln(100)

        # Test AICc calculation
        # AICc = AIC + (2k(k + 1)) / (n - k-1)
        expected_aicc = 206.0 + (2 * 3 * (3 + 1)) / (100 - 3 - 1)
        assert result["aicc"] == pytest.approx(expected_aicc, abs=1e - 10)

        # Test HQIC calculation
        # HQIC = -2 * loglik + 2k * ln(ln(n))
        expected_hqic = -2 * (-100) + 2 * 3 * np.log(np.log(100))
        assert result["hqic"] == pytest.approx(expected_hqic, abs=1e - 10)

        # Test with invalid inputs
        with pytest.raises(InvalidParameterError):
            stats_analysis.model_selection_criteria("not a float", df, sample_size)

        with pytest.raises(InvalidParameterError):
            stats_analysis.model_selection_criteria(loglik, 0, 
                sample_size)  # df must be >= 1

        with pytest.raises(InvalidParameterError):
            stats_analysis.model_selection_criteria(loglik, df, 
                df)  # sample_size must be > df
