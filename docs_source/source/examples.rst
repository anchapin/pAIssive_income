.. _examples:

Examples
=======

This section provides practical examples for using pAIssive_income in various scenarios.

Niche Analysis Workflow
---------------------

This example demonstrates how to use the Niche Analysis module to identify promising niches:

.. code-block: python

    from pAIssive_income.niche_analysis import OpportunityAnalyzer, MarketResearch
    
    # Initialize market research component
    market_research = MarketResearch()
    
    # Research market trends for AI in education
    trends = market_research.analyze_trends("AI in education")
    print(f"Top trends in AI education: {trends[:3]}")
    
    # Initialize opportunity analyzer
    analyzer = OpportunityAnalyzer()
    
    # Analyze multiple niches
    niches = [
        "AI writing assistants for students",
        "Automated grading systems for teachers",
        "Personalized learning platforms"
    ]
    
    results = []
    for niche in niches:
        analysis = analyzer.analyze_niche(niche)
        results.append({
            "niche": niche,
            "score": analysis.opportunity_score,
            "market_size": analysis.market_data.market_size,
            "competition": analysis.market_data.competition,
            "problems": [p.name for p in analysis.problems[:3]]
        })
    
    # Sort by opportunity score
    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
    
    print("Top opportunity:")
    print(f"Niche: {sorted_results[0]['niche']}")
    print(f"Score: {sorted_results[0]['score']}")
    print(f"Market size: {sorted_results[0]['market_size']}")
    print(f"Competition: {sorted_results[0]['competition']}")
    print(f"Key problems: {', '.join(sorted_results[0]['problems'])}")

Solution Development Workflow
---------------------------

This example shows how to generate solution ideas for a specific niche:

.. code-block: python

    from pAIssive_income.niche_analysis import ProblemIdentifier, SolutionGenerator
    
    # Initialize problem identifier
    problem_id = ProblemIdentifier()
    
    # Identify problems in a specific niche
    niche = "AI productivity tools for writers"
    problems = problem_id.identify_problems(niche)
    
    print(f"Identified {len(problems)} problems in '{niche}':")
    for i, problem in enumerate(problems[:5], 1):
        print(f"{i}. {problem.name}: {problem.description} (Severity: {problem.severity})")
    
    # Initialize solution generator
    solution_gen = SolutionGenerator()
    
    # Generate solutions for each problem
    all_solutions = []
    for problem in problems[:3]:  # Focus on top 3 problems
        solutions = solution_gen.generate_solutions(problem)
        print(f"\nSolutions for {problem.name}:")
        for i, solution in enumerate(solutions[:2], 1):  # Show top 2 solutions per problem
            print(f"{i}. {solution.name}")
            print(f"   Description: {solution.description}")
            print(f"   Features: {', '.join([f.name for f in solution.features[:3]])}")
            all_solutions.append(solution)
    
    # Select best solution
    best_solution = max(all_solutions, key=lambda s: len(s.features))
    print(f"\nBest solution: {best_solution.name}")

Monetization Strategy Workflow
----------------------------

This example demonstrates how to develop monetization strategies:

.. code-block: python

    from pAIssive_income.monetization import BillingCalculator, Calculator
    from decimal import Decimal
    
    # Define solution costs and target margins
    costs = {
        "development": Decimal("50000"),
        "infrastructure": Decimal("1000"),  # Monthly
        "support": Decimal("2000"),         # Monthly
        "marketing": Decimal("3000")        # Monthly
    }
    
    target_margin = Decimal("0.6")  # 60% profit margin
    
    # Initialize billing calculator
    billing_calc = BillingCalculator()
    
    # Calculate subscription pricing tiers
    pricing_tiers = billing_calc.calculate_pricing_tiers(
        costs=costs,
        target_margin=target_margin,
        tiers=["Basic", "Pro", "Business"],
        feature_distribution={
            "Basic": 0.4,    # 40% of features
            "Pro": 0.7,      # 70% of features
            "Business": 1.0  # 100% of features
        }
    )
    
    print("Recommended Pricing Tiers:")
    for tier in pricing_tiers:
        print(f"{tier.name}: ${tier.price_monthly}/month (${tier.price_annually}/year)")
        print(f"  Features: {len(tier.features)}")
        print(f"  Break-even subscribers: {tier.break_even_subscribers}")
    
    # Calculate revenue projections
    calculator = Calculator()
    projections = calculator.project_revenue(
        pricing_tiers=pricing_tiers,
        subscriber_growth_rate=Decimal("0.1"),  # 10% monthly growth
        initial_subscribers={
            "Basic": 100,
            "Pro": 50,
            "Business": 10
        },
        months=24
    )
    
    print("\nRevenue Projections:")
    print(f"Month 6: ${projections[5].total_revenue}")
    print(f"Month 12: ${projections[11].total_revenue}")
    print(f"Month 24: ${projections[23].total_revenue}")

