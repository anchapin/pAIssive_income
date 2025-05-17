/**
 * Tests for the Layout component
 *
 * - Asserts that the app bar, navigation, and children render.
 * - Simulates navigation and drawer open/close.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Layout from './Layout';

// Mock react-router-dom hooks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/dashboard' }),
}));

describe('Layout', () => {
  it('renders the app bar title and children', () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );
    expect(screen.getByText('pAIssive Income Framework')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders all navigation items', () => {
    render(<Layout><div /></Layout>);
    [
      'Home',
      'Dashboard',
      'Niche Analysis',
      'Developer',
      'Monetization',
      'Marketing',
      'User Engagement',
      'API Analytics',
      'About',
    ].forEach((item) => {
      expect(screen.getByRole('button', { name: item })).toBeInTheDocument();
    });
  });

  it('shows the drawer and can close and open it', () => {
    render(<Layout><div /></Layout>);
    // Drawer is open by default, so close it
    const closeBtn = screen.getByLabelText(/close navigation drawer/i);
    expect(closeBtn).toBeInTheDocument();
    fireEvent.click(closeBtn);
    // The open button should now be visible
    const openBtn = screen.getByLabelText(/open navigation drawer/i);
    expect(openBtn).toBeInTheDocument();
    fireEvent.click(openBtn);
    // Drawer should be open again (close button appears)
    expect(screen.getByLabelText(/close navigation drawer/i)).toBeInTheDocument();
  });

  it('highlights the selected navigation item', () => {
    render(<Layout><div /></Layout>);
    const dashboardBtn = screen.getByRole('button', { name: 'Dashboard' });
    expect(dashboardBtn).toHaveAttribute('aria-current', 'page');
  });
});