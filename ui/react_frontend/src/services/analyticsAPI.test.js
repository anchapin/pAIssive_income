/**
 * Tests for the analyticsAPI module
 */

import analyticsAPI from './analyticsAPI';

// Mock fetchAPI
jest.mock('./apiClient', () => ({
  fetchAPI: jest.fn()
}));
const { fetchAPI } = require('./apiClient');

describe('analyticsAPI', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('calls getSummary with correct default days', async () => {
    fetchAPI.mockResolvedValue({ summary: true });
    await analyticsAPI.getSummary();
    expect(fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/summary?days=30');
  });

  it('calls getSummary with custom days', async () => {
    fetchAPI.mockResolvedValue({ summary: true });
    await analyticsAPI.getSummary(7);
    expect(fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/summary?days=7');
  });

  it('calls getRequests with all params', async () => {
    fetchAPI.mockResolvedValue({ requests: [] });
    await analyticsAPI.getRequests({
      days: 14, endpoint: '/foo', version: 'v1',
      user_id: 'u1', api_key_id: 'k2', status_code: 400,
      aggregate: 'daily', limit: 50, offset: 10
    });
    expect(fetchAPI).toHaveBeenCalledWith(
      expect.stringMatching(/^\/api\/v1\/analytics\/requests\?/),
    );
    const url = fetchAPI.mock.calls[0][0];
    expect(url).toContain('days=14');
    expect(url).toContain('endpoint=%2Ffoo');
    expect(url).toContain('version=v1');
    expect(url).toContain('user_id=u1');
    expect(url).toContain('api_key_id=k2');
    expect(url).toContain('status_code=400');
    expect(url).toContain('aggregate=daily');
    expect(url).toContain('limit=50');
    expect(url).toContain('offset=10');
  });

  it('calls getEndpointStats with correct default and custom days', async () => {
    fetchAPI.mockResolvedValue([{ endpoint: '/a' }]);
    await analyticsAPI.getEndpointStats();
    expect(fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/endpoints?days=30');
    await analyticsAPI.getEndpointStats(60);
    expect(fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/endpoints?days=60');
  });

  it('calls getUserStats with and without user_id', async () => {
    fetchAPI.mockResolvedValue([{ user: 'u1' }]);
    await analyticsAPI.getUserStats();
    expect(fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/users?days=30');
    await analyticsAPI.getUserStats(90, 'xyz');
    expect(fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/users?days=90&user_id=xyz');
  });

  it('calls getApiKeyStats with and without api_key_id', async () => {
    fetchAPI.mockResolvedValue([{ key: 'k1' }]);
    await analyticsAPI.getApiKeyStats();
    expect(fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/api-keys?days=30');
    await analyticsAPI.getApiKeyStats(15, 'k10');
    expect(fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/api-keys?days=15&api_key_id=k10');
  });

  it('calls exportRequestsCSV with correct params and options', async () => {
    fetchAPI.mockResolvedValue(new Blob(['csvdata'], { type: 'text/csv' }));
    await analyticsAPI.exportRequestsCSV({ days: 7, endpoint: '/foo' });
    expect(fetchAPI).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/analytics/export/requests?'),
      expect.objectContaining({ responseType: 'blob' })
    );
    const url = fetchAPI.mock.calls[0][0];
    expect(url).toContain('days=7');
    expect(url).toContain('endpoint=%2Ffoo');
  });
});