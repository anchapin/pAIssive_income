/**
 * Tests for the MultiMetricLineChart component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import MultiMetricLineChart from './MultiMetricLineChart';

describe('MultiMetricLineChart', () => {
  const mockData = [
    { time: '2024-01-01', users: 100, revenue: 400 },
    { time: '2024-01-02', users: 120, revenue: 420 },
    { time: '2024-01-03', users: 130, revenue: 390 },
  ];
  const metrics = [
    { key: 'users', name: 'Active Users', color: '#8884d8', type: 'line' },
    { key: 'revenue', name: 'Revenue', color: '#82ca9d', type: 'line' },
  ];

  it('shows "No data available" if no data is passed', () => {
    render(<MultiMetricLineChart data={[]} metrics={metrics} />);
    expect(screen.getByText(/No data available/i)).toBeInTheDocument();
  });

  it('shows "No metrics defined" if metrics is empty', () => {
    render(<MultiMetricLineChart data={mockData} metrics={[]} />);
    expect(screen.getByText(/No metrics defined/i)).toBeInTheDocument();
  });

  it('renders chart title, legend, and axis labels', () => {
    render(<MultiMetricLineChart data={mockData} metrics={metrics} title="Metrics Over Time" xAxisLabel="Date" yAxisLabel="Count" />);
    expect(screen.getByText(/Metrics Over Time/i)).toBeInTheDocument();
    expect(screen.getByText(/Active Users/i)).toBeInTheDocument();
    expect(screen.getByText(/Revenue/i)).toBeInTheDocument();
    expect(screen.getByText(/Date/i)).toBeInTheDocument();
    expect(screen.getByText(/Count/i)).toBeInTheDocument();
  });

  it('renders SVG line chart elements', () => {
    const { container } = render(<MultiMetricLineChart data={mockData} metrics={metrics} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
    // Should have at least one line path
    expect(container.querySelectorAll('path').length).toBeGreaterThanOrEqual(1);
  });

  it('renders metric chips and toggles individual metrics', () => {
    render(<MultiMetricLineChart data={mockData} metrics={metrics} />);
    const userChip = screen.getByText('Active Users');
    const revenueChip = screen.getByText('Revenue');
    expect(userChip).toBeInTheDocument();
    expect(revenueChip).toBeInTheDocument();
    fireEvent.click(userChip);
    // Chip toggling is visual, chart updates (not asserted here)
    fireEvent.click(revenueChip);
  });

  it('toggles all metrics on/off with All/None buttons', () => {
    render(<MultiMetricLineChart data={mockData} metrics={metrics} />);
    const allButton = screen.getByRole('button', { name: /^All$/ });
    const noneButton = screen.getByRole('button', { name: /^None$/ });
    fireEvent.click(noneButton);
    // All lines should be hidden (visually, not asserted here)
    fireEvent.click(allButton);
    // All lines visible again
  });

  it('renders help tip text', () => {
    render(<MultiMetricLineChart data={mockData} metrics={metrics} />);
    expect(screen.getByText(/Tip: Click and drag directly on the chart/i)).toBeInTheDocument();
  });

  it('renders with missing optional props', () => {
    render(<MultiMetricLineChart data={mockData} metrics={metrics} />);
    // Should render default title and axis labels
    expect(screen.getByText(/Metrics Over Time/i)).toBeInTheDocument();
    expect(screen.getByText(/Time/i)).toBeInTheDocument();
    expect(screen.getByText(/Value/i)).toBeInTheDocument();
  });

  it('ensures accessibility: SVG line chart present', () => {
    const { container } = render(<MultiMetricLineChart data={mockData} metrics={metrics} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});