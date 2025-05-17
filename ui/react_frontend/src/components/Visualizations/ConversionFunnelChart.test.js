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

  it('ensures accessibility: SVG chart is present', () => {
    const { container } = render(<ConversionFunnelChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});