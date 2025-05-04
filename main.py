"""
"""
Main script for the pAIssive Income project.
Main script for the pAIssive Income project.
Demonstrates how to use the framework to identify niches and develop AI tools.
Demonstrates how to use the framework to identify niches and develop AI tools.
"""
"""




from agent_team import AgentTeam
from agent_team import AgentTeam




def main():
    def main():
    ():
    ():
    """Main function to demonstrate the pAIssive Income framework."""
    print("=" * 80)
    print("pAIssive Income Framework Demo")
    print("=" * 80)

    # Create the agent team
    team = AgentTeam("Niche AI Tools")
    print(f"Created agent team: {team}")

    # Define market segments to analyze
    market_segments = [
    "e-commerce",
    "content creation",
    "freelancing",
    "education",
    "real estate",
    ]
    print(
    f"\nAnalyzing {len(market_segments)} market segments: {', '.join(market_segments)}"
    )

    # Run niche analysis
    niches = team.run_niche_analysis(market_segments)
    print(f"\nIdentified {len(niches)} potential niches:")
    for i, niche in enumerate(niches):
    print(f"{i+1}. {niche['name']} (Score: {niche['opportunity_score']:.2f})")

    # Select the top niche
    top_niche = niches[0]
    print(
    f"\nSelected top niche: {top_niche['name']} (Score: {top_niche['opportunity_score']:.2f})"
    )
    print(f"Description: {top_niche['description']}")
    print(f"Problem areas: {', '.join(top_niche['problem_areas'])}")

    # Develop a solution for the top niche
    solution = team.develop_solution(top_niche["id"])
    print(f"\nDeveloped solution: {solution['name']}")
    print(f"Description: {solution['description']}")
    print(
    f"Architecture: {solution['architecture']['type']} with {solution['architecture']['frontend']} frontend and {solution['architecture']['backend']} backend"
    )

    print("\nFeatures:")
    for i, feature in enumerate(solution["features"]):
    print(f"{i+1}. {feature['name']} - {feature['description']}")

    # Create a monetization strategy
    monetization = team.create_monetization_strategy()
    print("\nMonetization Strategy:")
    print("Subscription Tiers:")
    for tier in monetization["subscription_tiers"]:
    print(
    f"- {tier['name']}: ${tier['price_monthly']}/month or ${tier['price_yearly']}/year"
    )

    print("\nRevenue Projections:")
    for year, projection in monetization["revenue_projections"].items():
    print(
    f"- {year.replace('_', ' ').title()}: {projection['users']} users, ${projection['revenue']} revenue"
    )

    # Create a marketing plan
    marketing = team.create_marketing_plan()
    print("\nMarketing Plan:")
    print("Target Personas:")
    for persona in marketing["user_personas"]:
    print(f"- {persona['name']}: {persona['description']}")

    print("\nMarketing Channels:")
    for channel in marketing["marketing_channels"]:
    print(f"- {channel['name']}: {channel['description']}")

    # Export the project plan
    output_path = "project_plan.json"
    team.export_project_plan(output_path)
    print(f"\nExported project plan to {output_path}")

    print("\n" + "=" * 80)
    print("Demo Complete")
    print("=" * 80)


    if __name__ == "__main__":
    main()