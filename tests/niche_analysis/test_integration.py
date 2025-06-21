from niche_analysis import NicheAnalyzer

def test_run_analysis_returns_opportunities():
    analyzer = NicheAnalyzer()
    results = analyzer.run_analysis(["e-commerce", "content creation"])
    assert isinstance(results, list)
    assert len(results) > 0
    for opp in results:
        assert hasattr(opp, "overall_score")
        assert 0.0 <= opp.overall_score <= 1.0