/**
 * Tests for the OpportunityBarChart component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import OpportunityBarChart from './OpportunityBarChart';

describe('OpportunityBarChart', () => {
  const mockData = [
    { niche: 'AI Tools', overall_score: 0.9 },
    { niche: 'E-commerce', overall_score: 0.65 },
    { niche: 'Blogging', overall_score: 0.32 },
    { niche: 'Dropshipping', overall_score: 0.15 },
    { niche: 'Podcasts', overall_score: 0.45 },
  ];

  it('shows "No data available" if no data is passed', () => {
    render(<OpportunityBarChart data={[]} />);
    expect(screen.getByText(/No data available/i)).toBeInTheDocument();
  });

  it('renders chart title, legend, and axis labels', () => {
    render(<OpportunityBarChart data={mockData} title="Opportunity Score Comparison" dataKey="overall_score" />);
    expect(screen.getByText(/Opportunity Score Comparison/i)).toBeInTheDocument();
    expect(screen.getByText(/Overall Score/i)).toBeInTheDocument();
    // All niches
    expect(screen.getByText('AI Tools')).toBeInTheDocument();
    expect(screen.getByText('E-commerce')).toBeInTheDocument();
    expect(screen.getByText('Blogging')).toBeInTheDocument();
    expect(screen.getByText('Dropshipping')).toBeInTheDocument();
    expect(screen.getByText('Podcasts')).toBeInTheDocument();
  });

  it('renders SVG bar chart elements and colored bars', () => {
    const { container } = render(<OpportunityBarChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
    // Should have at least one bar rect
    expect(container.querySelectorAll('rect').length).toBeGreaterThanOrEqual(mockData.length);
    // Check for colored bars (green, yellow, orange, red)
    const rects = Array.from(container.querySelectorAll('rect'));
    // Should contain at least one bar with green, yellow, orange, red, and light green
    expect(rects.some(r => r.getAttribute('fill') === '#4CAF50')).toBe(true); // Green
    expect(rects.some(r => r.getAttribute('fill') === '#8BC34A')).toBe(true); // Light Green
    expect(rects.some(r => r.getAttribute('fill') === '#FFEB3B')).toBe(true); // Yellow
    expect(rects.some(r => r.getAttribute('fill') === '#FF9800')).toBe(true); // Orange
    expect(rects.some(r => r.getAttribute('fill') === '#F44336')).toBe(true); // Red
  });

  it('renders with missing optional props and unknown niche', () => {
    const data = [{ overall_score: 0.5 }];
    render(<OpportunityBarChart data={data} />);
    expect(screen.getByText('Unknown')).toBeInTheDocument();
    expect(screen.getByText(/Opportunity Score Comparison/i)).toBeInTheDocument();
  });

  it('ensures accessibility: SVG bar chart present', () => {
    const { container } = render(<OpportunityBarChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});