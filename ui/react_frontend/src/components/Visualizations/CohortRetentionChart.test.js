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

  it('renders with a single cohort and single period', () => {
    const singleData = [{ size: 50, retention: [100] }];
    render(<CohortRetentionChart data={singleData} />);
    expect(screen.getByText('Cohort 1')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('renders with missing cohortLabels', () => {
    render(<CohortRetentionChart data={mockData} />);
    // Fallbacks to "Cohort 1", "Cohort 2"
    expect(screen.getByText('Cohort 1')).toBeInTheDocument();
    expect(screen.getByText('Cohort 2')).toBeInTheDocument();
  });

  it('renders with unusual retention values (edge color logic)', () => {
    const edgeData = [
      { size: 10, retention: [100, 80, 60, 40, 20, 10, 0, 5] }
    ];
    render(<CohortRetentionChart data={edgeData} />);
    expect(screen.getByText('Cohort 1')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
    // All retention % values should be present as text
    [100, 80, 60, 40, 20, 10, 0, 5].forEach(val => {
      expect(screen.getAllByText(`${val}%`).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders with empty cohortLabels array', () => {
    render(<CohortRetentionChart data={mockData} cohortLabels={[]} />);
    expect(screen.getByText('Cohort 1')).toBeInTheDocument();
    expect(screen.getByText('Cohort 2')).toBeInTheDocument();
  });

  it('renders chart with only one period across multiple cohorts', () => {
    const data = [
      { size: 11, retention: [100] },
      { size: 22, retention: [100] },
    ];
    render(<CohortRetentionChart data={data} />);
    expect(screen.getByText('Cohort 1')).toBeInTheDocument();
    expect(screen.getByText('Cohort 2')).toBeInTheDocument();
    expect(screen.getByText('11')).toBeInTheDocument();
    expect(screen.getByText('22')).toBeInTheDocument();
    expect(screen.getAllByText('100%').length).toBeGreaterThanOrEqual(2);
  });
});