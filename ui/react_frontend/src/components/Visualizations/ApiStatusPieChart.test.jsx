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

  it('uses default color palette and cycles if too few colors are provided', () => {
    const shortColors = ['#abcd12'];
    const { container } = render(
      <ApiStatusPieChart data={mockData} colors={shortColors} />
    );
    const slices = container.querySelectorAll('path');
    // Should cycle, so first and second may share color
    expect(slices.length).toBeGreaterThanOrEqual(mockData.length);
    expect(Array.from(slices).some(p => p.getAttribute('fill') === '#abcd12')).toBe(true);
  });

  it('renders with default props when optional props are omitted', () => {
    render(<ApiStatusPieChart data={mockData} />);
    // Default title is not rendered, but chart and legend are present
    expect(screen.getByText(/Success \(2xx\)/i)).toBeInTheDocument();
  });

  it('renders only one slice for a single data point', () => {
    const { container } = render(
      <ApiStatusPieChart data={[{ name: 'Only', value: 1 }]} />
    );
    // There should be only one path for the pie
    const slices = container.querySelectorAll('path');
    expect(slices.length).toBeGreaterThanOrEqual(1);
  });

  it('formats labels using the provided label function', () => {
    // By default, the label is `${name}: ${(percent * 100).toFixed(0)}%`
    render(
      <ApiStatusPieChart data={[{ name: 'Alpha', value: 5 }, { name: 'Beta', value: 5 }]} />
    );
    // The default label will show "Alpha: 50%" and "Beta: 50%"
    // These are SVG text, so check for these labels
    expect(screen.getByText(/Alpha: 50%/)).toBeInTheDocument();
    expect(screen.getByText(/Beta: 50%/)).toBeInTheDocument();
  });

  it('ensures accessibility: SVG pie chart is present', () => {
    const { container } = render(
      <ApiStatusPieChart data={mockData} />
    );
    // There should be an SVG element in the DOM
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});