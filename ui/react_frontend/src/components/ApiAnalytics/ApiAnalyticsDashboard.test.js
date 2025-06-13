/**
 * Comprehensive tests for the ApiAnalyticsDashboard component.
 *
 * These tests mock API fetches and verify UI states:
 * - Loading spinner
 * - Error state
 * - Main dashboard render
 * - Time range selector and fetch re-trigger
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ApiAnalyticsDashboard from './ApiAnalyticsDashboard';

// Utility to mock fetch with different endpoints
function setupFetchMock({ summaryData, requestsData, endpointStats, fail = false }) {
  global.fetch = jest.fn((url) => {
    if (fail) {
      return Promise.resolve({
        ok: false,
        statusText: 'Internal Server Error',
      });
    }
    if (url.includes('analytics/summary')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(summaryData),
      });
    }
    if (url.includes('analytics/requests')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(requestsData),
      });
    }
    if (url.includes('analytics/endpoints')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(endpointStats),
      });
    }
    return Promise.reject(new Error('Unknown endpoint: ' + url));
  });
}

afterEach(() => {
  jest.resetAllMocks();
});

describe('ApiAnalyticsDashboard', () => {
  const mockSummary = {
    total_requests: 1234,
    error_rate: 0.042,
    avg_response_time: 87.3,
    unique_users: 56,
  };
  const mockRequests = {
    items: [
      { day: '2023-10-01', request_count: 100, error_count: 4, status_code: 200 },
      { day: '2023-10-02', request_count: 200, error_count: 8, status_code: 200 },
    ],
  };
  const mockEndpoints = [
    { endpoint: '/api/test', count: 42, avg_response_time: 120 },
    { endpoint: '/api/agent', count: 17, avg_response_time: 80 },
  ];

  it('shows a loading spinner initially', async () => {
    setupFetchMock({
      summaryData: mockSummary,
      requestsData: mockRequests,
      endpointStats: mockEndpoints,
    });
    render(<ApiAnalyticsDashboard />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByRole('progressbar')).not.toBeInTheDocument());
  });

  it('renders dashboard title and summary cards after loading', async () => {
    setupFetchMock({
      summaryData: mockSummary,
      requestsData: mockRequests,
      endpointStats: mockEndpoints,
    });
    render(<ApiAnalyticsDashboard />);
    expect(await screen.findByText(/API Analytics Dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/Total Requests/i)).toBeInTheDocument();
    expect(screen.getByText(/1,234/)).toBeInTheDocument();
    expect(screen.getByText(/Error Rate/i)).toBeInTheDocument();
    expect(screen.getByText('4.20%')).toBeInTheDocument();
    expect(screen.getByText(/Avg Response Time/i)).toBeInTheDocument();
    expect(screen.getByText('87.30ms')).toBeInTheDocument();
    expect(screen.getByText(/Unique Users/i)).toBeInTheDocument();
    expect(screen.getByText('56')).toBeInTheDocument();
  });

  it('renders time range selector and triggers fetch on change', async () => {
    setupFetchMock({
      summaryData: mockSummary,
      requestsData: mockRequests,
      endpointStats: mockEndpoints,
    });
    render(<ApiAnalyticsDashboard />);
    // Wait for dashboard to load
    await screen.findByText(/API Analytics Dashboard/i);
    const select = screen.getByLabelText(/Time Range/i);
    expect(select).toBeInTheDocument();
    fireEvent.mouseDown(select);
    // The dropdown should now show options
    expect(await screen.findByText(/Last 7 days/i)).toBeInTheDocument();
    fireEvent.click(screen.getByText(/Last 7 days/i));
    // Should trigger fetch (mocked)
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
  });

  it('shows an error alert if fetch fails', async () => {
    setupFetchMock({
      summaryData: {},
      requestsData: {},
      endpointStats: {},
      fail: true,
    });
    render(<ApiAnalyticsDashboard />);
    expect(await screen.findByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(/Error loading analytics data/i)).toBeInTheDocument();
  });
});