"""Implements ProblemIdentifier for niche problem discovery and severity analysis."""

from __future__ import annotations
from typing import List, Dict
from datetime import datetime

from .schemas import Problem, ProblemSeverityAnalysis
from .errors import InvalidInputError

class ProblemIdentifier:
    """Identifies problems and pain points in a niche."""

    # Pre-defined problems for some known niches (case-insensitive keys)
    _NICHE_PROBLEMS: Dict[str, List[Dict]] = {
        "inventory management for small e-commerce": [
            {
                "name": "Overstocking",
                "description": "Small e-commerce businesses often overstock inventory, tying up capital",
                "consequences": [
                    "capital inefficiency",
                    "storage costs",
                    "product obsolescence",
                ],
                "severity": "high",
                "current_solutions": {
                    "manual_processes": "Users currently solve this manually",
                    "general_tools": "Users currently use general-purpose tools",
                    "outsourcing": "Users currently outsource this task",
                },
                "solution_gaps": {
                    "automation": "Current solutions lack automation",
                    "specialization": "Current solutions are not specialized for this niche",
                    "integration": "Current solutions don't integrate with other tools",
                },
            },
            {
                "name": "Stockouts",
                "description": "Running out of stock results in lost sales and unhappy customers",
                "consequences": [
                    "lost revenue",
                    "customer churn",
                    "damaged reputation",
                ],
                "severity": "high",
                "current_solutions": {
                    "manual_reordering": "Manual tracking and reordering",
                    "spreadsheet_tracking": "Basic spreadsheet tools",
                },
                "solution_gaps": {
                    "real_time_alerts": "No real-time stockout alerts",
                    "forecasting": "Lack of demand forecasting",
                },
            }
        ],
        "youtube script generation": [
            {
                "name": "Writer's block",
                "description": "Creators struggle to consistently generate engaging scripts",
                "consequences": ["irregular upload schedule", "lowered audience engagement"],
                "severity": "medium",
                "current_solutions": {
                    "reuse_old_scripts": "Reusing previous scripts/templates",
                    "manual_brainstorming": "Manual brainstorming sessions",
                },
                "solution_gaps": {
                    "creativity_boost": "No AI creativity boost",
                    "automation": "No automation for idea generation",
                },
            }
        ],
        "freelance proposal writing": [
            {
                "name": "Low response rate",
                "description": "Freelancers receive few replies to proposals",
                "consequences": ["revenue loss", "low project win rate"],
                "severity": "medium",
                "current_solutions": {
                    "generic_templates": "Use of generic templates",
                    "manual_customization": "Manual customization for each client",
                },
                "solution_gaps": {
                    "personalization": "Lack of personalization at scale",
                    "analytics": "Limited analytics on proposal effectiveness",
                },
            }
        ]
    }

    # Domain-generic fallback problems by keyword
    _GENERIC_PROBLEMS = {
        "e-commerce": [
            {
                "name": "Long order processing times",
                "description": "Manual order processes increase fulfillment time",
                "consequences": ["customer churn", "mistakes", "delayed shipping"],
                "severity": "medium",
                "current_solutions": {"manual": "Mostly manual"},
                "solution_gaps": {"automation": "Few automated solutions"},
            },
        ],
        "content": [
            {
                "name": "Content fatigue",
                "description": "Difficult to generate new, unique content regularly",
                "consequences": ["audience disengagement", "brand stagnation"],
                "severity": "medium",
                "current_solutions": {"repurposing": "Repurposing old content"},
                "solution_gaps": {"originality": "Originality tools lacking"},
            },
        ],
        "freelance": [
            {
                "name": "Payment delays",
                "description": "Freelancers face slow or late payments from clients",
                "consequences": ["cash flow issues"],
                "severity": "medium",
                "current_solutions": {"manual_chasing": "Manual invoice chasing"},
                "solution_gaps": {"automation": "No automated follow-up"},
            },
        ],
        "generic": [
            {
                "name": "Time management",
                "description": "Users struggle to organize and prioritize tasks",
                "consequences": ["missed deadlines", "stress"],
                "severity": "low",
                "current_solutions": {"to_do_list": "Basic to-do lists"},
                "solution_gaps": {"personalization": "Lack of personalized suggestions"},
            }
        ]
    }

    def identify_problems(self, niche: str) -> List[Problem]:
        """Identify problems and pain points in a given niche.

        Returns a list of Problem models.
        """
        if not niche or not isinstance(niche, str):
            raise InvalidInputError("niche must be a non-empty string")
        now = datetime.utcnow()

        problems = self._NICHE_PROBLEMS.get(niche.lower())
        if problems:
            return [
                Problem(
                    name=p["name"],
                    description=p["description"],
                    consequences=p["consequences"],
                    severity=p["severity"],  # type: ignore
                    current_solutions=p["current_solutions"],
                    solution_gaps=p["solution_gaps"],
                    timestamp=now,
                )
                for p in problems
            ]

        n = niche.lower()
        # Keyword fallback
        if "e-commerce" in n or "ecommerce" in n:
            domain_key = "e-commerce"
        elif "content" in n or "writing" in n:
            domain_key = "content"
        elif "freelance" in n or "freelancing" in n:
            domain_key = "freelance"
        else:
            domain_key = "generic"
        generic_problems = self._GENERIC_PROBLEMS[domain_key]
        return [
            Problem(
                name=p["name"],
                description=p["description"],
                consequences=p["consequences"],
                severity=p["severity"],  # type: ignore
                current_solutions=p["current_solutions"],
                solution_gaps=p["solution_gaps"],
                timestamp=now,
            )
            for p in generic_problems
        ]

    def analyze_problem_severity(self, problem: Problem) -> ProblemSeverityAnalysis:
        """Return a detailed analysis of the severity of a given problem."""
        if not isinstance(problem, Problem):
            raise InvalidInputError("problem must be a Problem model")

        mapping = {
            "high": {
                "impact_on_users": "Significant negative impact",
                "frequency": "Frequently experienced",
                "emotional_response": "High frustration",
                "business_impact": "Significant revenue loss",
                "urgency": "Immediate solution needed",
                "potential_impact_of_solution": "High impact",
                "user_willingness_to_pay": "High willingness to pay",
            },
            "medium": {
                "impact_on_users": "Moderate negative impact",
                "frequency": "Occasionally experienced",
                "emotional_response": "Moderate frustration",
                "business_impact": "Moderate revenue loss",
                "urgency": "Solution needed in near term",
                "potential_impact_of_solution": "Medium impact",
                "user_willingness_to_pay": "Medium willingness to pay",
            },
            "low": {
                "impact_on_users": "Minor negative impact",
                "frequency": "Rarely experienced",
                "emotional_response": "Minor annoyance",
                "business_impact": "Minimal revenue loss",
                "urgency": "Solution beneficial but not urgent",
                "potential_impact_of_solution": "Low impact",
                "user_willingness_to_pay": "Low willingness to pay",
            }
        }
        sev = problem.severity
        detail = mapping.get(sev, mapping["low"])
        analysis_dict = {
            "impact_on_users": detail["impact_on_users"],
            "frequency": detail["frequency"],
            "emotional_response": detail["emotional_response"],
            "business_impact": detail["business_impact"],
            "urgency": detail["urgency"],
        }
        return ProblemSeverityAnalysis(
            severity=sev,
            analysis=analysis_dict,
            potential_impact_of_solution=detail["potential_impact_of_solution"],
            user_willingness_to_pay=detail["user_willingness_to_pay"],
        )