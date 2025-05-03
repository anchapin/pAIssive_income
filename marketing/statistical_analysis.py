"""
Statistical Analysis Framework for Marketing.

This module provides statistical analysis tools for marketing data, including:
- Statistical significance testing
- Confidence interval calculations
- Effect size calculations
- Power analysis
- Multiple comparison corrections
- Sequential analysis

These tools are designed to support data-driven decision making in marketing,
particularly for A/B testing, campaign performance analysis, and ROI calculations.
"""

import logging
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
from scipy import stats

# Configure logger
logger = logging.getLogger(__name__)


class StatisticalAnalysisError(Exception):
    """Base exception for statistical analysis errors."""

    pass


class InsufficientDataError(StatisticalAnalysisError):
    """Raised when there is not enough data for statistical analysis."""

    pass


class InvalidParameterError(StatisticalAnalysisError):
    """Raised when an invalid parameter is provided."""

    pass


class StatisticalAnalysis:
    """
    Statistical analysis framework for marketing data.

    This class provides methods for statistical testing, confidence intervals,
    effect size calculations, and other statistical analyses relevant to
    marketing decision making.
    """

    def __init__(self, default_alpha: float = 0.05):
        """
        Initialize the statistical analysis framework.

        Args:
            default_alpha: Default significance level (default: 0.05)
        """
        self.default_alpha = default_alpha
        self.logger = logging.getLogger(__name__)

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    def validate_data(
        self,
        data: Any,
        data_type: type,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        min_length: Optional[int] = None,
        allow_none: bool = False,
    ) -> bool:
        """
        Validate data based on type and constraints.

        Args:
            data: Data to validate
            data_type: Expected data type
            min_value: Minimum allowed value (for numeric types)
            max_value: Maximum allowed value (for numeric types)
            min_length: Minimum length (for sequences)
            allow_none: Whether None is allowed

        Returns:
            True if data is valid

        Raises:
            InvalidParameterError: If data is invalid
        """
        # Check for None
        if data is None:
            if allow_none:
                return True
            raise InvalidParameterError("Data cannot be None")

        # Check type
        if not isinstance(data, data_type):
            if isinstance(data_type, tuple):
                expected_types = ", ".join(t.__name__ for t in data_type)
                raise InvalidParameterError(
                    f"Expected one of: {expected_types}, got {type(data).__name__}"
                )
            else:
                raise InvalidParameterError(
                    f"Expected {data_type.__name__}, got {type(data).__name__}"
                )

        # Check numeric constraints
        if min_value is not None and isinstance(data, (int, float)):
            if data < min_value:
                raise InvalidParameterError(f"Value must be at least {min_value}")

        if max_value is not None and isinstance(data, (int, float)):
            if data > max_value:
                raise InvalidParameterError(f"Value must be at most {max_value}")

        # Check sequence length
        if min_length is not None and hasattr(data, "__len__"):
            if len(data) < min_length:
                raise InvalidParameterError(f"Sequence must have at least {min_length} elements")

        return True

    def check_sufficient_data(self, data: Union[List, np.ndarray], min_samples: int = 30) -> bool:
        """
        Check if there is sufficient data for statistical analysis.

        Args:
            data: Data to check
            min_samples: Minimum number of samples required

        Returns:
            True if there is sufficient data

        Raises:
            InsufficientDataError: If there is not enough data
        """
        if len(data) < min_samples:
            raise InsufficientDataError(
                f"Insufficient data: {len(data)} samples, minimum required: {min_samples}"
            )
        return True

    # -------------------------------------------------------------------------
    # Basic Statistical Methods
    # -------------------------------------------------------------------------

    def mean_and_std(self, data: Union[List[float], np.ndarray]) -> Tuple[float, float]:
        """
        Calculate mean and standard deviation.

        Args:
            data: Numeric data

        Returns:
            Tuple of (mean, standard_deviation)
        """
        self.validate_data(data, (list, np.ndarray), min_length=1)
        return np.mean(data), np.std(data, ddof=1)  # ddof=1 for sample std dev

    def median_and_iqr(self, data: Union[List[float], np.ndarray]) -> Tuple[float, float]:
        """
        Calculate median and interquartile range.

        Args:
            data: Numeric data

        Returns:
            Tuple of (median, iqr)
        """
        self.validate_data(data, (list, np.ndarray), min_length=1)

        # Convert to numpy array for consistent handling
        data_array = np.array(data)

        # Sort the data
        sorted_data = np.sort(data_array)

        # Calculate median
        n = len(sorted_data)
        median = np.median(sorted_data)

        # Calculate quartiles using linear interpolation method
        # This matches the expected test values
        q1 = np.percentile(sorted_data, 25, method="linear")
        q3 = np.percentile(sorted_data, 75, method="linear")
        iqr = q3 - q1

        return median, iqr

    def summary_statistics(self, data: Union[List[float], np.ndarray]) -> Dict[str, float]:
        """
        Calculate summary statistics for a dataset.

        Args:
            data: Numeric data

        Returns:
            Dictionary of summary statistics
        """
        self.validate_data(data, (list, np.ndarray), min_length=1)

        # Convert to numpy array for consistent handling
        data_array = np.array(data)

        # Calculate quartiles using linear interpolation method
        q1 = np.percentile(data_array, 25, method="linear")
        q3 = np.percentile(data_array, 75, method="linear")

        return {
            "count": len(data_array),
            "mean": np.mean(data_array),
            "median": np.median(data_array),
            "std": np.std(data_array, ddof=1),
            "min": np.min(data_array),
            "max": np.max(data_array),
            "q1": q1,
            "q3": q3,
            "iqr": q3 - q1,
            "skewness": stats.skew(data_array),
            "kurtosis": stats.kurtosis(data_array),
        }

    # -------------------------------------------------------------------------
    # Statistical Tests
    # -------------------------------------------------------------------------

    def chi_square_test(
        self,
        observed: Union[List[List[int]], np.ndarray],
        expected: Optional[Union[List[List[float]], np.ndarray]] = None,
    ) -> Dict[str, Any]:
        """
        Perform a chi-square test for independence or goodness of fit.

        For a contingency table (observed counts), this tests for independence
        between rows and columns. For a 1D array compared against expected values,
        this tests for goodness of fit.

        Args:
            observed: Observed frequencies (counts) as a 2D array or list of lists
            expected: Expected frequencies (optional) - if not provided, will be calculated
                     assuming independence between rows and columns

        Returns:
            Dictionary with test results including:
            - chi2: Chi-square statistic
            - p_value: P-value for the test
            - dof: Degrees of freedom
            - expected: Expected frequencies
            - residuals: Standardized residuals
            - is_significant: Whether the result is significant at alpha level

        Raises:
            InvalidParameterError: If inputs are invalid
            InsufficientDataError: If there is not enough data
        """
        # Validate inputs
        if isinstance(observed, list):
            observed = np.array(observed)

        self.validate_data(observed, np.ndarray, min_length=1)

        # Check if we have a 1D or 2D array
        if observed.ndim == 1:
            # For 1D arrays, we need expected values
            if expected is None:
                raise InvalidParameterError(
                    "Expected frequencies must be provided for 1D observed data"
                )

            if isinstance(expected, list):
                expected = np.array(expected)

            self.validate_data(expected, np.ndarray, min_length=1)

            if len(observed) != len(expected):
                raise InvalidParameterError(
                    "Observed and expected arrays must have the same length"
                )

            # Ensure we have sufficient data
            if np.sum(observed) < 20:
                raise InsufficientDataError(
                    "Chi-square test requires at least 20 total observations"
                )

            # Check if any expected value is too small
            if np.any(expected < 5):
                self.logger.warning(
                    "Some expected frequencies are less than 5, chi-square may not be valid"
                )

            # Calculate chi-square statistic
            chi2_stat = np.sum((observed - expected) ** 2 / expected)
            dof = len(observed) - 1

        elif observed.ndim == 2:
            # For contingency tables
            if expected is not None and isinstance(expected, list):
                expected = np.array(expected)

            # Check for sufficient data
            if np.sum(observed) < 20:
                raise InsufficientDataError(
                    "Chi-square test requires at least 20 total observations"
                )

            # Calculate expected frequencies if not provided
            if expected is None:
                row_sums = np.sum(observed, axis=1, keepdims=True)
                col_sums = np.sum(observed, axis=0, keepdims=True)
                total = np.sum(observed)
                expected = row_sums * col_sums / total

            # Check if any expected value is too small
            if np.any(expected < 5):
                self.logger.warning(
                    "Some expected frequencies are less than 5, chi-square may not be valid"
                )

            # Calculate chi-square statistic
            chi2_stat = np.sum((observed - expected) ** 2 / expected)
            dof = (observed.shape[0] - 1) * (observed.shape[1] - 1)

        else:
            raise InvalidParameterError("Observed data must be a 1D or 2D array")

        # Calculate p-value
        p_value = 1 - stats.chi2.cdf(chi2_stat, dof)

        # Calculate standardized residuals
        residuals = (observed - expected) / np.sqrt(expected)

        # Determine significance
        is_significant = p_value < self.default_alpha

        return {
            "chi2": chi2_stat,
            "p_value": p_value,
            "dof": dof,
            "expected": expected.tolist() if isinstance(expected, np.ndarray) else expected,
            "residuals": residuals.tolist() if isinstance(residuals, np.ndarray) else residuals,
            "is_significant": is_significant,
            "test_name": "chi_square",
            "alpha": self.default_alpha,
        }

    def fishers_exact_test(
        self, table: Union[List[List[int]], np.ndarray], alternative: str = "two-sided"
    ) -> Dict[str, Any]:
        """
        Perform Fisher's exact test on a 2x2 contingency table.

        This test is used when sample sizes are small and the chi-square test
        may not be valid. It calculates the exact probability of observing a
        table at least as extreme as the one provided.

        Args:
            table: 2x2 contingency table as a list of lists or numpy array
            alternative: Alternative hypothesis, one of:
                        "two-sided" (default): two-tailed test
                        "less": one-tailed test (probability of a more extreme table with a smaller odds ratio)
                        "greater": one-tailed test (probability of a more extreme table with a larger odds ratio)

        Returns:
            Dictionary with test results including:
            - odds_ratio: The odds ratio
            - p_value: P-value for the test
            - is_significant: Whether the result is significant at alpha level

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        if isinstance(table, list):
            table = np.array(table)

        self.validate_data(table, np.ndarray, min_length=1)

        if table.shape != (2, 2):
            raise InvalidParameterError("Fisher's exact test requires a 2x2 contingency table")

        if alternative not in ["two-sided", "less", "greater"]:
            raise InvalidParameterError(
                "Alternative must be one of: 'two-sided', 'less', 'greater'"
            )

        # Calculate odds ratio and p-value
        odds_ratio, p_value = stats.fisher_exact(table, alternative=alternative)

        # Determine significance
        is_significant = p_value < self.default_alpha

        return {
            "odds_ratio": odds_ratio,
            "p_value": p_value,
            "is_significant": is_significant,
            "test_name": "fishers_exact",
            "alternative": alternative,
            "alpha": self.default_alpha,
            "table": table.tolist() if isinstance(table, np.ndarray) else table,
        }

    def z_test_proportions(
        self,
        count1: int,
        nobs1: int,
        count2: int = None,
        nobs2: int = None,
        value: float = None,
        alternative: str = "two-sided",
    ) -> Dict[str, Any]:
        """
        Perform a z-test for proportions.

        This test can be used to:
        1. Compare a single proportion to a known value (one-sample test)
        2. Compare two proportions (two-sample test)

        Args:
            count1: Number of successes in first sample
            nobs1: Number of observations in first sample
            count2: Number of successes in second sample (for two-sample test)
            nobs2: Number of observations in second sample (for two-sample test)
            value: Known proportion to compare against (for one-sample test)
            alternative: Alternative hypothesis, one of:
                        "two-sided" (default): two-tailed test
                        "less": one-tailed test (proportion is less than value or proportion2)
                        "greater": one-tailed test (proportion is greater than value or proportion2)

        Returns:
            Dictionary with test results including:
            - z_score: Z-statistic
            - p_value: P-value for the test
            - proportion1: First sample proportion
            - proportion2: Second sample proportion or comparison value
            - is_significant: Whether the result is significant at alpha level

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(count1, int, min_value=0)
        self.validate_data(nobs1, int, min_value=count1)

        if alternative not in ["two-sided", "less", "greater"]:
            raise InvalidParameterError(
                "Alternative must be one of: 'two-sided', 'less', 'greater'"
            )

        # Calculate first proportion
        proportion1 = count1 / nobs1

        # Determine test type
        if count2 is not None and nobs2 is not None:
            # Two-sample test
            self.validate_data(count2, int, min_value=0)
            self.validate_data(nobs2, int, min_value=count2)

            proportion2 = count2 / nobs2

            # Check normal approximation conditions
            if (
                nobs1 * proportion1 < 5
                or nobs1 * (1 - proportion1) < 5
                or nobs2 * proportion2 < 5
                or nobs2 * (1 - proportion2) < 5
            ):
                self.logger.warning(
                    "Normal approximation may not be valid due to small expected counts"
                )

            # Calculate pooled proportion
            pooled_prop = (count1 + count2) / (nobs1 + nobs2)

            # Calculate standard error
            se = math.sqrt(pooled_prop * (1 - pooled_prop) * (1 / nobs1 + 1 / nobs2))

            # Calculate z-score
            z_score = (proportion1 - proportion2) / se

            # Calculate p-value
            if alternative == "two-sided":
                p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
            elif alternative == "less":
                p_value = stats.norm.cdf(z_score)
            else:  # alternative == "greater"
                p_value = 1 - stats.norm.cdf(z_score)

            result = {
                "z_score": z_score,
                "p_value": p_value,
                "proportion1": proportion1,
                "proportion2": proportion2,
                "difference": proportion1 - proportion2,
                "pooled_proportion": pooled_prop,
                "standard_error": se,
                "test_type": "two-sample",
            }

        elif value is not None:
            # One-sample test
            self.validate_data(value, float, min_value=0.0, max_value=1.0)

            # Check normal approximation conditions
            if nobs1 * value < 5 or nobs1 * (1 - value) < 5:
                self.logger.warning(
                    "Normal approximation may not be valid due to small expected counts"
                )

            # Calculate standard error
            se = math.sqrt(value * (1 - value) / nobs1)

            # Calculate z-score
            z_score = (proportion1 - value) / se

            # Calculate p-value
            if alternative == "two-sided":
                p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
            elif alternative == "less":
                p_value = stats.norm.cdf(z_score)
            else:  # alternative == "greater"
                p_value = 1 - stats.norm.cdf(z_score)

            result = {
                "z_score": z_score,
                "p_value": p_value,
                "proportion1": proportion1,
                "proportion2": value,
                "difference": proportion1 - value,
                "standard_error": se,
                "test_type": "one-sample",
            }

        else:
            raise InvalidParameterError("Either (count2, nobs2) or value must be provided")

        # Add common fields
        result.update(
            {
                "is_significant": result["p_value"] < self.default_alpha,
                "test_name": "z_test_proportions",
                "alternative": alternative,
                "alpha": self.default_alpha,
                "count1": count1,
                "nobs1": nobs1,
            }
        )

        # Add count2 and nobs2 if provided
        if count2 is not None and nobs2 is not None:
            result.update({"count2": count2, "nobs2": nobs2})

        return result

    # -------------------------------------------------------------------------
    # Confidence Intervals
    # -------------------------------------------------------------------------

    def confidence_interval_mean(
        self, data: Union[List[float], np.ndarray], confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calculate confidence interval for the mean of a dataset.

        Args:
            data: Numeric data
            confidence_level: Confidence level (default: 0.95)

        Returns:
            Dictionary with confidence interval information including:
            - mean: Sample mean
            - lower_bound: Lower bound of the confidence interval
            - upper_bound: Upper bound of the confidence interval
            - confidence_level: Confidence level
            - standard_error: Standard error of the mean
            - margin_of_error: Margin of error
            - degrees_of_freedom: Degrees of freedom

        Raises:
            InvalidParameterError: If inputs are invalid
            InsufficientDataError: If there is not enough data
        """
        # Validate inputs
        self.validate_data(data, (list, np.ndarray), min_length=1)
        self.validate_data(confidence_level, float, min_value=0.0, max_value=1.0)

        # Convert to numpy array for consistent handling
        data_array = np.array(data)

        # Check for sufficient data
        n = len(data_array)
        if n < 2:
            raise InsufficientDataError(
                "At least 2 data points are required for confidence interval calculation"
            )

        # Calculate mean and standard deviation
        mean = np.mean(data_array)
        std_dev = np.std(data_array, ddof=1)  # ddof=1 for sample std dev

        # Calculate standard error of the mean
        standard_error = std_dev / math.sqrt(n)

        # Calculate degrees of freedom
        degrees_of_freedom = n - 1

        # Calculate t-value for the given confidence level
        alpha = 1 - confidence_level
        t_value = stats.t.ppf(1 - alpha / 2, degrees_of_freedom)

        # Calculate margin of error
        margin_of_error = t_value * standard_error

        # Calculate confidence interval
        lower_bound = mean - margin_of_error
        upper_bound = mean + margin_of_error

        return {
            "mean": mean,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "confidence_level": confidence_level,
            "standard_error": standard_error,
            "margin_of_error": margin_of_error,
            "degrees_of_freedom": degrees_of_freedom,
            "sample_size": n,
            "standard_deviation": std_dev,
            "t_value": t_value,
        }

    def confidence_interval_proportion(
        self, count: int, nobs: int, confidence_level: float = 0.95, method: str = "normal"
    ) -> Dict[str, Any]:
        """
        Calculate confidence interval for a proportion.

        Args:
            count: Number of successes
            nobs: Number of observations
            confidence_level: Confidence level (default: 0.95)
            method: Method to use for calculation:
                   "normal": Normal approximation (default)
                   "wilson": Wilson score interval (better for small samples)
                   "agresti-coull": Agresti-Coull interval (adjusted Wald)
                   "exact": Exact (Clopper-Pearson) interval

        Returns:
            Dictionary with confidence interval information including:
            - proportion: Sample proportion
            - lower_bound: Lower bound of the confidence interval
            - upper_bound: Upper bound of the confidence interval
            - confidence_level: Confidence level
            - method: Method used for calculation

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(count, int, min_value=0)
        self.validate_data(nobs, int, min_value=count)
        self.validate_data(confidence_level, float, min_value=0.0, max_value=1.0)

        if method not in ["normal", "wilson", "agresti-coull", "exact"]:
            raise InvalidParameterError(
                "Method must be one of: 'normal', 'wilson', 'agresti-coull', 'exact'"
            )

        # Calculate proportion
        proportion = count / nobs

        # Calculate alpha
        alpha = 1 - confidence_level

        # Calculate z-value for the given confidence level
        z_value = stats.norm.ppf(1 - alpha / 2)

        # Calculate confidence interval based on the specified method
        if method == "normal":
            # Check if normal approximation is valid
            if nobs * proportion < 5 or nobs * (1 - proportion) < 5:
                self.logger.warning(
                    "Normal approximation may not be valid due to small expected counts"
                )

            # Calculate standard error
            standard_error = math.sqrt(proportion * (1 - proportion) / nobs)

            # Calculate margin of error
            margin_of_error = z_value * standard_error

            # Calculate confidence interval
            lower_bound = max(0.0, proportion - margin_of_error)
            upper_bound = min(1.0, proportion + margin_of_error)

            result = {"standard_error": standard_error, "margin_of_error": margin_of_error}

        elif method == "wilson":
            # Wilson score interval (better for small samples)
            denominator = 1 + z_value**2 / nobs
            center = (proportion + z_value**2 / (2 * nobs)) / denominator
            margin = (
                z_value
                * math.sqrt(proportion * (1 - proportion) / nobs + z_value**2 / (4 * nobs**2))
                / denominator
            )

            lower_bound = max(0.0, center - margin)
            upper_bound = min(1.0, center + margin)

            result = {"center": center, "margin": margin}

        elif method == "agresti-coull":
            # Agresti-Coull interval (adjusted Wald)
            n_tilde = nobs + z_value**2
            p_tilde = (count + z_value**2 / 2) / n_tilde

            # Calculate standard error
            standard_error = math.sqrt(p_tilde * (1 - p_tilde) / n_tilde)

            # Calculate margin of error
            margin_of_error = z_value * standard_error

            # Calculate confidence interval
            lower_bound = max(0.0, p_tilde - margin_of_error)
            upper_bound = min(1.0, p_tilde + margin_of_error)

            result = {
                "adjusted_proportion": p_tilde,
                "adjusted_sample_size": n_tilde,
                "standard_error": standard_error,
                "margin_of_error": margin_of_error,
            }

        else:  # method == "exact"
            # Exact (Clopper-Pearson) interval
            lower_bound = stats.beta.ppf(alpha / 2, count, nobs - count + 1) if count > 0 else 0.0
            upper_bound = (
                stats.beta.ppf(1 - alpha / 2, count + 1, nobs - count) if count < nobs else 1.0
            )

            result = {}

        # Add common fields
        result.update(
            {
                "proportion": proportion,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "confidence_level": confidence_level,
                "method": method,
                "count": count,
                "nobs": nobs,
                "z_value": z_value,
            }
        )

        return result

    def confidence_interval_difference_proportions(
        self,
        count1: int,
        nobs1: int,
        count2: int,
        nobs2: int,
        confidence_level: float = 0.95,
        method: str = "normal",
    ) -> Dict[str, Any]:
        """
        Calculate confidence interval for the difference between two proportions.

        Args:
            count1: Number of successes in first sample
            nobs1: Number of observations in first sample
            count2: Number of successes in second sample
            nobs2: Number of observations in second sample
            confidence_level: Confidence level (default: 0.95)
            method: Method to use for calculation:
                   "normal": Normal approximation (default)
                   "agresti-caffo": Agresti-Caffo interval (better for small samples)

        Returns:
            Dictionary with confidence interval information including:
            - proportion1: First sample proportion
            - proportion2: Second sample proportion
            - difference: Difference between proportions (proportion1 - proportion2)
            - lower_bound: Lower bound of the confidence interval
            - upper_bound: Upper bound of the confidence interval
            - confidence_level: Confidence level
            - method: Method used for calculation

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(count1, int, min_value=0)
        self.validate_data(nobs1, int, min_value=count1)
        self.validate_data(count2, int, min_value=0)
        self.validate_data(nobs2, int, min_value=count2)
        self.validate_data(confidence_level, float, min_value=0.0, max_value=1.0)

        if method not in ["normal", "agresti-caffo"]:
            raise InvalidParameterError("Method must be one of: 'normal', 'agresti-caffo'")

        # Calculate proportions
        proportion1 = count1 / nobs1
        proportion2 = count2 / nobs2
        difference = proportion1 - proportion2

        # Calculate alpha
        alpha = 1 - confidence_level

        # Calculate z-value for the given confidence level
        z_value = stats.norm.ppf(1 - alpha / 2)

        # Calculate confidence interval based on the specified method
        if method == "normal":
            # Check if normal approximation is valid
            if (
                nobs1 * proportion1 < 5
                or nobs1 * (1 - proportion1) < 5
                or nobs2 * proportion2 < 5
                or nobs2 * (1 - proportion2) < 5
            ):
                self.logger.warning(
                    "Normal approximation may not be valid due to small expected counts"
                )

            # Calculate standard error
            standard_error = math.sqrt(
                proportion1 * (1 - proportion1) / nobs1 + proportion2 * (1 - proportion2) / nobs2
            )

            # Calculate margin of error
            margin_of_error = z_value * standard_error

            # Calculate confidence interval
            lower_bound = difference - margin_of_error
            upper_bound = difference + margin_of_error

            result = {"standard_error": standard_error, "margin_of_error": margin_of_error}

        else:  # method == "agresti-caffo"
            # Agresti-Caffo interval (better for small samples)
            # Add 1 to each cell of the 2x2 table
            adjusted_count1 = count1 + 1
            adjusted_nobs1 = nobs1 + 2
            adjusted_count2 = count2 + 1
            adjusted_nobs2 = nobs2 + 2

            # Calculate adjusted proportions
            adjusted_proportion1 = adjusted_count1 / adjusted_nobs1
            adjusted_proportion2 = adjusted_count2 / adjusted_nobs2
            adjusted_difference = adjusted_proportion1 - adjusted_proportion2

            # Calculate standard error
            standard_error = math.sqrt(
                adjusted_proportion1 * (1 - adjusted_proportion1) / adjusted_nobs1
                + adjusted_proportion2 * (1 - adjusted_proportion2) / adjusted_nobs2
            )

            # Calculate margin of error
            margin_of_error = z_value * standard_error

            # Calculate confidence interval
            lower_bound = adjusted_difference - margin_of_error
            upper_bound = adjusted_difference + margin_of_error

            result = {
                "adjusted_proportion1": adjusted_proportion1,
                "adjusted_proportion2": adjusted_proportion2,
                "adjusted_difference": adjusted_difference,
                "standard_error": standard_error,
                "margin_of_error": margin_of_error,
            }

        # Add common fields
        result.update(
            {
                "proportion1": proportion1,
                "proportion2": proportion2,
                "difference": difference,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "confidence_level": confidence_level,
                "method": method,
                "count1": count1,
                "nobs1": nobs1,
                "count2": count2,
                "nobs2": nobs2,
                "z_value": z_value,
            }
        )

        return result

    # -------------------------------------------------------------------------
    # Effect Size Calculations
    # -------------------------------------------------------------------------

    def cohens_d(
        self,
        group1: Union[List[float], np.ndarray],
        group2: Union[List[float], np.ndarray],
        correction: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculate Cohen's d effect size for the difference between two groups.

        Cohen's d measures the standardized difference between two means,
        expressed in standard deviation units.

        Args:
            group1: First group data
            group2: Second group data
            correction: Whether to apply Hedges' correction for small samples

        Returns:
            Dictionary with effect size information including:
            - effect_size: Cohen's d value
            - interpretation: Qualitative interpretation of the effect size
            - mean1: Mean of first group
            - mean2: Mean of second group
            - std1: Standard deviation of first group
            - std2: Standard deviation of second group
            - pooled_std: Pooled standard deviation
            - n1: Size of first group
            - n2: Size of second group

        Raises:
            InvalidParameterError: If inputs are invalid
            InsufficientDataError: If there is not enough data
        """
        # Validate inputs
        self.validate_data(group1, (list, np.ndarray), min_length=1)
        self.validate_data(group2, (list, np.ndarray), min_length=1)

        # Convert to numpy arrays for consistent handling
        group1_array = np.array(group1)
        group2_array = np.array(group2)

        # Check for sufficient data
        n1 = len(group1_array)
        n2 = len(group2_array)

        if n1 < 2 or n2 < 2:
            raise InsufficientDataError(
                "Each group must have at least 2 data points for effect size calculation"
            )

        # Calculate means and standard deviations
        mean1 = np.mean(group1_array)
        mean2 = np.mean(group2_array)
        std1 = np.std(group1_array, ddof=1)  # ddof=1 for sample std dev
        std2 = np.std(group2_array, ddof=1)

        # Calculate pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

        # Calculate Cohen's d
        d = (mean1 - mean2) / pooled_std

        # Apply Hedges' correction for small samples if requested
        if correction:
            # Hedges' g correction factor
            correction_factor = 1 - (3 / (4 * (n1 + n2 - 2) - 1))
            d = d * correction_factor

        # Interpret effect size
        if abs(d) < 0.2:
            interpretation = "negligible"
        elif abs(d) < 0.5:
            interpretation = "small"
        elif abs(d) < 0.8:
            interpretation = "medium"
        else:
            interpretation = "large"

        return {
            "effect_size": d,
            "interpretation": interpretation,
            "mean1": mean1,
            "mean2": mean2,
            "std1": std1,
            "std2": std2,
            "pooled_std": pooled_std,
            "n1": n1,
            "n2": n2,
            "correction_applied": correction,
        }

    def odds_ratio(
        self, table: Union[List[List[int]], np.ndarray], ci_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calculate odds ratio for a 2x2 contingency table.

        The odds ratio is a measure of association between exposure and outcome.

        Args:
            table: 2x2 contingency table as [[a, b], [c, d]] where:
                  a = exposed cases, b = exposed non-cases
                  c = unexposed cases, d = unexposed non-cases
            ci_level: Confidence level for confidence interval

        Returns:
            Dictionary with effect size information including:
            - odds_ratio: Odds ratio value
            - log_odds_ratio: Natural logarithm of the odds ratio
            - se_log_odds_ratio: Standard error of the log odds ratio
            - ci_lower: Lower bound of the confidence interval
            - ci_upper: Upper bound of the confidence interval
            - interpretation: Qualitative interpretation of the odds ratio

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        if isinstance(table, list):
            table = np.array(table)

        self.validate_data(table, np.ndarray, min_length=1)
        self.validate_data(ci_level, float, min_value=0.0, max_value=1.0)

        if table.shape != (2, 2):
            raise InvalidParameterError("Odds ratio calculation requires a 2x2 contingency table")

        # Extract values from the table
        a, b = table[0]
        c, d = table[1]

        # Check for zero cells
        if b == 0 or c == 0:
            # Apply Haldane correction (add 0.5 to all cells)
            self.logger.warning(
                "Zero cell detected, applying Haldane correction (adding 0.5 to all cells)"
            )
            a += 0.5
            b += 0.5
            c += 0.5
            d += 0.5

        # Calculate odds ratio
        or_value = (a * d) / (b * c)

        # Calculate log odds ratio and its standard error
        log_or = np.log(or_value)
        se_log_or = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)

        # Calculate confidence interval
        z_value = stats.norm.ppf(1 - (1 - ci_level) / 2)
        ci_lower = np.exp(log_or - z_value * se_log_or)
        ci_upper = np.exp(log_or + z_value * se_log_or)

        # Interpret odds ratio
        if or_value < 1:
            interpretation = "negative association"
        elif or_value > 1:
            interpretation = "positive association"
        else:
            interpretation = "no association"

        # Add strength of association
        if abs(np.log(or_value)) < np.log(1.5):
            interpretation += " (weak)"
        elif abs(np.log(or_value)) < np.log(3.5):
            interpretation += " (moderate)"
        else:
            interpretation += " (strong)"

        return {
            "odds_ratio": or_value,
            "log_odds_ratio": log_or,
            "se_log_odds_ratio": se_log_or,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "ci_level": ci_level,
            "interpretation": interpretation,
            "table": table.tolist() if isinstance(table, np.ndarray) else table,
        }

    def relative_risk(
        self, table: Union[List[List[int]], np.ndarray], ci_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calculate relative risk (risk ratio) for a 2x2 contingency table.

        The relative risk is the ratio of the probability of an outcome in an
        exposed group to the probability of an outcome in an unexposed group.

        Args:
            table: 2x2 contingency table as [[a, b], [c, d]] where:
                  a = exposed cases, b = exposed non-cases
                  c = unexposed cases, d = unexposed non-cases
            ci_level: Confidence level for confidence interval

        Returns:
            Dictionary with effect size information including:
            - relative_risk: Relative risk value
            - log_relative_risk: Natural logarithm of the relative risk
            - se_log_relative_risk: Standard error of the log relative risk
            - ci_lower: Lower bound of the confidence interval
            - ci_upper: Upper bound of the confidence interval
            - interpretation: Qualitative interpretation of the relative risk

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        if isinstance(table, list):
            table = np.array(table)

        self.validate_data(table, np.ndarray, min_length=1)
        self.validate_data(ci_level, float, min_value=0.0, max_value=1.0)

        if table.shape != (2, 2):
            raise InvalidParameterError(
                "Relative risk calculation requires a 2x2 contingency table"
            )

        # Extract values from the table
        a, b = table[0]
        c, d = table[1]

        # Calculate risk in exposed and unexposed groups
        if a + b == 0:
            raise InvalidParameterError("No exposed subjects in the table")
        if c + d == 0:
            raise InvalidParameterError("No unexposed subjects in the table")

        risk_exposed = a / (a + b)
        risk_unexposed = c / (c + d)

        # Check for zero risk
        if risk_unexposed == 0:
            # Apply correction
            self.logger.warning("Zero risk in unexposed group, applying correction")
            c += 0.5
            d += 0.5
            risk_unexposed = c / (c + d)

        # Calculate relative risk
        rr_value = risk_exposed / risk_unexposed

        # Calculate log relative risk and its standard error
        log_rr = np.log(rr_value)
        se_log_rr = np.sqrt((b / (a * (a + b))) + (d / (c * (c + d))))

        # Calculate confidence interval
        z_value = stats.norm.ppf(1 - (1 - ci_level) / 2)
        ci_lower = np.exp(log_rr - z_value * se_log_rr)
        ci_upper = np.exp(log_rr + z_value * se_log_rr)

        # Interpret relative risk
        if rr_value < 1:
            interpretation = "protective effect"
        elif rr_value > 1:
            interpretation = "increased risk"
        else:
            interpretation = "no effect"

        # Add strength of effect
        if abs(np.log(rr_value)) < np.log(1.5):
            interpretation += " (weak)"
        elif abs(np.log(rr_value)) < np.log(3):
            interpretation += " (moderate)"
        else:
            interpretation += " (strong)"

        return {
            "relative_risk": rr_value,
            "log_relative_risk": log_rr,
            "se_log_relative_risk": se_log_rr,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "ci_level": ci_level,
            "risk_exposed": risk_exposed,
            "risk_unexposed": risk_unexposed,
            "interpretation": interpretation,
            "table": table.tolist() if isinstance(table, np.ndarray) else table,
        }

    def number_needed_to_treat(
        self, table: Union[List[List[int]], np.ndarray], ci_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calculate Number Needed to Treat (NNT) for a 2x2 contingency table.

        NNT is the average number of patients who need to be treated to
        prevent one additional bad outcome.

        Args:
            table: 2x2 contingency table as [[a, b], [c, d]] where:
                  a = treatment cases, b = treatment non-cases
                  c = control cases, d = control non-cases
            ci_level: Confidence level for confidence interval

        Returns:
            Dictionary with effect size information including:
            - nnt: Number Needed to Treat
            - arr: Absolute Risk Reduction
            - ci_lower: Lower bound of the confidence interval
            - ci_upper: Upper bound of the confidence interval
            - interpretation: Qualitative interpretation of the NNT

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        if isinstance(table, list):
            table = np.array(table)

        self.validate_data(table, np.ndarray, min_length=1)
        self.validate_data(ci_level, float, min_value=0.0, max_value=1.0)

        if table.shape != (2, 2):
            raise InvalidParameterError("NNT calculation requires a 2x2 contingency table")

        # Extract values from the table
        a, b = table[0]  # treatment group
        c, d = table[1]  # control group

        # Calculate risk in treatment and control groups
        if a + b == 0:
            raise InvalidParameterError("No subjects in the treatment group")
        if c + d == 0:
            raise InvalidParameterError("No subjects in the control group")

        risk_treatment = a / (a + b)
        risk_control = c / (c + d)

        # Calculate Absolute Risk Reduction (ARR)
        arr = risk_control - risk_treatment

        # Calculate NNT
        if arr == 0:
            nnt = float("inf")
            ci_lower = float("inf")
            ci_upper = float("inf")
            interpretation = "no effect (infinite NNT)"
        else:
            nnt = 1 / abs(arr)

            # Calculate confidence interval for ARR
            se_arr = np.sqrt(
                (risk_treatment * (1 - risk_treatment) / (a + b))
                + (risk_control * (1 - risk_control) / (c + d))
            )

            z_value = stats.norm.ppf(1 - (1 - ci_level) / 2)
            arr_ci_lower = arr - z_value * se_arr
            arr_ci_upper = arr + z_value * se_arr

            # Convert ARR CI to NNT CI (note: CI bounds are inverted for negative ARR)
            if arr > 0:
                ci_lower = 1 / arr_ci_upper if arr_ci_upper > 0 else float("inf")
                ci_upper = 1 / arr_ci_lower if arr_ci_lower > 0 else float("inf")
            else:
                ci_lower = 1 / arr_ci_lower if arr_ci_lower < 0 else float("-inf")
                ci_upper = 1 / arr_ci_upper if arr_ci_upper < 0 else float("-inf")

            # Interpret NNT
            if arr > 0:
                interpretation = f"beneficial (need to treat {int(nnt) if nnt < float('inf') else 'infinite'} patients to prevent one bad outcome)"
            else:
                interpretation = f"harmful (treating {int(nnt) if nnt < float('inf') else 'infinite'} patients leads to one additional bad outcome)"

        return {
            "nnt": nnt,
            "arr": arr,
            "risk_treatment": risk_treatment,
            "risk_control": risk_control,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "ci_level": ci_level,
            "interpretation": interpretation,
            "table": table.tolist() if isinstance(table, np.ndarray) else table,
        }

    # -------------------------------------------------------------------------
    # Power Analysis
    # -------------------------------------------------------------------------

    def sample_size_for_proportion_test(
        self,
        effect_size: float,
        alpha: float = 0.05,
        power: float = 0.8,
        alternative: str = "two-sided",
        p_null: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Calculate the required sample size for a proportion test.

        This method calculates the sample size needed to detect a specified effect size
        with the desired statistical power for a proportion test.

        Args:
            effect_size: Minimum detectable effect size (difference in proportions)
            alpha: Significance level (Type I error rate, default: 0.05)
            power: Statistical power (1 - Type II error rate, default: 0.8)
            alternative: Alternative hypothesis, one of:
                        "two-sided" (default): two-tailed test
                        "one-sided": one-tailed test
            p_null: Null hypothesis proportion (default: 0.5)

        Returns:
            Dictionary with sample size calculation results including:
            - sample_size: Required sample size
            - effect_size: Specified effect size
            - alpha: Significance level
            - power: Statistical power
            - alternative: Alternative hypothesis
            - p_null: Null hypothesis proportion
            - p_alt: Alternative hypothesis proportion
            - test_type: Type of test ("proportion")

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(effect_size, float, min_value=0.0, max_value=1.0)
        self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
        self.validate_data(power, float, min_value=0.0, max_value=1.0)
        self.validate_data(p_null, float, min_value=0.0, max_value=1.0)

        if alternative not in ["two-sided", "one-sided"]:
            raise InvalidParameterError("Alternative must be one of: 'two-sided', 'one-sided'")

        # Calculate alternative proportion
        p_alt = p_null + effect_size

        # Ensure p_alt is within valid range
        if p_alt < 0 or p_alt > 1:
            raise InvalidParameterError(
                f"Alternative proportion (p_null + effect_size = {p_alt}) must be between 0 and 1"
            )

        # Calculate z-values for alpha and power
        z_alpha = (
            stats.norm.ppf(1 - alpha / 2)
            if alternative == "two-sided"
            else stats.norm.ppf(1 - alpha)
        )
        z_beta = stats.norm.ppf(power)

        # Calculate pooled proportion
        p_pooled = (p_null + p_alt) / 2

        # Calculate sample size
        numerator = (
            z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled))
            + z_beta * math.sqrt(p_null * (1 - p_null) + p_alt * (1 - p_alt))
        ) ** 2
        denominator = (p_null - p_alt) ** 2

        # Calculate sample size and round up
        sample_size = math.ceil(numerator / denominator)

        return {
            "sample_size": sample_size,
            "effect_size": effect_size,
            "alpha": alpha,
            "power": power,
            "alternative": alternative,
            "p_null": p_null,
            "p_alt": p_alt,
            "test_type": "proportion",
        }

    def sample_size_for_mean_test(
        self,
        effect_size: float,
        std_dev: float,
        alpha: float = 0.05,
        power: float = 0.8,
        alternative: str = "two-sided",
    ) -> Dict[str, Any]:
        """
        Calculate the required sample size for a mean test.

        This method calculates the sample size needed to detect a specified effect size
        with the desired statistical power for a mean test (t-test).

        Args:
            effect_size: Minimum detectable effect size (difference in means)
            std_dev: Standard deviation of the population
            alpha: Significance level (Type I error rate, default: 0.05)
            power: Statistical power (1 - Type II error rate, default: 0.8)
            alternative: Alternative hypothesis, one of:
                        "two-sided" (default): two-tailed test
                        "one-sided": one-tailed test

        Returns:
            Dictionary with sample size calculation results including:
            - sample_size: Required sample size
            - effect_size: Specified effect size
            - std_dev: Standard deviation
            - alpha: Significance level
            - power: Statistical power
            - alternative: Alternative hypothesis
            - test_type: Type of test ("mean")

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(effect_size, float, min_value=0.0)
        self.validate_data(std_dev, float, min_value=0.0)
        self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
        self.validate_data(power, float, min_value=0.0, max_value=1.0)

        if alternative not in ["two-sided", "one-sided"]:
            raise InvalidParameterError("Alternative must be one of: 'two-sided', 'one-sided'")

        # Calculate standardized effect size (Cohen's d)
        d = effect_size / std_dev

        # Calculate z-values for alpha and power
        z_alpha = (
            stats.norm.ppf(1 - alpha / 2)
            if alternative == "two-sided"
            else stats.norm.ppf(1 - alpha)
        )
        z_beta = stats.norm.ppf(power)

        # Calculate sample size
        sample_size = math.ceil(2 * ((z_alpha + z_beta) / d) ** 2)

        return {
            "sample_size": sample_size,
            "effect_size": effect_size,
            "std_dev": std_dev,
            "standardized_effect_size": d,
            "alpha": alpha,
            "power": power,
            "alternative": alternative,
            "test_type": "mean",
        }

    def sample_size_for_correlation(
        self,
        effect_size: float,
        alpha: float = 0.05,
        power: float = 0.8,
        alternative: str = "two-sided",
    ) -> Dict[str, Any]:
        """
        Calculate the required sample size for a correlation test.

        This method calculates the sample size needed to detect a specified correlation
        coefficient with the desired statistical power.

        Args:
            effect_size: Minimum detectable correlation coefficient (r)
            alpha: Significance level (Type I error rate, default: 0.05)
            power: Statistical power (1 - Type II error rate, default: 0.8)
            alternative: Alternative hypothesis, one of:
                        "two-sided" (default): two-tailed test
                        "one-sided": one-tailed test

        Returns:
            Dictionary with sample size calculation results including:
            - sample_size: Required sample size
            - effect_size: Specified effect size (correlation coefficient)
            - alpha: Significance level
            - power: Statistical power
            - alternative: Alternative hypothesis
            - test_type: Type of test ("correlation")

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(effect_size, float, min_value=-1.0, max_value=1.0)
        self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
        self.validate_data(power, float, min_value=0.0, max_value=1.0)

        if alternative not in ["two-sided", "one-sided"]:
            raise InvalidParameterError("Alternative must be one of: 'two-sided', 'one-sided'")

        # Use absolute value of correlation for calculation
        r = abs(effect_size)

        # Calculate z-values for alpha and power
        z_alpha = (
            stats.norm.ppf(1 - alpha / 2)
            if alternative == "two-sided"
            else stats.norm.ppf(1 - alpha)
        )
        z_beta = stats.norm.ppf(power)

        # Fisher's z transformation of r
        z_r = 0.5 * math.log((1 + r) / (1 - r))

        # Calculate sample size
        sample_size = math.ceil(((z_alpha + z_beta) / z_r) ** 2 + 3)

        return {
            "sample_size": sample_size,
            "effect_size": effect_size,
            "alpha": alpha,
            "power": power,
            "alternative": alternative,
            "test_type": "correlation",
        }

    def minimum_detectable_effect_size(
        self,
        sample_size: int,
        alpha: float = 0.05,
        power: float = 0.8,
        test_type: str = "proportion",
        alternative: str = "two-sided",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Calculate the minimum detectable effect size for a given sample size.

        This method calculates the smallest effect size that can be detected with
        the specified statistical power given a fixed sample size.

        Args:
            sample_size: Available sample size
            alpha: Significance level (Type I error rate, default: 0.05)
            power: Statistical power (1 - Type II error rate, default: 0.8)
            test_type: Type of test, one of:
                      "proportion": Test for proportions
                      "mean": Test for means (t-test)
                      "correlation": Test for correlation
            alternative: Alternative hypothesis, one of:
                        "two-sided" (default): two-tailed test
                        "one-sided": one-tailed test
            **kwargs: Additional parameters specific to the test type:
                     - For "proportion": p_null (default: 0.5)
                     - For "mean": std_dev (required)

        Returns:
            Dictionary with effect size calculation results including:
            - effect_size: Minimum detectable effect size
            - sample_size: Specified sample size
            - alpha: Significance level
            - power: Statistical power
            - test_type: Type of test
            - alternative: Alternative hypothesis
            - Additional test-specific parameters

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(sample_size, int, min_value=2)
        self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
        self.validate_data(power, float, min_value=0.0, max_value=1.0)

        if test_type not in ["proportion", "mean", "correlation"]:
            raise InvalidParameterError(
                "Test type must be one of: 'proportion', 'mean', 'correlation'"
            )

        if alternative not in ["two-sided", "one-sided"]:
            raise InvalidParameterError("Alternative must be one of: 'two-sided', 'one-sided'")

        # Calculate z-values for alpha and power
        z_alpha = (
            stats.norm.ppf(1 - alpha / 2)
            if alternative == "two-sided"
            else stats.norm.ppf(1 - alpha)
        )
        z_beta = stats.norm.ppf(power)

        result = {
            "sample_size": sample_size,
            "alpha": alpha,
            "power": power,
            "test_type": test_type,
            "alternative": alternative,
        }

        if test_type == "proportion":
            # Get null proportion
            p_null = kwargs.get("p_null", 0.5)
            self.validate_data(p_null, float, min_value=0.0, max_value=1.0)

            # Calculate minimum detectable effect size for proportion test
            # This is an approximation using the normal approximation
            effect_size = (z_alpha + z_beta) * math.sqrt(2 * p_null * (1 - p_null) / sample_size)

            result.update({"effect_size": effect_size, "p_null": p_null})

        elif test_type == "mean":
            # Get standard deviation
            if "std_dev" not in kwargs:
                raise InvalidParameterError(
                    "Standard deviation (std_dev) must be provided for mean test"
                )

            std_dev = kwargs["std_dev"]
            self.validate_data(std_dev, float, min_value=0.0)

            # Calculate minimum detectable effect size for mean test
            effect_size = (z_alpha + z_beta) * std_dev * math.sqrt(2 / sample_size)

            result.update({"effect_size": effect_size, "std_dev": std_dev})

        elif test_type == "correlation":
            # Calculate minimum detectable correlation coefficient
            # Using Fisher's z transformation
            z_min = (z_alpha + z_beta) / math.sqrt(sample_size - 3)

            # Convert back from Fisher's z to correlation coefficient
            effect_size = (math.exp(2 * z_min) - 1) / (math.exp(2 * z_min) + 1)

            result["effect_size"] = effect_size

        return result

    def power_analysis(
        self,
        test_type: str,
        effect_size: float,
        sample_size: int,
        alpha: float = 0.05,
        alternative: str = "two-sided",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Calculate statistical power for a given test, effect size, and sample size.

        This method calculates the probability of correctly rejecting the null hypothesis
        (statistical power) for a specified test, effect size, and sample size.

        Args:
            test_type: Type of test, one of:
                      "proportion": Test for proportions
                      "mean": Test for means (t-test)
                      "correlation": Test for correlation
            effect_size: Effect size to detect
            sample_size: Available sample size
            alpha: Significance level (Type I error rate, default: 0.05)
            alternative: Alternative hypothesis, one of:
                        "two-sided" (default): two-tailed test
                        "one-sided": one-tailed test
            **kwargs: Additional parameters specific to the test type:
                     - For "proportion": p_null (default: 0.5)
                     - For "mean": std_dev (required)

        Returns:
            Dictionary with power analysis results including:
            - power: Statistical power (1 - Type II error rate)
            - effect_size: Specified effect size
            - sample_size: Specified sample size
            - alpha: Significance level
            - test_type: Type of test
            - alternative: Alternative hypothesis
            - Additional test-specific parameters

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(effect_size, float)
        self.validate_data(sample_size, int, min_value=2)
        self.validate_data(alpha, float, min_value=0.001, max_value=0.5)

        if test_type not in ["proportion", "mean", "correlation"]:
            raise InvalidParameterError(
                "Test type must be one of: 'proportion', 'mean', 'correlation'"
            )

        if alternative not in ["two-sided", "one-sided"]:
            raise InvalidParameterError("Alternative must be one of: 'two-sided', 'one-sided'")

        # Calculate critical value
        z_alpha = (
            stats.norm.ppf(1 - alpha / 2)
            if alternative == "two-sided"
            else stats.norm.ppf(1 - alpha)
        )

        result = {
            "effect_size": effect_size,
            "sample_size": sample_size,
            "alpha": alpha,
            "test_type": test_type,
            "alternative": alternative,
        }

        if test_type == "proportion":
            # Get null proportion
            p_null = kwargs.get("p_null", 0.5)
            self.validate_data(p_null, float, min_value=0.0, max_value=1.0)

            # Calculate alternative proportion
            p_alt = p_null + effect_size

            # Ensure p_alt is within valid range
            if p_alt < 0 or p_alt > 1:
                raise InvalidParameterError(
                    f"Alternative proportion (p_null + effect_size = {p_alt}) must be between 0 and 1"
                )

            # Calculate standard error under null and alternative
            se_null = math.sqrt(p_null * (1 - p_null) / sample_size)
            se_alt = math.sqrt(p_alt * (1 - p_alt) / sample_size)

            # Calculate non-centrality parameter
            if alternative == "two-sided":
                # For two-sided test, we need to consider both tails
                critical_value = p_null + z_alpha * se_null
                z_power = (p_alt - critical_value) / se_alt
                power = stats.norm.cdf(z_power)

                # For the other tail
                critical_value_lower = p_null - z_alpha * se_null
                z_power_lower = (critical_value_lower - p_alt) / se_alt
                power_lower = stats.norm.cdf(z_power_lower)

                # Total power is the sum of powers in both tails
                power = power + power_lower
            else:
                # For one-sided test
                if effect_size > 0:  # Greater alternative
                    critical_value = p_null + z_alpha * se_null
                    z_power = (p_alt - critical_value) / se_alt
                    power = stats.norm.cdf(z_power)
                else:  # Less alternative
                    critical_value = p_null - z_alpha * se_null
                    z_power = (critical_value - p_alt) / se_alt
                    power = stats.norm.cdf(z_power)

            result.update({"power": power, "p_null": p_null, "p_alt": p_alt})

        elif test_type == "mean":
            # Get standard deviation
            if "std_dev" not in kwargs:
                raise InvalidParameterError(
                    "Standard deviation (std_dev) must be provided for mean test"
                )

            std_dev = kwargs["std_dev"]
            self.validate_data(std_dev, float, min_value=0.0)

            # Calculate standardized effect size (Cohen's d)
            d = effect_size / std_dev

            # Calculate non-centrality parameter
            ncp = d * math.sqrt(sample_size / 2)

            # Calculate power
            if alternative == "two-sided":
                power = stats.norm.cdf(ncp - z_alpha) + stats.norm.cdf(-ncp - z_alpha)
            else:
                if effect_size > 0:  # Greater alternative
                    power = stats.norm.cdf(ncp - z_alpha)
                else:  # Less alternative
                    power = stats.norm.cdf(-ncp - z_alpha)

            result.update({"power": power, "std_dev": std_dev, "standardized_effect_size": d})

        elif test_type == "correlation":
            # Use absolute value of correlation for calculation
            r = abs(effect_size)

            # Fisher's z transformation of r
            z_r = 0.5 * math.log((1 + r) / (1 - r))

            # Calculate standard error
            se = 1 / math.sqrt(sample_size - 3)

            # Calculate non-centrality parameter
            ncp = z_r / se

            # Calculate power
            if alternative == "two-sided":
                power = stats.norm.cdf(ncp - z_alpha) + stats.norm.cdf(-ncp - z_alpha)
            else:
                power = stats.norm.cdf(ncp - z_alpha)

            result["power"] = power

        return result

    def type_error_rates(
        self,
        test_type: str,
        effect_size: float,
        sample_size: int,
        alpha: float = 0.05,
        alternative: str = "two-sided",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Calculate Type I and Type II error rates for a statistical test.

        This method calculates the probability of Type I error (false positive) and
        Type II error (false negative) for a specified test, effect size, and sample size.

        Args:
            test_type: Type of test, one of:
                      "proportion": Test for proportions
                      "mean": Test for means (t-test)
                      "correlation": Test for correlation
            effect_size: Effect size to detect
            sample_size: Available sample size
            alpha: Significance level (Type I error rate, default: 0.05)
            alternative: Alternative hypothesis, one of:
                        "two-sided" (default): two-tailed test
                        "one-sided": one-tailed test
            **kwargs: Additional parameters specific to the test type:
                     - For "proportion": p_null (default: 0.5)
                     - For "mean": std_dev (required)

        Returns:
            Dictionary with error rate analysis results including:
            - type_i_error: Type I error rate (alpha)
            - type_ii_error: Type II error rate (beta)
            - power: Statistical power (1 - beta)
            - effect_size: Specified effect size
            - sample_size: Specified sample size
            - test_type: Type of test
            - alternative: Alternative hypothesis
            - Additional test-specific parameters

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Calculate power
        power_result = self.power_analysis(
            test_type=test_type,
            effect_size=effect_size,
            sample_size=sample_size,
            alpha=alpha,
            alternative=alternative,
            **kwargs,
        )

        # Calculate Type II error rate (beta)
        type_ii_error = 1 - power_result["power"]

        # Create result dictionary
        result = {
            "type_i_error": alpha,
            "type_ii_error": type_ii_error,
            "power": power_result["power"],
            "effect_size": effect_size,
            "sample_size": sample_size,
            "test_type": test_type,
            "alternative": alternative,
        }

        # Add test-specific parameters
        if test_type == "proportion":
            result["p_null"] = power_result.get("p_null", 0.5)
            result["p_alt"] = power_result.get("p_alt")
        elif test_type == "mean":
            result["std_dev"] = power_result.get("std_dev")
            result["standardized_effect_size"] = power_result.get("standardized_effect_size")

        return result

    # -------------------------------------------------------------------------
    # Multiple Comparison Corrections
    # -------------------------------------------------------------------------

    def bonferroni_correction(self, p_values: Union[List[float], np.ndarray]) -> Dict[str, Any]:
        """
        Apply Bonferroni correction to a set of p-values.

        The Bonferroni correction is a simple but conservative method to control
        the family-wise error rate (FWER) when performing multiple hypothesis tests.
        It multiplies each p-value by the number of tests to maintain the overall
        significance level.

        Args:
            p_values: List or array of p-values from multiple hypothesis tests

        Returns:
            Dictionary with correction results including:
            - original_p_values: Original p-values
            - adjusted_p_values: Bonferroni-adjusted p-values
            - significant: Boolean array indicating which tests are significant after correction
            - alpha: Significance level
            - n_tests: Number of tests
            - correction_method: Name of the correction method

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(p_values, (list, np.ndarray), min_length=1)

        # Convert to numpy array for consistent handling
        p_values_array = np.array(p_values)

        # Check if p-values are valid
        if np.any((p_values_array < 0) | (p_values_array > 1)):
            raise InvalidParameterError("P-values must be between 0 and 1")

        # Get number of tests
        n_tests = len(p_values_array)

        # Apply Bonferroni correction
        adjusted_p_values = np.minimum(p_values_array * n_tests, 1.0)

        # Determine which tests are significant after correction
        significant = adjusted_p_values < self.default_alpha

        return {
            "original_p_values": p_values_array.tolist(),
            "adjusted_p_values": adjusted_p_values.tolist(),
            "significant": significant.tolist(),
            "alpha": self.default_alpha,
            "n_tests": n_tests,
            "correction_method": "bonferroni",
        }

    def holm_bonferroni_correction(
        self, p_values: Union[List[float], np.ndarray]
    ) -> Dict[str, Any]:
        """
        Apply Holm-Bonferroni correction to a set of p-values.

        The Holm-Bonferroni method is a step-down procedure that is more powerful
        than the standard Bonferroni correction while still controlling the
        family-wise error rate (FWER).

        Args:
            p_values: List or array of p-values from multiple hypothesis tests

        Returns:
            Dictionary with correction results including:
            - original_p_values: Original p-values
            - adjusted_p_values: Holm-Bonferroni-adjusted p-values
            - significant: Boolean array indicating which tests are significant after correction
            - alpha: Significance level
            - n_tests: Number of tests
            - correction_method: Name of the correction method

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(p_values, (list, np.ndarray), min_length=1)

        # Convert to numpy array for consistent handling
        p_values_array = np.array(p_values)

        # Check if p-values are valid
        if np.any((p_values_array < 0) | (p_values_array > 1)):
            raise InvalidParameterError("P-values must be between 0 and 1")

        # Get number of tests
        n_tests = len(p_values_array)

        # Get the indices that would sort p-values in ascending order
        sorted_indices = np.argsort(p_values_array)

        # Initialize adjusted p-values array
        adjusted_p_values = np.ones_like(p_values_array)

        # Apply Holm-Bonferroni correction
        for i, idx in enumerate(sorted_indices):
            # Adjust p-value: p * (n - rank + 1)
            adjusted_p_values[idx] = min(p_values_array[idx] * (n_tests - i), 1.0)

        # Ensure adjusted p-values are monotonically increasing
        for i in range(1, n_tests):
            idx_prev = sorted_indices[i - 1]
            idx_curr = sorted_indices[i]
            adjusted_p_values[idx_curr] = max(
                adjusted_p_values[idx_curr], adjusted_p_values[idx_prev]
            )

        # Determine which tests are significant after correction
        significant = adjusted_p_values < self.default_alpha

        return {
            "original_p_values": p_values_array.tolist(),
            "adjusted_p_values": adjusted_p_values.tolist(),
            "significant": significant.tolist(),
            "alpha": self.default_alpha,
            "n_tests": n_tests,
            "correction_method": "holm-bonferroni",
        }

    def benjamini_hochberg_correction(
        self, p_values: Union[List[float], np.ndarray]
    ) -> Dict[str, Any]:
        """
        Apply Benjamini-Hochberg correction to a set of p-values.

        The Benjamini-Hochberg procedure controls the false discovery rate (FDR),
        which is the expected proportion of false positives among all rejected hypotheses.
        This method is less conservative than FWER-controlling methods like Bonferroni.

        Args:
            p_values: List or array of p-values from multiple hypothesis tests

        Returns:
            Dictionary with correction results including:
            - original_p_values: Original p-values
            - adjusted_p_values: Benjamini-Hochberg-adjusted p-values
            - significant: Boolean array indicating which tests are significant after correction
            - alpha: Significance level
            - n_tests: Number of tests
            - correction_method: Name of the correction method

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(p_values, (list, np.ndarray), min_length=1)

        # Convert to numpy array for consistent handling
        p_values_array = np.array(p_values)

        # Check if p-values are valid
        if np.any((p_values_array < 0) | (p_values_array > 1)):
            raise InvalidParameterError("P-values must be between 0 and 1")

        # Get number of tests
        n_tests = len(p_values_array)

        # Get the indices that would sort p-values in ascending order
        sorted_indices = np.argsort(p_values_array)

        # Initialize adjusted p-values array
        adjusted_p_values = np.ones_like(p_values_array)

        # Apply Benjamini-Hochberg correction
        for i, idx in enumerate(sorted_indices):
            # Adjust p-value: p * n / rank
            rank = i + 1
            adjusted_p_values[idx] = p_values_array[idx] * n_tests / rank

        # Ensure adjusted p-values are monotonically decreasing
        for i in range(n_tests - 2, -1, -1):
            idx_next = sorted_indices[i + 1]
            idx_curr = sorted_indices[i]
            adjusted_p_values[idx_curr] = min(
                adjusted_p_values[idx_curr], adjusted_p_values[idx_next]
            )

        # Cap adjusted p-values at 1.0
        adjusted_p_values = np.minimum(adjusted_p_values, 1.0)

        # Determine which tests are significant after correction
        significant = adjusted_p_values < self.default_alpha

        return {
            "original_p_values": p_values_array.tolist(),
            "adjusted_p_values": adjusted_p_values.tolist(),
            "significant": significant.tolist(),
            "alpha": self.default_alpha,
            "n_tests": n_tests,
            "correction_method": "benjamini-hochberg",
        }

    def benjamini_yekutieli_correction(
        self, p_values: Union[List[float], np.ndarray]
    ) -> Dict[str, Any]:
        """
        Apply Benjamini-Yekutieli correction to a set of p-values.

        The Benjamini-Yekutieli procedure is a more conservative version of the
        Benjamini-Hochberg procedure that controls the false discovery rate (FDR)
        under arbitrary dependence assumptions.

        Args:
            p_values: List or array of p-values from multiple hypothesis tests

        Returns:
            Dictionary with correction results including:
            - original_p_values: Original p-values
            - adjusted_p_values: Benjamini-Yekutieli-adjusted p-values
            - significant: Boolean array indicating which tests are significant after correction
            - alpha: Significance level
            - n_tests: Number of tests
            - correction_method: Name of the correction method

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(p_values, (list, np.ndarray), min_length=1)

        # Convert to numpy array for consistent handling
        p_values_array = np.array(p_values)

        # Check if p-values are valid
        if np.any((p_values_array < 0) | (p_values_array > 1)):
            raise InvalidParameterError("P-values must be between 0 and 1")

        # Get number of tests
        n_tests = len(p_values_array)

        # Calculate the correction factor (sum of 1/i)
        correction_factor = np.sum(1.0 / np.arange(1, n_tests + 1))

        # Get the indices that would sort p-values in ascending order
        sorted_indices = np.argsort(p_values_array)

        # Initialize adjusted p-values array
        adjusted_p_values = np.ones_like(p_values_array)

        # Apply Benjamini-Yekutieli correction
        for i, idx in enumerate(sorted_indices):
            # Adjust p-value: p * n * c / rank
            rank = i + 1
            adjusted_p_values[idx] = p_values_array[idx] * n_tests * correction_factor / rank

        # Ensure adjusted p-values are monotonically decreasing
        for i in range(n_tests - 2, -1, -1):
            idx_next = sorted_indices[i + 1]
            idx_curr = sorted_indices[i]
            adjusted_p_values[idx_curr] = min(
                adjusted_p_values[idx_curr], adjusted_p_values[idx_next]
            )

        # Cap adjusted p-values at 1.0
        adjusted_p_values = np.minimum(adjusted_p_values, 1.0)

        # Determine which tests are significant after correction
        significant = adjusted_p_values < self.default_alpha

        return {
            "original_p_values": p_values_array.tolist(),
            "adjusted_p_values": adjusted_p_values.tolist(),
            "significant": significant.tolist(),
            "alpha": self.default_alpha,
            "n_tests": n_tests,
            "correction_factor": correction_factor,
            "correction_method": "benjamini-yekutieli",
        }

    def sidak_correction(self, p_values: Union[List[float], np.ndarray]) -> Dict[str, Any]:
        """
        Apply Šidák correction to a set of p-values.

        The Šidák correction is a method to control the family-wise error rate (FWER)
        that is slightly less conservative than the Bonferroni correction.

        Args:
            p_values: List or array of p-values from multiple hypothesis tests

        Returns:
            Dictionary with correction results including:
            - original_p_values: Original p-values
            - adjusted_p_values: Šidák-adjusted p-values
            - significant: Boolean array indicating which tests are significant after correction
            - alpha: Significance level
            - n_tests: Number of tests
            - correction_method: Name of the correction method

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(p_values, (list, np.ndarray), min_length=1)

        # Convert to numpy array for consistent handling
        p_values_array = np.array(p_values)

        # Check if p-values are valid
        if np.any((p_values_array < 0) | (p_values_array > 1)):
            raise InvalidParameterError("P-values must be between 0 and 1")

        # Get number of tests
        n_tests = len(p_values_array)

        # Apply Šidák correction
        adjusted_p_values = 1.0 - (1.0 - p_values_array) ** n_tests

        # Determine which tests are significant after correction
        significant = adjusted_p_values < self.default_alpha

        return {
            "original_p_values": p_values_array.tolist(),
            "adjusted_p_values": adjusted_p_values.tolist(),
            "significant": significant.tolist(),
            "alpha": self.default_alpha,
            "n_tests": n_tests,
            "correction_method": "sidak",
        }

    def adjust_alpha(
        self, alpha: float, n_tests: int, method: str = "bonferroni"
    ) -> Dict[str, Any]:
        """
        Adjust the significance level (alpha) for multiple comparisons.

        This method calculates an adjusted significance level to maintain
        the overall error rate when performing multiple hypothesis tests.

        Args:
            alpha: Original significance level
            n_tests: Number of tests being performed
            method: Method to use for adjustment, one of:
                   "bonferroni": Bonferroni correction (default)
                   "sidak": Šidák correction
                   "none": No correction

        Returns:
            Dictionary with adjustment results including:
            - original_alpha: Original significance level
            - adjusted_alpha: Adjusted significance level
            - n_tests: Number of tests
            - adjustment_method: Method used for adjustment

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(alpha, float, min_value=0.0, max_value=1.0)
        self.validate_data(n_tests, int, min_value=1)

        if method not in ["bonferroni", "sidak", "none"]:
            raise InvalidParameterError("Method must be one of: 'bonferroni', 'sidak', 'none'")

        # Initialize result dictionary
        result = {"original_alpha": alpha, "n_tests": n_tests, "adjustment_method": method}

        # Apply the selected adjustment method
        if method == "bonferroni":
            # Bonferroni correction: alpha / n
            adjusted_alpha = alpha / n_tests
            result["adjusted_alpha"] = adjusted_alpha

        elif method == "sidak":
            # Šidák correction: 1 - (1 - alpha)^(1/n)
            adjusted_alpha = 1.0 - (1.0 - alpha) ** (1.0 / n_tests)
            result["adjusted_alpha"] = adjusted_alpha

        else:  # method == "none"
            # No correction
            result["adjusted_alpha"] = alpha

        return result

    # -------------------------------------------------------------------------
    # Sequential Analysis
    # -------------------------------------------------------------------------

    def obrien_fleming_boundary(self, num_looks: int, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Calculate O'Brien-Fleming stopping boundaries for group sequential testing.

        The O'Brien-Fleming approach uses more conservative boundaries early in the trial
        and less conservative boundaries later, making it harder to stop early.

        Args:
            num_looks: Number of interim analyses (including final analysis)
            alpha: Overall significance level (default: 0.05)

        Returns:
            Dictionary with boundary calculation results including:
            - boundaries: List of alpha spending at each look
            - cumulative_alpha: Cumulative alpha spent at each look
            - z_boundaries: Z-score boundaries at each look
            - information_fractions: Fraction of information at each look
            - num_looks: Number of looks
            - alpha: Overall significance level
            - method: Name of the boundary method

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(num_looks, int, min_value=1)
        self.validate_data(alpha, float, min_value=0.001, max_value=0.5)

        # Calculate information fractions (assuming equal spacing)
        information_fractions = np.array([(i + 1) / num_looks for i in range(num_looks)])

        # Calculate O'Brien-Fleming boundaries
        z_boundaries = []
        boundaries = []
        cumulative_alpha = []

        for i, fraction in enumerate(information_fractions):
            # O'Brien-Fleming Z-score boundary
            z_boundary = stats.norm.ppf(1 - alpha / 2) / np.sqrt(fraction)
            z_boundaries.append(z_boundary)

            # Convert Z-score to alpha level
            if i == 0:
                # First look
                boundary = 2 * (1 - stats.norm.cdf(z_boundary))
                cumulative = boundary
            else:
                # Subsequent looks
                # Calculate incremental alpha spent at this look
                boundary = 2 * (1 - stats.norm.cdf(z_boundary)) - cumulative_alpha[i - 1]
                cumulative = cumulative_alpha[i - 1] + boundary

            boundaries.append(boundary)
            cumulative_alpha.append(cumulative)

        return {
            "boundaries": boundaries,
            "cumulative_alpha": cumulative_alpha,
            "z_boundaries": z_boundaries,
            "information_fractions": information_fractions.tolist(),
            "num_looks": num_looks,
            "alpha": alpha,
            "method": "obrien_fleming",
        }

    def pocock_boundary(self, num_looks: int, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Calculate Pocock stopping boundaries for group sequential testing.

        The Pocock approach uses constant boundaries across all looks,
        making it easier to stop early compared to O'Brien-Fleming.

        Args:
            num_looks: Number of interim analyses (including final analysis)
            alpha: Overall significance level (default: 0.05)

        Returns:
            Dictionary with boundary calculation results including:
            - boundaries: List of alpha spending at each look
            - cumulative_alpha: Cumulative alpha spent at each look
            - z_boundaries: Z-score boundaries at each look
            - information_fractions: Fraction of information at each look
            - num_looks: Number of looks
            - alpha: Overall significance level
            - method: Name of the boundary method

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(num_looks, int, min_value=1)
        self.validate_data(alpha, float, min_value=0.001, max_value=0.5)

        # Calculate information fractions (assuming equal spacing)
        information_fractions = np.array([(i + 1) / num_looks for i in range(num_looks)])

        # Calculate Pocock boundaries
        # For Pocock, the same nominal p-value is used at each look
        # We need to find the nominal p-value that gives the overall alpha

        # Function to solve for the nominal p-value
        def cumulative_alpha_error(nominal_p):
            # Convert nominal p-value to z-score
            z = stats.norm.ppf(1 - nominal_p / 2)

            # Calculate cumulative alpha spent over all looks
            cum_alpha = 0
            for i in range(num_looks):
                if i == 0:
                    # First look
                    cum_alpha = 2 * (1 - stats.norm.cdf(z))
                else:
                    # Subsequent looks - this is an approximation
                    # In practice, more complex calculations involving multivariate normal
                    # distributions would be used
                    cum_alpha += 2 * (1 - stats.norm.cdf(z)) / (num_looks - i)

            return cum_alpha - alpha

        # Solve for nominal p-value
        from scipy.optimize import brentq

        try:
            nominal_p = brentq(cumulative_alpha_error, 0.00001, 0.1)
        except ValueError:
            # If brentq fails, use a simple approximation
            nominal_p = alpha / num_looks

        # Calculate z-score boundary
        z_boundary = stats.norm.ppf(1 - nominal_p / 2)

        # Create results
        z_boundaries = [z_boundary] * num_looks
        boundaries = [nominal_p] * num_looks
        cumulative_alpha = [nominal_p * (i + 1) for i in range(num_looks)]

        return {
            "boundaries": boundaries,
            "cumulative_alpha": cumulative_alpha,
            "z_boundaries": z_boundaries,
            "information_fractions": information_fractions.tolist(),
            "num_looks": num_looks,
            "alpha": alpha,
            "method": "pocock",
        }

    def alpha_spending_function(
        self,
        information_fractions: Union[List[float], np.ndarray],
        alpha: float = 0.05,
        method: str = "obrien_fleming",
    ) -> Dict[str, Any]:
        """
        Calculate alpha spending function for group sequential testing.

        Alpha spending functions determine how much of the total Type I error
        is "spent" at each interim analysis.

        Args:
            information_fractions: List or array of information fractions at each look
                                  (values between 0 and 1, with the last value typically being 1)
            alpha: Overall significance level (default: 0.05)
            method: Method to use for alpha spending, one of:
                   "obrien_fleming": O'Brien-Fleming spending function (default)
                   "pocock": Pocock spending function
                   "hwang_shih_decosta": Hwang-Shih-DeCosta spending function
                   "linear": Linear spending function

        Returns:
            Dictionary with alpha spending results including:
            - alpha_spent: List of alpha spent at each look
            - cumulative_alpha: Cumulative alpha spent at each look
            - information_fractions: Information fractions at each look
            - num_looks: Number of looks
            - alpha: Overall significance level
            - method: Method used for alpha spending

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(information_fractions, (list, np.ndarray), min_length=1)
        self.validate_data(alpha, float, min_value=0.001, max_value=0.5)

        if method not in ["obrien_fleming", "pocock", "hwang_shih_decosta", "linear"]:
            raise InvalidParameterError(
                "Method must be one of: 'obrien_fleming', 'pocock', 'hwang_shih_decosta', 'linear'"
            )

        # Convert to numpy array for consistent handling
        info_fractions = np.array(information_fractions)

        # Check if information fractions are valid
        if np.any((info_fractions < 0) | (info_fractions > 1)):
            raise InvalidParameterError("Information fractions must be between 0 and 1")

        # Check if information fractions are in ascending order
        if not np.all(np.diff(info_fractions) >= 0):
            raise InvalidParameterError("Information fractions must be in ascending order")

        # Number of looks
        num_looks = len(info_fractions)

        # Calculate cumulative alpha spent at each look
        cumulative_alpha = np.zeros(num_looks)

        if method == "obrien_fleming":
            # O'Brien-Fleming spending function
            for i, t in enumerate(info_fractions):
                if t > 0:
                    cumulative_alpha[i] = 2 * (
                        1 - stats.norm.cdf(stats.norm.ppf(1 - alpha / 2) / np.sqrt(t))
                    )
                else:
                    cumulative_alpha[i] = 0

        elif method == "pocock":
            # Pocock spending function
            for i, t in enumerate(info_fractions):
                cumulative_alpha[i] = alpha * np.log(1 + (np.e - 1) * t)

        elif method == "hwang_shih_decosta":
            # Hwang-Shih-DeCosta spending function
            for i, t in enumerate(info_fractions):
                if t > 0:
                    cumulative_alpha[i] = alpha * t**1.5
                else:
                    cumulative_alpha[i] = 0

        elif method == "linear":
            # Linear spending function
            for i, t in enumerate(info_fractions):
                cumulative_alpha[i] = alpha * t

        # Calculate incremental alpha spent at each look
        alpha_spent = np.zeros(num_looks)
        alpha_spent[0] = cumulative_alpha[0]
        for i in range(1, num_looks):
            alpha_spent[i] = cumulative_alpha[i] - cumulative_alpha[i - 1]

        return {
            "alpha_spent": alpha_spent.tolist(),
            "cumulative_alpha": cumulative_alpha.tolist(),
            "information_fractions": info_fractions.tolist(),
            "num_looks": num_looks,
            "alpha": alpha,
            "method": method,
        }

    def sequential_test_analysis(
        self,
        z_scores: Union[List[float], np.ndarray],
        information_fractions: Union[List[float], np.ndarray] = None,
        alpha: float = 0.05,
        method: str = "obrien_fleming",
    ) -> Dict[str, Any]:
        """
        Analyze results from a sequential test with multiple looks.

        This method evaluates whether stopping boundaries were crossed at any look
        and provides adjusted p-values for sequential testing.

        Args:
            z_scores: List or array of Z-scores at each look
            information_fractions: List or array of information fractions at each look
                                  (values between 0 and 1, with the last value typically being 1)
                                  If None, assumes equal spacing
            alpha: Overall significance level (default: 0.05)
            method: Method to use for boundary calculation, one of:
                   "obrien_fleming": O'Brien-Fleming boundaries (default)
                   "pocock": Pocock boundaries

        Returns:
            Dictionary with sequential test analysis results including:
            - z_scores: Z-scores at each look
            - boundaries: Stopping boundaries at each look
            - crossed: Boolean array indicating whether boundaries were crossed at each look
            - adjusted_p_values: P-values adjusted for sequential testing
            - information_fractions: Information fractions at each look
            - num_looks: Number of looks
            - alpha: Overall significance level
            - method: Method used for boundary calculation
            - stop_early: Whether the test should have stopped early
            - first_significant_look: Index of the first look where boundaries were crossed (or None)

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(z_scores, (list, np.ndarray), min_length=1)
        self.validate_data(alpha, float, min_value=0.001, max_value=0.5)

        if method not in ["obrien_fleming", "pocock"]:
            raise InvalidParameterError("Method must be one of: 'obrien_fleming', 'pocock'")

        # Convert to numpy array for consistent handling
        z_scores_array = np.array(z_scores)

        # Number of looks
        num_looks = len(z_scores_array)

        # If information fractions not provided, assume equal spacing
        if information_fractions is None:
            info_fractions = np.array([(i + 1) / num_looks for i in range(num_looks)])
        else:
            self.validate_data(information_fractions, (list, np.ndarray), min_length=num_looks)
            info_fractions = np.array(information_fractions)

            # Check if information fractions are valid
            if np.any((info_fractions < 0) | (info_fractions > 1)):
                raise InvalidParameterError("Information fractions must be between 0 and 1")

            # Check if information fractions are in ascending order
            if not np.all(np.diff(info_fractions) >= 0):
                raise InvalidParameterError("Information fractions must be in ascending order")

        # Calculate boundaries based on method
        if method == "obrien_fleming":
            # O'Brien-Fleming boundaries
            boundaries = stats.norm.ppf(1 - alpha / 2) / np.sqrt(info_fractions)
        else:  # method == "pocock"
            # Pocock boundaries - constant across all looks
            # This is an approximation; in practice, more complex calculations would be used
            nominal_p = alpha / num_looks
            z_boundary = stats.norm.ppf(1 - nominal_p / 2)
            boundaries = np.array([z_boundary] * num_looks)

        # Check if boundaries were crossed at each look
        crossed = np.abs(z_scores_array) >= boundaries

        # Find the first look where boundaries were crossed (if any)
        first_significant_look = None
        for i, is_crossed in enumerate(crossed):
            if is_crossed:
                first_significant_look = i
                break

        # Determine if the test should have stopped early
        stop_early = first_significant_look is not None and first_significant_look < num_looks - 1

        # Calculate adjusted p-values
        adjusted_p_values = []
        for i, z in enumerate(z_scores_array):
            # For each look, calculate the adjusted p-value
            # This is an approximation; in practice, more complex calculations would be used
            if method == "obrien_fleming":
                # O'Brien-Fleming adjustment
                adjusted_p = 2 * (1 - stats.norm.cdf(np.abs(z) * np.sqrt(info_fractions[i])))
            else:  # method == "pocock"
                # Pocock adjustment
                adjusted_p = 2 * (1 - stats.norm.cdf(np.abs(z))) * num_looks
                adjusted_p = min(adjusted_p, 1.0)  # Cap at 1.0

            adjusted_p_values.append(adjusted_p)

        return {
            "z_scores": z_scores_array.tolist(),
            "boundaries": boundaries.tolist(),
            "crossed": crossed.tolist(),
            "adjusted_p_values": adjusted_p_values,
            "information_fractions": info_fractions.tolist(),
            "num_looks": num_looks,
            "alpha": alpha,
            "method": method,
            "stop_early": stop_early,
            "first_significant_look": first_significant_look,
        }

    def conditional_power(
        self,
        current_z: float,
        information_fraction: float,
        target_effect: float = None,
        observed_effect: float = None,
        alpha: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Calculate conditional power for a sequential test.

        Conditional power is the probability of rejecting the null hypothesis at the
        final analysis, given the current data.

        Args:
            current_z: Current Z-score
            information_fraction: Current fraction of information (between 0 and 1)
            target_effect: Target effect size (standardized) to detect
                          If None, uses observed_effect
            observed_effect: Observed effect size (standardized) from current data
                            If None and target_effect is None, uses current_z / sqrt(information_fraction)
            alpha: Significance level (default: 0.05)

        Returns:
            Dictionary with conditional power calculation results including:
            - conditional_power: Probability of rejecting null at final analysis
            - current_z: Current Z-score
            - information_fraction: Current fraction of information
            - target_effect: Target effect size used in calculation
            - observed_effect: Observed effect size from current data
            - alpha: Significance level
            - z_critical: Critical Z-score for final analysis

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(current_z, float)
        self.validate_data(information_fraction, float, min_value=0.0, max_value=1.0)
        self.validate_data(alpha, float, min_value=0.001, max_value=0.5)

        if target_effect is not None:
            self.validate_data(target_effect, float)

        if observed_effect is not None:
            self.validate_data(observed_effect, float)

        # Critical Z-score for final analysis
        z_critical = stats.norm.ppf(1 - alpha / 2)

        # Determine effect size to use in calculation
        if target_effect is not None:
            effect = target_effect
        elif observed_effect is not None:
            effect = observed_effect
        else:
            # Estimate effect size from current data
            effect = current_z / np.sqrt(information_fraction)

        # Calculate conditional power
        remaining_info = 1 - information_fraction

        # Mean of the distribution of the final Z-score, conditional on current Z
        conditional_mean = current_z * np.sqrt(information_fraction / 1) + effect * np.sqrt(
            remaining_info
        )

        # Standard deviation of the distribution of the final Z-score, conditional on current Z
        conditional_sd = np.sqrt(remaining_info)

        # Calculate probability that final Z > z_critical
        cp_upper = 1 - stats.norm.cdf((z_critical - conditional_mean) / conditional_sd)

        # Calculate probability that final Z < -z_critical
        cp_lower = stats.norm.cdf((-z_critical - conditional_mean) / conditional_sd)

        # Total conditional power (probability of rejecting null)
        conditional_power = cp_upper + cp_lower

        return {
            "conditional_power": conditional_power,
            "current_z": current_z,
            "information_fraction": information_fraction,
            "target_effect": effect,
            "observed_effect": (
                observed_effect
                if observed_effect is not None
                else current_z / np.sqrt(information_fraction)
            ),
            "alpha": alpha,
            "z_critical": z_critical,
        }

    def futility_boundary(
        self,
        information_fractions: Union[List[float], np.ndarray],
        beta: float = 0.2,
        method: str = "obrien_fleming",
    ) -> Dict[str, Any]:
        """
        Calculate futility boundaries for group sequential testing.

        Futility boundaries are used to stop a trial early for lack of efficacy.

        Args:
            information_fractions: List or array of information fractions at each look
                                  (values between 0 and 1, with the last value typically being 1)
            beta: Type II error rate (1 - power, default: 0.2)
            method: Method to use for boundary calculation, one of:
                   "obrien_fleming": O'Brien-Fleming-like boundaries (default)
                   "pocock": Pocock-like boundaries

        Returns:
            Dictionary with futility boundary calculation results including:
            - futility_boundaries: Z-score boundaries for futility at each look
            - information_fractions: Information fractions at each look
            - num_looks: Number of looks
            - beta: Type II error rate
            - method: Method used for boundary calculation

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(information_fractions, (list, np.ndarray), min_length=1)
        self.validate_data(beta, float, min_value=0.001, max_value=0.5)

        if method not in ["obrien_fleming", "pocock"]:
            raise InvalidParameterError("Method must be one of: 'obrien_fleming', 'pocock'")

        # Convert to numpy array for consistent handling
        info_fractions = np.array(information_fractions)

        # Check if information fractions are valid
        if np.any((info_fractions < 0) | (info_fractions > 1)):
            raise InvalidParameterError("Information fractions must be between 0 and 1")

        # Check if information fractions are in ascending order
        if not np.all(np.diff(info_fractions) >= 0):
            raise InvalidParameterError("Information fractions must be in ascending order")

        # Number of looks
        num_looks = len(info_fractions)

        # Calculate futility boundaries
        futility_boundaries = np.zeros(num_looks)

        if method == "obrien_fleming":
            # O'Brien-Fleming-like futility boundaries
            for i, t in enumerate(info_fractions):
                if t < 1:  # No futility boundary at final analysis
                    futility_boundaries[i] = stats.norm.ppf(beta) / np.sqrt(1 - t)
                else:
                    futility_boundaries[i] = float(
                        "-inf"
                    )  # No stopping for futility at final analysis
        else:  # method == "pocock"
            # Pocock-like futility boundaries - constant across all looks
            z_boundary = stats.norm.ppf(beta)
            futility_boundaries = np.array([z_boundary] * (num_looks - 1) + [float("-inf")])

        return {
            "futility_boundaries": futility_boundaries.tolist(),
            "information_fractions": info_fractions.tolist(),
            "num_looks": num_looks,
            "beta": beta,
            "method": method,
        }

    def log_likelihood_ratio_test(
        self, model1_loglik: float, model2_loglik: float, df1: int, df2: int
    ) -> Dict[str, Any]:
        """
        Perform a log-likelihood ratio test for nested model comparison.

        This test compares two nested models to determine if the more complex model
        (with more parameters) provides a significantly better fit than the simpler model.
        The test statistic follows a chi-square distribution with degrees of freedom
        equal to the difference in the number of parameters between the models.

        Args:
            model1_loglik: Log-likelihood of the simpler model (null model)
            model2_loglik: Log-likelihood of the more complex model (alternative model)
            df1: Degrees of freedom (number of parameters) in the simpler model
            df2: Degrees of freedom (number of parameters) in the more complex model

        Returns:
            Dictionary with test results including:
            - test_statistic: Log-likelihood ratio test statistic (2 * (loglik2 - loglik1))
            - p_value: P-value for the test
            - df_diff: Difference in degrees of freedom between models
            - is_significant: Whether the result is significant at alpha level
            - model_selection: Dictionary with model selection criteria (AIC, BIC)
            - test_name: Name of the test

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(model1_loglik, float)
        self.validate_data(model2_loglik, float)
        self.validate_data(df1, int, min_value=1)
        self.validate_data(df2, int, min_value=1)

        if df2 <= df1:
            raise InvalidParameterError(
                "The more complex model (model2) must have more parameters than the simpler model (model1)"
            )

        # Calculate test statistic: 2 * (loglik2 - loglik1)
        # The factor of 2 makes the statistic follow a chi-square distribution
        test_statistic = 2 * (model2_loglik - model1_loglik)

        # Calculate degrees of freedom difference
        df_diff = df2 - df1

        # Calculate p-value from chi-square distribution
        # We use 1 - cdf because we're testing if test_statistic is significantly large
        p_value = 1 - stats.chi2.cdf(test_statistic, df_diff)

        # Determine significance
        is_significant = p_value < self.default_alpha

        # Calculate model selection criteria
        # AIC = -2 * loglik + 2 * k (where k is the number of parameters)
        # BIC = -2 * loglik + k * ln(n) (where n is the sample size, which we don't have)
        # Since we don't have sample size, we'll use a placeholder value of 100
        # In practice, the actual sample size should be provided
        sample_size = 100  # Placeholder - in real usage, this should be provided

        aic1 = -2 * model1_loglik + 2 * df1
        aic2 = -2 * model2_loglik + 2 * df2

        bic1 = -2 * model1_loglik + df1 * np.log(sample_size)
        bic2 = -2 * model2_loglik + df2 * np.log(sample_size)

        # Determine which model is preferred by each criterion
        # Lower values of AIC and BIC indicate better models
        aic_preferred = "model1" if aic1 < aic2 else "model2"
        bic_preferred = "model1" if bic1 < bic2 else "model2"

        # Return results
        return {
            "test_statistic": test_statistic,
            "p_value": p_value,
            "df_diff": df_diff,
            "df1": df1,
            "df2": df2,
            "loglik1": model1_loglik,
            "loglik2": model2_loglik,
            "is_significant": is_significant,
            "model_selection": {
                "aic1": aic1,
                "aic2": aic2,
                "bic1": bic1,
                "bic2": bic2,
                "aic_preferred": aic_preferred,
                "bic_preferred": bic_preferred,
                "sample_size_used": sample_size,
            },
            "test_name": "log_likelihood_ratio",
            "alpha": self.default_alpha,
        }

    def model_selection_criteria(
        self, loglik: float, df: int, sample_size: int
    ) -> Dict[str, float]:
        """
        Calculate model selection criteria for a given model.

        This method calculates various information criteria used for model selection,
        including AIC (Akaike Information Criterion), BIC (Bayesian Information Criterion),
        and others.

        Args:
            loglik: Log-likelihood of the model
            df: Degrees of freedom (number of parameters) in the model
            sample_size: Number of observations used to fit the model

        Returns:
            Dictionary with model selection criteria including:
            - aic: Akaike Information Criterion
            - bic: Bayesian Information Criterion
            - aicc: AIC with correction for small sample sizes
            - hqic: Hannan-Quinn Information Criterion

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(loglik, float)
        self.validate_data(df, int, min_value=1)
        self.validate_data(sample_size, int, min_value=df + 1)

        # Calculate AIC: -2 * loglik + 2 * k
        aic = -2 * loglik + 2 * df

        # Calculate BIC: -2 * loglik + k * ln(n)
        bic = -2 * loglik + df * np.log(sample_size)

        # Calculate AICc: AIC + (2k(k+1))/(n-k-1)
        # This is a correction for small sample sizes
        aicc = aic + (2 * df * (df + 1)) / (sample_size - df - 1)

        # Calculate HQIC: -2 * loglik + 2k * ln(ln(n))
        hqic = -2 * loglik + 2 * df * np.log(np.log(sample_size))

        return {
            "aic": aic,
            "bic": bic,
            "aicc": aicc,
            "hqic": hqic,
            "loglik": loglik,
            "df": df,
            "sample_size": sample_size,
        }

    def optional_stopping_correction(
        self, p_value: float, num_looks: int, method: str = "bonferroni"
    ) -> Dict[str, Any]:
        """
        Apply correction for optional stopping in sequential testing.

        This method adjusts p-values to account for multiple looks at the data,
        which can inflate Type I error rates.

        Args:
            p_value: Uncorrected p-value
            num_looks: Number of potential looks at the data
            method: Method to use for correction, one of:
                   "bonferroni": Bonferroni correction (default)
                   "sidak": Šidák correction
                   "sequential": Sequential testing correction

        Returns:
            Dictionary with correction results including:
            - original_p_value: Original uncorrected p-value
            - adjusted_p_value: P-value adjusted for optional stopping
            - num_looks: Number of potential looks
            - method: Method used for correction

        Raises:
            InvalidParameterError: If inputs are invalid
        """
        # Validate inputs
        self.validate_data(p_value, float, min_value=0.0, max_value=1.0)
        self.validate_data(num_looks, int, min_value=1)

        if method not in ["bonferroni", "sidak", "sequential"]:
            raise InvalidParameterError(
                "Method must be one of: 'bonferroni', 'sidak', 'sequential'"
            )

        # Initialize result dictionary
        result = {"original_p_value": p_value, "num_looks": num_looks, "method": method}

        # Apply the selected correction method
        if method == "bonferroni":
            # Bonferroni correction: p * num_looks
            adjusted_p = min(p_value * num_looks, 1.0)
            result["adjusted_p_value"] = adjusted_p

        elif method == "sidak":
            # Šidák correction: 1 - (1 - p)^num_looks
            adjusted_p = 1.0 - (1.0 - p_value) ** num_looks
            result["adjusted_p_value"] = adjusted_p

        else:  # method == "sequential"
            # Sequential testing correction
            # This is an approximation based on the expected maximum of num_looks independent tests
            # In practice, more complex calculations would be used

            # Convert p-value to z-score
            if p_value > 0:
                z = stats.norm.ppf(1 - p_value / 2)
            else:
                z = float("inf")

            # Adjust z-score for multiple looks
            # This is based on the expected maximum of num_looks independent standard normal variables
            # E[max(Z_1, ..., Z_n)] ≈ sqrt(2 * log(n))
            adjustment = np.sqrt(2 * np.log(num_looks))
            adjusted_z = z - adjustment

            # Convert back to p-value
            if adjusted_z < 0:
                adjusted_p = 1.0
            else:
                adjusted_p = 2 * (1 - stats.norm.cdf(adjusted_z))

            result["adjusted_p_value"] = min(adjusted_p, 1.0)
            result["z_score"] = z
            result["adjusted_z_score"] = adjusted_z

        return result
