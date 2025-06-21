"""
Test agent collaboration workflow (no CrewAI/mem0).
"""

from agent_team.agent_profiles.researcher import ResearcherAgent
from agent_team.agent_profiles.developer import DeveloperAgent
from agent_team.agent_profiles.monetization import MonetizationAgent

def test_minimal_agent_workflow():
    researcher = ResearcherAgent(goal="Find market niche", backstory="Foresight analyst.")
    dev = DeveloperAgent(goal="Build prototype", backstory="Backend specialist.")
    monetizer = MonetizationAgent(goal="Monetize MVP", backstory="Product manager.")

    research = researcher.identify_niche("productivity automation")
    assert "niche" in research
    niche = research["niche"]

    solution = dev.design_solution(niche)
    assert solution["niche"] == niche
    assert "solution" in solution

    plan = monetizer.build_plan(solution["solution"])
    assert "plan" in plan
    assert niche.split()[0] in solution["solution"]
    assert "subscription" in plan["plan"]