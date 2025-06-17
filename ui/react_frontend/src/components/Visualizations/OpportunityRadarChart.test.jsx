/**
 * Tests for the OpportunityRadarChart component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import OpportunityRadarChart from './OpportunityRadarChart';

describe('OpportunityRadarChart', () => {
  const singleOpportunity = {
    niche: 'AI Tools',
    factors: {
      market_size: 0.9,
      growth_rate: 0.8,
      competition: 0.6,
      problem_severity: 0.7,
      solution_feasibility: 0.5,
      monetization_potential: 0.8
    }
  };

  const multiOpportunities = [
    {
      niche: 'AI Tools',
      factors: {
        market_size: 0.9,
        growth_rate: 0.8,
        competition: 0.6,
        problem_severity: 0.7,
        solution_feasibility: 0.5,
        monetization_potential: 0.8
      }
    },
    {
      niche: 'E-commerce',
      factors: {
        market_size: 0.7,
        growth_rate: 0.6,
        competition: 0.4,
        problem_severity: 0.6,
        solution_feasibility: 0.4,
        monetization_potential: 0.6
      }
    }
  ];

  it('renders chart title and radar for a single opportunity', () => {
    render(<OpportunityRadarChart data={singleOpportunity} title="Opportunity Factor Analysis" />);
    expect(screen.getByText(/Opportunity Factor Analysis/i)).toBeInTheDocument();
    expect(screen.getByText(/Market Size/i)).toBeInTheDocument();
    expect(screen.getByText(/Growth Rate/i)).toBeInTheDocument();
    expect(screen.getByText(/Competition/i)).toBeInTheDocument();
    expect(screen.getByText(/Problem Severity/i)).toBeInTheDocument();
    expect(screen.getByText(/Solution Feasibility/i)).toBeInTheDocument();
    expect(screen.getByText(/Monetization Potential/i)).toBeInTheDocument();
  });

  it('renders SVG radar chart and legend for single opportunity', () => {
    const { container } = render(<OpportunityRadarChart data={singleOpportunity} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
    expect(screen.getByText(/Opportunity Score/i)).toBeInTheDocument();
  });

  it('renders multiple opportunities for comparison', () => {
    render(<OpportunityRadarChart data={multiOpportunities} />);
    expect(screen.getByText('AI Tools')).toBeInTheDocument();
    expect(screen.getByText('E-commerce')).toBeInTheDocument();
    // Should render radar legend for all six factors
    expect(screen.getByText(/Market Size/i)).toBeInTheDocument();
    expect(screen.getByText(/Growth Rate/i)).toBeInTheDocument();
    expect(screen.getByText(/Competition/i)).toBeInTheDocument();
    expect(screen.getByText(/Problem Severity/i)).toBeInTheDocument();
    expect(screen.getByText(/Solution Feasibility/i)).toBeInTheDocument();
    expect(screen.getByText(/Monetization Potential/i)).toBeInTheDocument();
  });

  it('renders gracefully with missing/empty data', () => {
    const { container } = render(<OpportunityRadarChart data={[]} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});