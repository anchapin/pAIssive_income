/**
 * Tests for the RevenueAreaChart component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import RevenueAreaChart from './RevenueAreaChart';

describe('RevenueAreaChart', () => {
  const mockData = [
    { month: 1, monthlyRevenue: 1000, cumulativeRevenue: 1000, total_revenue: 1000, cumulative_revenue: 1000 },
    { month: 2, monthlyRevenue: 2000, cumulativeRevenue: 3000, total_revenue: 2000, cumulative_revenue: 3000 },
    { month: 3, monthlyRevenue: 4000, cumulativeRevenue: 7000, total_revenue: 4000, cumulative_revenue: 7000 },
  ];

  it('shows "No revenue projection data available" if no data is passed', () => {
    render(<RevenueAreaChart data={[]} />);
    expect(screen.getByText(/No revenue projection data available/i)).toBeInTheDocument();
  });

  it('renders chart title, legend, and axes', () => {
    render(<RevenueAreaChart data={mockData} title="Revenue Projections" />);
    expect(screen.getByText(/Revenue Projections/i)).toBeInTheDocument();
    expect(screen.getByText(/Monthly Revenue/i)).toBeInTheDocument();
    expect(screen.getByText(/Cumulative Revenue/i)).toBeInTheDocument();
    expect(screen.getByText('Month 1')).toBeInTheDocument();
    expect(screen.getByText('Month 2')).toBeInTheDocument();
    expect(screen.getByText('Month 3')).toBeInTheDocument();
  });

  it('renders SVG area chart elements', () => {
    const { container } = render(<RevenueAreaChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
    // Should have at least one area path
    expect(container.querySelectorAll('path').length).toBeGreaterThanOrEqual(1);
  });

  it('renders checkboxes for toggling series', () => {
    render(<RevenueAreaChart data={mockData} />);
    expect(screen.getByLabelText(/Monthly Revenue/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Cumulative Revenue/i)).toBeInTheDocument();
  });

  it('toggles area visibility when checkboxes are clicked', () => {
    render(<RevenueAreaChart data={mockData} />);
    const monthlyCheckbox = screen.getByLabelText(/Monthly Revenue/i);
    const cumulativeCheckbox = screen.getByLabelText(/Cumulative Revenue/i);

    expect(monthlyCheckbox).toBeChecked();
    expect(cumulativeCheckbox).toBeChecked();

    fireEvent.click(monthlyCheckbox);
    expect(monthlyCheckbox).not.toBeChecked();

    fireEvent.click(cumulativeCheckbox);
    expect(cumulativeCheckbox).not.toBeChecked();

    // Both toggled off: legend present, but area not rendered (visual test)
  });

  it('renders milestone reference lines if milestones prop provided', () => {
    const milestones = [
      { month: 2, label: 'Break-even' },
      { month: 3, label: 'Goal' },
    ];
    render(<RevenueAreaChart data={mockData} milestones={milestones} />);
    // Check for milestone labels in the DOM (SVG text)
    expect(screen.getByText(/Break-even/i)).toBeInTheDocument();
    expect(screen.getByText(/Goal/i)).toBeInTheDocument();
  });

  it('renders with missing optional props', () => {
    render(<RevenueAreaChart data={mockData} />);
    // Uses default title
    expect(screen.getByText(/Revenue Projections/i)).toBeInTheDocument();
  });

  it('renders a single data point', () => {
    const singleData = [{ month: 1, monthlyRevenue: 500, cumulativeRevenue: 500, total_revenue: 500, cumulative_revenue: 500 }];
    render(<RevenueAreaChart data={singleData} />);
    expect(screen.getByText('Month 1')).toBeInTheDocument();
  });

  it('ensures accessibility: SVG area chart is present', () => {
    const { container } = render(<RevenueAreaChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});