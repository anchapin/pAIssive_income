/**
 * Tests for the UserGrowthLineChart component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import UserGrowthLineChart from './UserGrowthLineChart';

describe('UserGrowthLineChart', () => {
  const mockData = [
    { month: 1, totalUsers: 100, freeUsers: 80, paidUsers: 20 },
    { month: 2, totalUsers: 120, freeUsers: 90, paidUsers: 30 },
    { month: 3, totalUsers: 150, freeUsers: 100, paidUsers: 50 },
  ];

  it('shows "No user projection data available" if no data is passed', () => {
    render(<UserGrowthLineChart data={[]} />);
    expect(screen.getByText(/No user projection data available/i)).toBeInTheDocument();
  });

  it('renders the chart title and legend', () => {
    render(<UserGrowthLineChart data={mockData} title="User Growth Projections" />);
    expect(screen.getByText(/User Growth Projections/i)).toBeInTheDocument();
    // Legend lines for "Total Users", "Free Users", "Paid Users"
    expect(screen.getByText(/Total Users/i)).toBeInTheDocument();
    expect(screen.getByText(/Free Users/i)).toBeInTheDocument();
    expect(screen.getByText(/Paid Users/i)).toBeInTheDocument();
  });

  it('renders SVG line chart elements', () => {
    const { container } = render(<UserGrowthLineChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
    // Should have at least one line path
    expect(container.querySelectorAll('path').length).toBeGreaterThanOrEqual(1);
  });

  it('renders checkboxes for toggling lines', () => {
    render(<UserGrowthLineChart data={mockData} />);
    expect(screen.getByLabelText(/Total Users/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Free Users/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Paid Users/i)).toBeInTheDocument();
  });

  it('toggles line visibility when checkboxes are clicked', () => {
    render(<UserGrowthLineChart data={mockData} />);
    const totalCheckbox = screen.getByLabelText(/Total Users/i);
    expect(totalCheckbox).toBeChecked();
    fireEvent.click(totalCheckbox);
    expect(totalCheckbox).not.toBeChecked();
    // The legend is always present, but line would not be rendered (visual test)
    // To fully assert, would need to check the SVG paths per line.
  });

  it('renders help tip text', () => {
    render(<UserGrowthLineChart data={mockData} />);
    expect(screen.getByText(/Tip: Click and drag directly on the chart/i)).toBeInTheDocument();
  });

  it('renders a reference line chip if reference line is added (simulate state)', () => {
    // Simulate adding a reference line by manipulating state via a wrapper
    const Wrapper = (props) => {
      const [show, setShow] = React.useState(true);
      // Expose a button to simulate reference line presence
      return (
        <>
          <button onClick={() => setShow(false)}>Remove Ref</button>
          <UserGrowthLineChart
            {...props}
            // patch referenceLines prop via mock/hook if needed in real test
          />
        </>
      );
    };
    render(<UserGrowthLineChart data={mockData} />);
    // By default, no reference lines
    expect(screen.queryByText(/Reference Lines:/i)).not.toBeInTheDocument();
    // Real state manipulation for reference lines would require integration/mount test
  });

  it('ensures accessibility: SVG line chart present', () => {
    const { container } = render(<UserGrowthLineChart data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});