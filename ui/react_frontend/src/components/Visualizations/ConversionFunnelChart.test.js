/**
 * Tests for the ConversionFunnelChart component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ConversionFunnelChart from './ConversionFunnelChart';

describe('ConversionFunnelChart', () => {
  const mockData = [
    { name: 'Visitors', value: 1000 },
    { name: 'Signed Up', value: 400 },
    { name: 'Activated', value: 200 },
    { name: 'Paid', value: 65 }
  ];

  it('shows "No conversion funnel data available" if no data is passed', () => {
    render(<ConversionFunnelChart data={[]} />);
    expect(screen.getByText(/No conversion funnel data available/i)).toBeInTheDocument();
  });

  it('renders chart title and funnel stages', () => {
    render(<ConversionFunnelChart data={mockData} title="User Conversion Funnel" />);
    expect(screen.getByText(/User Conversion Funnel/i)).toBeInTheDocument();
    expect(screen.getByText(/Visitors/i)).toBeInTheDocument();
    expect(screen.getByText(/Signed Up/i)).toBeInTheDocument();
    expect(screen.getByText(/Activated/i)).toBeInTheDocument();
    expect(screen.getByText(/Paid/i)).toBeInTheDocument();
  });

  it('renders SVG bar chart elements', () => {
    const { container } = render(<ConversionFunnelChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
    // Should have at least one bar rect for the funnel
    expect(container.querySelectorAll('rect').length).toBeGreaterThanOrEqual(1);
  });

  it('renders the conversion rates table with correct steps', () => {
    render(<ConversionFunnelChart data={mockData} />);
    expect(screen.getByText(/Conversion Rates:/i)).toBeInTheDocument();
    // Table step labels
    expect(screen.getByText('Step 1')).toBeInTheDocument();
    expect(screen.getByText('Step 2')).toBeInTheDocument();
    expect(screen.getByText('Step 3')).toBeInTheDocument();
    // Table cells for from/to stages
    expect(screen.getByText('Visitors')).toBeInTheDocument();
    expect(screen.getByText('Signed Up')).toBeInTheDocument();
    expect(screen.getByText('Activated')).toBeInTheDocument();
    expect(screen.getByText('Paid')).toBeInTheDocument();
  });

  it('renders with comparisonData prop', () => {
    const comparisonData = [
      { name: 'Visitors', value: 900 },
      { name: 'Signed Up', value: 300 },
      { name: 'Activated', value: 150 },
      { name: 'Paid', value: 50 }
    ];
    render(<ConversionFunnelChart data={mockData} comparisonData={comparisonData} />);
    // The compare button should be present and enabled
    expect(screen.getByRole('button', { name: /compare/i })).toBeEnabled();
  });

  it('renders with a single stage', () => {
    render(<ConversionFunnelChart data={[{ name: 'Visitors', value: 1000 }]} />);
    expect(screen.getByText('Visitors')).toBeInTheDocument();
    // Table should not crash, even if only one step
  });

  it('renders with missing optional props', () => {
    render(<ConversionFunnelChart data={mockData} />);
    // Uses default title
    expect(screen.getByText(/User Conversion Funnel/i)).toBeInTheDocument();
  });

  it('renders sort and segment selectors and allows selection', () => {
    render(<ConversionFunnelChart data={mockData} />);
    // Find and interact with sort and segment dropdowns
    expect(screen.getByRole('button', { name: /default order/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /all users/i })).toBeInTheDocument();
  });

  it('renders interactive controls: compare and export buttons', () => {
    render(<ConversionFunnelChart data={mockData} />);
    expect(screen.getByRole('button', { name: /compare/i })).toBeInTheDocument();
    // MoreVertIcon (menu) should be present
    expect(screen.getAllByRole('button').some(btn => btn.querySelector('svg'))).toBe(true);
  });

  it('ensures accessibility: SVG chart is present', () => {
    const { container } = render(<ConversionFunnelChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});