/**
 * Tests for the analyticsAPI module
 */

import analyticsAPI from './analyticsAPI';
import * as apiClient from './apiClient';

vi.mock('./apiClient');

describe('analyticsAPI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiClient.fetchAPI.mockResolvedValue(new Response(JSON.stringify({}), { status: 200, headers: { 'Content-Type': 'application/json' } }));
  });

  it('calls getSummary with correct default days', async () => {
    await analyticsAPI.getSummary();
    expect(apiClient.fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/summary?days=30', expect.any(Object));
  });

  it('calls getSummary with custom days', async () => {
    await analyticsAPI.getSummary(7);
    expect(apiClient.fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/summary?days=7', expect.any(Object));
  });

  it('calls getRequests with all params', async () => {
    await analyticsAPI.getRequests({
      days: 14, endpoint: '/foo', version: 'v1',
      user_id: 'u1', api_key_id: 'k2', status_code: 400,
      aggregate: 'daily', limit: 50, offset: 10
    });
    expect(apiClient.fetchAPI).toHaveBeenCalledWith(
      expect.stringMatching(/^\/api\/v1\/analytics\/requests\?/),
      expect.any(Object)
    );
    const url = apiClient.fetchAPI.mock.calls[0][0];
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
    await analyticsAPI.getEndpointStats();
    expect(apiClient.fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/endpoints?days=30', expect.any(Object));
    await analyticsAPI.getEndpointStats(60);
    expect(apiClient.fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/endpoints?days=60', expect.any(Object));
  });

  it('calls getUserStats with and without user_id', async () => {
    await analyticsAPI.getUserStats();
    expect(apiClient.fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/users?days=30', expect.any(Object));
    await analyticsAPI.getUserStats(90, 'xyz');
    expect(apiClient.fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/users?days=90&user_id=xyz', expect.any(Object));
  });

  it('calls getApiKeyStats with and without api_key_id', async () => {
    await analyticsAPI.getApiKeyStats();
    expect(apiClient.fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/api-keys?days=30', expect.any(Object));
    await analyticsAPI.getApiKeyStats(15, 'k10');
    expect(apiClient.fetchAPI).toHaveBeenCalledWith('/api/v1/analytics/api-keys?days=15&api_key_id=k10', expect.any(Object));
  });

  it('calls exportRequestsCSV with correct params and options', async () => {
    apiClient.fetchAPI.mockResolvedValue(new Response(new Blob(['csvdata'], { type: 'text/csv' })));
    await analyticsAPI.exportRequestsCSV({ days: 7, endpoint: '/foo' });
    expect(apiClient.fetchAPI).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/analytics/export/requests?'),
      expect.objectContaining({ responseType: 'blob' })
    );
    const url = apiClient.fetchAPI.mock.calls[0][0];
    expect(url).toContain('days=7');
    expect(url).toContain('endpoint=%2Ffoo');
  });
});
