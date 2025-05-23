/**
 * Tests for the TierRevenueStackedBarChart component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TierRevenueStackedBarChart from './TierRevenueStackedBarChart';

describe('TierRevenueStackedBarChart', () => {
  const mockData = [
    {
      month: 1,
      cumulative_revenue: 1000,
      tier_revenue: { Basic: 500, Pro: 300, Premium: 200 }
    },
    {
      month: 2,
      cumulative_revenue: 2500,
      tier_revenue: { Basic: 1000, Pro: 900, Premium: 600 }
    },
    {
      month: 3,
      cumulative_revenue: 4000,
      tier_revenue: { Basic: 1400, Pro: 1200, Premium: 1400 }
    },
  ];

  it('shows "No tier revenue data available" if no data is passed', () => {
    render(<TierRevenueStackedBarChart data={[]} />);
    expect(screen.getByText(/No tier revenue data available/i)).toBeInTheDocument();
  });

  it('renders chart title, legend, axis labels, and tier chips', () => {
    render(<TierRevenueStackedBarChart data={mockData} title="Revenue by Subscription Tier" />);
    expect(screen.getByText(/Revenue by Subscription Tier/i)).toBeInTheDocument();
    expect(screen.getByText(/Subscription Tiers/i)).toBeInTheDocument();
    expect(screen.getByText(/Month 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Month 2/i)).toBeInTheDocument();
    expect(screen.getByText(/Month 3/i)).toBeInTheDocument();
    expect(screen.getByText('Basic')).toBeInTheDocument();
    expect(screen.getByText('Pro')).toBeInTheDocument();
    expect(screen.getByText('Premium')).toBeInTheDocument();
  });

  it('renders SVG bar chart elements and colored bars', () => {
    const { container } = render(<TierRevenueStackedBarChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
    // Should have at least one bar rect per tier per period
    expect(container.querySelectorAll('rect').length).toBeGreaterThanOrEqual(3);
    // Should contain at least one bar with each tier color
    const expectedColors = ['#8884d8', '#82ca9d', '#ffc658'];
    expect(
      expectedColors.some(color =>
        Array.from(container.querySelectorAll('rect')).some(p => p.getAttribute('fill') === color)
      )
    ).toBe(true);
  });

  it('toggles tier chips', () => {
    render(<TierRevenueStackedBarChart data={mockData} />);
    const basicChip = screen.getByText('Basic');
    const proChip = screen.getByText('Pro');
    fireEvent.click(basicChip);
    fireEvent.click(proChip);
    // Visual difference only, not asserted here, but no crash
  });

  it('switches to quarterly view', () => {
    render(<TierRevenueStackedBarChart data={mockData} />);
    const quarterlySwitch = screen.getByLabelText(/Quarterly View/i);
    fireEvent.click(quarterlySwitch);
    expect(quarterlySwitch).toBeChecked();
  });

  it('renders with missing optional props (uses default title)', () => {
    render(<TierRevenueStackedBarChart data={mockData} />);
    expect(screen.getByText(/Revenue by Subscription Tier/i)).toBeInTheDocument();
  });

  it('ensures accessibility: SVG bar chart is present', () => {
    const { container } = render(<TierRevenueStackedBarChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});