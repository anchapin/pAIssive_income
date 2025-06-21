"""
Unit tests for agent_team agent profiles.
"""

import pytest

from agent_team.agent_profiles.developer import DeveloperAgent
from agent_team.agent_profiles.researcher import ResearcherAgent
from agent_team.agent_profiles.monetization import MonetizationAgent
from agent_team.agent_profiles.marketing import MarketingAgent
from agent_team.agent_profiles.feedback import FeedbackAgent

def test_developer_agent_design_solution():
    dev = DeveloperAgent(goal="Build MVP", backstory="Experienced software engineer.")
    result = dev.design_solution("e-commerce")
    assert result == {
        "niche": "e-commerce",
        "solution": "Design a minimal MVP web app for 'e-commerce'."
    }
    assert dev.to_dict()["role"] == "developer"
    assert "goal" in dev.to_dict()
    assert str(dev).startswith("DeveloperAgent(")

def test_researcher_agent_identify_niche_keywords():
    researcher = ResearcherAgent(goal="Find market opportunity", backstory="Tech analyst.")
    result = researcher.identify_niche("blockchain automation")
    assert "AI-powered Blockchain" in result["niche"]
    assert researcher.to_dict()["role"] == "researcher"
    assert "goal" in researcher.to_dict()

def test_monetization_agent_build_plan():
    monetizer = MonetizationAgent(goal="Create revenue streams", backstory="Startup CFO.")
    plan = monetizer.build_plan("MVP web app")
    assert "subscription model" in plan["plan"]
    assert monetizer.estimate_revenue(3) == 3 * monetizer.DEFAULT_MONTHLY_REVENUE_ESTIMATE

def test_monetization_agent_default_monthly_estimate():
    monetizer = MonetizationAgent(goal="Create revenue streams", backstory="Startup CFO.")
    assert monetizer.estimate_revenue() == 6 * monetizer.DEFAULT_MONTHLY_REVENUE_ESTIMATE  # 6 is default months in agent

def test_researcher_agent_identify_niche_empty():
    researcher = ResearcherAgent(goal="Find market opportunity", backstory="Tech analyst.")
    result = researcher.identify_niche("")
    assert result["niche"] == "AI-powered General Platform"

def test_marketing_agent_create_campaign():
    marketer = MarketingAgent(goal="Drive user adoption", backstory="Growth hacker.")
    campaign = marketer.create_campaign("AI MVP")
    assert "Launch campaign" in campaign["campaign"]
    assert marketer.analyze_audience("AI MVP").startswith("Target audience")

def test_feedback_agent_collect_analyze():
    feedbacker = FeedbackAgent(goal="Collect user insights", backstory="UX researcher.")
    fb = feedbacker.collect_feedback("AI MVP")
    assert "easy to use" in fb["feedback"]
    analysis = feedbacker.analyze_feedback("Great product!")
    assert "positive" in analysis