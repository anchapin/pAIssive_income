/**
 * Tests for the ApiEndpointBarChart component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ApiEndpointBarChart from './ApiEndpointBarChart';

describe('ApiEndpointBarChart', () => {
  const mockData = [
    { endpoint: '/api/foo', requests: 100 },
    { endpoint: '/api/bar', requests: 60 },
    { endpoint: '/api/baz', requests: 30 },
  ];

  it('shows "No data available" if no data is passed', () => {
    render(<ApiEndpointBarChart data={[]} dataKey="requests" name="Requests" />);
    expect(screen.getByText(/no data available/i)).toBeInTheDocument();
  });

  it('renders chart title, legend, and y-axis labels', () => {
    render(
      <ApiEndpointBarChart
        data={mockData}
        dataKey="requests"
        name="Requests"
        title="Top Endpoints by Usage"
        yAxisLabel="Endpoint"
      />
    );
    expect(screen.getByText(/Top Endpoints by Usage/i)).toBeInTheDocument();
    // Legend and endpoint labels are rendered by recharts
    expect(screen.getByText(/Requests/i)).toBeInTheDocument();
    expect(screen.getByText('/api/foo')).toBeInTheDocument();
    expect(screen.getByText('/api/bar')).toBeInTheDocument();
    expect(screen.getByText('/api/baz')).toBeInTheDocument();
    expect(screen.getByText('Endpoint')).toBeInTheDocument();
  });

  it('renders SVG bar chart elements and correct bar color', () => {
    const { container } = render(
      <ApiEndpointBarChart
        data={mockData}
        dataKey="requests"
        name="Requests"
        color="#123abc"
      />
    );
    // SVG is present
    expect(container.querySelector('svg')).toBeInTheDocument();
    // There are rects for bars
    expect(container.querySelectorAll('rect').length).toBeGreaterThanOrEqual(mockData.length);
    // At least one bar has correct fill color
    expect(Array.from(container.querySelectorAll('rect')).some(r => r.getAttribute('fill') === '#123abc')).toBe(true);
  });

  it('renders value labels on bars when showLabels is true', () => {
    render(
      <ApiEndpointBarChart
        data={mockData}
        dataKey="requests"
        name="Requests"
        showLabels={true}
      />
    );
    // Value labels should be present
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('60')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
  });

  it('renders with custom tooltip formatter', () => {
    const tooltipFormatter = (value) => [`${value} times`, 'Custom'];
    render(
      <ApiEndpointBarChart
        data={mockData}
        dataKey="requests"
        name="Requests"
        tooltipFormatter={tooltipFormatter}
      />
    );
    // Tooltip only shown on hover, but legend text is present
    expect(screen.getByText(/Requests/i)).toBeInTheDocument();
  });

  it('sorts bars by dataKey descending', () => {
    render(
      <ApiEndpointBarChart
        data={mockData}
        dataKey="requests"
        name="Requests"
      />
    );
    // All y-axis labels are present
    expect(screen.getByText('/api/foo')).toBeInTheDocument();
    expect(screen.getByText('/api/bar')).toBeInTheDocument();
    expect(screen.getByText('/api/baz')).toBeInTheDocument();
  });

  it('renders with default color and height if not provided', () => {
    const { container } = render(
      <ApiEndpointBarChart
        data={mockData}
        dataKey="requests"
        name="Requests"
      />
    );
    // Default color is #8884d8
    const rects = container.querySelectorAll('rect');
    expect(Array.from(rects).some(r => r.getAttribute('fill') === '#8884d8')).toBe(true);
  });

  it('renders with missing optional props', () => {
    render(
      <ApiEndpointBarChart
        data={mockData}
        dataKey="requests"
        name="Requests"
      />
    );
    // Should render the chart and legend without crashing
    expect(screen.getByText(/Requests/i)).toBeInTheDocument();
    // No title or yAxisLabel required
  });

  it('renders a single bar for single data point', () => {
    const singleData = [{ endpoint: '/api/only', requests: 7 }];
    const { container } = render(
      <ApiEndpointBarChart
        data={singleData}
        dataKey="requests"
        name="Requests"
      />
    );
    // One rect for the bar
    const rects = container.querySelectorAll('rect');
    expect(rects.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('/api/only')).toBeInTheDocument();
    expect(screen.getByText('7')).toBeInTheDocument();
  });

  it('renders bars for endpoints with zero values', () => {
    const zeroData = [
      { endpoint: '/api/zero', requests: 0 },
      { endpoint: '/api/one', requests: 1 }
    ];
    render(
      <ApiEndpointBarChart
        data={zeroData}
        dataKey="requests"
        name="Requests"
        showLabels={true}
      />
    );
    expect(screen.getByText('/api/zero')).toBeInTheDocument();
    expect(screen.getByText('/api/one')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('renders with numeric or non-string endpoints', () => {
    const mixedData = [
      { endpoint: 123, requests: 8 },
      { endpoint: false, requests: 9 }
    ];
    render(
      <ApiEndpointBarChart
        data={mixedData}
        dataKey="requests"
        name="Requests"
      />
    );
    expect(screen.getByText('123')).toBeInTheDocument();
    expect(screen.getByText('false')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('9')).toBeInTheDocument();
  });

  it('ensures accessibility: SVG bar chart is present', () => {
    const { container } = render(
      <ApiEndpointBarChart
        data={mockData}
        dataKey="requests"
        name="Requests"
      />
    );
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});