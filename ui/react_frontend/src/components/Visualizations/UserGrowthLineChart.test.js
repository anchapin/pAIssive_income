/**
 * Tests for the UserGrowthLineChart component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import UserGrowthLineChart from './UserGrowthLineChart';

describe('UserGrowthLineChart', () => {
  const mockData = [
    { month: 1, totalUsers: 100, freeUsers: 80, paidUsers: 20 },
    { month: 2, totalUsers: 120, freeUsers: 90, paidUsers: 30 },
    { month: 3, totalUsers: 150, freeUsers: 100, paidUsers: 50 },
  ];

  it('shows "No user projection data available" if no data is passed', () => {
    render(<UserGrowthLineChart data={[]} />);
    expect(screen.getByText(/No user projection data available/i)).toBeInTheDocument();
  });

  it('renders the chart title and legend', () => {
    render(<UserGrowthLineChart data={mockData} title="User Growth Projections" />);
    expect(screen.getByText(/User Growth Projections/i)).toBeInTheDocument();
    // Legend lines for "Total Users", "Free Users", "Paid Users"
    expect(screen.getByText(/Total Users/i)).toBeInTheDocument();
    expect(screen.getByText(/Free Users/i)).toBeInTheDocument();
    expect(screen.getByText(/Paid Users/i)).toBeInTheDocument();
  });

  it('renders SVG line chart elements', () => {
    const { container } = render(<UserGrowthLineChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
    // Should have at least one line path
    expect(container.querySelectorAll('path').length).toBeGreaterThanOrEqual(1);
  });

  it('renders checkboxes for toggling lines', () => {
    render(<UserGrowthLineChart data={mockData} />);
    expect(screen.getByLabelText(/Total Users/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Free Users/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Paid Users/i)).toBeInTheDocument();
  });

  it('toggles line visibility when checkboxes are clicked', () => {
    render(<UserGrowthLineChart data={mockData} />);
    const totalCheckbox = screen.getByLabelText(/Total Users/i);
    const freeCheckbox = screen.getByLabelText(/Free Users/i);
    const paidCheckbox = screen.getByLabelText(/Paid Users/i);

    expect(totalCheckbox).toBeChecked();
    expect(freeCheckbox).toBeChecked();
    expect(paidCheckbox).toBeChecked();

    fireEvent.click(totalCheckbox);
    expect(totalCheckbox).not.toBeChecked();

    fireEvent.click(freeCheckbox);
    expect(freeCheckbox).not.toBeChecked();

    fireEvent.click(paidCheckbox);
    expect(paidCheckbox).not.toBeChecked();

    // All lines toggled off: legend is still present, but lines are not visually rendered
    // Would require SVG inspection for visual assertion
  });

  it('renders help tip text', () => {
    render(<UserGrowthLineChart data={mockData} />);
    expect(screen.getByText(/Tip: Click and drag directly on the chart/i)).toBeInTheDocument();
  });

  it('renders a single data point', () => {
    const singleData = [{ month: 1, totalUsers: 50, freeUsers: 30, paidUsers: 20 }];
    render(<UserGrowthLineChart data={singleData} />);
    expect(screen.getByText(/User Growth Projections/i)).toBeInTheDocument();
    expect(screen.getByText('Month 1')).toBeInTheDocument();
    expect(screen.getByText(/Total Users/i)).toBeInTheDocument();
  });

  it('renders with missing optional props (no title)', () => {
    render(<UserGrowthLineChart data={mockData} />);
    // Default title is "User Growth Projections"
    expect(screen.getByText(/User Growth Projections/i)).toBeInTheDocument();
  });

  it('shows the "Reset Zoom" button', () => {
    render(<UserGrowthLineChart data={mockData} />);
    expect(screen.getByRole('button', { name: /reset zoom/i })).toBeInTheDocument();
  });

  it('ensures accessibility: SVG line chart present', () => {
    const { container } = render(<UserGrowthLineChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});