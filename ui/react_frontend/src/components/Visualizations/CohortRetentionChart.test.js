/**
 * Tests for the CohortRetentionChart component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import CohortRetentionChart from './CohortRetentionChart';

describe('CohortRetentionChart', () => {
  const mockData = [
    { size: 100, retention: [100, 80, 60, 40, 20, 10, 0] },
    { size: 200, retention: [100, 75, 55, 35, 15, 5, 0] },
  ];
  const cohortLabels = ['Jan 2023', 'Feb 2023'];

  it('shows "No retention data available" if no data is passed', () => {
    render(<CohortRetentionChart data={[]} />);
    expect(screen.getByText(/No retention data available/i)).toBeInTheDocument();
  });

  it('renders chart title, cohort labels, and period headers', () => {
    render(<CohortRetentionChart data={mockData} title="User Retention Analysis" periodLabel="Month" cohortLabels={cohortLabels} />);
    expect(screen.getByText(/User Retention Analysis/i)).toBeInTheDocument();
    expect(screen.getByText('Jan 2023')).toBeInTheDocument();
    expect(screen.getByText('Feb 2023')).toBeInTheDocument();
    // Table headers for periods
    expect(screen.getByText('Month 0')).toBeInTheDocument();
    expect(screen.getByText('Month 6')).toBeInTheDocument();
  });

  it('renders cohort sizes and retention values', () => {
    render(<CohortRetentionChart data={mockData} cohortLabels={cohortLabels} />);
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument();
    // Retention values are rendered as background with text via styled cell
    expect(screen.getAllByText(/%/i).length).toBeGreaterThanOrEqual(2);
  });

  it('renders legend for color mapping', () => {
    render(<CohortRetentionChart data={mockData} />);
    expect(screen.getByText(/Legend:/i)).toBeInTheDocument();
    // Legend values
    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('ensures accessibility: table and rows present', () => {
    const { container } = render(<CohortRetentionChart data={mockData} />);
    expect(container.querySelector('table')).toBeInTheDocument();
    expect(container.querySelectorAll('tr').length).toBeGreaterThanOrEqual(3); // header + 2 rows
  });
});