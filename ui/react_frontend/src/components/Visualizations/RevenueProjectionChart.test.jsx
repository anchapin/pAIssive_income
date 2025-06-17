/**
 * Tests for the RevenueProjectionChart component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import RevenueProjectionChart from './RevenueProjectionChart';

describe('RevenueProjectionChart', () => {
  const mockData = [
    { month: 1, date: '2024-01', revenue: 1000 },
    { month: 2, date: '2024-02', revenue: 1200 },
    { month: 3, date: '2024-03', revenue: 1500 },
    { month: 4, date: '2024-04', revenue: 1700 },
    { month: 5, date: '2024-05', revenue: 2000 },
    { month: 6, date: '2024-06', revenue: 2200 },
    { month: 7, date: '2024-07', revenue: 2300 },
    { month: 8, date: '2024-08', revenue: 2450 },
    { month: 9, date: '2024-09', revenue: 2600 },
    { month: 10, date: '2024-10', revenue: 2800 },
    { month: 11, date: '2024-11', revenue: 3000 },
    { month: 12, date: '2024-12', revenue: 3200 },
  ];

  it('renders chart title, scenario toggles, and SVG lines (main tab)', () => {
    render(<RevenueProjectionChart data={mockData} title="Revenue Projection" />);
    expect(screen.getByText(/Revenue Projection/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Baseline/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Optimistic/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Pessimistic/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Custom/i })).toBeInTheDocument();
    // Chart SVG is present
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders key metrics in the Analysis tab', () => {
    render(<RevenueProjectionChart data={mockData} title="Revenue Projection" />);
    // Switch to Analysis tab
    const analysisTab = screen.getByRole('tab', { name: /Analysis/i });
    fireEvent.click(analysisTab);
    expect(screen.getByText(/Total Projected Revenue/i)).toBeInTheDocument();
    expect(screen.getByText(/Break Even Point/i)).toBeInTheDocument();
    expect(screen.getByText(/Monthly Growth Rate/i)).toBeInTheDocument();
    expect(screen.getByText(/Peak Revenue Month/i)).toBeInTheDocument();
  });

  it('renders scenario comparison table in the Scenarios tab', () => {
    render(<RevenueProjectionChart data={mockData} title="Revenue Projection" />);
    const scenarioTab = screen.getByRole('tab', { name: /Scenarios/i });
    fireEvent.click(scenarioTab);
    expect(screen.getByText(/Scenario Comparison/i)).toBeInTheDocument();
    expect(screen.getByText(/Total Revenue/i)).toBeInTheDocument();
    expect(screen.getByText(/Average Monthly/i)).toBeInTheDocument();
    expect(screen.getByText(/Final Month/i)).toBeInTheDocument();
    expect(screen.getByText(/Peak Revenue/i)).toBeInTheDocument();
    expect(screen.getByText(/Growth Rate/i)).toBeInTheDocument();
  });

  it('renders with missing optional props (uses default title)', () => {
    render(<RevenueProjectionChart data={mockData} />);
    expect(screen.getByText(/Revenue Projection/i)).toBeInTheDocument();
  });

  it('ensures accessibility: SVG chart is present', () => {
    render(<RevenueProjectionChart data={mockData} />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });
});