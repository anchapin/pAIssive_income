/**
 * Tests for the CustomerLifetimeValueGauge component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import CustomerLifetimeValueGauge from './CustomerLifetimeValueGauge';

describe('CustomerLifetimeValueGauge', () => {
  const mockData = {
    one_year_value: 350,
    three_year_value: 800,
    five_year_value: 1200,
    lifetime_value: 1500,
    average_revenue_per_user: 23.45,
    churn_rate: 0.12,
    average_lifetime_months: 27.6,
  };

  it('shows "No lifetime value data available" if no data is passed', () => {
    render(<CustomerLifetimeValueGauge data={null} />);
    expect(screen.getByText(/No lifetime value data available/i)).toBeInTheDocument();
  });

  it('renders the chart title, gauge, and all value metrics', () => {
    render(<CustomerLifetimeValueGauge data={mockData} title="Customer Lifetime Value" />);
    expect(screen.getByText(/Customer Lifetime Value/i)).toBeInTheDocument();
    // Year and lifetime headers
    expect(screen.getByText(/1-Year/i)).toBeInTheDocument();
    expect(screen.getByText(/3-Year/i)).toBeInTheDocument();
    expect(screen.getByText(/5-Year/i)).toBeInTheDocument();
    expect(screen.getByText(/Lifetime/i)).toBeInTheDocument();
    // Value cells
    expect(screen.getByText(/\$350\.00/)).toBeInTheDocument();
    expect(screen.getByText(/\$800\.00/)).toBeInTheDocument();
    expect(screen.getByText(/\$1,200\.00/)).toBeInTheDocument();
    expect(screen.getByText(/\$1,500\.00/)).toBeInTheDocument();
    // Additional metrics
    expect(screen.getByText(/Monthly ARPU:/i)).toBeInTheDocument();
    expect(screen.getByText(/\$23\.45/)).toBeInTheDocument();
    expect(screen.getByText(/Churn Rate:/i)).toBeInTheDocument();
    expect(screen.getByText(/12\.0%/)).toBeInTheDocument();
    expect(screen.getByText(/Avg. Customer Lifetime:/i)).toBeInTheDocument();
    expect(screen.getByText(/27\.6 months/)).toBeInTheDocument();
  });

  it('renders SVG gauge chart', () => {
    const { container } = render(<CustomerLifetimeValueGauge data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('renders with missing optional props and zeros', () => {
    const zeroData = {
      one_year_value: 0,
      three_year_value: 0,
      five_year_value: 0,
      lifetime_value: 0,
      average_revenue_per_user: 0,
      churn_rate: 0,
      average_lifetime_months: 0,
    };
    render(<CustomerLifetimeValueGauge data={zeroData} />);
    expect(screen.getAllByText(/\$0\.00/).length).toBeGreaterThanOrEqual(4);
    expect(screen.getByText(/0\.0%/)).toBeInTheDocument();
    expect(screen.getByText(/0\.0 months/)).toBeInTheDocument();
  });
});