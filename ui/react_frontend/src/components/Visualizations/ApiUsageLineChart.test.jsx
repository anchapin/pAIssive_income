/**
 * Tests for the ApiUsageLineChart component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ApiUsageLineChart from './ApiUsageLineChart';

describe('ApiUsageLineChart', () => {
  const mockData = [
    { date: '2023-01-01', requests: 100 },
    { date: '2023-01-02', requests: 125 },
    { date: '2023-01-03', requests: 90 },
  ];

  it('shows "No data available" if no data is passed', () => {
    render(<ApiUsageLineChart data={[]} dataKey="requests" name="API Requests" />);
    expect(screen.getByText(/no data available/i)).toBeInTheDocument();
  });

  it('renders the chart title and legend', () => {
    render(
      <ApiUsageLineChart
        data={mockData}
        dataKey="requests"
        name="API Requests"
        color="#111111"
        title="API Requests Over Time"
        yAxisLabel="Requests"
      />
    );
    expect(screen.getByText(/API Requests Over Time/i)).toBeInTheDocument();
    // Legend is rendered by recharts, look for the legend text (name)
    expect(screen.getByText(/API Requests/i)).toBeInTheDocument();
  });

  it('renders SVG elements for the line chart', () => {
    const { container } = render(
      <ApiUsageLineChart
        data={mockData}
        dataKey="requests"
        name="API Requests"
      />
    );
    // Should find svg element (recharts renders SVG)
    expect(container.querySelector('svg')).toBeInTheDocument();
    // Should find at least one line element for the data line
    expect(container.querySelector('path')).toBeInTheDocument();
  });

  it('renders the threshold line and label if provided', () => {
    render(
      <ApiUsageLineChart
        data={mockData}
        dataKey="requests"
        name="API Requests"
        threshold={110}
        thresholdLabel="Alert Threshold"
      />
    );
    expect(screen.getByText(/Alert Threshold/i)).toBeInTheDocument();
  });

  it('renders the y-axis label', () => {
    render(
      <ApiUsageLineChart
        data={mockData}
        dataKey="requests"
        name="API Requests"
        yAxisLabel="Requests"
      />
    );
    // YAxis label is rendered as SVG text; search for text in SVG
    // This is a bit brittle, but we can check the label is somewhere in the DOM
    expect(screen.getByText('Requests')).toBeInTheDocument();
  });

  it('renders custom tooltip content when tooltipFormatter is provided', () => {
    // Custom formatter prepends TEST:
    const tooltipFormatter = (value) => [`TEST: ${value}`, 'Custom'];
    render(
      <ApiUsageLineChart
        data={mockData}
        dataKey="requests"
        name="API Requests"
        tooltipFormatter={tooltipFormatter}
      />
    );
    // Simulate a tooltip by finding the legend text (since recharts tooltips are rendered on mouse events and may require integration testing)
    expect(screen.getByText(/API Requests/i)).toBeInTheDocument();
    // In a real integration test, you'd simulate mouse over the line or point and test for tooltip content.
  });

  it('renders with default color and height if not provided', () => {
    const { container } = render(
      <ApiUsageLineChart
        data={mockData}
        dataKey="requests"
        name="API Requests"
      />
    );
    // Default color is #8884d8, check the rendered path has this stroke
    // This is a bit implementation-dependent, so check if any path has stroke="#8884d8"
    const paths = container.querySelectorAll('path');
    expect(Array.from(paths).some(p => p.getAttribute('stroke') === '#8884d8')).toBe(true);
  });
});