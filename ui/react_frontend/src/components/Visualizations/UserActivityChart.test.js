/**
 * Tests for the UserActivityChart component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import UserActivityChart from './UserActivityChart';

describe('UserActivityChart', () => {
  const mockData = [
    {
      date: '2024-01-01',
      dau: 100,
      wau: 220,
      mau: 350,
      avg_session_time: 12.5,
      avg_actions_per_session: 4.2
    },
    {
      date: '2024-01-02',
      dau: 110,
      wau: 230,
      mau: 360,
      avg_session_time: 13.1,
      avg_actions_per_session: 4.4
    }
  ];

  it('shows "No user activity data available" if no data is passed', () => {
    render(<UserActivityChart data={[]} />);
    expect(screen.getByText(/No user activity data available/i)).toBeInTheDocument();
  });

  it('renders chart title, metric checkboxes, and axes labels', () => {
    render(<UserActivityChart data={mockData} />);
    expect(screen.getByText(/User Activity Metrics/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Daily Active Users/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Weekly Active Users/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Monthly Active Users/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Avg. Session Time \(min\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Avg. Actions Per Session/i)).toBeInTheDocument();
    expect(screen.getByText(/User Count/i)).toBeInTheDocument();
    expect(screen.getByText(/Session Metrics/i)).toBeInTheDocument();
  });

  it('renders SVG composed chart elements for bars and lines', () => {
    const { container } = render(<UserActivityChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
    // Should have bar and line elements
    expect(container.querySelectorAll('rect').length).toBeGreaterThanOrEqual(2);
    expect(container.querySelectorAll('path').length).toBeGreaterThanOrEqual(1);
  });

  it('toggles metric checkboxes', () => {
    render(<UserActivityChart data={mockData} />);
    const dauCheckbox = screen.getByLabelText(/Daily Active Users/i);
    expect(dauCheckbox).toBeChecked();
    fireEvent.click(dauCheckbox);
    expect(dauCheckbox).not.toBeChecked();
  });

  it('renders help text and legend', () => {
    render(<UserActivityChart data={mockData} />);
    expect(screen.getByText(/DAU/i)).toBeInTheDocument();
    expect(screen.getByText(/WAU/i)).toBeInTheDocument();
    expect(screen.getByText(/MAU/i)).toBeInTheDocument();
    // Legend is rendered by recharts
    expect(screen.getByText(/Legend/i) || screen.getByText(/Daily Active Users/i)).toBeInTheDocument();
  });

  it('renders with missing optional props (uses default metrics)', () => {
    render(<UserActivityChart data={mockData} />);
    expect(screen.getByLabelText(/Daily Active Users/i)).toBeInTheDocument();
  });

  it('ensures accessibility: SVG chart is present', () => {
    const { container } = render(<UserActivityChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});