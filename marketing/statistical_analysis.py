"""
"""
Statistical Analysis Framework for Marketing.
Statistical Analysis Framework for Marketing.


This module provides statistical analysis tools for marketing data, including:
    This module provides statistical analysis tools for marketing data, including:
    - Statistical significance testing
    - Statistical significance testing
    - Confidence interval calculations
    - Confidence interval calculations
    - Effect size calculations
    - Effect size calculations
    - Power analysis
    - Power analysis
    - Multiple comparison corrections
    - Multiple comparison corrections
    - Sequential analysis
    - Sequential analysis


    These tools are designed to support data-driven decision making in marketing,
    These tools are designed to support data-driven decision making in marketing,
    particularly for A/B testing, campaign performance analysis, and ROI calculations.
    particularly for A/B testing, campaign performance analysis, and ROI calculations.
    """
    """




    import logging
    import logging
    import math
    import math
    from typing import Any, Dict, List, Optional, Tuple, Union
    from typing import Any, Dict, List, Optional, Tuple, Union


    import numpy as np
    import numpy as np
    from scipy import stats
    from scipy import stats
    from scipy.optimize import brentq
    from scipy.optimize import brentq


    try
    try


    # Configure logger
    # Configure logger
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)




    class StatisticalAnalysisError(Exception):
    class StatisticalAnalysisError(Exception):
    """Base exception for statistical analysis errors."""

    pass


    class InsufficientDataError(StatisticalAnalysisError):

    pass


    class InvalidParameterError(StatisticalAnalysisError):

    pass


    class StatisticalAnalysis:
    """
    """
    Statistical analysis framework for marketing data.
    Statistical analysis framework for marketing data.


    This class provides methods for statistical testing, confidence intervals,
    This class provides methods for statistical testing, confidence intervals,
    effect size calculations, and other statistical analyses relevant to
    effect size calculations, and other statistical analyses relevant to
    marketing decision making.
    marketing decision making.
    """
    """


    def __init__(self, default_alpha: float = 0.05):
    def __init__(self, default_alpha: float = 0.05):
    """
    """
    Initialize the statistical analysis framework.
    Initialize the statistical analysis framework.


    Args:
    Args:
    default_alpha: Default significance level (default: 0.05)
    default_alpha: Default significance level (default: 0.05)
    """
    """
    self.default_alpha = default_alpha
    self.default_alpha = default_alpha
    self.logger = logging.getLogger(__name__)
    self.logger = logging.getLogger(__name__)


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Utility Methods
    # Utility Methods
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------


    def validate_data(
    def validate_data(
    self,
    self,
    data: Any,
    data: Any,
    data_type: type,
    data_type: type,
    min_value: Optional[float] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    max_value: Optional[float] = None,
    min_length: Optional[int] = None,
    min_length: Optional[int] = None,
    allow_none: bool = False,
    allow_none: bool = False,
    ) -> bool:
    ) -> bool:
    """
    """
    Validate data based on type and constraints.
    Validate data based on type and constraints.


    Args:
    Args:
    data: Data to validate
    data: Data to validate
    data_type: Expected data type
    data_type: Expected data type
    min_value: Minimum allowed value (for numeric types)
    min_value: Minimum allowed value (for numeric types)
    max_value: Maximum allowed value (for numeric types)
    max_value: Maximum allowed value (for numeric types)
    min_length: Minimum length (for sequences)
    min_length: Minimum length (for sequences)
    allow_none: Whether None is allowed
    allow_none: Whether None is allowed


    Returns:
    Returns:
    True if data is valid
    True if data is valid


    Raises:
    Raises:
    InvalidParameterError: If data is invalid
    InvalidParameterError: If data is invalid
    """
    """
    # Check for None
    # Check for None
    if data is None:
    if data is None:
    if allow_none:
    if allow_none:
    return True
    return True
    raise InvalidParameterError("Data cannot be None")
    raise InvalidParameterError("Data cannot be None")


    # Check type
    # Check type
    if not isinstance(data, data_type):
    if not isinstance(data, data_type):
    if isinstance(data_type, tuple):
    if isinstance(data_type, tuple):
    expected_types = ", ".join(t.__name__ for t in data_type)
    expected_types = ", ".join(t.__name__ for t in data_type)
    raise InvalidParameterError(
    raise InvalidParameterError(
    f"Expected one of: {expected_types}, got {type(data).__name__}"
    f"Expected one of: {expected_types}, got {type(data).__name__}"
    )
    )
    else:
    else:
    raise InvalidParameterError(
    raise InvalidParameterError(
    f"Expected {data_type.__name__}, got {type(data).__name__}"
    f"Expected {data_type.__name__}, got {type(data).__name__}"
    )
    )


    # Check numeric constraints
    # Check numeric constraints
    if min_value is not None and isinstance(data, (int, float)):
    if min_value is not None and isinstance(data, (int, float)):
    if data < min_value:
    if data < min_value:
    raise InvalidParameterError(f"Value must be at least {min_value}")
    raise InvalidParameterError(f"Value must be at least {min_value}")


    if max_value is not None and isinstance(data, (int, float)):
    if max_value is not None and isinstance(data, (int, float)):
    if data > max_value:
    if data > max_value:
    raise InvalidParameterError(f"Value must be at most {max_value}")
    raise InvalidParameterError(f"Value must be at most {max_value}")


    # Check sequence length
    # Check sequence length
    if min_length is not None and hasattr(data, "__len__"):
    if min_length is not None and hasattr(data, "__len__"):
    if len(data) < min_length:
    if len(data) < min_length:
    raise InvalidParameterError(
    raise InvalidParameterError(
    f"Sequence must have at least {min_length} elements"
    f"Sequence must have at least {min_length} elements"
    )
    )


    return True
    return True


    def check_sufficient_data(
    def check_sufficient_data(
    self, data: Union[List, np.ndarray], min_samples: int = 30
    self, data: Union[List, np.ndarray], min_samples: int = 30
    ) -> bool:
    ) -> bool:
    """
    """
    Check if there is sufficient data for statistical analysis.
    Check if there is sufficient data for statistical analysis.


    Args:
    Args:
    data: Data to check
    data: Data to check
    min_samples: Minimum number of samples required
    min_samples: Minimum number of samples required


    Returns:
    Returns:
    True if there is sufficient data
    True if there is sufficient data


    Raises:
    Raises:
    InsufficientDataError: If there is not enough data
    InsufficientDataError: If there is not enough data
    """
    """
    if len(data) < min_samples:
    if len(data) < min_samples:
    raise InsufficientDataError(
    raise InsufficientDataError(
    f"Insufficient data: {len(data)} samples, minimum required: {min_samples}"
    f"Insufficient data: {len(data)} samples, minimum required: {min_samples}"
    )
    )
    return True
    return True


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Basic Statistical Methods
    # Basic Statistical Methods
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------


    def mean_and_std(self, data: Union[List[float], np.ndarray]) -> Tuple[float, float]:
    def mean_and_std(self, data: Union[List[float], np.ndarray]) -> Tuple[float, float]:
    """
    """
    Calculate mean and standard deviation.
    Calculate mean and standard deviation.


    Args:
    Args:
    data: Numeric data
    data: Numeric data


    Returns:
    Returns:
    Tuple of (mean, standard_deviation)
    Tuple of (mean, standard_deviation)
    """
    """
    self.validate_data(data, (list, np.ndarray), min_length=1)
    self.validate_data(data, (list, np.ndarray), min_length=1)
    return np.mean(data), np.std(data, ddof=1)  # ddof=1 for sample std dev
    return np.mean(data), np.std(data, ddof=1)  # ddof=1 for sample std dev


    def median_and_iqr(
    def median_and_iqr(
    self, data: Union[List[float], np.ndarray]
    self, data: Union[List[float], np.ndarray]
    ) -> Tuple[float, float]:
    ) -> Tuple[float, float]:
    """
    """
    Calculate median and interquartile range.
    Calculate median and interquartile range.


    Args:
    Args:
    data: Numeric data
    data: Numeric data


    Returns:
    Returns:
    Tuple of (median, iqr)
    Tuple of (median, iqr)
    """
    """
    self.validate_data(data, (list, np.ndarray), min_length=1)
    self.validate_data(data, (list, np.ndarray), min_length=1)


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    data_array = np.array(data)
    data_array = np.array(data)


    # Sort the data
    # Sort the data
    sorted_data = np.sort(data_array)
    sorted_data = np.sort(data_array)


    # Calculate median
    # Calculate median
    len(sorted_data)
    len(sorted_data)
    median = np.median(sorted_data)
    median = np.median(sorted_data)


    # Calculate quartiles using linear interpolation method
    # Calculate quartiles using linear interpolation method
    # This matches the expected test values
    # This matches the expected test values
    q1 = np.percentile(sorted_data, 25, method="linear")
    q1 = np.percentile(sorted_data, 25, method="linear")
    q3 = np.percentile(sorted_data, 75, method="linear")
    q3 = np.percentile(sorted_data, 75, method="linear")
    iqr = q3 - q1
    iqr = q3 - q1


    return median, iqr
    return median, iqr


    def summary_statistics(
    def summary_statistics(
    self, data: Union[List[float], np.ndarray]
    self, data: Union[List[float], np.ndarray]
    ) -> Dict[str, float]:
    ) -> Dict[str, float]:
    """
    """
    Calculate summary statistics for a dataset.
    Calculate summary statistics for a dataset.


    Args:
    Args:
    data: Numeric data
    data: Numeric data


    Returns:
    Returns:
    Dictionary of summary statistics
    Dictionary of summary statistics
    """
    """
    self.validate_data(data, (list, np.ndarray), min_length=1)
    self.validate_data(data, (list, np.ndarray), min_length=1)


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    data_array = np.array(data)
    data_array = np.array(data)


    # Calculate quartiles using linear interpolation method
    # Calculate quartiles using linear interpolation method
    q1 = np.percentile(data_array, 25, method="linear")
    q1 = np.percentile(data_array, 25, method="linear")
    q3 = np.percentile(data_array, 75, method="linear")
    q3 = np.percentile(data_array, 75, method="linear")


    return {
    return {
    "count": len(data_array),
    "count": len(data_array),
    "mean": np.mean(data_array),
    "mean": np.mean(data_array),
    "median": np.median(data_array),
    "median": np.median(data_array),
    "std": np.std(data_array, ddof=1),
    "std": np.std(data_array, ddof=1),
    "min": np.min(data_array),
    "min": np.min(data_array),
    "max": np.max(data_array),
    "max": np.max(data_array),
    "q1": q1,
    "q1": q1,
    "q3": q3,
    "q3": q3,
    "iqr": q3 - q1,
    "iqr": q3 - q1,
    "skewness": stats.skew(data_array),
    "skewness": stats.skew(data_array),
    "kurtosis": stats.kurtosis(data_array),
    "kurtosis": stats.kurtosis(data_array),
    }
    }


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Statistical Tests
    # Statistical Tests
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------


    def chi_square_test(
    def chi_square_test(
    self,
    self,
    observed: Union[List[List[int]], np.ndarray],
    observed: Union[List[List[int]], np.ndarray],
    expected: Optional[Union[List[List[float]], np.ndarray]] = None,
    expected: Optional[Union[List[List[float]], np.ndarray]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Perform a chi-square test for independence or goodness of fit.
    Perform a chi-square test for independence or goodness of fit.


    For a contingency table (observed counts), this tests for independence
    For a contingency table (observed counts), this tests for independence
    between rows and columns. For a 1D array compared against expected values,
    between rows and columns. For a 1D array compared against expected values,
    this tests for goodness of fit.
    this tests for goodness of fit.


    Args:
    Args:
    observed: Observed frequencies (counts) as a 2D array or list of lists
    observed: Observed frequencies (counts) as a 2D array or list of lists
    expected: Expected frequencies (optional) - if not provided, will be calculated
    expected: Expected frequencies (optional) - if not provided, will be calculated
    assuming independence between rows and columns
    assuming independence between rows and columns


    Returns:
    Returns:
    Dictionary with test results including:
    Dictionary with test results including:
    - chi2: Chi-square statistic
    - chi2: Chi-square statistic
    - p_value: P-value for the test
    - p_value: P-value for the test
    - dof: Degrees of freedom
    - dof: Degrees of freedom
    - expected: Expected frequencies
    - expected: Expected frequencies
    - residuals: Standardized residuals
    - residuals: Standardized residuals
    - is_significant: Whether the result is significant at alpha level
    - is_significant: Whether the result is significant at alpha level


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    InsufficientDataError: If there is not enough data
    InsufficientDataError: If there is not enough data
    """
    """
    # Validate inputs
    # Validate inputs
    if isinstance(observed, list):
    if isinstance(observed, list):
    observed = np.array(observed)
    observed = np.array(observed)


    self.validate_data(observed, np.ndarray, min_length=1)
    self.validate_data(observed, np.ndarray, min_length=1)


    # Check if we have a 1D or 2D array
    # Check if we have a 1D or 2D array
    if observed.ndim == 1:
    if observed.ndim == 1:
    # For 1D arrays, we need expected values
    # For 1D arrays, we need expected values
    if expected is None:
    if expected is None:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Expected frequencies must be provided for 1D observed data"
    "Expected frequencies must be provided for 1D observed data"
    )
    )


    if isinstance(expected, list):
    if isinstance(expected, list):
    expected = np.array(expected)
    expected = np.array(expected)


    self.validate_data(expected, np.ndarray, min_length=1)
    self.validate_data(expected, np.ndarray, min_length=1)


    if len(observed) != len(expected):
    if len(observed) != len(expected):
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Observed and expected arrays must have the same length"
    "Observed and expected arrays must have the same length"
    )
    )


    # Ensure we have sufficient data
    # Ensure we have sufficient data
    if np.sum(observed) < 20:
    if np.sum(observed) < 20:
    raise InsufficientDataError(
    raise InsufficientDataError(
    "Chi-square test requires at least 20 total observations"
    "Chi-square test requires at least 20 total observations"
    )
    )


    # Check if any expected value is too small
    # Check if any expected value is too small
    if np.any(expected < 5):
    if np.any(expected < 5):
    self.logger.warning(
    self.logger.warning(
    "Some expected frequencies are less than 5, chi-square may not be valid"
    "Some expected frequencies are less than 5, chi-square may not be valid"
    )
    )


    # Calculate chi-square statistic
    # Calculate chi-square statistic
    chi2_stat = np.sum((observed - expected) ** 2 / expected)
    chi2_stat = np.sum((observed - expected) ** 2 / expected)
    dof = len(observed) - 1
    dof = len(observed) - 1


    elif observed.ndim == 2:
    elif observed.ndim == 2:
    # For contingency tables
    # For contingency tables
    if expected is not None and isinstance(expected, list):
    if expected is not None and isinstance(expected, list):
    expected = np.array(expected)
    expected = np.array(expected)


    # Check for sufficient data
    # Check for sufficient data
    if np.sum(observed) < 20:
    if np.sum(observed) < 20:
    raise InsufficientDataError(
    raise InsufficientDataError(
    "Chi-square test requires at least 20 total observations"
    "Chi-square test requires at least 20 total observations"
    )
    )


    # Calculate expected frequencies if not provided
    # Calculate expected frequencies if not provided
    if expected is None:
    if expected is None:
    row_sums = np.sum(observed, axis=1, keepdims=True)
    row_sums = np.sum(observed, axis=1, keepdims=True)
    col_sums = np.sum(observed, axis=0, keepdims=True)
    col_sums = np.sum(observed, axis=0, keepdims=True)
    total = np.sum(observed)
    total = np.sum(observed)
    expected = row_sums * col_sums / total
    expected = row_sums * col_sums / total


    # Check if any expected value is too small
    # Check if any expected value is too small
    if np.any(expected < 5):
    if np.any(expected < 5):
    self.logger.warning(
    self.logger.warning(
    "Some expected frequencies are less than 5, chi-square may not be valid"
    "Some expected frequencies are less than 5, chi-square may not be valid"
    )
    )


    # Calculate chi-square statistic
    # Calculate chi-square statistic
    chi2_stat = np.sum((observed - expected) ** 2 / expected)
    chi2_stat = np.sum((observed - expected) ** 2 / expected)
    dof = (observed.shape[0] - 1) * (observed.shape[1] - 1)
    dof = (observed.shape[0] - 1) * (observed.shape[1] - 1)


    else:
    else:
    raise InvalidParameterError("Observed data must be a 1D or 2D array")
    raise InvalidParameterError("Observed data must be a 1D or 2D array")


    # Calculate p-value
    # Calculate p-value
    p_value = 1 - stats.chi2.cdf(chi2_stat, dof)
    p_value = 1 - stats.chi2.cdf(chi2_stat, dof)


    # Calculate standardized residuals
    # Calculate standardized residuals
    residuals = (observed - expected) / np.sqrt(expected)
    residuals = (observed - expected) / np.sqrt(expected)


    # Determine significance
    # Determine significance
    is_significant = p_value < self.default_alpha
    is_significant = p_value < self.default_alpha


    return {
    return {
    "chi2": chi2_stat,
    "chi2": chi2_stat,
    "p_value": p_value,
    "p_value": p_value,
    "do": dof,
    "do": dof,
    "expected": (
    "expected": (
    expected.tolist() if isinstance(expected, np.ndarray) else expected
    expected.tolist() if isinstance(expected, np.ndarray) else expected
    ),
    ),
    "residuals": (
    "residuals": (
    residuals.tolist() if isinstance(residuals, np.ndarray) else residuals
    residuals.tolist() if isinstance(residuals, np.ndarray) else residuals
    ),
    ),
    "is_significant": is_significant,
    "is_significant": is_significant,
    "test_name": "chi_square",
    "test_name": "chi_square",
    "alpha": self.default_alpha,
    "alpha": self.default_alpha,
    }
    }


    def fishers_exact_test(
    def fishers_exact_test(
    self, table: Union[List[List[int]], np.ndarray], alternative: str = "two-sided"
    self, table: Union[List[List[int]], np.ndarray], alternative: str = "two-sided"
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Perform Fisher's exact test on a 2x2 contingency table.
    Perform Fisher's exact test on a 2x2 contingency table.


    This test is used when sample sizes are small and the chi-square test
    This test is used when sample sizes are small and the chi-square test
    may not be valid. It calculates the exact probability of observing a
    may not be valid. It calculates the exact probability of observing a
    table at least as extreme as the one provided.
    table at least as extreme as the one provided.


    Args:
    Args:
    table: 2x2 contingency table as a list of lists or numpy array
    table: 2x2 contingency table as a list of lists or numpy array
    alternative: Alternative hypothesis, one of:
    alternative: Alternative hypothesis, one of:
    "two-sided" (default): two-tailed test
    "two-sided" (default): two-tailed test
    "less": one-tailed test (probability of a more extreme table with a smaller odds ratio)
    "less": one-tailed test (probability of a more extreme table with a smaller odds ratio)
    "greater": one-tailed test (probability of a more extreme table with a larger odds ratio)
    "greater": one-tailed test (probability of a more extreme table with a larger odds ratio)


    Returns:
    Returns:
    Dictionary with test results including:
    Dictionary with test results including:
    - odds_ratio: The odds ratio
    - odds_ratio: The odds ratio
    - p_value: P-value for the test
    - p_value: P-value for the test
    - is_significant: Whether the result is significant at alpha level
    - is_significant: Whether the result is significant at alpha level


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    if isinstance(table, list):
    if isinstance(table, list):
    table = np.array(table)
    table = np.array(table)


    self.validate_data(table, np.ndarray, min_length=1)
    self.validate_data(table, np.ndarray, min_length=1)


    if table.shape != (2, 2):
    if table.shape != (2, 2):
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Fisher's exact test requires a 2x2 contingency table"
    "Fisher's exact test requires a 2x2 contingency table"
    )
    )


    if alternative not in ["two-sided", "less", "greater"]:
    if alternative not in ["two-sided", "less", "greater"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Alternative must be one of: 'two-sided', 'less', 'greater'"
    "Alternative must be one of: 'two-sided', 'less', 'greater'"
    )
    )


    # Calculate odds ratio and p-value
    # Calculate odds ratio and p-value
    odds_ratio, p_value = stats.fisher_exact(table, alternative=alternative)
    odds_ratio, p_value = stats.fisher_exact(table, alternative=alternative)


    # Determine significance
    # Determine significance
    is_significant = p_value < self.default_alpha
    is_significant = p_value < self.default_alpha


    return {
    return {
    "odds_ratio": odds_ratio,
    "odds_ratio": odds_ratio,
    "p_value": p_value,
    "p_value": p_value,
    "is_significant": is_significant,
    "is_significant": is_significant,
    "test_name": "fishers_exact",
    "test_name": "fishers_exact",
    "alternative": alternative,
    "alternative": alternative,
    "alpha": self.default_alpha,
    "alpha": self.default_alpha,
    "table": table.tolist() if isinstance(table, np.ndarray) else table,
    "table": table.tolist() if isinstance(table, np.ndarray) else table,
    }
    }


    def z_test_proportions(
    def z_test_proportions(
    self,
    self,
    count1: int,
    count1: int,
    nobs1: int,
    nobs1: int,
    count2: int = None,
    count2: int = None,
    nobs2: int = None,
    nobs2: int = None,
    value: float = None,
    value: float = None,
    alternative: str = "two-sided",
    alternative: str = "two-sided",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Perform a z-test for proportions.
    Perform a z-test for proportions.


    This test can be used to:
    This test can be used to:
    1. Compare a single proportion to a known value (one-sample test)
    1. Compare a single proportion to a known value (one-sample test)
    2. Compare two proportions (two-sample test)
    2. Compare two proportions (two-sample test)


    Args:
    Args:
    count1: Number of successes in first sample
    count1: Number of successes in first sample
    nobs1: Number of observations in first sample
    nobs1: Number of observations in first sample
    count2: Number of successes in second sample (for two-sample test)
    count2: Number of successes in second sample (for two-sample test)
    nobs2: Number of observations in second sample (for two-sample test)
    nobs2: Number of observations in second sample (for two-sample test)
    value: Known proportion to compare against (for one-sample test)
    value: Known proportion to compare against (for one-sample test)
    alternative: Alternative hypothesis, one of:
    alternative: Alternative hypothesis, one of:
    "two-sided" (default): two-tailed test
    "two-sided" (default): two-tailed test
    "less": one-tailed test (proportion is less than value or proportion2)
    "less": one-tailed test (proportion is less than value or proportion2)
    "greater": one-tailed test (proportion is greater than value or proportion2)
    "greater": one-tailed test (proportion is greater than value or proportion2)


    Returns:
    Returns:
    Dictionary with test results including:
    Dictionary with test results including:
    - z_score: Z-statistic
    - z_score: Z-statistic
    - p_value: P-value for the test
    - p_value: P-value for the test
    - proportion1: First sample proportion
    - proportion1: First sample proportion
    - proportion2: Second sample proportion or comparison value
    - proportion2: Second sample proportion or comparison value
    - is_significant: Whether the result is significant at alpha level
    - is_significant: Whether the result is significant at alpha level


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(count1, int, min_value=0)
    self.validate_data(count1, int, min_value=0)
    self.validate_data(nobs1, int, min_value=count1)
    self.validate_data(nobs1, int, min_value=count1)


    if alternative not in ["two-sided", "less", "greater"]:
    if alternative not in ["two-sided", "less", "greater"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Alternative must be one of: 'two-sided', 'less', 'greater'"
    "Alternative must be one of: 'two-sided', 'less', 'greater'"
    )
    )


    # Calculate first proportion
    # Calculate first proportion
    proportion1 = count1 / nobs1
    proportion1 = count1 / nobs1


    # Determine test type
    # Determine test type
    if count2 is not None and nobs2 is not None:
    if count2 is not None and nobs2 is not None:
    # Two-sample test
    # Two-sample test
    self.validate_data(count2, int, min_value=0)
    self.validate_data(count2, int, min_value=0)
    self.validate_data(nobs2, int, min_value=count2)
    self.validate_data(nobs2, int, min_value=count2)


    proportion2 = count2 / nobs2
    proportion2 = count2 / nobs2


    # Check normal approximation conditions
    # Check normal approximation conditions
    if (
    if (
    nobs1 * proportion1 < 5
    nobs1 * proportion1 < 5
    or nobs1 * (1 - proportion1) < 5
    or nobs1 * (1 - proportion1) < 5
    or nobs2 * proportion2 < 5
    or nobs2 * proportion2 < 5
    or nobs2 * (1 - proportion2) < 5
    or nobs2 * (1 - proportion2) < 5
    ):
    ):
    self.logger.warning(
    self.logger.warning(
    "Normal approximation may not be valid due to small expected counts"
    "Normal approximation may not be valid due to small expected counts"
    )
    )


    # Calculate pooled proportion
    # Calculate pooled proportion
    pooled_prop = (count1 + count2) / (nobs1 + nobs2)
    pooled_prop = (count1 + count2) / (nobs1 + nobs2)


    # Calculate standard error
    # Calculate standard error
    se = math.sqrt(pooled_prop * (1 - pooled_prop) * (1 / nobs1 + 1 / nobs2))
    se = math.sqrt(pooled_prop * (1 - pooled_prop) * (1 / nobs1 + 1 / nobs2))


    # Calculate z-score
    # Calculate z-score
    z_score = (proportion1 - proportion2) / se
    z_score = (proportion1 - proportion2) / se


    # Calculate p-value
    # Calculate p-value
    if alternative == "two-sided":
    if alternative == "two-sided":
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    elif alternative == "less":
    elif alternative == "less":
    p_value = stats.norm.cdf(z_score)
    p_value = stats.norm.cdf(z_score)
    else:  # alternative == "greater"
    else:  # alternative == "greater"
    p_value = 1 - stats.norm.cdf(z_score)
    p_value = 1 - stats.norm.cdf(z_score)


    result = {
    result = {
    "z_score": z_score,
    "z_score": z_score,
    "p_value": p_value,
    "p_value": p_value,
    "proportion1": proportion1,
    "proportion1": proportion1,
    "proportion2": proportion2,
    "proportion2": proportion2,
    "difference": proportion1 - proportion2,
    "difference": proportion1 - proportion2,
    "pooled_proportion": pooled_prop,
    "pooled_proportion": pooled_prop,
    "standard_error": se,
    "standard_error": se,
    "test_type": "two-sample",
    "test_type": "two-sample",
    }
    }


    elif value is not None:
    elif value is not None:
    # One-sample test
    # One-sample test
    self.validate_data(value, float, min_value=0.0, max_value=1.0)
    self.validate_data(value, float, min_value=0.0, max_value=1.0)


    # Check normal approximation conditions
    # Check normal approximation conditions
    if nobs1 * value < 5 or nobs1 * (1 - value) < 5:
    if nobs1 * value < 5 or nobs1 * (1 - value) < 5:
    self.logger.warning(
    self.logger.warning(
    "Normal approximation may not be valid due to small expected counts"
    "Normal approximation may not be valid due to small expected counts"
    )
    )


    # Calculate standard error
    # Calculate standard error
    se = math.sqrt(value * (1 - value) / nobs1)
    se = math.sqrt(value * (1 - value) / nobs1)


    # Calculate z-score
    # Calculate z-score
    z_score = (proportion1 - value) / se
    z_score = (proportion1 - value) / se


    # Calculate p-value
    # Calculate p-value
    if alternative == "two-sided":
    if alternative == "two-sided":
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    elif alternative == "less":
    elif alternative == "less":
    p_value = stats.norm.cdf(z_score)
    p_value = stats.norm.cdf(z_score)
    else:  # alternative == "greater"
    else:  # alternative == "greater"
    p_value = 1 - stats.norm.cdf(z_score)
    p_value = 1 - stats.norm.cdf(z_score)


    result = {
    result = {
    "z_score": z_score,
    "z_score": z_score,
    "p_value": p_value,
    "p_value": p_value,
    "proportion1": proportion1,
    "proportion1": proportion1,
    "proportion2": value,
    "proportion2": value,
    "difference": proportion1 - value,
    "difference": proportion1 - value,
    "standard_error": se,
    "standard_error": se,
    "test_type": "one-sample",
    "test_type": "one-sample",
    }
    }


    else:
    else:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Either (count2, nobs2) or value must be provided"
    "Either (count2, nobs2) or value must be provided"
    )
    )


    # Add common fields
    # Add common fields
    result.update(
    result.update(
    {
    {
    "is_significant": result["p_value"] < self.default_alpha,
    "is_significant": result["p_value"] < self.default_alpha,
    "test_name": "z_test_proportions",
    "test_name": "z_test_proportions",
    "alternative": alternative,
    "alternative": alternative,
    "alpha": self.default_alpha,
    "alpha": self.default_alpha,
    "count1": count1,
    "count1": count1,
    "nobs1": nobs1,
    "nobs1": nobs1,
    }
    }
    )
    )


    # Add count2 and nobs2 if provided
    # Add count2 and nobs2 if provided
    if count2 is not None and nobs2 is not None:
    if count2 is not None and nobs2 is not None:
    result.update({"count2": count2, "nobs2": nobs2})
    result.update({"count2": count2, "nobs2": nobs2})


    return result
    return result


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Confidence Intervals
    # Confidence Intervals
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------


    def confidence_interval_mean(
    def confidence_interval_mean(
    self, data: Union[List[float], np.ndarray], confidence_level: float = 0.95
    self, data: Union[List[float], np.ndarray], confidence_level: float = 0.95
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate confidence interval for the mean of a dataset.
    Calculate confidence interval for the mean of a dataset.


    Args:
    Args:
    data: Numeric data
    data: Numeric data
    confidence_level: Confidence level (default: 0.95)
    confidence_level: Confidence level (default: 0.95)


    Returns:
    Returns:
    Dictionary with confidence interval information including:
    Dictionary with confidence interval information including:
    - mean: Sample mean
    - mean: Sample mean
    - lower_bound: Lower bound of the confidence interval
    - lower_bound: Lower bound of the confidence interval
    - upper_bound: Upper bound of the confidence interval
    - upper_bound: Upper bound of the confidence interval
    - confidence_level: Confidence level
    - confidence_level: Confidence level
    - standard_error: Standard error of the mean
    - standard_error: Standard error of the mean
    - margin_of_error: Margin of error
    - margin_of_error: Margin of error
    - degrees_of_freedom: Degrees of freedom
    - degrees_of_freedom: Degrees of freedom


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    InsufficientDataError: If there is not enough data
    InsufficientDataError: If there is not enough data
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(data, (list, np.ndarray), min_length=1)
    self.validate_data(data, (list, np.ndarray), min_length=1)
    self.validate_data(confidence_level, float, min_value=0.0, max_value=1.0)
    self.validate_data(confidence_level, float, min_value=0.0, max_value=1.0)


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    data_array = np.array(data)
    data_array = np.array(data)


    # Check for sufficient data
    # Check for sufficient data
    n = len(data_array)
    n = len(data_array)
    if n < 2:
    if n < 2:
    raise InsufficientDataError(
    raise InsufficientDataError(
    "At least 2 data points are required for confidence interval calculation"
    "At least 2 data points are required for confidence interval calculation"
    )
    )


    # Calculate mean and standard deviation
    # Calculate mean and standard deviation
    mean = np.mean(data_array)
    mean = np.mean(data_array)
    std_dev = np.std(data_array, ddof=1)  # ddof=1 for sample std dev
    std_dev = np.std(data_array, ddof=1)  # ddof=1 for sample std dev


    # Calculate standard error of the mean
    # Calculate standard error of the mean
    standard_error = std_dev / math.sqrt(n)
    standard_error = std_dev / math.sqrt(n)


    # Calculate degrees of freedom
    # Calculate degrees of freedom
    degrees_of_freedom = n - 1
    degrees_of_freedom = n - 1


    # Calculate t-value for the given confidence level
    # Calculate t-value for the given confidence level
    alpha = 1 - confidence_level
    alpha = 1 - confidence_level
    t_value = stats.t.ppf(1 - alpha / 2, degrees_of_freedom)
    t_value = stats.t.ppf(1 - alpha / 2, degrees_of_freedom)


    # Calculate margin of error
    # Calculate margin of error
    margin_of_error = t_value * standard_error
    margin_of_error = t_value * standard_error


    # Calculate confidence interval
    # Calculate confidence interval
    lower_bound = mean - margin_of_error
    lower_bound = mean - margin_of_error
    upper_bound = mean + margin_of_error
    upper_bound = mean + margin_of_error


    return {
    return {
    "mean": mean,
    "mean": mean,
    "lower_bound": lower_bound,
    "lower_bound": lower_bound,
    "upper_bound": upper_bound,
    "upper_bound": upper_bound,
    "confidence_level": confidence_level,
    "confidence_level": confidence_level,
    "standard_error": standard_error,
    "standard_error": standard_error,
    "margin_of_error": margin_of_error,
    "margin_of_error": margin_of_error,
    "degrees_of_freedom": degrees_of_freedom,
    "degrees_of_freedom": degrees_of_freedom,
    "sample_size": n,
    "sample_size": n,
    "standard_deviation": std_dev,
    "standard_deviation": std_dev,
    "t_value": t_value,
    "t_value": t_value,
    }
    }


    def confidence_interval_proportion(
    def confidence_interval_proportion(
    self,
    self,
    count: int,
    count: int,
    nobs: int,
    nobs: int,
    confidence_level: float = 0.95,
    confidence_level: float = 0.95,
    method: str = "normal",
    method: str = "normal",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate confidence interval for a proportion.
    Calculate confidence interval for a proportion.


    Args:
    Args:
    count: Number of successes
    count: Number of successes
    nobs: Number of observations
    nobs: Number of observations
    confidence_level: Confidence level (default: 0.95)
    confidence_level: Confidence level (default: 0.95)
    method: Method to use for calculation:
    method: Method to use for calculation:
    "normal": Normal approximation (default)
    "normal": Normal approximation (default)
    "wilson": Wilson score interval (better for small samples)
    "wilson": Wilson score interval (better for small samples)
    "agresti-coull": Agresti-Coull interval (adjusted Wald)
    "agresti-coull": Agresti-Coull interval (adjusted Wald)
    "exact": Exact (Clopper-Pearson) interval
    "exact": Exact (Clopper-Pearson) interval


    Returns:
    Returns:
    Dictionary with confidence interval information including:
    Dictionary with confidence interval information including:
    - proportion: Sample proportion
    - proportion: Sample proportion
    - lower_bound: Lower bound of the confidence interval
    - lower_bound: Lower bound of the confidence interval
    - upper_bound: Upper bound of the confidence interval
    - upper_bound: Upper bound of the confidence interval
    - confidence_level: Confidence level
    - confidence_level: Confidence level
    - method: Method used for calculation
    - method: Method used for calculation


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(count, int, min_value=0)
    self.validate_data(count, int, min_value=0)
    self.validate_data(nobs, int, min_value=count)
    self.validate_data(nobs, int, min_value=count)
    self.validate_data(confidence_level, float, min_value=0.0, max_value=1.0)
    self.validate_data(confidence_level, float, min_value=0.0, max_value=1.0)


    if method not in ["normal", "wilson", "agresti-coull", "exact"]:
    if method not in ["normal", "wilson", "agresti-coull", "exact"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Method must be one of: 'normal', 'wilson', 'agresti-coull', 'exact'"
    "Method must be one of: 'normal', 'wilson', 'agresti-coull', 'exact'"
    )
    )


    # Calculate proportion
    # Calculate proportion
    proportion = count / nobs
    proportion = count / nobs


    # Calculate alpha
    # Calculate alpha
    alpha = 1 - confidence_level
    alpha = 1 - confidence_level


    # Calculate z-value for the given confidence level
    # Calculate z-value for the given confidence level
    z_value = stats.norm.ppf(1 - alpha / 2)
    z_value = stats.norm.ppf(1 - alpha / 2)


    # Calculate confidence interval based on the specified method
    # Calculate confidence interval based on the specified method
    if method == "normal":
    if method == "normal":
    # Check if normal approximation is valid
    # Check if normal approximation is valid
    if nobs * proportion < 5 or nobs * (1 - proportion) < 5:
    if nobs * proportion < 5 or nobs * (1 - proportion) < 5:
    self.logger.warning(
    self.logger.warning(
    "Normal approximation may not be valid due to small expected counts"
    "Normal approximation may not be valid due to small expected counts"
    )
    )


    # Calculate standard error
    # Calculate standard error
    standard_error = math.sqrt(proportion * (1 - proportion) / nobs)
    standard_error = math.sqrt(proportion * (1 - proportion) / nobs)


    # Calculate margin of error
    # Calculate margin of error
    margin_of_error = z_value * standard_error
    margin_of_error = z_value * standard_error


    # Calculate confidence interval
    # Calculate confidence interval
    lower_bound = max(0.0, proportion - margin_of_error)
    lower_bound = max(0.0, proportion - margin_of_error)
    upper_bound = min(1.0, proportion + margin_of_error)
    upper_bound = min(1.0, proportion + margin_of_error)


    result = {
    result = {
    "standard_error": standard_error,
    "standard_error": standard_error,
    "margin_of_error": margin_of_error,
    "margin_of_error": margin_of_error,
    }
    }


    elif method == "wilson":
    elif method == "wilson":
    # Wilson score interval (better for small samples)
    # Wilson score interval (better for small samples)
    denominator = 1 + z_value**2 / nobs
    denominator = 1 + z_value**2 / nobs
    center = (proportion + z_value**2 / (2 * nobs)) / denominator
    center = (proportion + z_value**2 / (2 * nobs)) / denominator
    margin = (
    margin = (
    z_value
    z_value
    * math.sqrt(
    * math.sqrt(
    proportion * (1 - proportion) / nobs + z_value**2 / (4 * nobs**2)
    proportion * (1 - proportion) / nobs + z_value**2 / (4 * nobs**2)
    )
    )
    / denominator
    / denominator
    )
    )


    lower_bound = max(0.0, center - margin)
    lower_bound = max(0.0, center - margin)
    upper_bound = min(1.0, center + margin)
    upper_bound = min(1.0, center + margin)


    result = {"center": center, "margin": margin}
    result = {"center": center, "margin": margin}


    elif method == "agresti-coull":
    elif method == "agresti-coull":
    # Agresti-Coull interval (adjusted Wald)
    # Agresti-Coull interval (adjusted Wald)
    n_tilde = nobs + z_value**2
    n_tilde = nobs + z_value**2
    p_tilde = (count + z_value**2 / 2) / n_tilde
    p_tilde = (count + z_value**2 / 2) / n_tilde


    # Calculate standard error
    # Calculate standard error
    standard_error = math.sqrt(p_tilde * (1 - p_tilde) / n_tilde)
    standard_error = math.sqrt(p_tilde * (1 - p_tilde) / n_tilde)


    # Calculate margin of error
    # Calculate margin of error
    margin_of_error = z_value * standard_error
    margin_of_error = z_value * standard_error


    # Calculate confidence interval
    # Calculate confidence interval
    lower_bound = max(0.0, p_tilde - margin_of_error)
    lower_bound = max(0.0, p_tilde - margin_of_error)
    upper_bound = min(1.0, p_tilde + margin_of_error)
    upper_bound = min(1.0, p_tilde + margin_of_error)


    result = {
    result = {
    "adjusted_proportion": p_tilde,
    "adjusted_proportion": p_tilde,
    "adjusted_sample_size": n_tilde,
    "adjusted_sample_size": n_tilde,
    "standard_error": standard_error,
    "standard_error": standard_error,
    "margin_of_error": margin_of_error,
    "margin_of_error": margin_of_error,
    }
    }


    else:  # method == "exact"
    else:  # method == "exact"
    # Exact (Clopper-Pearson) interval
    # Exact (Clopper-Pearson) interval
    lower_bound = (
    lower_bound = (
    stats.beta.ppf(alpha / 2, count, nobs - count + 1) if count > 0 else 0.0
    stats.beta.ppf(alpha / 2, count, nobs - count + 1) if count > 0 else 0.0
    )
    )
    upper_bound = (
    upper_bound = (
    stats.beta.ppf(1 - alpha / 2, count + 1, nobs - count)
    stats.beta.ppf(1 - alpha / 2, count + 1, nobs - count)
    if count < nobs
    if count < nobs
    else 1.0
    else 1.0
    )
    )


    result = {}
    result = {}


    # Add common fields
    # Add common fields
    result.update(
    result.update(
    {
    {
    "proportion": proportion,
    "proportion": proportion,
    "lower_bound": lower_bound,
    "lower_bound": lower_bound,
    "upper_bound": upper_bound,
    "upper_bound": upper_bound,
    "confidence_level": confidence_level,
    "confidence_level": confidence_level,
    "method": method,
    "method": method,
    "count": count,
    "count": count,
    "nobs": nobs,
    "nobs": nobs,
    "z_value": z_value,
    "z_value": z_value,
    }
    }
    )
    )


    return result
    return result


    def confidence_interval_difference_proportions(
    def confidence_interval_difference_proportions(
    self,
    self,
    count1: int,
    count1: int,
    nobs1: int,
    nobs1: int,
    count2: int,
    count2: int,
    nobs2: int,
    nobs2: int,
    confidence_level: float = 0.95,
    confidence_level: float = 0.95,
    method: str = "normal",
    method: str = "normal",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate confidence interval for the difference between two proportions.
    Calculate confidence interval for the difference between two proportions.


    Args:
    Args:
    count1: Number of successes in first sample
    count1: Number of successes in first sample
    nobs1: Number of observations in first sample
    nobs1: Number of observations in first sample
    count2: Number of successes in second sample
    count2: Number of successes in second sample
    nobs2: Number of observations in second sample
    nobs2: Number of observations in second sample
    confidence_level: Confidence level (default: 0.95)
    confidence_level: Confidence level (default: 0.95)
    method: Method to use for calculation:
    method: Method to use for calculation:
    "normal": Normal approximation (default)
    "normal": Normal approximation (default)
    "agresti-caffo": Agresti-Caffo interval (better for small samples)
    "agresti-caffo": Agresti-Caffo interval (better for small samples)


    Returns:
    Returns:
    Dictionary with confidence interval information including:
    Dictionary with confidence interval information including:
    - proportion1: First sample proportion
    - proportion1: First sample proportion
    - proportion2: Second sample proportion
    - proportion2: Second sample proportion
    - difference: Difference between proportions (proportion1 - proportion2)
    - difference: Difference between proportions (proportion1 - proportion2)
    - lower_bound: Lower bound of the confidence interval
    - lower_bound: Lower bound of the confidence interval
    - upper_bound: Upper bound of the confidence interval
    - upper_bound: Upper bound of the confidence interval
    - confidence_level: Confidence level
    - confidence_level: Confidence level
    - method: Method used for calculation
    - method: Method used for calculation


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(count1, int, min_value=0)
    self.validate_data(count1, int, min_value=0)
    self.validate_data(nobs1, int, min_value=count1)
    self.validate_data(nobs1, int, min_value=count1)
    self.validate_data(count2, int, min_value=0)
    self.validate_data(count2, int, min_value=0)
    self.validate_data(nobs2, int, min_value=count2)
    self.validate_data(nobs2, int, min_value=count2)
    self.validate_data(confidence_level, float, min_value=0.0, max_value=1.0)
    self.validate_data(confidence_level, float, min_value=0.0, max_value=1.0)


    if method not in ["normal", "agresti-caffo"]:
    if method not in ["normal", "agresti-caffo"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Method must be one of: 'normal', 'agresti-caffo'"
    "Method must be one of: 'normal', 'agresti-caffo'"
    )
    )


    # Calculate proportions
    # Calculate proportions
    proportion1 = count1 / nobs1
    proportion1 = count1 / nobs1
    proportion2 = count2 / nobs2
    proportion2 = count2 / nobs2
    difference = proportion1 - proportion2
    difference = proportion1 - proportion2


    # Calculate alpha
    # Calculate alpha
    alpha = 1 - confidence_level
    alpha = 1 - confidence_level


    # Calculate z-value for the given confidence level
    # Calculate z-value for the given confidence level
    z_value = stats.norm.ppf(1 - alpha / 2)
    z_value = stats.norm.ppf(1 - alpha / 2)


    # Calculate confidence interval based on the specified method
    # Calculate confidence interval based on the specified method
    if method == "normal":
    if method == "normal":
    # Check if normal approximation is valid
    # Check if normal approximation is valid
    if (
    if (
    nobs1 * proportion1 < 5
    nobs1 * proportion1 < 5
    or nobs1 * (1 - proportion1) < 5
    or nobs1 * (1 - proportion1) < 5
    or nobs2 * proportion2 < 5
    or nobs2 * proportion2 < 5
    or nobs2 * (1 - proportion2) < 5
    or nobs2 * (1 - proportion2) < 5
    ):
    ):
    self.logger.warning(
    self.logger.warning(
    "Normal approximation may not be valid due to small expected counts"
    "Normal approximation may not be valid due to small expected counts"
    )
    )


    # Calculate standard error
    # Calculate standard error
    standard_error = math.sqrt(
    standard_error = math.sqrt(
    proportion1 * (1 - proportion1) / nobs1
    proportion1 * (1 - proportion1) / nobs1
    + proportion2 * (1 - proportion2) / nobs2
    + proportion2 * (1 - proportion2) / nobs2
    )
    )


    # Calculate margin of error
    # Calculate margin of error
    margin_of_error = z_value * standard_error
    margin_of_error = z_value * standard_error


    # Calculate confidence interval
    # Calculate confidence interval
    lower_bound = difference - margin_of_error
    lower_bound = difference - margin_of_error
    upper_bound = difference + margin_of_error
    upper_bound = difference + margin_of_error


    result = {
    result = {
    "standard_error": standard_error,
    "standard_error": standard_error,
    "margin_of_error": margin_of_error,
    "margin_of_error": margin_of_error,
    }
    }


    else:  # method == "agresti-caffo"
    else:  # method == "agresti-caffo"
    # Agresti-Caffo interval (better for small samples)
    # Agresti-Caffo interval (better for small samples)
    # Add 1 to each cell of the 2x2 table
    # Add 1 to each cell of the 2x2 table
    adjusted_count1 = count1 + 1
    adjusted_count1 = count1 + 1
    adjusted_nobs1 = nobs1 + 2
    adjusted_nobs1 = nobs1 + 2
    adjusted_count2 = count2 + 1
    adjusted_count2 = count2 + 1
    adjusted_nobs2 = nobs2 + 2
    adjusted_nobs2 = nobs2 + 2


    # Calculate adjusted proportions
    # Calculate adjusted proportions
    adjusted_proportion1 = adjusted_count1 / adjusted_nobs1
    adjusted_proportion1 = adjusted_count1 / adjusted_nobs1
    adjusted_proportion2 = adjusted_count2 / adjusted_nobs2
    adjusted_proportion2 = adjusted_count2 / adjusted_nobs2
    adjusted_difference = adjusted_proportion1 - adjusted_proportion2
    adjusted_difference = adjusted_proportion1 - adjusted_proportion2


    # Calculate standard error
    # Calculate standard error
    standard_error = math.sqrt(
    standard_error = math.sqrt(
    adjusted_proportion1 * (1 - adjusted_proportion1) / adjusted_nobs1
    adjusted_proportion1 * (1 - adjusted_proportion1) / adjusted_nobs1
    + adjusted_proportion2 * (1 - adjusted_proportion2) / adjusted_nobs2
    + adjusted_proportion2 * (1 - adjusted_proportion2) / adjusted_nobs2
    )
    )


    # Calculate margin of error
    # Calculate margin of error
    margin_of_error = z_value * standard_error
    margin_of_error = z_value * standard_error


    # Calculate confidence interval
    # Calculate confidence interval
    lower_bound = adjusted_difference - margin_of_error
    lower_bound = adjusted_difference - margin_of_error
    upper_bound = adjusted_difference + margin_of_error
    upper_bound = adjusted_difference + margin_of_error


    result = {
    result = {
    "adjusted_proportion1": adjusted_proportion1,
    "adjusted_proportion1": adjusted_proportion1,
    "adjusted_proportion2": adjusted_proportion2,
    "adjusted_proportion2": adjusted_proportion2,
    "adjusted_difference": adjusted_difference,
    "adjusted_difference": adjusted_difference,
    "standard_error": standard_error,
    "standard_error": standard_error,
    "margin_of_error": margin_of_error,
    "margin_of_error": margin_of_error,
    }
    }


    # Add common fields
    # Add common fields
    result.update(
    result.update(
    {
    {
    "proportion1": proportion1,
    "proportion1": proportion1,
    "proportion2": proportion2,
    "proportion2": proportion2,
    "difference": difference,
    "difference": difference,
    "lower_bound": lower_bound,
    "lower_bound": lower_bound,
    "upper_bound": upper_bound,
    "upper_bound": upper_bound,
    "confidence_level": confidence_level,
    "confidence_level": confidence_level,
    "method": method,
    "method": method,
    "count1": count1,
    "count1": count1,
    "nobs1": nobs1,
    "nobs1": nobs1,
    "count2": count2,
    "count2": count2,
    "nobs2": nobs2,
    "nobs2": nobs2,
    "z_value": z_value,
    "z_value": z_value,
    }
    }
    )
    )


    return result
    return result


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Effect Size Calculations
    # Effect Size Calculations
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------


    def cohens_d(
    def cohens_d(
    self,
    self,
    group1: Union[List[float], np.ndarray],
    group1: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray],
    group2: Union[List[float], np.ndarray],
    correction: bool = False,
    correction: bool = False,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate Cohen's d effect size for the difference between two groups.
    Calculate Cohen's d effect size for the difference between two groups.


    Cohen's d measures the standardized difference between two means,
    Cohen's d measures the standardized difference between two means,
    expressed in standard deviation units.
    expressed in standard deviation units.


    Args:
    Args:
    group1: First group data
    group1: First group data
    group2: Second group data
    group2: Second group data
    correction: Whether to apply Hedges' correction for small samples
    correction: Whether to apply Hedges' correction for small samples


    Returns:
    Returns:
    Dictionary with effect size information including:
    Dictionary with effect size information including:
    - effect_size: Cohen's d value
    - effect_size: Cohen's d value
    - interpretation: Qualitative interpretation of the effect size
    - interpretation: Qualitative interpretation of the effect size
    - mean1: Mean of first group
    - mean1: Mean of first group
    - mean2: Mean of second group
    - mean2: Mean of second group
    - std1: Standard deviation of first group
    - std1: Standard deviation of first group
    - std2: Standard deviation of second group
    - std2: Standard deviation of second group
    - pooled_std: Pooled standard deviation
    - pooled_std: Pooled standard deviation
    - n1: Size of first group
    - n1: Size of first group
    - n2: Size of second group
    - n2: Size of second group


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    InsufficientDataError: If there is not enough data
    InsufficientDataError: If there is not enough data
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(group1, (list, np.ndarray), min_length=1)
    self.validate_data(group1, (list, np.ndarray), min_length=1)
    self.validate_data(group2, (list, np.ndarray), min_length=1)
    self.validate_data(group2, (list, np.ndarray), min_length=1)


    # Convert to numpy arrays for consistent handling
    # Convert to numpy arrays for consistent handling
    group1_array = np.array(group1)
    group1_array = np.array(group1)
    group2_array = np.array(group2)
    group2_array = np.array(group2)


    # Check for sufficient data
    # Check for sufficient data
    n1 = len(group1_array)
    n1 = len(group1_array)
    n2 = len(group2_array)
    n2 = len(group2_array)


    if n1 < 2 or n2 < 2:
    if n1 < 2 or n2 < 2:
    raise InsufficientDataError(
    raise InsufficientDataError(
    "Each group must have at least 2 data points for effect size calculation"
    "Each group must have at least 2 data points for effect size calculation"
    )
    )


    # Calculate means and standard deviations
    # Calculate means and standard deviations
    mean1 = np.mean(group1_array)
    mean1 = np.mean(group1_array)
    mean2 = np.mean(group2_array)
    mean2 = np.mean(group2_array)
    std1 = np.std(group1_array, ddof=1)  # ddof=1 for sample std dev
    std1 = np.std(group1_array, ddof=1)  # ddof=1 for sample std dev
    std2 = np.std(group2_array, ddof=1)
    std2 = np.std(group2_array, ddof=1)


    # Calculate pooled standard deviation
    # Calculate pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
    pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))


    # Calculate Cohen's d
    # Calculate Cohen's d
    d = (mean1 - mean2) / pooled_std
    d = (mean1 - mean2) / pooled_std


    # Apply Hedges' correction for small samples if requested
    # Apply Hedges' correction for small samples if requested
    if correction:
    if correction:
    # Hedges' g correction factor
    # Hedges' g correction factor
    correction_factor = 1 - (3 / (4 * (n1 + n2 - 2) - 1))
    correction_factor = 1 - (3 / (4 * (n1 + n2 - 2) - 1))
    d = d * correction_factor
    d = d * correction_factor


    # Interpret effect size
    # Interpret effect size
    if abs(d) < 0.2:
    if abs(d) < 0.2:
    interpretation = "negligible"
    interpretation = "negligible"
    elif abs(d) < 0.5:
    elif abs(d) < 0.5:
    interpretation = "small"
    interpretation = "small"
    elif abs(d) < 0.8:
    elif abs(d) < 0.8:
    interpretation = "medium"
    interpretation = "medium"
    else:
    else:
    interpretation = "large"
    interpretation = "large"


    return {
    return {
    "effect_size": d,
    "effect_size": d,
    "interpretation": interpretation,
    "interpretation": interpretation,
    "mean1": mean1,
    "mean1": mean1,
    "mean2": mean2,
    "mean2": mean2,
    "std1": std1,
    "std1": std1,
    "std2": std2,
    "std2": std2,
    "pooled_std": pooled_std,
    "pooled_std": pooled_std,
    "n1": n1,
    "n1": n1,
    "n2": n2,
    "n2": n2,
    "correction_applied": correction,
    "correction_applied": correction,
    }
    }


    def odds_ratio(
    def odds_ratio(
    self, table: Union[List[List[int]], np.ndarray], ci_level: float = 0.95
    self, table: Union[List[List[int]], np.ndarray], ci_level: float = 0.95
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate odds ratio for a 2x2 contingency table.
    Calculate odds ratio for a 2x2 contingency table.


    The odds ratio is a measure of association between exposure and outcome.
    The odds ratio is a measure of association between exposure and outcome.


    Args:
    Args:
    table: 2x2 contingency table as [[a, b], [c, d]] where:
    table: 2x2 contingency table as [[a, b], [c, d]] where:
    a = exposed cases, b = exposed non-cases
    a = exposed cases, b = exposed non-cases
    c = unexposed cases, d = unexposed non-cases
    c = unexposed cases, d = unexposed non-cases
    ci_level: Confidence level for confidence interval
    ci_level: Confidence level for confidence interval


    Returns:
    Returns:
    Dictionary with effect size information including:
    Dictionary with effect size information including:
    - odds_ratio: Odds ratio value
    - odds_ratio: Odds ratio value
    - log_odds_ratio: Natural logarithm of the odds ratio
    - log_odds_ratio: Natural logarithm of the odds ratio
    - se_log_odds_ratio: Standard error of the log odds ratio
    - se_log_odds_ratio: Standard error of the log odds ratio
    - ci_lower: Lower bound of the confidence interval
    - ci_lower: Lower bound of the confidence interval
    - ci_upper: Upper bound of the confidence interval
    - ci_upper: Upper bound of the confidence interval
    - interpretation: Qualitative interpretation of the odds ratio
    - interpretation: Qualitative interpretation of the odds ratio


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    if isinstance(table, list):
    if isinstance(table, list):
    table = np.array(table)
    table = np.array(table)


    self.validate_data(table, np.ndarray, min_length=1)
    self.validate_data(table, np.ndarray, min_length=1)
    self.validate_data(ci_level, float, min_value=0.0, max_value=1.0)
    self.validate_data(ci_level, float, min_value=0.0, max_value=1.0)


    if table.shape != (2, 2):
    if table.shape != (2, 2):
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Odds ratio calculation requires a 2x2 contingency table"
    "Odds ratio calculation requires a 2x2 contingency table"
    )
    )


    # Extract values from the table
    # Extract values from the table
    a, b = table[0]
    a, b = table[0]
    c, d = table[1]
    c, d = table[1]


    # Check for zero cells
    # Check for zero cells
    if b == 0 or c == 0:
    if b == 0 or c == 0:
    # Apply Haldane correction (add 0.5 to all cells)
    # Apply Haldane correction (add 0.5 to all cells)
    self.logger.warning(
    self.logger.warning(
    "Zero cell detected, applying Haldane correction (adding 0.5 to all cells)"
    "Zero cell detected, applying Haldane correction (adding 0.5 to all cells)"
    )
    )
    a += 0.5
    a += 0.5
    b += 0.5
    b += 0.5
    c += 0.5
    c += 0.5
    d += 0.5
    d += 0.5


    # Calculate odds ratio
    # Calculate odds ratio
    or_value = (a * d) / (b * c)
    or_value = (a * d) / (b * c)


    # Calculate log odds ratio and its standard error
    # Calculate log odds ratio and its standard error
    log_or = np.log(or_value)
    log_or = np.log(or_value)
    se_log_or = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    se_log_or = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)


    # Calculate confidence interval
    # Calculate confidence interval
    z_value = stats.norm.ppf(1 - (1 - ci_level) / 2)
    z_value = stats.norm.ppf(1 - (1 - ci_level) / 2)
    ci_lower = np.exp(log_or - z_value * se_log_or)
    ci_lower = np.exp(log_or - z_value * se_log_or)
    ci_upper = np.exp(log_or + z_value * se_log_or)
    ci_upper = np.exp(log_or + z_value * se_log_or)


    # Interpret odds ratio
    # Interpret odds ratio
    if or_value < 1:
    if or_value < 1:
    interpretation = "negative association"
    interpretation = "negative association"
    elif or_value > 1:
    elif or_value > 1:
    interpretation = "positive association"
    interpretation = "positive association"
    else:
    else:
    interpretation = "no association"
    interpretation = "no association"


    # Add strength of association
    # Add strength of association
    if abs(np.log(or_value)) < np.log(1.5):
    if abs(np.log(or_value)) < np.log(1.5):
    interpretation += " (weak)"
    interpretation += " (weak)"
    elif abs(np.log(or_value)) < np.log(3.5):
    elif abs(np.log(or_value)) < np.log(3.5):
    interpretation += " (moderate)"
    interpretation += " (moderate)"
    else:
    else:
    interpretation += " (strong)"
    interpretation += " (strong)"


    return {
    return {
    "odds_ratio": or_value,
    "odds_ratio": or_value,
    "log_odds_ratio": log_or,
    "log_odds_ratio": log_or,
    "se_log_odds_ratio": se_log_or,
    "se_log_odds_ratio": se_log_or,
    "ci_lower": ci_lower,
    "ci_lower": ci_lower,
    "ci_upper": ci_upper,
    "ci_upper": ci_upper,
    "ci_level": ci_level,
    "ci_level": ci_level,
    "interpretation": interpretation,
    "interpretation": interpretation,
    "table": table.tolist() if isinstance(table, np.ndarray) else table,
    "table": table.tolist() if isinstance(table, np.ndarray) else table,
    }
    }


    def relative_risk(
    def relative_risk(
    self, table: Union[List[List[int]], np.ndarray], ci_level: float = 0.95
    self, table: Union[List[List[int]], np.ndarray], ci_level: float = 0.95
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate relative risk (risk ratio) for a 2x2 contingency table.
    Calculate relative risk (risk ratio) for a 2x2 contingency table.


    The relative risk is the ratio of the probability of an outcome in an
    The relative risk is the ratio of the probability of an outcome in an
    exposed group to the probability of an outcome in an unexposed group.
    exposed group to the probability of an outcome in an unexposed group.


    Args:
    Args:
    table: 2x2 contingency table as [[a, b], [c, d]] where:
    table: 2x2 contingency table as [[a, b], [c, d]] where:
    a = exposed cases, b = exposed non-cases
    a = exposed cases, b = exposed non-cases
    c = unexposed cases, d = unexposed non-cases
    c = unexposed cases, d = unexposed non-cases
    ci_level: Confidence level for confidence interval
    ci_level: Confidence level for confidence interval


    Returns:
    Returns:
    Dictionary with effect size information including:
    Dictionary with effect size information including:
    - relative_risk: Relative risk value
    - relative_risk: Relative risk value
    - log_relative_risk: Natural logarithm of the relative risk
    - log_relative_risk: Natural logarithm of the relative risk
    - se_log_relative_risk: Standard error of the log relative risk
    - se_log_relative_risk: Standard error of the log relative risk
    - ci_lower: Lower bound of the confidence interval
    - ci_lower: Lower bound of the confidence interval
    - ci_upper: Upper bound of the confidence interval
    - ci_upper: Upper bound of the confidence interval
    - interpretation: Qualitative interpretation of the relative risk
    - interpretation: Qualitative interpretation of the relative risk


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    if isinstance(table, list):
    if isinstance(table, list):
    table = np.array(table)
    table = np.array(table)


    self.validate_data(table, np.ndarray, min_length=1)
    self.validate_data(table, np.ndarray, min_length=1)
    self.validate_data(ci_level, float, min_value=0.0, max_value=1.0)
    self.validate_data(ci_level, float, min_value=0.0, max_value=1.0)


    if table.shape != (2, 2):
    if table.shape != (2, 2):
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Relative risk calculation requires a 2x2 contingency table"
    "Relative risk calculation requires a 2x2 contingency table"
    )
    )


    # Extract values from the table
    # Extract values from the table
    a, b = table[0]
    a, b = table[0]
    c, d = table[1]
    c, d = table[1]


    # Calculate risk in exposed and unexposed groups
    # Calculate risk in exposed and unexposed groups
    if a + b == 0:
    if a + b == 0:
    raise InvalidParameterError("No exposed subjects in the table")
    raise InvalidParameterError("No exposed subjects in the table")
    if c + d == 0:
    if c + d == 0:
    raise InvalidParameterError("No unexposed subjects in the table")
    raise InvalidParameterError("No unexposed subjects in the table")


    risk_exposed = a / (a + b)
    risk_exposed = a / (a + b)
    risk_unexposed = c / (c + d)
    risk_unexposed = c / (c + d)


    # Check for zero risk
    # Check for zero risk
    if risk_unexposed == 0:
    if risk_unexposed == 0:
    # Apply correction
    # Apply correction
    self.logger.warning("Zero risk in unexposed group, applying correction")
    self.logger.warning("Zero risk in unexposed group, applying correction")
    c += 0.5
    c += 0.5
    d += 0.5
    d += 0.5
    risk_unexposed = c / (c + d)
    risk_unexposed = c / (c + d)


    # Calculate relative risk
    # Calculate relative risk
    rr_value = risk_exposed / risk_unexposed
    rr_value = risk_exposed / risk_unexposed


    # Calculate log relative risk and its standard error
    # Calculate log relative risk and its standard error
    log_rr = np.log(rr_value)
    log_rr = np.log(rr_value)
    se_log_rr = np.sqrt((b / (a * (a + b))) + (d / (c * (c + d))))
    se_log_rr = np.sqrt((b / (a * (a + b))) + (d / (c * (c + d))))


    # Calculate confidence interval
    # Calculate confidence interval
    z_value = stats.norm.ppf(1 - (1 - ci_level) / 2)
    z_value = stats.norm.ppf(1 - (1 - ci_level) / 2)
    ci_lower = np.exp(log_rr - z_value * se_log_rr)
    ci_lower = np.exp(log_rr - z_value * se_log_rr)
    ci_upper = np.exp(log_rr + z_value * se_log_rr)
    ci_upper = np.exp(log_rr + z_value * se_log_rr)


    # Interpret relative risk
    # Interpret relative risk
    if rr_value < 1:
    if rr_value < 1:
    interpretation = "protective effect"
    interpretation = "protective effect"
    elif rr_value > 1:
    elif rr_value > 1:
    interpretation = "increased risk"
    interpretation = "increased risk"
    else:
    else:
    interpretation = "no effect"
    interpretation = "no effect"


    # Add strength of effect
    # Add strength of effect
    if abs(np.log(rr_value)) < np.log(1.5):
    if abs(np.log(rr_value)) < np.log(1.5):
    interpretation += " (weak)"
    interpretation += " (weak)"
    elif abs(np.log(rr_value)) < np.log(3):
    elif abs(np.log(rr_value)) < np.log(3):
    interpretation += " (moderate)"
    interpretation += " (moderate)"
    else:
    else:
    interpretation += " (strong)"
    interpretation += " (strong)"


    return {
    return {
    "relative_risk": rr_value,
    "relative_risk": rr_value,
    "log_relative_risk": log_rr,
    "log_relative_risk": log_rr,
    "se_log_relative_risk": se_log_rr,
    "se_log_relative_risk": se_log_rr,
    "ci_lower": ci_lower,
    "ci_lower": ci_lower,
    "ci_upper": ci_upper,
    "ci_upper": ci_upper,
    "ci_level": ci_level,
    "ci_level": ci_level,
    "risk_exposed": risk_exposed,
    "risk_exposed": risk_exposed,
    "risk_unexposed": risk_unexposed,
    "risk_unexposed": risk_unexposed,
    "interpretation": interpretation,
    "interpretation": interpretation,
    "table": table.tolist() if isinstance(table, np.ndarray) else table,
    "table": table.tolist() if isinstance(table, np.ndarray) else table,
    }
    }


    def number_needed_to_treat(
    def number_needed_to_treat(
    self, table: Union[List[List[int]], np.ndarray], ci_level: float = 0.95
    self, table: Union[List[List[int]], np.ndarray], ci_level: float = 0.95
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate Number Needed to Treat (NNT) for a 2x2 contingency table.
    Calculate Number Needed to Treat (NNT) for a 2x2 contingency table.


    NNT is the average number of patients who need to be treated to
    NNT is the average number of patients who need to be treated to
    prevent one additional bad outcome.
    prevent one additional bad outcome.


    Args:
    Args:
    table: 2x2 contingency table as [[a, b], [c, d]] where:
    table: 2x2 contingency table as [[a, b], [c, d]] where:
    a = treatment cases, b = treatment non-cases
    a = treatment cases, b = treatment non-cases
    c = control cases, d = control non-cases
    c = control cases, d = control non-cases
    ci_level: Confidence level for confidence interval
    ci_level: Confidence level for confidence interval


    Returns:
    Returns:
    Dictionary with effect size information including:
    Dictionary with effect size information including:
    - nnt: Number Needed to Treat
    - nnt: Number Needed to Treat
    - arr: Absolute Risk Reduction
    - arr: Absolute Risk Reduction
    - ci_lower: Lower bound of the confidence interval
    - ci_lower: Lower bound of the confidence interval
    - ci_upper: Upper bound of the confidence interval
    - ci_upper: Upper bound of the confidence interval
    - interpretation: Qualitative interpretation of the NNT
    - interpretation: Qualitative interpretation of the NNT


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    if isinstance(table, list):
    if isinstance(table, list):
    table = np.array(table)
    table = np.array(table)


    self.validate_data(table, np.ndarray, min_length=1)
    self.validate_data(table, np.ndarray, min_length=1)
    self.validate_data(ci_level, float, min_value=0.0, max_value=1.0)
    self.validate_data(ci_level, float, min_value=0.0, max_value=1.0)


    if table.shape != (2, 2):
    if table.shape != (2, 2):
    raise InvalidParameterError(
    raise InvalidParameterError(
    "NNT calculation requires a 2x2 contingency table"
    "NNT calculation requires a 2x2 contingency table"
    )
    )


    # Extract values from the table
    # Extract values from the table
    a, b = table[0]  # treatment group
    a, b = table[0]  # treatment group
    c, d = table[1]  # control group
    c, d = table[1]  # control group


    # Calculate risk in treatment and control groups
    # Calculate risk in treatment and control groups
    if a + b == 0:
    if a + b == 0:
    raise InvalidParameterError("No subjects in the treatment group")
    raise InvalidParameterError("No subjects in the treatment group")
    if c + d == 0:
    if c + d == 0:
    raise InvalidParameterError("No subjects in the control group")
    raise InvalidParameterError("No subjects in the control group")


    risk_treatment = a / (a + b)
    risk_treatment = a / (a + b)
    risk_control = c / (c + d)
    risk_control = c / (c + d)


    # Calculate Absolute Risk Reduction (ARR)
    # Calculate Absolute Risk Reduction (ARR)
    arr = risk_control - risk_treatment
    arr = risk_control - risk_treatment


    # Calculate NNT
    # Calculate NNT
    if arr == 0:
    if arr == 0:
    nnt = float("in")
    nnt = float("in")
    ci_lower = float("in")
    ci_lower = float("in")
    ci_upper = float("in")
    ci_upper = float("in")
    interpretation = "no effect (infinite NNT)"
    interpretation = "no effect (infinite NNT)"
    else:
    else:
    nnt = 1 / abs(arr)
    nnt = 1 / abs(arr)


    # Calculate confidence interval for ARR
    # Calculate confidence interval for ARR
    se_arr = np.sqrt(
    se_arr = np.sqrt(
    (risk_treatment * (1 - risk_treatment) / (a + b))
    (risk_treatment * (1 - risk_treatment) / (a + b))
    + (risk_control * (1 - risk_control) / (c + d))
    + (risk_control * (1 - risk_control) / (c + d))
    )
    )


    z_value = stats.norm.ppf(1 - (1 - ci_level) / 2)
    z_value = stats.norm.ppf(1 - (1 - ci_level) / 2)
    arr_ci_lower = arr - z_value * se_arr
    arr_ci_lower = arr - z_value * se_arr
    arr_ci_upper = arr + z_value * se_arr
    arr_ci_upper = arr + z_value * se_arr


    # Convert ARR CI to NNT CI (note: CI bounds are inverted for negative ARR)
    # Convert ARR CI to NNT CI (note: CI bounds are inverted for negative ARR)
    if arr > 0:
    if arr > 0:
    ci_lower = 1 / arr_ci_upper if arr_ci_upper > 0 else float("in")
    ci_lower = 1 / arr_ci_upper if arr_ci_upper > 0 else float("in")
    ci_upper = 1 / arr_ci_lower if arr_ci_lower > 0 else float("in")
    ci_upper = 1 / arr_ci_lower if arr_ci_lower > 0 else float("in")
    else:
    else:
    ci_lower = 1 / arr_ci_lower if arr_ci_lower < 0 else float("-in")
    ci_lower = 1 / arr_ci_lower if arr_ci_lower < 0 else float("-in")
    ci_upper = 1 / arr_ci_upper if arr_ci_upper < 0 else float("-in")
    ci_upper = 1 / arr_ci_upper if arr_ci_upper < 0 else float("-in")


    # Interpret NNT
    # Interpret NNT
    if arr > 0:
    if arr > 0:
    interpretation = f"beneficial (need to treat {int(nnt) if nnt < float('inf') else 'infinite'} patients to prevent one bad outcome)"
    interpretation = f"beneficial (need to treat {int(nnt) if nnt < float('inf') else 'infinite'} patients to prevent one bad outcome)"
    else:
    else:
    interpretation = f"harmful (treating {int(nnt) if nnt < float('inf') else 'infinite'} patients leads to one additional bad outcome)"
    interpretation = f"harmful (treating {int(nnt) if nnt < float('inf') else 'infinite'} patients leads to one additional bad outcome)"


    return {
    return {
    "nnt": nnt,
    "nnt": nnt,
    "arr": arr,
    "arr": arr,
    "risk_treatment": risk_treatment,
    "risk_treatment": risk_treatment,
    "risk_control": risk_control,
    "risk_control": risk_control,
    "ci_lower": ci_lower,
    "ci_lower": ci_lower,
    "ci_upper": ci_upper,
    "ci_upper": ci_upper,
    "ci_level": ci_level,
    "ci_level": ci_level,
    "interpretation": interpretation,
    "interpretation": interpretation,
    "table": table.tolist() if isinstance(table, np.ndarray) else table,
    "table": table.tolist() if isinstance(table, np.ndarray) else table,
    }
    }


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Power Analysis
    # Power Analysis
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------


    def sample_size_for_proportion_test(
    def sample_size_for_proportion_test(
    self,
    self,
    effect_size: float,
    effect_size: float,
    alpha: float = 0.05,
    alpha: float = 0.05,
    power: float = 0.8,
    power: float = 0.8,
    alternative: str = "two-sided",
    alternative: str = "two-sided",
    p_null: float = 0.5,
    p_null: float = 0.5,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate the required sample size for a proportion test.
    Calculate the required sample size for a proportion test.


    This method calculates the sample size needed to detect a specified effect size
    This method calculates the sample size needed to detect a specified effect size
    with the desired statistical power for a proportion test.
    with the desired statistical power for a proportion test.


    Args:
    Args:
    effect_size: Minimum detectable effect size (difference in proportions)
    effect_size: Minimum detectable effect size (difference in proportions)
    alpha: Significance level (Type I error rate, default: 0.05)
    alpha: Significance level (Type I error rate, default: 0.05)
    power: Statistical power (1 - Type II error rate, default: 0.8)
    power: Statistical power (1 - Type II error rate, default: 0.8)
    alternative: Alternative hypothesis, one of:
    alternative: Alternative hypothesis, one of:
    "two-sided" (default): two-tailed test
    "two-sided" (default): two-tailed test
    "one-sided": one-tailed test
    "one-sided": one-tailed test
    p_null: Null hypothesis proportion (default: 0.5)
    p_null: Null hypothesis proportion (default: 0.5)


    Returns:
    Returns:
    Dictionary with sample size calculation results including:
    Dictionary with sample size calculation results including:
    - sample_size: Required sample size
    - sample_size: Required sample size
    - effect_size: Specified effect size
    - effect_size: Specified effect size
    - alpha: Significance level
    - alpha: Significance level
    - power: Statistical power
    - power: Statistical power
    - alternative: Alternative hypothesis
    - alternative: Alternative hypothesis
    - p_null: Null hypothesis proportion
    - p_null: Null hypothesis proportion
    - p_alt: Alternative hypothesis proportion
    - p_alt: Alternative hypothesis proportion
    - test_type: Type of test ("proportion")
    - test_type: Type of test ("proportion")


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(effect_size, float, min_value=0.0, max_value=1.0)
    self.validate_data(effect_size, float, min_value=0.0, max_value=1.0)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(power, float, min_value=0.0, max_value=1.0)
    self.validate_data(power, float, min_value=0.0, max_value=1.0)
    self.validate_data(p_null, float, min_value=0.0, max_value=1.0)
    self.validate_data(p_null, float, min_value=0.0, max_value=1.0)


    if alternative not in ["two-sided", "one-sided"]:
    if alternative not in ["two-sided", "one-sided"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Alternative must be one of: 'two-sided', 'one-sided'"
    "Alternative must be one of: 'two-sided', 'one-sided'"
    )
    )


    # Calculate alternative proportion
    # Calculate alternative proportion
    p_alt = p_null + effect_size
    p_alt = p_null + effect_size


    # Ensure p_alt is within valid range
    # Ensure p_alt is within valid range
    if p_alt < 0 or p_alt > 1:
    if p_alt < 0 or p_alt > 1:
    raise InvalidParameterError(
    raise InvalidParameterError(
    f"Alternative proportion (p_null + effect_size = {p_alt}) must be between 0 and 1"
    f"Alternative proportion (p_null + effect_size = {p_alt}) must be between 0 and 1"
    )
    )


    # Calculate z-values for alpha and power
    # Calculate z-values for alpha and power
    z_alpha = (
    z_alpha = (
    stats.norm.ppf(1 - alpha / 2)
    stats.norm.ppf(1 - alpha / 2)
    if alternative == "two-sided"
    if alternative == "two-sided"
    else stats.norm.ppf(1 - alpha)
    else stats.norm.ppf(1 - alpha)
    )
    )
    z_beta = stats.norm.ppf(power)
    z_beta = stats.norm.ppf(power)


    # Calculate pooled proportion
    # Calculate pooled proportion
    p_pooled = (p_null + p_alt) / 2
    p_pooled = (p_null + p_alt) / 2


    # Calculate sample size
    # Calculate sample size
    numerator = (
    numerator = (
    z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled))
    z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled))
    + z_beta * math.sqrt(p_null * (1 - p_null) + p_alt * (1 - p_alt))
    + z_beta * math.sqrt(p_null * (1 - p_null) + p_alt * (1 - p_alt))
    ) ** 2
    ) ** 2
    denominator = (p_null - p_alt) ** 2
    denominator = (p_null - p_alt) ** 2


    # Calculate sample size and round up
    # Calculate sample size and round up
    sample_size = math.ceil(numerator / denominator)
    sample_size = math.ceil(numerator / denominator)


    return {
    return {
    "sample_size": sample_size,
    "sample_size": sample_size,
    "effect_size": effect_size,
    "effect_size": effect_size,
    "alpha": alpha,
    "alpha": alpha,
    "power": power,
    "power": power,
    "alternative": alternative,
    "alternative": alternative,
    "p_null": p_null,
    "p_null": p_null,
    "p_alt": p_alt,
    "p_alt": p_alt,
    "test_type": "proportion",
    "test_type": "proportion",
    }
    }


    def sample_size_for_mean_test(
    def sample_size_for_mean_test(
    self,
    self,
    effect_size: float,
    effect_size: float,
    std_dev: float,
    std_dev: float,
    alpha: float = 0.05,
    alpha: float = 0.05,
    power: float = 0.8,
    power: float = 0.8,
    alternative: str = "two-sided",
    alternative: str = "two-sided",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate the required sample size for a mean test.
    Calculate the required sample size for a mean test.


    This method calculates the sample size needed to detect a specified effect size
    This method calculates the sample size needed to detect a specified effect size
    with the desired statistical power for a mean test (t-test).
    with the desired statistical power for a mean test (t-test).


    Args:
    Args:
    effect_size: Minimum detectable effect size (difference in means)
    effect_size: Minimum detectable effect size (difference in means)
    std_dev: Standard deviation of the population
    std_dev: Standard deviation of the population
    alpha: Significance level (Type I error rate, default: 0.05)
    alpha: Significance level (Type I error rate, default: 0.05)
    power: Statistical power (1 - Type II error rate, default: 0.8)
    power: Statistical power (1 - Type II error rate, default: 0.8)
    alternative: Alternative hypothesis, one of:
    alternative: Alternative hypothesis, one of:
    "two-sided" (default): two-tailed test
    "two-sided" (default): two-tailed test
    "one-sided": one-tailed test
    "one-sided": one-tailed test


    Returns:
    Returns:
    Dictionary with sample size calculation results including:
    Dictionary with sample size calculation results including:
    - sample_size: Required sample size
    - sample_size: Required sample size
    - effect_size: Specified effect size
    - effect_size: Specified effect size
    - std_dev: Standard deviation
    - std_dev: Standard deviation
    - alpha: Significance level
    - alpha: Significance level
    - power: Statistical power
    - power: Statistical power
    - alternative: Alternative hypothesis
    - alternative: Alternative hypothesis
    - test_type: Type of test ("mean")
    - test_type: Type of test ("mean")


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(effect_size, float, min_value=0.0)
    self.validate_data(effect_size, float, min_value=0.0)
    self.validate_data(std_dev, float, min_value=0.0)
    self.validate_data(std_dev, float, min_value=0.0)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(power, float, min_value=0.0, max_value=1.0)
    self.validate_data(power, float, min_value=0.0, max_value=1.0)


    if alternative not in ["two-sided", "one-sided"]:
    if alternative not in ["two-sided", "one-sided"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Alternative must be one of: 'two-sided', 'one-sided'"
    "Alternative must be one of: 'two-sided', 'one-sided'"
    )
    )


    # Calculate standardized effect size (Cohen's d)
    # Calculate standardized effect size (Cohen's d)
    d = effect_size / std_dev
    d = effect_size / std_dev


    # Calculate z-values for alpha and power
    # Calculate z-values for alpha and power
    z_alpha = (
    z_alpha = (
    stats.norm.ppf(1 - alpha / 2)
    stats.norm.ppf(1 - alpha / 2)
    if alternative == "two-sided"
    if alternative == "two-sided"
    else stats.norm.ppf(1 - alpha)
    else stats.norm.ppf(1 - alpha)
    )
    )
    z_beta = stats.norm.ppf(power)
    z_beta = stats.norm.ppf(power)


    # Calculate sample size
    # Calculate sample size
    sample_size = math.ceil(2 * ((z_alpha + z_beta) / d) ** 2)
    sample_size = math.ceil(2 * ((z_alpha + z_beta) / d) ** 2)


    return {
    return {
    "sample_size": sample_size,
    "sample_size": sample_size,
    "effect_size": effect_size,
    "effect_size": effect_size,
    "std_dev": std_dev,
    "std_dev": std_dev,
    "standardized_effect_size": d,
    "standardized_effect_size": d,
    "alpha": alpha,
    "alpha": alpha,
    "power": power,
    "power": power,
    "alternative": alternative,
    "alternative": alternative,
    "test_type": "mean",
    "test_type": "mean",
    }
    }


    def sample_size_for_correlation(
    def sample_size_for_correlation(
    self,
    self,
    effect_size: float,
    effect_size: float,
    alpha: float = 0.05,
    alpha: float = 0.05,
    power: float = 0.8,
    power: float = 0.8,
    alternative: str = "two-sided",
    alternative: str = "two-sided",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate the required sample size for a correlation test.
    Calculate the required sample size for a correlation test.


    This method calculates the sample size needed to detect a specified correlation
    This method calculates the sample size needed to detect a specified correlation
    coefficient with the desired statistical power.
    coefficient with the desired statistical power.


    Args:
    Args:
    effect_size: Minimum detectable correlation coefficient (r)
    effect_size: Minimum detectable correlation coefficient (r)
    alpha: Significance level (Type I error rate, default: 0.05)
    alpha: Significance level (Type I error rate, default: 0.05)
    power: Statistical power (1 - Type II error rate, default: 0.8)
    power: Statistical power (1 - Type II error rate, default: 0.8)
    alternative: Alternative hypothesis, one of:
    alternative: Alternative hypothesis, one of:
    "two-sided" (default): two-tailed test
    "two-sided" (default): two-tailed test
    "one-sided": one-tailed test
    "one-sided": one-tailed test


    Returns:
    Returns:
    Dictionary with sample size calculation results including:
    Dictionary with sample size calculation results including:
    - sample_size: Required sample size
    - sample_size: Required sample size
    - effect_size: Specified effect size (correlation coefficient)
    - effect_size: Specified effect size (correlation coefficient)
    - alpha: Significance level
    - alpha: Significance level
    - power: Statistical power
    - power: Statistical power
    - alternative: Alternative hypothesis
    - alternative: Alternative hypothesis
    - test_type: Type of test ("correlation")
    - test_type: Type of test ("correlation")


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(effect_size, float, min_value=-1.0, max_value=1.0)
    self.validate_data(effect_size, float, min_value=-1.0, max_value=1.0)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(power, float, min_value=0.0, max_value=1.0)
    self.validate_data(power, float, min_value=0.0, max_value=1.0)


    if alternative not in ["two-sided", "one-sided"]:
    if alternative not in ["two-sided", "one-sided"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Alternative must be one of: 'two-sided', 'one-sided'"
    "Alternative must be one of: 'two-sided', 'one-sided'"
    )
    )


    # Use absolute value of correlation for calculation
    # Use absolute value of correlation for calculation
    r = abs(effect_size)
    r = abs(effect_size)


    # Calculate z-values for alpha and power
    # Calculate z-values for alpha and power
    z_alpha = (
    z_alpha = (
    stats.norm.ppf(1 - alpha / 2)
    stats.norm.ppf(1 - alpha / 2)
    if alternative == "two-sided"
    if alternative == "two-sided"
    else stats.norm.ppf(1 - alpha)
    else stats.norm.ppf(1 - alpha)
    )
    )
    z_beta = stats.norm.ppf(power)
    z_beta = stats.norm.ppf(power)


    # Fisher's z transformation of r
    # Fisher's z transformation of r
    z_r = 0.5 * math.log((1 + r) / (1 - r))
    z_r = 0.5 * math.log((1 + r) / (1 - r))


    # Calculate sample size
    # Calculate sample size
    sample_size = math.ceil(((z_alpha + z_beta) / z_r) ** 2 + 3)
    sample_size = math.ceil(((z_alpha + z_beta) / z_r) ** 2 + 3)


    return {
    return {
    "sample_size": sample_size,
    "sample_size": sample_size,
    "effect_size": effect_size,
    "effect_size": effect_size,
    "alpha": alpha,
    "alpha": alpha,
    "power": power,
    "power": power,
    "alternative": alternative,
    "alternative": alternative,
    "test_type": "correlation",
    "test_type": "correlation",
    }
    }


    def minimum_detectable_effect_size(
    def minimum_detectable_effect_size(
    self,
    self,
    sample_size: int,
    sample_size: int,
    alpha: float = 0.05,
    alpha: float = 0.05,
    power: float = 0.8,
    power: float = 0.8,
    test_type: str = "proportion",
    test_type: str = "proportion",
    alternative: str = "two-sided",
    alternative: str = "two-sided",
    **kwargs,
    **kwargs,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate the minimum detectable effect size for a given sample size.
    Calculate the minimum detectable effect size for a given sample size.


    This method calculates the smallest effect size that can be detected with
    This method calculates the smallest effect size that can be detected with
    the specified statistical power given a fixed sample size.
    the specified statistical power given a fixed sample size.


    Args:
    Args:
    sample_size: Available sample size
    sample_size: Available sample size
    alpha: Significance level (Type I error rate, default: 0.05)
    alpha: Significance level (Type I error rate, default: 0.05)
    power: Statistical power (1 - Type II error rate, default: 0.8)
    power: Statistical power (1 - Type II error rate, default: 0.8)
    test_type: Type of test, one of:
    test_type: Type of test, one of:
    "proportion": Test for proportions
    "proportion": Test for proportions
    "mean": Test for means (t-test)
    "mean": Test for means (t-test)
    "correlation": Test for correlation
    "correlation": Test for correlation
    alternative: Alternative hypothesis, one of:
    alternative: Alternative hypothesis, one of:
    "two-sided" (default): two-tailed test
    "two-sided" (default): two-tailed test
    "one-sided": one-tailed test
    "one-sided": one-tailed test
    **kwargs: Additional parameters specific to the test type:
    **kwargs: Additional parameters specific to the test type:
    - For "proportion": p_null (default: 0.5)
    - For "proportion": p_null (default: 0.5)
    - For "mean": std_dev (required)
    - For "mean": std_dev (required)


    Returns:
    Returns:
    Dictionary with effect size calculation results including:
    Dictionary with effect size calculation results including:
    - effect_size: Minimum detectable effect size
    - effect_size: Minimum detectable effect size
    - sample_size: Specified sample size
    - sample_size: Specified sample size
    - alpha: Significance level
    - alpha: Significance level
    - power: Statistical power
    - power: Statistical power
    - test_type: Type of test
    - test_type: Type of test
    - alternative: Alternative hypothesis
    - alternative: Alternative hypothesis
    - Additional test-specific parameters
    - Additional test-specific parameters


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(sample_size, int, min_value=2)
    self.validate_data(sample_size, int, min_value=2)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(power, float, min_value=0.0, max_value=1.0)
    self.validate_data(power, float, min_value=0.0, max_value=1.0)


    if test_type not in ["proportion", "mean", "correlation"]:
    if test_type not in ["proportion", "mean", "correlation"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Test type must be one of: 'proportion', 'mean', 'correlation'"
    "Test type must be one of: 'proportion', 'mean', 'correlation'"
    )
    )


    if alternative not in ["two-sided", "one-sided"]:
    if alternative not in ["two-sided", "one-sided"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Alternative must be one of: 'two-sided', 'one-sided'"
    "Alternative must be one of: 'two-sided', 'one-sided'"
    )
    )


    # Calculate z-values for alpha and power
    # Calculate z-values for alpha and power
    z_alpha = (
    z_alpha = (
    stats.norm.ppf(1 - alpha / 2)
    stats.norm.ppf(1 - alpha / 2)
    if alternative == "two-sided"
    if alternative == "two-sided"
    else stats.norm.ppf(1 - alpha)
    else stats.norm.ppf(1 - alpha)
    )
    )
    z_beta = stats.norm.ppf(power)
    z_beta = stats.norm.ppf(power)


    result = {
    result = {
    "sample_size": sample_size,
    "sample_size": sample_size,
    "alpha": alpha,
    "alpha": alpha,
    "power": power,
    "power": power,
    "test_type": test_type,
    "test_type": test_type,
    "alternative": alternative,
    "alternative": alternative,
    }
    }


    if test_type == "proportion":
    if test_type == "proportion":
    # Get null proportion
    # Get null proportion
    p_null = kwargs.get("p_null", 0.5)
    p_null = kwargs.get("p_null", 0.5)
    self.validate_data(p_null, float, min_value=0.0, max_value=1.0)
    self.validate_data(p_null, float, min_value=0.0, max_value=1.0)


    # Calculate minimum detectable effect size for proportion test
    # Calculate minimum detectable effect size for proportion test
    # This is an approximation using the normal approximation
    # This is an approximation using the normal approximation
    effect_size = (z_alpha + z_beta) * math.sqrt(
    effect_size = (z_alpha + z_beta) * math.sqrt(
    2 * p_null * (1 - p_null) / sample_size
    2 * p_null * (1 - p_null) / sample_size
    )
    )


    result.update({"effect_size": effect_size, "p_null": p_null})
    result.update({"effect_size": effect_size, "p_null": p_null})


    elif test_type == "mean":
    elif test_type == "mean":
    # Get standard deviation
    # Get standard deviation
    if "std_dev" not in kwargs:
    if "std_dev" not in kwargs:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Standard deviation (std_dev) must be provided for mean test"
    "Standard deviation (std_dev) must be provided for mean test"
    )
    )


    std_dev = kwargs["std_dev"]
    std_dev = kwargs["std_dev"]
    self.validate_data(std_dev, float, min_value=0.0)
    self.validate_data(std_dev, float, min_value=0.0)


    # Calculate minimum detectable effect size for mean test
    # Calculate minimum detectable effect size for mean test
    effect_size = (z_alpha + z_beta) * std_dev * math.sqrt(2 / sample_size)
    effect_size = (z_alpha + z_beta) * std_dev * math.sqrt(2 / sample_size)


    result.update({"effect_size": effect_size, "std_dev": std_dev})
    result.update({"effect_size": effect_size, "std_dev": std_dev})


    elif test_type == "correlation":
    elif test_type == "correlation":
    # Calculate minimum detectable correlation coefficient
    # Calculate minimum detectable correlation coefficient
    # Using Fisher's z transformation
    # Using Fisher's z transformation
    z_min = (z_alpha + z_beta) / math.sqrt(sample_size - 3)
    z_min = (z_alpha + z_beta) / math.sqrt(sample_size - 3)


    # Convert back from Fisher's z to correlation coefficient
    # Convert back from Fisher's z to correlation coefficient
    effect_size = (math.exp(2 * z_min) - 1) / (math.exp(2 * z_min) + 1)
    effect_size = (math.exp(2 * z_min) - 1) / (math.exp(2 * z_min) + 1)


    result["effect_size"] = effect_size
    result["effect_size"] = effect_size


    return result
    return result


    def power_analysis(
    def power_analysis(
    self,
    self,
    test_type: str,
    test_type: str,
    effect_size: float,
    effect_size: float,
    sample_size: int,
    sample_size: int,
    alpha: float = 0.05,
    alpha: float = 0.05,
    alternative: str = "two-sided",
    alternative: str = "two-sided",
    **kwargs,
    **kwargs,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate statistical power for a given test, effect size, and sample size.
    Calculate statistical power for a given test, effect size, and sample size.


    This method calculates the probability of correctly rejecting the null hypothesis
    This method calculates the probability of correctly rejecting the null hypothesis
    (statistical power) for a specified test, effect size, and sample size.
    (statistical power) for a specified test, effect size, and sample size.


    Args:
    Args:
    test_type: Type of test, one of:
    test_type: Type of test, one of:
    "proportion": Test for proportions
    "proportion": Test for proportions
    "mean": Test for means (t-test)
    "mean": Test for means (t-test)
    "correlation": Test for correlation
    "correlation": Test for correlation
    effect_size: Effect size to detect
    effect_size: Effect size to detect
    sample_size: Available sample size
    sample_size: Available sample size
    alpha: Significance level (Type I error rate, default: 0.05)
    alpha: Significance level (Type I error rate, default: 0.05)
    alternative: Alternative hypothesis, one of:
    alternative: Alternative hypothesis, one of:
    "two-sided" (default): two-tailed test
    "two-sided" (default): two-tailed test
    "one-sided": one-tailed test
    "one-sided": one-tailed test
    **kwargs: Additional parameters specific to the test type:
    **kwargs: Additional parameters specific to the test type:
    - For "proportion": p_null (default: 0.5)
    - For "proportion": p_null (default: 0.5)
    - For "mean": std_dev (required)
    - For "mean": std_dev (required)


    Returns:
    Returns:
    Dictionary with power analysis results including:
    Dictionary with power analysis results including:
    - power: Statistical power (1 - Type II error rate)
    - power: Statistical power (1 - Type II error rate)
    - effect_size: Specified effect size
    - effect_size: Specified effect size
    - sample_size: Specified sample size
    - sample_size: Specified sample size
    - alpha: Significance level
    - alpha: Significance level
    - test_type: Type of test
    - test_type: Type of test
    - alternative: Alternative hypothesis
    - alternative: Alternative hypothesis
    - Additional test-specific parameters
    - Additional test-specific parameters


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(effect_size, float)
    self.validate_data(effect_size, float)
    self.validate_data(sample_size, int, min_value=2)
    self.validate_data(sample_size, int, min_value=2)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)


    if test_type not in ["proportion", "mean", "correlation"]:
    if test_type not in ["proportion", "mean", "correlation"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Test type must be one of: 'proportion', 'mean', 'correlation'"
    "Test type must be one of: 'proportion', 'mean', 'correlation'"
    )
    )


    if alternative not in ["two-sided", "one-sided"]:
    if alternative not in ["two-sided", "one-sided"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Alternative must be one of: 'two-sided', 'one-sided'"
    "Alternative must be one of: 'two-sided', 'one-sided'"
    )
    )


    # Calculate critical value
    # Calculate critical value
    z_alpha = (
    z_alpha = (
    stats.norm.ppf(1 - alpha / 2)
    stats.norm.ppf(1 - alpha / 2)
    if alternative == "two-sided"
    if alternative == "two-sided"
    else stats.norm.ppf(1 - alpha)
    else stats.norm.ppf(1 - alpha)
    )
    )


    result = {
    result = {
    "effect_size": effect_size,
    "effect_size": effect_size,
    "sample_size": sample_size,
    "sample_size": sample_size,
    "alpha": alpha,
    "alpha": alpha,
    "test_type": test_type,
    "test_type": test_type,
    "alternative": alternative,
    "alternative": alternative,
    }
    }


    if test_type == "proportion":
    if test_type == "proportion":
    # Get null proportion
    # Get null proportion
    p_null = kwargs.get("p_null", 0.5)
    p_null = kwargs.get("p_null", 0.5)
    self.validate_data(p_null, float, min_value=0.0, max_value=1.0)
    self.validate_data(p_null, float, min_value=0.0, max_value=1.0)


    # Calculate alternative proportion
    # Calculate alternative proportion
    p_alt = p_null + effect_size
    p_alt = p_null + effect_size


    # Ensure p_alt is within valid range
    # Ensure p_alt is within valid range
    if p_alt < 0 or p_alt > 1:
    if p_alt < 0 or p_alt > 1:
    raise InvalidParameterError(
    raise InvalidParameterError(
    f"Alternative proportion (p_null + effect_size = {p_alt}) must be between 0 and 1"
    f"Alternative proportion (p_null + effect_size = {p_alt}) must be between 0 and 1"
    )
    )


    # Calculate standard error under null and alternative
    # Calculate standard error under null and alternative
    se_null = math.sqrt(p_null * (1 - p_null) / sample_size)
    se_null = math.sqrt(p_null * (1 - p_null) / sample_size)
    se_alt = math.sqrt(p_alt * (1 - p_alt) / sample_size)
    se_alt = math.sqrt(p_alt * (1 - p_alt) / sample_size)


    # Calculate non-centrality parameter
    # Calculate non-centrality parameter
    if alternative == "two-sided":
    if alternative == "two-sided":
    # For two-sided test, we need to consider both tails
    # For two-sided test, we need to consider both tails
    critical_value = p_null + z_alpha * se_null
    critical_value = p_null + z_alpha * se_null
    z_power = (p_alt - critical_value) / se_alt
    z_power = (p_alt - critical_value) / se_alt
    power = stats.norm.cdf(z_power)
    power = stats.norm.cdf(z_power)


    # For the other tail
    # For the other tail
    critical_value_lower = p_null - z_alpha * se_null
    critical_value_lower = p_null - z_alpha * se_null
    z_power_lower = (critical_value_lower - p_alt) / se_alt
    z_power_lower = (critical_value_lower - p_alt) / se_alt
    power_lower = stats.norm.cdf(z_power_lower)
    power_lower = stats.norm.cdf(z_power_lower)


    # Total power is the sum of powers in both tails
    # Total power is the sum of powers in both tails
    power = power + power_lower
    power = power + power_lower
    else:
    else:
    # For one-sided test
    # For one-sided test
    if effect_size > 0:  # Greater alternative
    if effect_size > 0:  # Greater alternative
    critical_value = p_null + z_alpha * se_null
    critical_value = p_null + z_alpha * se_null
    z_power = (p_alt - critical_value) / se_alt
    z_power = (p_alt - critical_value) / se_alt
    power = stats.norm.cdf(z_power)
    power = stats.norm.cdf(z_power)
    else:  # Less alternative
    else:  # Less alternative
    critical_value = p_null - z_alpha * se_null
    critical_value = p_null - z_alpha * se_null
    z_power = (critical_value - p_alt) / se_alt
    z_power = (critical_value - p_alt) / se_alt
    power = stats.norm.cdf(z_power)
    power = stats.norm.cdf(z_power)


    result.update({"power": power, "p_null": p_null, "p_alt": p_alt})
    result.update({"power": power, "p_null": p_null, "p_alt": p_alt})


    elif test_type == "mean":
    elif test_type == "mean":
    # Get standard deviation
    # Get standard deviation
    if "std_dev" not in kwargs:
    if "std_dev" not in kwargs:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Standard deviation (std_dev) must be provided for mean test"
    "Standard deviation (std_dev) must be provided for mean test"
    )
    )


    std_dev = kwargs["std_dev"]
    std_dev = kwargs["std_dev"]
    self.validate_data(std_dev, float, min_value=0.0)
    self.validate_data(std_dev, float, min_value=0.0)


    # Calculate standardized effect size (Cohen's d)
    # Calculate standardized effect size (Cohen's d)
    d = effect_size / std_dev
    d = effect_size / std_dev


    # Calculate non-centrality parameter
    # Calculate non-centrality parameter
    ncp = d * math.sqrt(sample_size / 2)
    ncp = d * math.sqrt(sample_size / 2)


    # Calculate power
    # Calculate power
    if alternative == "two-sided":
    if alternative == "two-sided":
    power = stats.norm.cdf(ncp - z_alpha) + stats.norm.cdf(-ncp - z_alpha)
    power = stats.norm.cdf(ncp - z_alpha) + stats.norm.cdf(-ncp - z_alpha)
    else:
    else:
    if effect_size > 0:  # Greater alternative
    if effect_size > 0:  # Greater alternative
    power = stats.norm.cdf(ncp - z_alpha)
    power = stats.norm.cdf(ncp - z_alpha)
    else:  # Less alternative
    else:  # Less alternative
    power = stats.norm.cdf(-ncp - z_alpha)
    power = stats.norm.cdf(-ncp - z_alpha)


    result.update(
    result.update(
    {"power": power, "std_dev": std_dev, "standardized_effect_size": d}
    {"power": power, "std_dev": std_dev, "standardized_effect_size": d}
    )
    )


    elif test_type == "correlation":
    elif test_type == "correlation":
    # Use absolute value of correlation for calculation
    # Use absolute value of correlation for calculation
    r = abs(effect_size)
    r = abs(effect_size)


    # Fisher's z transformation of r
    # Fisher's z transformation of r
    z_r = 0.5 * math.log((1 + r) / (1 - r))
    z_r = 0.5 * math.log((1 + r) / (1 - r))


    # Calculate standard error
    # Calculate standard error
    se = 1 / math.sqrt(sample_size - 3)
    se = 1 / math.sqrt(sample_size - 3)


    # Calculate non-centrality parameter
    # Calculate non-centrality parameter
    ncp = z_r / se
    ncp = z_r / se


    # Calculate power
    # Calculate power
    if alternative == "two-sided":
    if alternative == "two-sided":
    power = stats.norm.cdf(ncp - z_alpha) + stats.norm.cdf(-ncp - z_alpha)
    power = stats.norm.cdf(ncp - z_alpha) + stats.norm.cdf(-ncp - z_alpha)
    else:
    else:
    power = stats.norm.cdf(ncp - z_alpha)
    power = stats.norm.cdf(ncp - z_alpha)


    result["power"] = power
    result["power"] = power


    return result
    return result


    def type_error_rates(
    def type_error_rates(
    self,
    self,
    test_type: str,
    test_type: str,
    effect_size: float,
    effect_size: float,
    sample_size: int,
    sample_size: int,
    alpha: float = 0.05,
    alpha: float = 0.05,
    alternative: str = "two-sided",
    alternative: str = "two-sided",
    **kwargs,
    **kwargs,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate Type I and Type II error rates for a statistical test.
    Calculate Type I and Type II error rates for a statistical test.


    This method calculates the probability of Type I error (false positive) and
    This method calculates the probability of Type I error (false positive) and
    Type II error (false negative) for a specified test, effect size, and sample size.
    Type II error (false negative) for a specified test, effect size, and sample size.


    Args:
    Args:
    test_type: Type of test, one of:
    test_type: Type of test, one of:
    "proportion": Test for proportions
    "proportion": Test for proportions
    "mean": Test for means (t-test)
    "mean": Test for means (t-test)
    "correlation": Test for correlation
    "correlation": Test for correlation
    effect_size: Effect size to detect
    effect_size: Effect size to detect
    sample_size: Available sample size
    sample_size: Available sample size
    alpha: Significance level (Type I error rate, default: 0.05)
    alpha: Significance level (Type I error rate, default: 0.05)
    alternative: Alternative hypothesis, one of:
    alternative: Alternative hypothesis, one of:
    "two-sided" (default): two-tailed test
    "two-sided" (default): two-tailed test
    "one-sided": one-tailed test
    "one-sided": one-tailed test
    **kwargs: Additional parameters specific to the test type:
    **kwargs: Additional parameters specific to the test type:
    - For "proportion": p_null (default: 0.5)
    - For "proportion": p_null (default: 0.5)
    - For "mean": std_dev (required)
    - For "mean": std_dev (required)


    Returns:
    Returns:
    Dictionary with error rate analysis results including:
    Dictionary with error rate analysis results including:
    - type_i_error: Type I error rate (alpha)
    - type_i_error: Type I error rate (alpha)
    - type_ii_error: Type II error rate (beta)
    - type_ii_error: Type II error rate (beta)
    - power: Statistical power (1 - beta)
    - power: Statistical power (1 - beta)
    - effect_size: Specified effect size
    - effect_size: Specified effect size
    - sample_size: Specified sample size
    - sample_size: Specified sample size
    - test_type: Type of test
    - test_type: Type of test
    - alternative: Alternative hypothesis
    - alternative: Alternative hypothesis
    - Additional test-specific parameters
    - Additional test-specific parameters


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Calculate power
    # Calculate power
    power_result = self.power_analysis(
    power_result = self.power_analysis(
    test_type=test_type,
    test_type=test_type,
    effect_size=effect_size,
    effect_size=effect_size,
    sample_size=sample_size,
    sample_size=sample_size,
    alpha=alpha,
    alpha=alpha,
    alternative=alternative,
    alternative=alternative,
    **kwargs,
    **kwargs,
    )
    )


    # Calculate Type II error rate (beta)
    # Calculate Type II error rate (beta)
    type_ii_error = 1 - power_result["power"]
    type_ii_error = 1 - power_result["power"]


    # Create result dictionary
    # Create result dictionary
    result = {
    result = {
    "type_i_error": alpha,
    "type_i_error": alpha,
    "type_ii_error": type_ii_error,
    "type_ii_error": type_ii_error,
    "power": power_result["power"],
    "power": power_result["power"],
    "effect_size": effect_size,
    "effect_size": effect_size,
    "sample_size": sample_size,
    "sample_size": sample_size,
    "test_type": test_type,
    "test_type": test_type,
    "alternative": alternative,
    "alternative": alternative,
    }
    }


    # Add test-specific parameters
    # Add test-specific parameters
    if test_type == "proportion":
    if test_type == "proportion":
    result["p_null"] = power_result.get("p_null", 0.5)
    result["p_null"] = power_result.get("p_null", 0.5)
    result["p_alt"] = power_result.get("p_alt")
    result["p_alt"] = power_result.get("p_alt")
    elif test_type == "mean":
    elif test_type == "mean":
    result["std_dev"] = power_result.get("std_dev")
    result["std_dev"] = power_result.get("std_dev")
    result["standardized_effect_size"] = power_result.get(
    result["standardized_effect_size"] = power_result.get(
    "standardized_effect_size"
    "standardized_effect_size"
    )
    )


    return result
    return result


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Multiple Comparison Corrections
    # Multiple Comparison Corrections
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------


    def bonferroni_correction(
    def bonferroni_correction(
    self, p_values: Union[List[float], np.ndarray]
    self, p_values: Union[List[float], np.ndarray]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Apply Bonferroni correction to a set of p-values.
    Apply Bonferroni correction to a set of p-values.


    The Bonferroni correction is a simple but conservative method to control
    The Bonferroni correction is a simple but conservative method to control
    the family-wise error rate (FWER) when performing multiple hypothesis tests.
    the family-wise error rate (FWER) when performing multiple hypothesis tests.
    It multiplies each p-value by the number of tests to maintain the overall
    It multiplies each p-value by the number of tests to maintain the overall
    significance level.
    significance level.


    Args:
    Args:
    p_values: List or array of p-values from multiple hypothesis tests
    p_values: List or array of p-values from multiple hypothesis tests


    Returns:
    Returns:
    Dictionary with correction results including:
    Dictionary with correction results including:
    - original_p_values: Original p-values
    - original_p_values: Original p-values
    - adjusted_p_values: Bonferroni-adjusted p-values
    - adjusted_p_values: Bonferroni-adjusted p-values
    - significant: Boolean array indicating which tests are significant after correction
    - significant: Boolean array indicating which tests are significant after correction
    - alpha: Significance level
    - alpha: Significance level
    - n_tests: Number of tests
    - n_tests: Number of tests
    - correction_method: Name of the correction method
    - correction_method: Name of the correction method


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(p_values, (list, np.ndarray), min_length=1)
    self.validate_data(p_values, (list, np.ndarray), min_length=1)


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    p_values_array = np.array(p_values)
    p_values_array = np.array(p_values)


    # Check if p-values are valid
    # Check if p-values are valid
    if np.any((p_values_array < 0) | (p_values_array > 1)):
    if np.any((p_values_array < 0) | (p_values_array > 1)):
    raise InvalidParameterError("P-values must be between 0 and 1")
    raise InvalidParameterError("P-values must be between 0 and 1")


    # Get number of tests
    # Get number of tests
    n_tests = len(p_values_array)
    n_tests = len(p_values_array)


    # Apply Bonferroni correction
    # Apply Bonferroni correction
    adjusted_p_values = np.minimum(p_values_array * n_tests, 1.0)
    adjusted_p_values = np.minimum(p_values_array * n_tests, 1.0)


    # Determine which tests are significant after correction
    # Determine which tests are significant after correction
    significant = adjusted_p_values < self.default_alpha
    significant = adjusted_p_values < self.default_alpha


    return {
    return {
    "original_p_values": p_values_array.tolist(),
    "original_p_values": p_values_array.tolist(),
    "adjusted_p_values": adjusted_p_values.tolist(),
    "adjusted_p_values": adjusted_p_values.tolist(),
    "significant": significant.tolist(),
    "significant": significant.tolist(),
    "alpha": self.default_alpha,
    "alpha": self.default_alpha,
    "n_tests": n_tests,
    "n_tests": n_tests,
    "correction_method": "bonferroni",
    "correction_method": "bonferroni",
    }
    }


    def holm_bonferroni_correction(
    def holm_bonferroni_correction(
    self, p_values: Union[List[float], np.ndarray]
    self, p_values: Union[List[float], np.ndarray]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Apply Holm-Bonferroni correction to a set of p-values.
    Apply Holm-Bonferroni correction to a set of p-values.


    The Holm-Bonferroni method is a step-down procedure that is more powerful
    The Holm-Bonferroni method is a step-down procedure that is more powerful
    than the standard Bonferroni correction while still controlling the
    than the standard Bonferroni correction while still controlling the
    family-wise error rate (FWER).
    family-wise error rate (FWER).


    Args:
    Args:
    p_values: List or array of p-values from multiple hypothesis tests
    p_values: List or array of p-values from multiple hypothesis tests


    Returns:
    Returns:
    Dictionary with correction results including:
    Dictionary with correction results including:
    - original_p_values: Original p-values
    - original_p_values: Original p-values
    - adjusted_p_values: Holm-Bonferroni-adjusted p-values
    - adjusted_p_values: Holm-Bonferroni-adjusted p-values
    - significant: Boolean array indicating which tests are significant after correction
    - significant: Boolean array indicating which tests are significant after correction
    - alpha: Significance level
    - alpha: Significance level
    - n_tests: Number of tests
    - n_tests: Number of tests
    - correction_method: Name of the correction method
    - correction_method: Name of the correction method


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(p_values, (list, np.ndarray), min_length=1)
    self.validate_data(p_values, (list, np.ndarray), min_length=1)


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    p_values_array = np.array(p_values)
    p_values_array = np.array(p_values)


    # Check if p-values are valid
    # Check if p-values are valid
    if np.any((p_values_array < 0) | (p_values_array > 1)):
    if np.any((p_values_array < 0) | (p_values_array > 1)):
    raise InvalidParameterError("P-values must be between 0 and 1")
    raise InvalidParameterError("P-values must be between 0 and 1")


    # Get number of tests
    # Get number of tests
    n_tests = len(p_values_array)
    n_tests = len(p_values_array)


    # Get the indices that would sort p-values in ascending order
    # Get the indices that would sort p-values in ascending order
    sorted_indices = np.argsort(p_values_array)
    sorted_indices = np.argsort(p_values_array)


    # Initialize adjusted p-values array
    # Initialize adjusted p-values array
    adjusted_p_values = np.ones_like(p_values_array)
    adjusted_p_values = np.ones_like(p_values_array)


    # Apply Holm-Bonferroni correction
    # Apply Holm-Bonferroni correction
    for i, idx in enumerate(sorted_indices):
    for i, idx in enumerate(sorted_indices):
    # Adjust p-value: p * (n - rank + 1)
    # Adjust p-value: p * (n - rank + 1)
    adjusted_p_values[idx] = min(p_values_array[idx] * (n_tests - i), 1.0)
    adjusted_p_values[idx] = min(p_values_array[idx] * (n_tests - i), 1.0)


    # Ensure adjusted p-values are monotonically increasing
    # Ensure adjusted p-values are monotonically increasing
    for i in range(1, n_tests):
    for i in range(1, n_tests):
    idx_prev = sorted_indices[i - 1]
    idx_prev = sorted_indices[i - 1]
    idx_curr = sorted_indices[i]
    idx_curr = sorted_indices[i]
    adjusted_p_values[idx_curr] = max(
    adjusted_p_values[idx_curr] = max(
    adjusted_p_values[idx_curr], adjusted_p_values[idx_prev]
    adjusted_p_values[idx_curr], adjusted_p_values[idx_prev]
    )
    )


    # Determine which tests are significant after correction
    # Determine which tests are significant after correction
    significant = adjusted_p_values < self.default_alpha
    significant = adjusted_p_values < self.default_alpha


    return {
    return {
    "original_p_values": p_values_array.tolist(),
    "original_p_values": p_values_array.tolist(),
    "adjusted_p_values": adjusted_p_values.tolist(),
    "adjusted_p_values": adjusted_p_values.tolist(),
    "significant": significant.tolist(),
    "significant": significant.tolist(),
    "alpha": self.default_alpha,
    "alpha": self.default_alpha,
    "n_tests": n_tests,
    "n_tests": n_tests,
    "correction_method": "holm-bonferroni",
    "correction_method": "holm-bonferroni",
    }
    }


    def benjamini_hochberg_correction(
    def benjamini_hochberg_correction(
    self, p_values: Union[List[float], np.ndarray]
    self, p_values: Union[List[float], np.ndarray]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Apply Benjamini-Hochberg correction to a set of p-values.
    Apply Benjamini-Hochberg correction to a set of p-values.


    The Benjamini-Hochberg procedure controls the false discovery rate (FDR),
    The Benjamini-Hochberg procedure controls the false discovery rate (FDR),
    which is the expected proportion of false positives among all rejected hypotheses.
    which is the expected proportion of false positives among all rejected hypotheses.
    This method is less conservative than FWER-controlling methods like Bonferroni.
    This method is less conservative than FWER-controlling methods like Bonferroni.


    Args:
    Args:
    p_values: List or array of p-values from multiple hypothesis tests
    p_values: List or array of p-values from multiple hypothesis tests


    Returns:
    Returns:
    Dictionary with correction results including:
    Dictionary with correction results including:
    - original_p_values: Original p-values
    - original_p_values: Original p-values
    - adjusted_p_values: Benjamini-Hochberg-adjusted p-values
    - adjusted_p_values: Benjamini-Hochberg-adjusted p-values
    - significant: Boolean array indicating which tests are significant after correction
    - significant: Boolean array indicating which tests are significant after correction
    - alpha: Significance level
    - alpha: Significance level
    - n_tests: Number of tests
    - n_tests: Number of tests
    - correction_method: Name of the correction method
    - correction_method: Name of the correction method


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(p_values, (list, np.ndarray), min_length=1)
    self.validate_data(p_values, (list, np.ndarray), min_length=1)


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    p_values_array = np.array(p_values)
    p_values_array = np.array(p_values)


    # Check if p-values are valid
    # Check if p-values are valid
    if np.any((p_values_array < 0) | (p_values_array > 1)):
    if np.any((p_values_array < 0) | (p_values_array > 1)):
    raise InvalidParameterError("P-values must be between 0 and 1")
    raise InvalidParameterError("P-values must be between 0 and 1")


    # Get number of tests
    # Get number of tests
    n_tests = len(p_values_array)
    n_tests = len(p_values_array)


    # Get the indices that would sort p-values in ascending order
    # Get the indices that would sort p-values in ascending order
    sorted_indices = np.argsort(p_values_array)
    sorted_indices = np.argsort(p_values_array)


    # Initialize adjusted p-values array
    # Initialize adjusted p-values array
    adjusted_p_values = np.ones_like(p_values_array)
    adjusted_p_values = np.ones_like(p_values_array)


    # Apply Benjamini-Hochberg correction
    # Apply Benjamini-Hochberg correction
    for i, idx in enumerate(sorted_indices):
    for i, idx in enumerate(sorted_indices):
    # Adjust p-value: p * n / rank
    # Adjust p-value: p * n / rank
    rank = i + 1
    rank = i + 1
    adjusted_p_values[idx] = p_values_array[idx] * n_tests / rank
    adjusted_p_values[idx] = p_values_array[idx] * n_tests / rank


    # Ensure adjusted p-values are monotonically decreasing
    # Ensure adjusted p-values are monotonically decreasing
    for i in range(n_tests - 2, -1, -1):
    for i in range(n_tests - 2, -1, -1):
    idx_next = sorted_indices[i + 1]
    idx_next = sorted_indices[i + 1]
    idx_curr = sorted_indices[i]
    idx_curr = sorted_indices[i]
    adjusted_p_values[idx_curr] = min(
    adjusted_p_values[idx_curr] = min(
    adjusted_p_values[idx_curr], adjusted_p_values[idx_next]
    adjusted_p_values[idx_curr], adjusted_p_values[idx_next]
    )
    )


    # Cap adjusted p-values at 1.0
    # Cap adjusted p-values at 1.0
    adjusted_p_values = np.minimum(adjusted_p_values, 1.0)
    adjusted_p_values = np.minimum(adjusted_p_values, 1.0)


    # Determine which tests are significant after correction
    # Determine which tests are significant after correction
    significant = adjusted_p_values < self.default_alpha
    significant = adjusted_p_values < self.default_alpha


    return {
    return {
    "original_p_values": p_values_array.tolist(),
    "original_p_values": p_values_array.tolist(),
    "adjusted_p_values": adjusted_p_values.tolist(),
    "adjusted_p_values": adjusted_p_values.tolist(),
    "significant": significant.tolist(),
    "significant": significant.tolist(),
    "alpha": self.default_alpha,
    "alpha": self.default_alpha,
    "n_tests": n_tests,
    "n_tests": n_tests,
    "correction_method": "benjamini-hochberg",
    "correction_method": "benjamini-hochberg",
    }
    }


    def benjamini_yekutieli_correction(
    def benjamini_yekutieli_correction(
    self, p_values: Union[List[float], np.ndarray]
    self, p_values: Union[List[float], np.ndarray]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Apply Benjamini-Yekutieli correction to a set of p-values.
    Apply Benjamini-Yekutieli correction to a set of p-values.


    The Benjamini-Yekutieli procedure is a more conservative version of the
    The Benjamini-Yekutieli procedure is a more conservative version of the
    Benjamini-Hochberg procedure that controls the false discovery rate (FDR)
    Benjamini-Hochberg procedure that controls the false discovery rate (FDR)
    under arbitrary dependence assumptions.
    under arbitrary dependence assumptions.


    Args:
    Args:
    p_values: List or array of p-values from multiple hypothesis tests
    p_values: List or array of p-values from multiple hypothesis tests


    Returns:
    Returns:
    Dictionary with correction results including:
    Dictionary with correction results including:
    - original_p_values: Original p-values
    - original_p_values: Original p-values
    - adjusted_p_values: Benjamini-Yekutieli-adjusted p-values
    - adjusted_p_values: Benjamini-Yekutieli-adjusted p-values
    - significant: Boolean array indicating which tests are significant after correction
    - significant: Boolean array indicating which tests are significant after correction
    - alpha: Significance level
    - alpha: Significance level
    - n_tests: Number of tests
    - n_tests: Number of tests
    - correction_method: Name of the correction method
    - correction_method: Name of the correction method


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(p_values, (list, np.ndarray), min_length=1)
    self.validate_data(p_values, (list, np.ndarray), min_length=1)


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    p_values_array = np.array(p_values)
    p_values_array = np.array(p_values)


    # Check if p-values are valid
    # Check if p-values are valid
    if np.any((p_values_array < 0) | (p_values_array > 1)):
    if np.any((p_values_array < 0) | (p_values_array > 1)):
    raise InvalidParameterError("P-values must be between 0 and 1")
    raise InvalidParameterError("P-values must be between 0 and 1")


    # Get number of tests
    # Get number of tests
    n_tests = len(p_values_array)
    n_tests = len(p_values_array)


    # Calculate the correction factor (sum of 1/i)
    # Calculate the correction factor (sum of 1/i)
    correction_factor = np.sum(1.0 / np.arange(1, n_tests + 1))
    correction_factor = np.sum(1.0 / np.arange(1, n_tests + 1))


    # Get the indices that would sort p-values in ascending order
    # Get the indices that would sort p-values in ascending order
    sorted_indices = np.argsort(p_values_array)
    sorted_indices = np.argsort(p_values_array)


    # Initialize adjusted p-values array
    # Initialize adjusted p-values array
    adjusted_p_values = np.ones_like(p_values_array)
    adjusted_p_values = np.ones_like(p_values_array)


    # Apply Benjamini-Yekutieli correction
    # Apply Benjamini-Yekutieli correction
    for i, idx in enumerate(sorted_indices):
    for i, idx in enumerate(sorted_indices):
    # Adjust p-value: p * n * c / rank
    # Adjust p-value: p * n * c / rank
    rank = i + 1
    rank = i + 1
    adjusted_p_values[idx] = (
    adjusted_p_values[idx] = (
    p_values_array[idx] * n_tests * correction_factor / rank
    p_values_array[idx] * n_tests * correction_factor / rank
    )
    )


    # Ensure adjusted p-values are monotonically decreasing
    # Ensure adjusted p-values are monotonically decreasing
    for i in range(n_tests - 2, -1, -1):
    for i in range(n_tests - 2, -1, -1):
    idx_next = sorted_indices[i + 1]
    idx_next = sorted_indices[i + 1]
    idx_curr = sorted_indices[i]
    idx_curr = sorted_indices[i]
    adjusted_p_values[idx_curr] = min(
    adjusted_p_values[idx_curr] = min(
    adjusted_p_values[idx_curr], adjusted_p_values[idx_next]
    adjusted_p_values[idx_curr], adjusted_p_values[idx_next]
    )
    )


    # Cap adjusted p-values at 1.0
    # Cap adjusted p-values at 1.0
    adjusted_p_values = np.minimum(adjusted_p_values, 1.0)
    adjusted_p_values = np.minimum(adjusted_p_values, 1.0)


    # Determine which tests are significant after correction
    # Determine which tests are significant after correction
    significant = adjusted_p_values < self.default_alpha
    significant = adjusted_p_values < self.default_alpha


    return {
    return {
    "original_p_values": p_values_array.tolist(),
    "original_p_values": p_values_array.tolist(),
    "adjusted_p_values": adjusted_p_values.tolist(),
    "adjusted_p_values": adjusted_p_values.tolist(),
    "significant": significant.tolist(),
    "significant": significant.tolist(),
    "alpha": self.default_alpha,
    "alpha": self.default_alpha,
    "n_tests": n_tests,
    "n_tests": n_tests,
    "correction_factor": correction_factor,
    "correction_factor": correction_factor,
    "correction_method": "benjamini-yekutieli",
    "correction_method": "benjamini-yekutieli",
    }
    }


    def sidak_correction(
    def sidak_correction(
    self, p_values: Union[List[float], np.ndarray]
    self, p_values: Union[List[float], np.ndarray]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Apply Šidák correction to a set of p-values.
    Apply Šidák correction to a set of p-values.


    The Šidák correction is a method to control the family-wise error rate (FWER)
    The Šidák correction is a method to control the family-wise error rate (FWER)
    that is slightly less conservative than the Bonferroni correction.
    that is slightly less conservative than the Bonferroni correction.


    Args:
    Args:
    p_values: List or array of p-values from multiple hypothesis tests
    p_values: List or array of p-values from multiple hypothesis tests


    Returns:
    Returns:
    Dictionary with correction results including:
    Dictionary with correction results including:
    - original_p_values: Original p-values
    - original_p_values: Original p-values
    - adjusted_p_values: Šidák-adjusted p-values
    - adjusted_p_values: Šidák-adjusted p-values
    - significant: Boolean array indicating which tests are significant after correction
    - significant: Boolean array indicating which tests are significant after correction
    - alpha: Significance level
    - alpha: Significance level
    - n_tests: Number of tests
    - n_tests: Number of tests
    - correction_method: Name of the correction method
    - correction_method: Name of the correction method


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(p_values, (list, np.ndarray), min_length=1)
    self.validate_data(p_values, (list, np.ndarray), min_length=1)


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    p_values_array = np.array(p_values)
    p_values_array = np.array(p_values)


    # Check if p-values are valid
    # Check if p-values are valid
    if np.any((p_values_array < 0) | (p_values_array > 1)):
    if np.any((p_values_array < 0) | (p_values_array > 1)):
    raise InvalidParameterError("P-values must be between 0 and 1")
    raise InvalidParameterError("P-values must be between 0 and 1")


    # Get number of tests
    # Get number of tests
    n_tests = len(p_values_array)
    n_tests = len(p_values_array)


    # Apply Šidák correction
    # Apply Šidák correction
    adjusted_p_values = 1.0 - (1.0 - p_values_array) ** n_tests
    adjusted_p_values = 1.0 - (1.0 - p_values_array) ** n_tests


    # Determine which tests are significant after correction
    # Determine which tests are significant after correction
    significant = adjusted_p_values < self.default_alpha
    significant = adjusted_p_values < self.default_alpha


    return {
    return {
    "original_p_values": p_values_array.tolist(),
    "original_p_values": p_values_array.tolist(),
    "adjusted_p_values": adjusted_p_values.tolist(),
    "adjusted_p_values": adjusted_p_values.tolist(),
    "significant": significant.tolist(),
    "significant": significant.tolist(),
    "alpha": self.default_alpha,
    "alpha": self.default_alpha,
    "n_tests": n_tests,
    "n_tests": n_tests,
    "correction_method": "sidak",
    "correction_method": "sidak",
    }
    }


    def adjust_alpha(
    def adjust_alpha(
    self, alpha: float, n_tests: int, method: str = "bonferroni"
    self, alpha: float, n_tests: int, method: str = "bonferroni"
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Adjust the significance level (alpha) for multiple comparisons.
    Adjust the significance level (alpha) for multiple comparisons.


    This method calculates an adjusted significance level to maintain
    This method calculates an adjusted significance level to maintain
    the overall error rate when performing multiple hypothesis tests.
    the overall error rate when performing multiple hypothesis tests.


    Args:
    Args:
    alpha: Original significance level
    alpha: Original significance level
    n_tests: Number of tests being performed
    n_tests: Number of tests being performed
    method: Method to use for adjustment, one of:
    method: Method to use for adjustment, one of:
    "bonferroni": Bonferroni correction (default)
    "bonferroni": Bonferroni correction (default)
    "sidak": Šidák correction
    "sidak": Šidák correction
    "none": No correction
    "none": No correction


    Returns:
    Returns:
    Dictionary with adjustment results including:
    Dictionary with adjustment results including:
    - original_alpha: Original significance level
    - original_alpha: Original significance level
    - adjusted_alpha: Adjusted significance level
    - adjusted_alpha: Adjusted significance level
    - n_tests: Number of tests
    - n_tests: Number of tests
    - adjustment_method: Method used for adjustment
    - adjustment_method: Method used for adjustment


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(alpha, float, min_value=0.0, max_value=1.0)
    self.validate_data(alpha, float, min_value=0.0, max_value=1.0)
    self.validate_data(n_tests, int, min_value=1)
    self.validate_data(n_tests, int, min_value=1)


    if method not in ["bonferroni", "sidak", "none"]:
    if method not in ["bonferroni", "sidak", "none"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Method must be one of: 'bonferroni', 'sidak', 'none'"
    "Method must be one of: 'bonferroni', 'sidak', 'none'"
    )
    )


    # Initialize result dictionary
    # Initialize result dictionary
    result = {
    result = {
    "original_alpha": alpha,
    "original_alpha": alpha,
    "n_tests": n_tests,
    "n_tests": n_tests,
    "adjustment_method": method,
    "adjustment_method": method,
    }
    }


    # Apply the selected adjustment method
    # Apply the selected adjustment method
    if method == "bonferroni":
    if method == "bonferroni":
    # Bonferroni correction: alpha / n
    # Bonferroni correction: alpha / n
    adjusted_alpha = alpha / n_tests
    adjusted_alpha = alpha / n_tests
    result["adjusted_alpha"] = adjusted_alpha
    result["adjusted_alpha"] = adjusted_alpha


    elif method == "sidak":
    elif method == "sidak":
    # Šidák correction: 1 - (1 - alpha)^(1/n)
    # Šidák correction: 1 - (1 - alpha)^(1/n)
    adjusted_alpha = 1.0 - (1.0 - alpha) ** (1.0 / n_tests)
    adjusted_alpha = 1.0 - (1.0 - alpha) ** (1.0 / n_tests)
    result["adjusted_alpha"] = adjusted_alpha
    result["adjusted_alpha"] = adjusted_alpha


    else:  # method == "none"
    else:  # method == "none"
    # No correction
    # No correction
    result["adjusted_alpha"] = alpha
    result["adjusted_alpha"] = alpha


    return result
    return result


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Sequential Analysis
    # Sequential Analysis
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------


    def obrien_fleming_boundary(
    def obrien_fleming_boundary(
    self, num_looks: int, alpha: float = 0.05
    self, num_looks: int, alpha: float = 0.05
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate O'Brien-Fleming stopping boundaries for group sequential testing.
    Calculate O'Brien-Fleming stopping boundaries for group sequential testing.


    The O'Brien-Fleming approach uses more conservative boundaries early in the trial
    The O'Brien-Fleming approach uses more conservative boundaries early in the trial
    and less conservative boundaries later, making it harder to stop early.
    and less conservative boundaries later, making it harder to stop early.


    Args:
    Args:
    num_looks: Number of interim analyses (including final analysis)
    num_looks: Number of interim analyses (including final analysis)
    alpha: Overall significance level (default: 0.05)
    alpha: Overall significance level (default: 0.05)


    Returns:
    Returns:
    Dictionary with boundary calculation results including:
    Dictionary with boundary calculation results including:
    - boundaries: List of alpha spending at each look
    - boundaries: List of alpha spending at each look
    - cumulative_alpha: Cumulative alpha spent at each look
    - cumulative_alpha: Cumulative alpha spent at each look
    - z_boundaries: Z-score boundaries at each look
    - z_boundaries: Z-score boundaries at each look
    - information_fractions: Fraction of information at each look
    - information_fractions: Fraction of information at each look
    - num_looks: Number of looks
    - num_looks: Number of looks
    - alpha: Overall significance level
    - alpha: Overall significance level
    - method: Name of the boundary method
    - method: Name of the boundary method


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(num_looks, int, min_value=1)
    self.validate_data(num_looks, int, min_value=1)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)


    # Calculate information fractions (assuming equal spacing)
    # Calculate information fractions (assuming equal spacing)
    information_fractions = np.array(
    information_fractions = np.array(
    [(i + 1) / num_looks for i in range(num_looks)]
    [(i + 1) / num_looks for i in range(num_looks)]
    )
    )


    # Calculate O'Brien-Fleming boundaries
    # Calculate O'Brien-Fleming boundaries
    z_boundaries = []
    z_boundaries = []
    boundaries = []
    boundaries = []
    cumulative_alpha = []
    cumulative_alpha = []


    for i, fraction in enumerate(information_fractions):
    for i, fraction in enumerate(information_fractions):
    # O'Brien-Fleming Z-score boundary
    # O'Brien-Fleming Z-score boundary
    z_boundary = stats.norm.ppf(1 - alpha / 2) / np.sqrt(fraction)
    z_boundary = stats.norm.ppf(1 - alpha / 2) / np.sqrt(fraction)
    z_boundaries.append(z_boundary)
    z_boundaries.append(z_boundary)


    # Convert Z-score to alpha level
    # Convert Z-score to alpha level
    if i == 0:
    if i == 0:
    # First look
    # First look
    boundary = 2 * (1 - stats.norm.cdf(z_boundary))
    boundary = 2 * (1 - stats.norm.cdf(z_boundary))
    cumulative = boundary
    cumulative = boundary
    else:
    else:
    # Subsequent looks
    # Subsequent looks
    # Calculate incremental alpha spent at this look
    # Calculate incremental alpha spent at this look
    boundary = (
    boundary = (
    2 * (1 - stats.norm.cdf(z_boundary)) - cumulative_alpha[i - 1]
    2 * (1 - stats.norm.cdf(z_boundary)) - cumulative_alpha[i - 1]
    )
    )
    cumulative = cumulative_alpha[i - 1] + boundary
    cumulative = cumulative_alpha[i - 1] + boundary


    boundaries.append(boundary)
    boundaries.append(boundary)
    cumulative_alpha.append(cumulative)
    cumulative_alpha.append(cumulative)


    return {
    return {
    "boundaries": boundaries,
    "boundaries": boundaries,
    "cumulative_alpha": cumulative_alpha,
    "cumulative_alpha": cumulative_alpha,
    "z_boundaries": z_boundaries,
    "z_boundaries": z_boundaries,
    "information_fractions": information_fractions.tolist(),
    "information_fractions": information_fractions.tolist(),
    "num_looks": num_looks,
    "num_looks": num_looks,
    "alpha": alpha,
    "alpha": alpha,
    "method": "obrien_fleming",
    "method": "obrien_fleming",
    }
    }


    def pocock_boundary(self, num_looks: int, alpha: float = 0.05) -> Dict[str, Any]:
    def pocock_boundary(self, num_looks: int, alpha: float = 0.05) -> Dict[str, Any]:
    """
    """
    Calculate Pocock stopping boundaries for group sequential testing.
    Calculate Pocock stopping boundaries for group sequential testing.


    The Pocock approach uses constant boundaries across all looks,
    The Pocock approach uses constant boundaries across all looks,
    making it easier to stop early compared to O'Brien-Fleming.
    making it easier to stop early compared to O'Brien-Fleming.


    Args:
    Args:
    num_looks: Number of interim analyses (including final analysis)
    num_looks: Number of interim analyses (including final analysis)
    alpha: Overall significance level (default: 0.05)
    alpha: Overall significance level (default: 0.05)


    Returns:
    Returns:
    Dictionary with boundary calculation results including:
    Dictionary with boundary calculation results including:
    - boundaries: List of alpha spending at each look
    - boundaries: List of alpha spending at each look
    - cumulative_alpha: Cumulative alpha spent at each look
    - cumulative_alpha: Cumulative alpha spent at each look
    - z_boundaries: Z-score boundaries at each look
    - z_boundaries: Z-score boundaries at each look
    - information_fractions: Fraction of information at each look
    - information_fractions: Fraction of information at each look
    - num_looks: Number of looks
    - num_looks: Number of looks
    - alpha: Overall significance level
    - alpha: Overall significance level
    - method: Name of the boundary method
    - method: Name of the boundary method


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(num_looks, int, min_value=1)
    self.validate_data(num_looks, int, min_value=1)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)


    # Calculate information fractions (assuming equal spacing)
    # Calculate information fractions (assuming equal spacing)
    information_fractions = np.array(
    information_fractions = np.array(
    [(i + 1) / num_looks for i in range(num_looks)]
    [(i + 1) / num_looks for i in range(num_looks)]
    )
    )


    # Calculate Pocock boundaries
    # Calculate Pocock boundaries
    # For Pocock, the same nominal p-value is used at each look
    # For Pocock, the same nominal p-value is used at each look
    # We need to find the nominal p-value that gives the overall alpha
    # We need to find the nominal p-value that gives the overall alpha


    # Function to solve for the nominal p-value
    # Function to solve for the nominal p-value
    def cumulative_alpha_error(nominal_p):
    def cumulative_alpha_error(nominal_p):
    # Convert nominal p-value to z-score
    # Convert nominal p-value to z-score
    z = stats.norm.ppf(1 - nominal_p / 2)
    z = stats.norm.ppf(1 - nominal_p / 2)


    # Calculate cumulative alpha spent over all looks
    # Calculate cumulative alpha spent over all looks
    cum_alpha = 0
    cum_alpha = 0
    for i in range(num_looks):
    for i in range(num_looks):
    if i == 0:
    if i == 0:
    # First look
    # First look
    cum_alpha = 2 * (1 - stats.norm.cdf(z))
    cum_alpha = 2 * (1 - stats.norm.cdf(z))
    else:
    else:
    # Subsequent looks - this is an approximation
    # Subsequent looks - this is an approximation
    # In practice, more complex calculations involving multivariate normal
    # In practice, more complex calculations involving multivariate normal
    # distributions would be used
    # distributions would be used
    cum_alpha += 2 * (1 - stats.norm.cdf(z)) / (num_looks - i)
    cum_alpha += 2 * (1 - stats.norm.cdf(z)) / (num_looks - i)


    return cum_alpha - alpha
    return cum_alpha - alpha


    # Solve for nominal p-value
    # Solve for nominal p-value
    :
    :
    nominal_p = brentq(cumulative_alpha_error, 0.00001, 0.1)
    nominal_p = brentq(cumulative_alpha_error, 0.00001, 0.1)
except ValueError:
except ValueError:
    # If brentq fails, use a simple approximation
    # If brentq fails, use a simple approximation
    nominal_p = alpha / num_looks
    nominal_p = alpha / num_looks


    # Calculate z-score boundary
    # Calculate z-score boundary
    z_boundary = stats.norm.ppf(1 - nominal_p / 2)
    z_boundary = stats.norm.ppf(1 - nominal_p / 2)


    # Create results
    # Create results
    z_boundaries = [z_boundary] * num_looks
    z_boundaries = [z_boundary] * num_looks
    boundaries = [nominal_p] * num_looks
    boundaries = [nominal_p] * num_looks
    cumulative_alpha = [nominal_p * (i + 1) for i in range(num_looks)]
    cumulative_alpha = [nominal_p * (i + 1) for i in range(num_looks)]


    return {
    return {
    "boundaries": boundaries,
    "boundaries": boundaries,
    "cumulative_alpha": cumulative_alpha,
    "cumulative_alpha": cumulative_alpha,
    "z_boundaries": z_boundaries,
    "z_boundaries": z_boundaries,
    "information_fractions": information_fractions.tolist(),
    "information_fractions": information_fractions.tolist(),
    "num_looks": num_looks,
    "num_looks": num_looks,
    "alpha": alpha,
    "alpha": alpha,
    "method": "pocock",
    "method": "pocock",
    }
    }


    def alpha_spending_function(
    def alpha_spending_function(
    self,
    self,
    information_fractions: Union[List[float], np.ndarray],
    information_fractions: Union[List[float], np.ndarray],
    alpha: float = 0.05,
    alpha: float = 0.05,
    method: str = "obrien_fleming",
    method: str = "obrien_fleming",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate alpha spending function for group sequential testing.
    Calculate alpha spending function for group sequential testing.


    Alpha spending functions determine how much of the total Type I error
    Alpha spending functions determine how much of the total Type I error
    is "spent" at each interim analysis.
    is "spent" at each interim analysis.


    Args:
    Args:
    information_fractions: List or array of information fractions at each look
    information_fractions: List or array of information fractions at each look
    (values between 0 and 1, with the last value typically being 1)
    (values between 0 and 1, with the last value typically being 1)
    alpha: Overall significance level (default: 0.05)
    alpha: Overall significance level (default: 0.05)
    method: Method to use for alpha spending, one of:
    method: Method to use for alpha spending, one of:
    "obrien_fleming": O'Brien-Fleming spending function (default)
    "obrien_fleming": O'Brien-Fleming spending function (default)
    "pocock": Pocock spending function
    "pocock": Pocock spending function
    "hwang_shih_decosta": Hwang-Shih-DeCosta spending function
    "hwang_shih_decosta": Hwang-Shih-DeCosta spending function
    "linear": Linear spending function
    "linear": Linear spending function


    Returns:
    Returns:
    Dictionary with alpha spending results including:
    Dictionary with alpha spending results including:
    - alpha_spent: List of alpha spent at each look
    - alpha_spent: List of alpha spent at each look
    - cumulative_alpha: Cumulative alpha spent at each look
    - cumulative_alpha: Cumulative alpha spent at each look
    - information_fractions: Information fractions at each look
    - information_fractions: Information fractions at each look
    - num_looks: Number of looks
    - num_looks: Number of looks
    - alpha: Overall significance level
    - alpha: Overall significance level
    - method: Method used for alpha spending
    - method: Method used for alpha spending


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(information_fractions, (list, np.ndarray), min_length=1)
    self.validate_data(information_fractions, (list, np.ndarray), min_length=1)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)


    if method not in ["obrien_fleming", "pocock", "hwang_shih_decosta", "linear"]:
    if method not in ["obrien_fleming", "pocock", "hwang_shih_decosta", "linear"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Method must be one of: 'obrien_fleming', 'pocock', 'hwang_shih_decosta', 'linear'"
    "Method must be one of: 'obrien_fleming', 'pocock', 'hwang_shih_decosta', 'linear'"
    )
    )


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    info_fractions = np.array(information_fractions)
    info_fractions = np.array(information_fractions)


    # Check if information fractions are valid
    # Check if information fractions are valid
    if np.any((info_fractions < 0) | (info_fractions > 1)):
    if np.any((info_fractions < 0) | (info_fractions > 1)):
    raise InvalidParameterError("Information fractions must be between 0 and 1")
    raise InvalidParameterError("Information fractions must be between 0 and 1")


    # Check if information fractions are in ascending order
    # Check if information fractions are in ascending order
    if not np.all(np.diff(info_fractions) >= 0):
    if not np.all(np.diff(info_fractions) >= 0):
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Information fractions must be in ascending order"
    "Information fractions must be in ascending order"
    )
    )


    # Number of looks
    # Number of looks
    num_looks = len(info_fractions)
    num_looks = len(info_fractions)


    # Calculate cumulative alpha spent at each look
    # Calculate cumulative alpha spent at each look
    cumulative_alpha = np.zeros(num_looks)
    cumulative_alpha = np.zeros(num_looks)


    if method == "obrien_fleming":
    if method == "obrien_fleming":
    # O'Brien-Fleming spending function
    # O'Brien-Fleming spending function
    for i, t in enumerate(info_fractions):
    for i, t in enumerate(info_fractions):
    if t > 0:
    if t > 0:
    cumulative_alpha[i] = 2 * (
    cumulative_alpha[i] = 2 * (
    1 - stats.norm.cdf(stats.norm.ppf(1 - alpha / 2) / np.sqrt(t))
    1 - stats.norm.cdf(stats.norm.ppf(1 - alpha / 2) / np.sqrt(t))
    )
    )
    else:
    else:
    cumulative_alpha[i] = 0
    cumulative_alpha[i] = 0


    elif method == "pocock":
    elif method == "pocock":
    # Pocock spending function
    # Pocock spending function
    for i, t in enumerate(info_fractions):
    for i, t in enumerate(info_fractions):
    cumulative_alpha[i] = alpha * np.log(1 + (np.e - 1) * t)
    cumulative_alpha[i] = alpha * np.log(1 + (np.e - 1) * t)


    elif method == "hwang_shih_decosta":
    elif method == "hwang_shih_decosta":
    # Hwang-Shih-DeCosta spending function
    # Hwang-Shih-DeCosta spending function
    for i, t in enumerate(info_fractions):
    for i, t in enumerate(info_fractions):
    if t > 0:
    if t > 0:
    cumulative_alpha[i] = alpha * t**1.5
    cumulative_alpha[i] = alpha * t**1.5
    else:
    else:
    cumulative_alpha[i] = 0
    cumulative_alpha[i] = 0


    elif method == "linear":
    elif method == "linear":
    # Linear spending function
    # Linear spending function
    for i, t in enumerate(info_fractions):
    for i, t in enumerate(info_fractions):
    cumulative_alpha[i] = alpha * t
    cumulative_alpha[i] = alpha * t


    # Calculate incremental alpha spent at each look
    # Calculate incremental alpha spent at each look
    alpha_spent = np.zeros(num_looks)
    alpha_spent = np.zeros(num_looks)
    alpha_spent[0] = cumulative_alpha[0]
    alpha_spent[0] = cumulative_alpha[0]
    for i in range(1, num_looks):
    for i in range(1, num_looks):
    alpha_spent[i] = cumulative_alpha[i] - cumulative_alpha[i - 1]
    alpha_spent[i] = cumulative_alpha[i] - cumulative_alpha[i - 1]


    return {
    return {
    "alpha_spent": alpha_spent.tolist(),
    "alpha_spent": alpha_spent.tolist(),
    "cumulative_alpha": cumulative_alpha.tolist(),
    "cumulative_alpha": cumulative_alpha.tolist(),
    "information_fractions": info_fractions.tolist(),
    "information_fractions": info_fractions.tolist(),
    "num_looks": num_looks,
    "num_looks": num_looks,
    "alpha": alpha,
    "alpha": alpha,
    "method": method,
    "method": method,
    }
    }


    def sequential_test_analysis(
    def sequential_test_analysis(
    self,
    self,
    z_scores: Union[List[float], np.ndarray],
    z_scores: Union[List[float], np.ndarray],
    information_fractions: Union[List[float], np.ndarray] = None,
    information_fractions: Union[List[float], np.ndarray] = None,
    alpha: float = 0.05,
    alpha: float = 0.05,
    method: str = "obrien_fleming",
    method: str = "obrien_fleming",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Analyze results from a sequential test with multiple looks.
    Analyze results from a sequential test with multiple looks.


    This method evaluates whether stopping boundaries were crossed at any look
    This method evaluates whether stopping boundaries were crossed at any look
    and provides adjusted p-values for sequential testing.
    and provides adjusted p-values for sequential testing.


    Args:
    Args:
    z_scores: List or array of Z-scores at each look
    z_scores: List or array of Z-scores at each look
    information_fractions: List or array of information fractions at each look
    information_fractions: List or array of information fractions at each look
    (values between 0 and 1, with the last value typically being 1)
    (values between 0 and 1, with the last value typically being 1)
    If None, assumes equal spacing
    If None, assumes equal spacing
    alpha: Overall significance level (default: 0.05)
    alpha: Overall significance level (default: 0.05)
    method: Method to use for boundary calculation, one of:
    method: Method to use for boundary calculation, one of:
    "obrien_fleming": O'Brien-Fleming boundaries (default)
    "obrien_fleming": O'Brien-Fleming boundaries (default)
    "pocock": Pocock boundaries
    "pocock": Pocock boundaries


    Returns:
    Returns:
    Dictionary with sequential test analysis results including:
    Dictionary with sequential test analysis results including:
    - z_scores: Z-scores at each look
    - z_scores: Z-scores at each look
    - boundaries: Stopping boundaries at each look
    - boundaries: Stopping boundaries at each look
    - crossed: Boolean array indicating whether boundaries were crossed at each look
    - crossed: Boolean array indicating whether boundaries were crossed at each look
    - adjusted_p_values: P-values adjusted for sequential testing
    - adjusted_p_values: P-values adjusted for sequential testing
    - information_fractions: Information fractions at each look
    - information_fractions: Information fractions at each look
    - num_looks: Number of looks
    - num_looks: Number of looks
    - alpha: Overall significance level
    - alpha: Overall significance level
    - method: Method used for boundary calculation
    - method: Method used for boundary calculation
    - stop_early: Whether the test should have stopped early
    - stop_early: Whether the test should have stopped early
    - first_significant_look: Index of the first look where boundaries were crossed (or None)
    - first_significant_look: Index of the first look where boundaries were crossed (or None)


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(z_scores, (list, np.ndarray), min_length=1)
    self.validate_data(z_scores, (list, np.ndarray), min_length=1)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)


    if method not in ["obrien_fleming", "pocock"]:
    if method not in ["obrien_fleming", "pocock"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Method must be one of: 'obrien_fleming', 'pocock'"
    "Method must be one of: 'obrien_fleming', 'pocock'"
    )
    )


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    z_scores_array = np.array(z_scores)
    z_scores_array = np.array(z_scores)


    # Number of looks
    # Number of looks
    num_looks = len(z_scores_array)
    num_looks = len(z_scores_array)


    # If information fractions not provided, assume equal spacing
    # If information fractions not provided, assume equal spacing
    if information_fractions is None:
    if information_fractions is None:
    info_fractions = np.array([(i + 1) / num_looks for i in range(num_looks)])
    info_fractions = np.array([(i + 1) / num_looks for i in range(num_looks)])
    else:
    else:
    self.validate_data(
    self.validate_data(
    information_fractions, (list, np.ndarray), min_length=num_looks
    information_fractions, (list, np.ndarray), min_length=num_looks
    )
    )
    info_fractions = np.array(information_fractions)
    info_fractions = np.array(information_fractions)


    # Check if information fractions are valid
    # Check if information fractions are valid
    if np.any((info_fractions < 0) | (info_fractions > 1)):
    if np.any((info_fractions < 0) | (info_fractions > 1)):
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Information fractions must be between 0 and 1"
    "Information fractions must be between 0 and 1"
    )
    )


    # Check if information fractions are in ascending order
    # Check if information fractions are in ascending order
    if not np.all(np.diff(info_fractions) >= 0):
    if not np.all(np.diff(info_fractions) >= 0):
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Information fractions must be in ascending order"
    "Information fractions must be in ascending order"
    )
    )


    # Calculate boundaries based on method
    # Calculate boundaries based on method
    if method == "obrien_fleming":
    if method == "obrien_fleming":
    # O'Brien-Fleming boundaries
    # O'Brien-Fleming boundaries
    boundaries = stats.norm.ppf(1 - alpha / 2) / np.sqrt(info_fractions)
    boundaries = stats.norm.ppf(1 - alpha / 2) / np.sqrt(info_fractions)
    else:  # method == "pocock"
    else:  # method == "pocock"
    # Pocock boundaries - constant across all looks
    # Pocock boundaries - constant across all looks
    # This is an approximation; in practice, more complex calculations would be used
    # This is an approximation; in practice, more complex calculations would be used
    nominal_p = alpha / num_looks
    nominal_p = alpha / num_looks
    z_boundary = stats.norm.ppf(1 - nominal_p / 2)
    z_boundary = stats.norm.ppf(1 - nominal_p / 2)
    boundaries = np.array([z_boundary] * num_looks)
    boundaries = np.array([z_boundary] * num_looks)


    # Check if boundaries were crossed at each look
    # Check if boundaries were crossed at each look
    crossed = np.abs(z_scores_array) >= boundaries
    crossed = np.abs(z_scores_array) >= boundaries


    # Find the first look where boundaries were crossed (if any)
    # Find the first look where boundaries were crossed (if any)
    first_significant_look = None
    first_significant_look = None
    for i, is_crossed in enumerate(crossed):
    for i, is_crossed in enumerate(crossed):
    if is_crossed:
    if is_crossed:
    first_significant_look = i
    first_significant_look = i
    break
    break


    # Determine if the test should have stopped early
    # Determine if the test should have stopped early
    stop_early = (
    stop_early = (
    first_significant_look is not None
    first_significant_look is not None
    and first_significant_look < num_looks - 1
    and first_significant_look < num_looks - 1
    )
    )


    # Calculate adjusted p-values
    # Calculate adjusted p-values
    adjusted_p_values = []
    adjusted_p_values = []
    for i, z in enumerate(z_scores_array):
    for i, z in enumerate(z_scores_array):
    # For each look, calculate the adjusted p-value
    # For each look, calculate the adjusted p-value
    # This is an approximation; in practice, more complex calculations would be used
    # This is an approximation; in practice, more complex calculations would be used
    if method == "obrien_fleming":
    if method == "obrien_fleming":
    # O'Brien-Fleming adjustment
    # O'Brien-Fleming adjustment
    adjusted_p = 2 * (
    adjusted_p = 2 * (
    1 - stats.norm.cdf(np.abs(z) * np.sqrt(info_fractions[i]))
    1 - stats.norm.cdf(np.abs(z) * np.sqrt(info_fractions[i]))
    )
    )
    else:  # method == "pocock"
    else:  # method == "pocock"
    # Pocock adjustment
    # Pocock adjustment
    adjusted_p = 2 * (1 - stats.norm.cdf(np.abs(z))) * num_looks
    adjusted_p = 2 * (1 - stats.norm.cdf(np.abs(z))) * num_looks
    adjusted_p = min(adjusted_p, 1.0)  # Cap at 1.0
    adjusted_p = min(adjusted_p, 1.0)  # Cap at 1.0


    adjusted_p_values.append(adjusted_p)
    adjusted_p_values.append(adjusted_p)


    return {
    return {
    "z_scores": z_scores_array.tolist(),
    "z_scores": z_scores_array.tolist(),
    "boundaries": boundaries.tolist(),
    "boundaries": boundaries.tolist(),
    "crossed": crossed.tolist(),
    "crossed": crossed.tolist(),
    "adjusted_p_values": adjusted_p_values,
    "adjusted_p_values": adjusted_p_values,
    "information_fractions": info_fractions.tolist(),
    "information_fractions": info_fractions.tolist(),
    "num_looks": num_looks,
    "num_looks": num_looks,
    "alpha": alpha,
    "alpha": alpha,
    "method": method,
    "method": method,
    "stop_early": stop_early,
    "stop_early": stop_early,
    "first_significant_look": first_significant_look,
    "first_significant_look": first_significant_look,
    }
    }


    def conditional_power(
    def conditional_power(
    self,
    self,
    current_z: float,
    current_z: float,
    information_fraction: float,
    information_fraction: float,
    target_effect: float = None,
    target_effect: float = None,
    observed_effect: float = None,
    observed_effect: float = None,
    alpha: float = 0.05,
    alpha: float = 0.05,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate conditional power for a sequential test.
    Calculate conditional power for a sequential test.


    Conditional power is the probability of rejecting the null hypothesis at the
    Conditional power is the probability of rejecting the null hypothesis at the
    final analysis, given the current data.
    final analysis, given the current data.


    Args:
    Args:
    current_z: Current Z-score
    current_z: Current Z-score
    information_fraction: Current fraction of information (between 0 and 1)
    information_fraction: Current fraction of information (between 0 and 1)
    target_effect: Target effect size (standardized) to detect
    target_effect: Target effect size (standardized) to detect
    If None, uses observed_effect
    If None, uses observed_effect
    observed_effect: Observed effect size (standardized) from current data
    observed_effect: Observed effect size (standardized) from current data
    If None and target_effect is None, uses current_z / sqrt(information_fraction)
    If None and target_effect is None, uses current_z / sqrt(information_fraction)
    alpha: Significance level (default: 0.05)
    alpha: Significance level (default: 0.05)


    Returns:
    Returns:
    Dictionary with conditional power calculation results including:
    Dictionary with conditional power calculation results including:
    - conditional_power: Probability of rejecting null at final analysis
    - conditional_power: Probability of rejecting null at final analysis
    - current_z: Current Z-score
    - current_z: Current Z-score
    - information_fraction: Current fraction of information
    - information_fraction: Current fraction of information
    - target_effect: Target effect size used in calculation
    - target_effect: Target effect size used in calculation
    - observed_effect: Observed effect size from current data
    - observed_effect: Observed effect size from current data
    - alpha: Significance level
    - alpha: Significance level
    - z_critical: Critical Z-score for final analysis
    - z_critical: Critical Z-score for final analysis


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(current_z, float)
    self.validate_data(current_z, float)
    self.validate_data(information_fraction, float, min_value=0.0, max_value=1.0)
    self.validate_data(information_fraction, float, min_value=0.0, max_value=1.0)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)
    self.validate_data(alpha, float, min_value=0.001, max_value=0.5)


    if target_effect is not None:
    if target_effect is not None:
    self.validate_data(target_effect, float)
    self.validate_data(target_effect, float)


    if observed_effect is not None:
    if observed_effect is not None:
    self.validate_data(observed_effect, float)
    self.validate_data(observed_effect, float)


    # Critical Z-score for final analysis
    # Critical Z-score for final analysis
    z_critical = stats.norm.ppf(1 - alpha / 2)
    z_critical = stats.norm.ppf(1 - alpha / 2)


    # Determine effect size to use in calculation
    # Determine effect size to use in calculation
    if target_effect is not None:
    if target_effect is not None:
    effect = target_effect
    effect = target_effect
    elif observed_effect is not None:
    elif observed_effect is not None:
    effect = observed_effect
    effect = observed_effect
    else:
    else:
    # Estimate effect size from current data
    # Estimate effect size from current data
    effect = current_z / np.sqrt(information_fraction)
    effect = current_z / np.sqrt(information_fraction)


    # Calculate conditional power
    # Calculate conditional power
    remaining_info = 1 - information_fraction
    remaining_info = 1 - information_fraction


    # Mean of the distribution of the final Z-score, conditional on current Z
    # Mean of the distribution of the final Z-score, conditional on current Z
    conditional_mean = current_z * np.sqrt(
    conditional_mean = current_z * np.sqrt(
    information_fraction / 1
    information_fraction / 1
    ) + effect * np.sqrt(remaining_info)
    ) + effect * np.sqrt(remaining_info)


    # Standard deviation of the distribution of the final Z-score, conditional on current Z
    # Standard deviation of the distribution of the final Z-score, conditional on current Z
    conditional_sd = np.sqrt(remaining_info)
    conditional_sd = np.sqrt(remaining_info)


    # Calculate probability that final Z > z_critical
    # Calculate probability that final Z > z_critical
    cp_upper = 1 - stats.norm.cdf((z_critical - conditional_mean) / conditional_sd)
    cp_upper = 1 - stats.norm.cdf((z_critical - conditional_mean) / conditional_sd)


    # Calculate probability that final Z < -z_critical
    # Calculate probability that final Z < -z_critical
    cp_lower = stats.norm.cdf((-z_critical - conditional_mean) / conditional_sd)
    cp_lower = stats.norm.cdf((-z_critical - conditional_mean) / conditional_sd)


    # Total conditional power (probability of rejecting null)
    # Total conditional power (probability of rejecting null)
    conditional_power = cp_upper + cp_lower
    conditional_power = cp_upper + cp_lower


    return {
    return {
    "conditional_power": conditional_power,
    "conditional_power": conditional_power,
    "current_z": current_z,
    "current_z": current_z,
    "information_fraction": information_fraction,
    "information_fraction": information_fraction,
    "target_effect": effect,
    "target_effect": effect,
    "observed_effect": (
    "observed_effect": (
    observed_effect
    observed_effect
    if observed_effect is not None
    if observed_effect is not None
    else current_z / np.sqrt(information_fraction)
    else current_z / np.sqrt(information_fraction)
    ),
    ),
    "alpha": alpha,
    "alpha": alpha,
    "z_critical": z_critical,
    "z_critical": z_critical,
    }
    }


    def futility_boundary(
    def futility_boundary(
    self,
    self,
    information_fractions: Union[List[float], np.ndarray],
    information_fractions: Union[List[float], np.ndarray],
    beta: float = 0.2,
    beta: float = 0.2,
    method: str = "obrien_fleming",
    method: str = "obrien_fleming",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate futility boundaries for group sequential testing.
    Calculate futility boundaries for group sequential testing.


    Futility boundaries are used to stop a trial early for lack of efficacy.
    Futility boundaries are used to stop a trial early for lack of efficacy.


    Args:
    Args:
    information_fractions: List or array of information fractions at each look
    information_fractions: List or array of information fractions at each look
    (values between 0 and 1, with the last value typically being 1)
    (values between 0 and 1, with the last value typically being 1)
    beta: Type II error rate (1 - power, default: 0.2)
    beta: Type II error rate (1 - power, default: 0.2)
    method: Method to use for boundary calculation, one of:
    method: Method to use for boundary calculation, one of:
    "obrien_fleming": O'Brien-Fleming-like boundaries (default)
    "obrien_fleming": O'Brien-Fleming-like boundaries (default)
    "pocock": Pocock-like boundaries
    "pocock": Pocock-like boundaries


    Returns:
    Returns:
    Dictionary with futility boundary calculation results including:
    Dictionary with futility boundary calculation results including:
    - futility_boundaries: Z-score boundaries for futility at each look
    - futility_boundaries: Z-score boundaries for futility at each look
    - information_fractions: Information fractions at each look
    - information_fractions: Information fractions at each look
    - num_looks: Number of looks
    - num_looks: Number of looks
    - beta: Type II error rate
    - beta: Type II error rate
    - method: Method used for boundary calculation
    - method: Method used for boundary calculation


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(information_fractions, (list, np.ndarray), min_length=1)
    self.validate_data(information_fractions, (list, np.ndarray), min_length=1)
    self.validate_data(beta, float, min_value=0.001, max_value=0.5)
    self.validate_data(beta, float, min_value=0.001, max_value=0.5)


    if method not in ["obrien_fleming", "pocock"]:
    if method not in ["obrien_fleming", "pocock"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Method must be one of: 'obrien_fleming', 'pocock'"
    "Method must be one of: 'obrien_fleming', 'pocock'"
    )
    )


    # Convert to numpy array for consistent handling
    # Convert to numpy array for consistent handling
    info_fractions = np.array(information_fractions)
    info_fractions = np.array(information_fractions)


    # Check if information fractions are valid
    # Check if information fractions are valid
    if np.any((info_fractions < 0) | (info_fractions > 1)):
    if np.any((info_fractions < 0) | (info_fractions > 1)):
    raise InvalidParameterError("Information fractions must be between 0 and 1")
    raise InvalidParameterError("Information fractions must be between 0 and 1")


    # Check if information fractions are in ascending order
    # Check if information fractions are in ascending order
    if not np.all(np.diff(info_fractions) >= 0):
    if not np.all(np.diff(info_fractions) >= 0):
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Information fractions must be in ascending order"
    "Information fractions must be in ascending order"
    )
    )


    # Number of looks
    # Number of looks
    num_looks = len(info_fractions)
    num_looks = len(info_fractions)


    # Calculate futility boundaries
    # Calculate futility boundaries
    futility_boundaries = np.zeros(num_looks)
    futility_boundaries = np.zeros(num_looks)


    if method == "obrien_fleming":
    if method == "obrien_fleming":
    # O'Brien-Fleming-like futility boundaries
    # O'Brien-Fleming-like futility boundaries
    for i, t in enumerate(info_fractions):
    for i, t in enumerate(info_fractions):
    if t < 1:  # No futility boundary at final analysis
    if t < 1:  # No futility boundary at final analysis
    futility_boundaries[i] = stats.norm.ppf(beta) / np.sqrt(1 - t)
    futility_boundaries[i] = stats.norm.ppf(beta) / np.sqrt(1 - t)
    else:
    else:
    futility_boundaries[i] = float(
    futility_boundaries[i] = float(
    "-in"
    "-in"
    )  # No stopping for futility at final analysis
    )  # No stopping for futility at final analysis
    else:  # method == "pocock"
    else:  # method == "pocock"
    # Pocock-like futility boundaries - constant across all looks
    # Pocock-like futility boundaries - constant across all looks
    z_boundary = stats.norm.ppf(beta)
    z_boundary = stats.norm.ppf(beta)
    futility_boundaries = np.array(
    futility_boundaries = np.array(
    [z_boundary] * (num_looks - 1) + [float("-inf")]
    [z_boundary] * (num_looks - 1) + [float("-inf")]
    )
    )


    return {
    return {
    "futility_boundaries": futility_boundaries.tolist(),
    "futility_boundaries": futility_boundaries.tolist(),
    "information_fractions": info_fractions.tolist(),
    "information_fractions": info_fractions.tolist(),
    "num_looks": num_looks,
    "num_looks": num_looks,
    "beta": beta,
    "beta": beta,
    "method": method,
    "method": method,
    }
    }


    def log_likelihood_ratio_test(
    def log_likelihood_ratio_test(
    self, model1_loglik: float, model2_loglik: float, df1: int, df2: int
    self, model1_loglik: float, model2_loglik: float, df1: int, df2: int
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Perform a log-likelihood ratio test for nested model comparison.
    Perform a log-likelihood ratio test for nested model comparison.


    This test compares two nested models to determine if the more complex model
    This test compares two nested models to determine if the more complex model
    (with more parameters) provides a significantly better fit than the simpler model.
    (with more parameters) provides a significantly better fit than the simpler model.
    The test statistic follows a chi-square distribution with degrees of freedom
    The test statistic follows a chi-square distribution with degrees of freedom
    equal to the difference in the number of parameters between the models.
    equal to the difference in the number of parameters between the models.


    Args:
    Args:
    model1_loglik: Log-likelihood of the simpler model (null model)
    model1_loglik: Log-likelihood of the simpler model (null model)
    model2_loglik: Log-likelihood of the more complex model (alternative model)
    model2_loglik: Log-likelihood of the more complex model (alternative model)
    df1: Degrees of freedom (number of parameters) in the simpler model
    df1: Degrees of freedom (number of parameters) in the simpler model
    df2: Degrees of freedom (number of parameters) in the more complex model
    df2: Degrees of freedom (number of parameters) in the more complex model


    Returns:
    Returns:
    Dictionary with test results including:
    Dictionary with test results including:
    - test_statistic: Log-likelihood ratio test statistic (2 * (loglik2 - loglik1))
    - test_statistic: Log-likelihood ratio test statistic (2 * (loglik2 - loglik1))
    - p_value: P-value for the test
    - p_value: P-value for the test
    - df_diff: Difference in degrees of freedom between models
    - df_diff: Difference in degrees of freedom between models
    - is_significant: Whether the result is significant at alpha level
    - is_significant: Whether the result is significant at alpha level
    - model_selection: Dictionary with model selection criteria (AIC, BIC)
    - model_selection: Dictionary with model selection criteria (AIC, BIC)
    - test_name: Name of the test
    - test_name: Name of the test


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(model1_loglik, float)
    self.validate_data(model1_loglik, float)
    self.validate_data(model2_loglik, float)
    self.validate_data(model2_loglik, float)
    self.validate_data(df1, int, min_value=1)
    self.validate_data(df1, int, min_value=1)
    self.validate_data(df2, int, min_value=1)
    self.validate_data(df2, int, min_value=1)


    if df2 <= df1:
    if df2 <= df1:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "The more complex model (model2) must have more parameters than the simpler model (model1)"
    "The more complex model (model2) must have more parameters than the simpler model (model1)"
    )
    )


    # Calculate test statistic: 2 * (loglik2 - loglik1)
    # Calculate test statistic: 2 * (loglik2 - loglik1)
    # The factor of 2 makes the statistic follow a chi-square distribution
    # The factor of 2 makes the statistic follow a chi-square distribution
    test_statistic = 2 * (model2_loglik - model1_loglik)
    test_statistic = 2 * (model2_loglik - model1_loglik)


    # Calculate degrees of freedom difference
    # Calculate degrees of freedom difference
    df_diff = df2 - df1
    df_diff = df2 - df1


    # Calculate p-value from chi-square distribution
    # Calculate p-value from chi-square distribution
    # We use 1 - cdf because we're testing if test_statistic is significantly large
    # We use 1 - cdf because we're testing if test_statistic is significantly large
    p_value = 1 - stats.chi2.cdf(test_statistic, df_diff)
    p_value = 1 - stats.chi2.cdf(test_statistic, df_diff)


    # Determine significance
    # Determine significance
    is_significant = p_value < self.default_alpha
    is_significant = p_value < self.default_alpha


    # Calculate model selection criteria
    # Calculate model selection criteria
    # AIC = -2 * loglik + 2 * k (where k is the number of parameters)
    # AIC = -2 * loglik + 2 * k (where k is the number of parameters)
    # BIC = -2 * loglik + k * ln(n) (where n is the sample size, which we don't have)
    # BIC = -2 * loglik + k * ln(n) (where n is the sample size, which we don't have)
    # Since we don't have sample size, we'll use a placeholder value of 100
    # Since we don't have sample size, we'll use a placeholder value of 100
    # In practice, the actual sample size should be provided
    # In practice, the actual sample size should be provided
    sample_size = 100  # Placeholder - in real usage, this should be provided
    sample_size = 100  # Placeholder - in real usage, this should be provided


    aic1 = -2 * model1_loglik + 2 * df1
    aic1 = -2 * model1_loglik + 2 * df1
    aic2 = -2 * model2_loglik + 2 * df2
    aic2 = -2 * model2_loglik + 2 * df2


    bic1 = -2 * model1_loglik + df1 * np.log(sample_size)
    bic1 = -2 * model1_loglik + df1 * np.log(sample_size)
    bic2 = -2 * model2_loglik + df2 * np.log(sample_size)
    bic2 = -2 * model2_loglik + df2 * np.log(sample_size)


    # Determine which model is preferred by each criterion
    # Determine which model is preferred by each criterion
    # Lower values of AIC and BIC indicate better models
    # Lower values of AIC and BIC indicate better models
    aic_preferred = "model1" if aic1 < aic2 else "model2"
    aic_preferred = "model1" if aic1 < aic2 else "model2"
    bic_preferred = "model1" if bic1 < bic2 else "model2"
    bic_preferred = "model1" if bic1 < bic2 else "model2"


    # Return results
    # Return results
    return {
    return {
    "test_statistic": test_statistic,
    "test_statistic": test_statistic,
    "p_value": p_value,
    "p_value": p_value,
    "df_dif": df_diff,
    "df_dif": df_diff,
    "df1": df1,
    "df1": df1,
    "df2": df2,
    "df2": df2,
    "loglik1": model1_loglik,
    "loglik1": model1_loglik,
    "loglik2": model2_loglik,
    "loglik2": model2_loglik,
    "is_significant": is_significant,
    "is_significant": is_significant,
    "model_selection": {
    "model_selection": {
    "aic1": aic1,
    "aic1": aic1,
    "aic2": aic2,
    "aic2": aic2,
    "bic1": bic1,
    "bic1": bic1,
    "bic2": bic2,
    "bic2": bic2,
    "aic_preferred": aic_preferred,
    "aic_preferred": aic_preferred,
    "bic_preferred": bic_preferred,
    "bic_preferred": bic_preferred,
    "sample_size_used": sample_size,
    "sample_size_used": sample_size,
    },
    },
    "test_name": "log_likelihood_ratio",
    "test_name": "log_likelihood_ratio",
    "alpha": self.default_alpha,
    "alpha": self.default_alpha,
    }
    }


    def model_selection_criteria(
    def model_selection_criteria(
    self, loglik: float, df: int, sample_size: int
    self, loglik: float, df: int, sample_size: int
    ) -> Dict[str, float]:
    ) -> Dict[str, float]:
    """
    """
    Calculate model selection criteria for a given model.
    Calculate model selection criteria for a given model.


    This method calculates various information criteria used for model selection,
    This method calculates various information criteria used for model selection,
    including AIC (Akaike Information Criterion), BIC (Bayesian Information Criterion),
    including AIC (Akaike Information Criterion), BIC (Bayesian Information Criterion),
    and others.
    and others.


    Args:
    Args:
    loglik: Log-likelihood of the model
    loglik: Log-likelihood of the model
    df: Degrees of freedom (number of parameters) in the model
    df: Degrees of freedom (number of parameters) in the model
    sample_size: Number of observations used to fit the model
    sample_size: Number of observations used to fit the model


    Returns:
    Returns:
    Dictionary with model selection criteria including:
    Dictionary with model selection criteria including:
    - aic: Akaike Information Criterion
    - aic: Akaike Information Criterion
    - bic: Bayesian Information Criterion
    - bic: Bayesian Information Criterion
    - aicc: AIC with correction for small sample sizes
    - aicc: AIC with correction for small sample sizes
    - hqic: Hannan-Quinn Information Criterion
    - hqic: Hannan-Quinn Information Criterion


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(loglik, float)
    self.validate_data(loglik, float)
    self.validate_data(df, int, min_value=1)
    self.validate_data(df, int, min_value=1)
    self.validate_data(sample_size, int, min_value=df + 1)
    self.validate_data(sample_size, int, min_value=df + 1)


    # Calculate AIC: -2 * loglik + 2 * k
    # Calculate AIC: -2 * loglik + 2 * k
    aic = -2 * loglik + 2 * df
    aic = -2 * loglik + 2 * df


    # Calculate BIC: -2 * loglik + k * ln(n)
    # Calculate BIC: -2 * loglik + k * ln(n)
    bic = -2 * loglik + df * np.log(sample_size)
    bic = -2 * loglik + df * np.log(sample_size)


    # Calculate AICc: AIC + (2k(k+1))/(n-k-1)
    # Calculate AICc: AIC + (2k(k+1))/(n-k-1)
    # This is a correction for small sample sizes
    # This is a correction for small sample sizes
    aicc = aic + (2 * df * (df + 1)) / (sample_size - df - 1)
    aicc = aic + (2 * df * (df + 1)) / (sample_size - df - 1)


    # Calculate HQIC: -2 * loglik + 2k * ln(ln(n))
    # Calculate HQIC: -2 * loglik + 2k * ln(ln(n))
    hqic = -2 * loglik + 2 * df * np.log(np.log(sample_size))
    hqic = -2 * loglik + 2 * df * np.log(np.log(sample_size))


    return {
    return {
    "aic": aic,
    "aic": aic,
    "bic": bic,
    "bic": bic,
    "aicc": aicc,
    "aicc": aicc,
    "hqic": hqic,
    "hqic": hqic,
    "loglik": loglik,
    "loglik": loglik,
    "d": df,
    "d": df,
    "sample_size": sample_size,
    "sample_size": sample_size,
    }
    }


    def optional_stopping_correction(
    def optional_stopping_correction(
    self, p_value: float, num_looks: int, method: str = "bonferroni"
    self, p_value: float, num_looks: int, method: str = "bonferroni"
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Apply correction for optional stopping in sequential testing.
    Apply correction for optional stopping in sequential testing.


    This method adjusts p-values to account for multiple looks at the data,
    This method adjusts p-values to account for multiple looks at the data,
    which can inflate Type I error rates.
    which can inflate Type I error rates.


    Args:
    Args:
    p_value: Uncorrected p-value
    p_value: Uncorrected p-value
    num_looks: Number of potential looks at the data
    num_looks: Number of potential looks at the data
    method: Method to use for correction, one of:
    method: Method to use for correction, one of:
    "bonferroni": Bonferroni correction (default)
    "bonferroni": Bonferroni correction (default)
    "sidak": Šidák correction
    "sidak": Šidák correction
    "sequential": Sequential testing correction
    "sequential": Sequential testing correction


    Returns:
    Returns:
    Dictionary with correction results including:
    Dictionary with correction results including:
    - original_p_value: Original uncorrected p-value
    - original_p_value: Original uncorrected p-value
    - adjusted_p_value: P-value adjusted for optional stopping
    - adjusted_p_value: P-value adjusted for optional stopping
    - num_looks: Number of potential looks
    - num_looks: Number of potential looks
    - method: Method used for correction
    - method: Method used for correction


    Raises:
    Raises:
    InvalidParameterError: If inputs are invalid
    InvalidParameterError: If inputs are invalid
    """
    """
    # Validate inputs
    # Validate inputs
    self.validate_data(p_value, float, min_value=0.0, max_value=1.0)
    self.validate_data(p_value, float, min_value=0.0, max_value=1.0)
    self.validate_data(num_looks, int, min_value=1)
    self.validate_data(num_looks, int, min_value=1)


    if method not in ["bonferroni", "sidak", "sequential"]:
    if method not in ["bonferroni", "sidak", "sequential"]:
    raise InvalidParameterError(
    raise InvalidParameterError(
    "Method must be one of: 'bonferroni', 'sidak', 'sequential'"
    "Method must be one of: 'bonferroni', 'sidak', 'sequential'"
    )
    )


    # Initialize result dictionary
    # Initialize result dictionary
    result = {"original_p_value": p_value, "num_looks": num_looks, "method": method}
    result = {"original_p_value": p_value, "num_looks": num_looks, "method": method}


    # Apply the selected correction method
    # Apply the selected correction method
    if method == "bonferroni":
    if method == "bonferroni":
    # Bonferroni correction: p * num_looks
    # Bonferroni correction: p * num_looks
    adjusted_p = min(p_value * num_looks, 1.0)
    adjusted_p = min(p_value * num_looks, 1.0)
    result["adjusted_p_value"] = adjusted_p
    result["adjusted_p_value"] = adjusted_p


    elif method == "sidak":
    elif method == "sidak":
    # Šidák correction: 1 - (1 - p)^num_looks
    # Šidák correction: 1 - (1 - p)^num_looks
    adjusted_p = 1.0 - (1.0 - p_value) ** num_looks
    adjusted_p = 1.0 - (1.0 - p_value) ** num_looks
    result["adjusted_p_value"] = adjusted_p
    result["adjusted_p_value"] = adjusted_p


    else:  # method == "sequential"
    else:  # method == "sequential"
    # Sequential testing correction
    # Sequential testing correction
    # This is an approximation based on the expected maximum of num_looks independent tests
    # This is an approximation based on the expected maximum of num_looks independent tests
    # In practice, more complex calculations would be used
    # In practice, more complex calculations would be used


    # Convert p-value to z-score
    # Convert p-value to z-score
    if p_value > 0:
    if p_value > 0:
    z = stats.norm.ppf(1 - p_value / 2)
    z = stats.norm.ppf(1 - p_value / 2)
    else:
    else:
    z = float("in")
    z = float("in")


    # Adjust z-score for multiple looks
    # Adjust z-score for multiple looks
    # This is based on the expected maximum of num_looks independent standard normal variables
    # This is based on the expected maximum of num_looks independent standard normal variables
    # E[max(Z_1, ..., Z_n)] ≈ sqrt(2 * log(n))
    # E[max(Z_1, ..., Z_n)] ≈ sqrt(2 * log(n))
    adjustment = np.sqrt(2 * np.log(num_looks))
    adjustment = np.sqrt(2 * np.log(num_looks))
    adjusted_z = z - adjustment
    adjusted_z = z - adjustment


    # Convert back to p-value
    # Convert back to p-value
    if adjusted_z < 0:
    if adjusted_z < 0:
    adjusted_p = 1.0
    adjusted_p = 1.0
    else:
    else:
    adjusted_p = 2 * (1 - stats.norm.cdf(adjusted_z))
    adjusted_p = 2 * (1 - stats.norm.cdf(adjusted_z))


    result["adjusted_p_value"] = min(adjusted_p, 1.0)
    result["adjusted_p_value"] = min(adjusted_p, 1.0)
    result["z_score"] = z
    result["z_score"] = z
    result["adjusted_z_score"] = adjusted_z
    result["adjusted_z_score"] = adjusted_z


    return result
    return result