Marketing Campaign Workflow
-------------------------

This example shows how to create marketing strategies and content:

.. code-block: python

    from pAIssive_income.marketing import StrategyGenerator, ContentGenerator, UserPersonas
    
    # Define solution
    solution = {
        "name": "WriterGPT",
        "description": "AI-powered writing assistant for authors and content creators",
        "features": [
            "Content outline generation",
            "Style analysis and suggestions",
            "Grammar and readability checks",
            "SEO optimization"
        ],
        "pricing": {
            "tiers": [
                {"name": "Basic", "price": "9.99", "features": ["Content outline generation"]},
                {"name": "Pro", "price": "19.99", "features": ["Content outline generation", "Style analysis", "Grammar checks"]},
                {"name": "Business", "price": "39.99", "features": ["All features", "Priority support", "Team collaboration"]}
            ]
        }
    }
    
    # Define target audience
    personas = UserPersonas()
    target_personas = personas.generate_personas(solution, num_personas=3)
    
    # Initialize strategy generator
    strategy_gen = StrategyGenerator()
    
    # Generate marketing strategy
    marketing_strategy = strategy_gen.generate_strategy(solution, target_personas)
    
    print(f"Marketing Strategy for {solution['name']}:")
    print(f"Channels: {', '.join(marketing_strategy.channels)}")
    print(f"Key messaging: {marketing_strategy.key_messaging}")
    print(f"Budget allocation: {marketing_strategy.budget_allocation}")
    
    # Initialize content generator
    content_gen = ContentGenerator()
    
    # Generate content for various channels
    channels = ["blog", "social_media", "email"]
    for channel in channels:
        content = content_gen.generate_content(
            solution=solution,
            marketing_strategy=marketing_strategy,
            channel=channel,
            persona=target_personas[0]  # Target the primary persona
        )
        
        print(f"\n{channel.upper()} Content:")
        print(f"Title: {content.title}")
        print(f"Summary: {content.summary}")
        print(f"Call to action: {content.call_to_action}")

End-to-End Example
---------------

This example demonstrates an end-to-end workflow from niche analysis to marketing:

.. code-block: python

    from pAIssive_income import niche_analysis, ai_models, monetization, marketing
    
    # 1. Niche Analysis
    analyzer = niche_analysis.OpportunityAnalyzer()
    niche_result = analyzer.analyze_niche("AI productivity tools for developers")
    
    print(f"Niche Analysis: {niche_result.name}")
    print(f"Opportunity Score: {niche_result.opportunity_score}")
    
    # 2. Generate Solution
    solution_gen = niche_analysis.SolutionGenerator()
    solutions = solution_gen.generate_solutions(niche_result)
    selected_solution = solutions[0]  # Pick the first solution
    
    print(f"\nSelected Solution: {selected_solution.name}")
    print(f"Description: {selected_solution.description}")
    
    # 3. Monetization Strategy
    billing_calc = monetization.BillingCalculator()
    costs = {
        "development": 40000,
        "infrastructure": 800,
        "support": 1500,
        "marketing": 2500
    }
    
    pricing_tiers = billing_calc.calculate_pricing_tiers(
        costs=costs,
        target_margin=0.5,
        tiers=["Free", "Pro", "Enterprise"]
    )
    
    print("\nPricing Strategy:")
    for tier in pricing_tiers:
        print(f"- {tier.name}: ${tier.price_monthly}/month")
    
    # 4. Marketing Strategy
    personas = marketing.UserPersonas().generate_personas(selected_solution)
    strategy = marketing.StrategyGenerator().generate_strategy(selected_solution, personas)
    
    print("\nMarketing Strategy:")
    print(f"Channels: {', '.join(strategy.channels)}")
    print(f"Target audience: {strategy.target_audience}")
    
    # 5. Generate Marketing Content
    content_gen = marketing.ContentGenerator()
    blog_post = content_gen.generate_content(
        solution=selected_solution,
        marketing_strategy=strategy,
        channel="blog"
    )
    
    print("\nBlog Post Title: " + blog_post.title)
    print("Intro: " + blog_post.content[:100] + "...")