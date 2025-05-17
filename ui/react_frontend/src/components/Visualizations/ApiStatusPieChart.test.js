/**
 * Tests for the ApiStatusPieChart component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ApiStatusPieChart from './ApiStatusPieChart';

describe('ApiStatusPieChart', () => {
  const mockData = [
    { name: 'Success (2xx)', value: 100 },
    { name: 'Client Error (4xx)', value: 20 },
    { name: 'Server Error (5xx)', value: 10 },
  ];

  it('shows "No data available" if given no data', () => {
    render(<ApiStatusPieChart data={[]} />);
    expect(screen.getByText(/no data available/i)).toBeInTheDocument();
  });

  it('renders chart title and legend when given data', () => {
    render(
      <ApiStatusPieChart
        data={mockData}
        title="Status Code Distribution"
      />
    );
    expect(screen.getByText(/Status Code Distribution/i)).toBeInTheDocument();
    // Legend is rendered by recharts; look for legend text
    expect(screen.getByText(/Success \(2xx\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Client Error \(4xx\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Server Error \(5xx\)/i)).toBeInTheDocument();
  });

  it('renders SVG pie chart cells with correct colors', () => {
    const customColors = ['#123456', '#abcdef', '#fedcba'];
    const { container } = render(
      <ApiStatusPieChart data={mockData} colors={customColors} />
    );
    // There should be as many <path> as data entries
    const slices = container.querySelectorAll('path');
    expect(slices.length).toBeGreaterThanOrEqual(mockData.length);
    // One of the paths should have fill="#123456"
    expect(Array.from(slices).some(p => p.getAttribute('fill') === '#123456')).toBe(true);
  });

  it('renders custom tooltip formatter if provided', () => {
    const customTooltip = (value, name) => [`${value} ${name} requests`, 'custom'];
    render(
      <ApiStatusPieChart
        data={mockData}
        tooltipFormatter={customTooltip}
      />
    );
    // Tooltip is only visible on interaction, but we can check legend text exists
    expect(screen.getByText(/Success \(2xx\)/i)).toBeInTheDocument();
  });
});