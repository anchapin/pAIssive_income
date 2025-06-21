"""Orchestrator for full niche opportunity analysis."""

from .market_analyzer import MarketAnalyzer
from .problem_identifier import ProblemIdentifier
from .opportunity_scorer import OpportunityScorer
from .schemas import OpportunityScore

class NicheAnalyzer:
    """Runs full pipeline analysis across a list of market segments."""

    def __init__(self):
        self.market_analyzer = MarketAnalyzer()
        self.problem_identifier = ProblemIdentifier()
        self.opportunity_scorer = OpportunityScorer()

    def run_analysis(self, market_segments: list[str]) -> list[OpportunityScore]:
        """Run end-to-end analysis for all potential niches in provided segments.

        Returns a flat list of scored opportunities.
        """
        opportunities: list[OpportunityScore] = []
        for segment in market_segments:
            segment_analysis = self.market_analyzer.analyze_segment(segment)
            potential_niches = getattr(segment_analysis, "potential_niches", [])
            for niche in potential_niches:
                market_data = self.market_analyzer.analyze_competition(niche)
                problems = self.problem_identifier.identify_problems(niche)
                opportunity = self.opportunity_scorer.score_opportunity(
                    niche, market_data.__dict__, problems
                )
                opportunities.append(opportunity)
        return opportunities
