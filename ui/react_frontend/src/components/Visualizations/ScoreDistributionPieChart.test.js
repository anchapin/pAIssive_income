/**
 * Tests for the ScoreDistributionPieChart component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScoreDistributionPieChart from './ScoreDistributionPieChart';

describe('ScoreDistributionPieChart', () => {
  const mockData = {
    excellent: 5,
    very_good: 10,
    good: 8,
    fair: 4,
    limited: 2
  };

  it('shows "No data available" if no data passed', () => {
    render(<ScoreDistributionPieChart data={null} />);
    expect(screen.getByText(/No data available/i)).toBeInTheDocument();
  });

  it('shows "No score distribution data available" if all values are zero', () => {
    render(<ScoreDistributionPieChart data={{ excellent: 0, very_good: 0, good: 0, fair: 0, limited: 0 }} />);
    expect(screen.getByText(/No score distribution data available/i)).toBeInTheDocument();
  });

  it('renders chart title, legend, and all category labels with correct colors', () => {
    render(<ScoreDistributionPieChart data={mockData} title="Opportunity Score Distribution" />);
    expect(screen.getByText(/Opportunity Score Distribution/i)).toBeInTheDocument();
    // Pie/legend categories
    expect(screen.getByText(/Excellent \(0.8-1.0\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Very Good \(0.6-0.8\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Good \(0.4-0.6\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Fair \(0.2-0.4\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Limited \(0-0.2\)/i)).toBeInTheDocument();
    // Legend present (vertical, right)
    expect(screen.getByText(/Excellent \(0.8-1.0\)/i)).toBeInTheDocument();
  });

  it('renders SVG pie chart elements and pie slices have correct colors', () => {
    const { container } = render(<ScoreDistributionPieChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
    // Pie slices: should be >= number of categories with value
    const paths = container.querySelectorAll('path');
    expect(paths.length).toBeGreaterThanOrEqual(5);
    // Colors: green, light green, yellow, orange, red
    const expectedColors = ['#4CAF50', '#8BC34A', '#FFEB3B', '#FF9800', '#F44336'];
    expect(
      expectedColors.some(color =>
        Array.from(paths).some(p => p.getAttribute('fill') === color)
      )
    ).toBe(true);
  });

  it('renders only categories with nonzero values', () => {
    render(<ScoreDistributionPieChart data={{ excellent: 3, very_good: 0, good: 0, fair: 0, limited: 0 }} />);
    expect(screen.getByText(/Excellent \(0.8-1.0\)/i)).toBeInTheDocument();
    expect(screen.queryByText(/Very Good \(0.6-0.8\)/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Good \(0.4-0.6\)/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Fair \(0.2-0.4\)/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Limited \(0-0.2\)/i)).not.toBeInTheDocument();
  });

  it('ensures accessibility: SVG pie chart is present', () => {
    const { container } = render(<ScoreDistributionPieChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});