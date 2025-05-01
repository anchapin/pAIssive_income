"""
Simple test runner for market analysis tests.
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import test modules
from tests.market_analysis.test_competitive_intelligence import (
    TestCompetitiveIntelligence,
    TestRealTimeCompetitorMonitoring,
    TestCompetitorPricingChangeDetection,
    TestFeatureComparisonMatrixGeneration
)
from tests.market_analysis.test_market_trends import (
    TestMarketTrendAnalysis,
    TestSeasonalPatternDetectionWithIrregularIntervals,
    TestHandlingMissingDataPointsInTrendAnalysis,
    TestMultiYearSeasonalTrendComparison
)

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()

    # Create a test loader
    loader = unittest.TestLoader()

    # Add test cases from competitive intelligence tests
    test_suite.addTest(loader.loadTestsFromTestCase(TestCompetitiveIntelligence))
    test_suite.addTest(loader.loadTestsFromTestCase(TestRealTimeCompetitorMonitoring))
    test_suite.addTest(loader.loadTestsFromTestCase(TestCompetitorPricingChangeDetection))
    test_suite.addTest(loader.loadTestsFromTestCase(TestFeatureComparisonMatrixGeneration))

    # Add test cases from market trends tests
    test_suite.addTest(loader.loadTestsFromTestCase(TestMarketTrendAnalysis))
    test_suite.addTest(loader.loadTestsFromTestCase(TestSeasonalPatternDetectionWithIrregularIntervals))
    test_suite.addTest(loader.loadTestsFromTestCase(TestHandlingMissingDataPointsInTrendAnalysis))
    test_suite.addTest(loader.loadTestsFromTestCase(TestMultiYearSeasonalTrendComparison))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Exit with appropriate status code
    sys.exit(not result.wasSuccessful())
