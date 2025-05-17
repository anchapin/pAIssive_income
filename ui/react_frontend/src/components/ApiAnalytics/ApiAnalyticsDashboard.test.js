/**
 * Tests for the ApiAnalyticsDashboard component
 *
 * These tests verify that the dashboard renders expected content
 * and handles analytics data correctly.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ApiAnalyticsDashboard from './ApiAnalyticsDashboard';

// Example mock analytics data (adjust as appropriate for the real component API)
const mockAnalytics = [
  { endpoint: '/api/test', count: 42, avgResponseTime: 120 },
  { endpoint: '/api/agent', count: 17, avgResponseTime: 80 },
];

describe('ApiAnalyticsDashboard', () => {
  it('renders dashboard title', () => {
    render(<ApiAnalyticsDashboard analytics={mockAnalytics} />);
    expect(screen.getByText(/analytics dashboard/i)).toBeInTheDocument();
  });

  it('renders analytics endpoints and counts', () => {
    render(<ApiAnalyticsDashboard analytics={mockAnalytics} />);
    expect(screen.getByText('/api/test')).toBeInTheDocument();
    expect(screen.getByText('/api/agent')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('17')).toBeInTheDocument();
  });

  it('renders average response times', () => {
    render(<ApiAnalyticsDashboard analytics={mockAnalytics} />);
    expect(screen.getByText('120')).toBeInTheDocument();
    expect(screen.getByText('80')).toBeInTheDocument();
  });
});