"""
Routes for the pAIssive Income UI.

This module defines the routes for the web interface, handling requests
for different parts of the application.
"""

from flask import render_template, request, jsonify, redirect, url_for, session, flash
import os
import json
import logging
from datetime import datetime
import uuid

from . import app
from .services import AgentTeamService, NicheAnalysisService, DeveloperService, MonetizationService, MarketingService

# Set up logging
logger = logging.getLogger(__name__)

# Services
agent_team_service = AgentTeamService()
niche_analysis_service = NicheAnalysisService()
developer_service = DeveloperService()
monetization_service = MonetizationService()
marketing_service = MarketingService()

# Home route
@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html', 
                          title='pAIssive Income Framework',
                          description='A comprehensive framework for developing and monetizing niche AI agents')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    """Render the dashboard page."""
    # Get project data
    projects = agent_team_service.get_projects()
    
    return render_template('dashboard.html', 
                          title='Dashboard',
                          projects=projects)

# Niche Analysis routes
@app.route('/niche-analysis')
def niche_analysis():
    """Render the niche analysis page."""
    # Get market segments
    market_segments = niche_analysis_service.get_market_segments()
    
    return render_template('niche_analysis.html', 
                          title='Niche Analysis',
                          market_segments=market_segments)

@app.route('/niche-analysis/run', methods=['POST'])
def run_niche_analysis():
    """Run niche analysis on selected market segments."""
    # Get selected market segments from form
    market_segments = request.form.getlist('market_segments')
    
    # Run niche analysis
    niches = niche_analysis_service.analyze_niches(market_segments)
    
    # Store results in session
    session['niches'] = niches
    
    return redirect(url_for('niche_results'))

@app.route('/niche-analysis/results')
def niche_results():
    """Render the niche analysis results page."""
    # Get niches from session
    niches = session.get('niches', [])
    
    return render_template('niche_results.html', 
                          title='Niche Analysis Results',
                          niches=niches)

# Developer routes
@app.route('/developer')
def developer():
    """Render the developer page."""
    # Get niches
    niches = niche_analysis_service.get_niches()
    
    return render_template('developer.html', 
                          title='Solution Development',
                          niches=niches)

@app.route('/developer/solution', methods=['POST'])
def develop_solution():
    """Develop a solution for a selected niche."""
    # Get selected niche from form
    niche_id = request.form.get('niche_id')
    
    # Develop solution
    solution = developer_service.develop_solution(niche_id)
    
    # Store results in session
    session['solution'] = solution
    
    return redirect(url_for('solution_results'))

@app.route('/developer/results')
def solution_results():
    """Render the solution results page."""
    # Get solution from session
    solution = session.get('solution', {})
    
    return render_template('solution_results.html', 
                          title='Solution Results',
                          solution=solution)

# Monetization routes
@app.route('/monetization')
def monetization():
    """Render the monetization page."""
    # Get solutions
    solutions = developer_service.get_solutions()
    
    return render_template('monetization.html', 
                          title='Monetization Strategy',
                          solutions=solutions)

@app.route('/monetization/strategy', methods=['POST'])
def create_monetization_strategy():
    """Create a monetization strategy for a selected solution."""
    # Get selected solution from form
    solution_id = request.form.get('solution_id')
    
    # Create monetization strategy
    strategy = monetization_service.create_strategy(solution_id)
    
    # Store results in session
    session['monetization_strategy'] = strategy
    
    return redirect(url_for('monetization_results'))

@app.route('/monetization/results')
def monetization_results():
    """Render the monetization results page."""
    # Get monetization strategy from session
    strategy = session.get('monetization_strategy', {})
    
    return render_template('monetization_results.html', 
                          title='Monetization Strategy Results',
                          strategy=strategy)

# Marketing routes
@app.route('/marketing')
def marketing():
    """Render the marketing page."""
    # Get solutions
    solutions = developer_service.get_solutions()
    
    return render_template('marketing.html', 
                          title='Marketing Campaign',
                          solutions=solutions)

@app.route('/marketing/campaign', methods=['POST'])
def create_marketing_campaign():
    """Create a marketing campaign for a selected solution."""
    # Get selected solution from form
    solution_id = request.form.get('solution_id')
    
    # Create marketing campaign
    campaign = marketing_service.create_campaign(solution_id)
    
    # Store results in session
    session['marketing_campaign'] = campaign
    
    return redirect(url_for('marketing_results'))

@app.route('/marketing/results')
def marketing_results():
    """Render the marketing results page."""
    # Get marketing campaign from session
    campaign = session.get('marketing_campaign', {})
    
    return render_template('marketing_results.html', 
                          title='Marketing Campaign Results',
                          campaign=campaign)

# About route
@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html', 
                          title='About pAIssive Income Framework')

# API routes
@app.route('/api/niches', methods=['GET'])
def api_get_niches():
    """API endpoint to get niches."""
    niches = niche_analysis_service.get_niches()
    return jsonify(niches)

@app.route('/api/solutions', methods=['GET'])
def api_get_solutions():
    """API endpoint to get solutions."""
    solutions = developer_service.get_solutions()
    return jsonify(solutions)

@app.route('/api/monetization-strategies', methods=['GET'])
def api_get_monetization_strategies():
    """API endpoint to get monetization strategies."""
    strategies = monetization_service.get_strategies()
    return jsonify(strategies)

@app.route('/api/marketing-campaigns', methods=['GET'])
def api_get_marketing_campaigns():
    """API endpoint to get marketing campaigns."""
    campaigns = marketing_service.get_campaigns()
    return jsonify(campaigns)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('errors/404.html', title='Page Not Found'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {e}")
    return render_template('errors/500.html', title='Server Error'), 500
