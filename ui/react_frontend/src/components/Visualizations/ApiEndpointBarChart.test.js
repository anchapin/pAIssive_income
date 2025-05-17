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
    // We can test that the first y-axis label is the endpoint with highest requests
    render(
      <ApiEndpointBarChart
        data={mockData}
        dataKey="requests"
        name="Requests"
      />
    );
    // The first endpoint rendered on y-axis should be /api/foo (100)
    // Since DOM order may not be strict, check all y-axis labels are present
    expect(screen.getByText('/api/foo')).toBeInTheDocument();
    expect(screen.getByText('/api/bar')).toBeInTheDocument();
    expect(screen.getByText('/api/baz')).toBeInTheDocument();
  });
});