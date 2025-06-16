/**
 * Tests for the apiClient module
 */

import apiClient, {
  nicheAnalysisAPI,
  developerAPI,
  monetizationAPI,
  marketingAPI,
  dashboardAPI,
  userAPI,
} from './apiClient';

const originalEnv = process.env;

describe('apiClient', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
    global.fetch = vi.fn();
    process.env = { ...originalEnv, NODE_ENV: 'development' };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('calls correct URL and method for user.getCurrentUser', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({ id: 'user', name: 'User' })
    });
    const data = await userAPI.getCurrentUser();
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/user/profile'),
      expect.objectContaining({ method: undefined, headers: expect.any(Object), signal: expect.any(Object) })
    );
    expect(data).toEqual({ id: 'user', name: 'User' });
  });

  it('calls correct method and body for user.login', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({ id: 'user', name: 'User' })
    });
    const creds = { username: 'x', password: 'y' };
    await userAPI.login(creds);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/auth/login'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(creds),
        headers: expect.any(Object),
        signal: expect.any(Object)
      })
    );
  });

  it('handles non-JSON responses', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: { get: () => '' }
    });
    const resp = await userAPI.logout();
    expect(resp.ok).toBe(true);
  });

  it('throws on API error with JSON message', async () => {
    global.fetch.mockResolvedValue({
      ok: false,
      headers: { get: () => 'application/json' },
      json: async () => ({ message: 'bad request' })
    });
    await expect(userAPI.getCurrentUser()).rejects.toThrow('bad request');
  });

  it('calls correct endpoint for dashboard.getProjectsOverview', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({ projects: [1, 2] })
    });
    const data = await dashboardAPI.getProjectsOverview();
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/dashboard/overview'),
      expect.any(Object)
    );
    expect(data).toEqual({ projects: [1, 2] });
  });

  it('returns mock data in development on fetch error', async () => {
    global.fetch.mockRejectedValue(new Error('fail'));
    const data = await dashboardAPI.getProjectsOverview();
    expect(data).toEqual({ projects: [], totalRevenue: 0, totalSubscribers: 0 });
  });

  it('returns mock user in development on fetch error', async () => {
    global.fetch.mockRejectedValue(new Error('fail'));
    const data = await userAPI.getCurrentUser();
    expect(data).toEqual({ id: 'mock-user', name: 'Test User', email: 'test@example.com' });
  });

  it('throws error in production on fetch error', async () => {
    process.env = { ...originalEnv, NODE_ENV: 'production' };
    global.fetch.mockRejectedValue(new Error('fail'));
    await expect(userAPI.getCurrentUser()).rejects.toThrow('fail');
  });

  it('nicheAnalysis.analyzeNiches calls correct endpoint', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({ result: 'ok' })
    });
    await nicheAnalysisAPI.analyzeNiches(['n1', 'n2']);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/niche-analysis/analyze'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ segments: ['n1', 'n2'] })
      })
    );
  });

  it('developer.generateSolution calls correct endpoint', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({ solution: 'ok' })
    });
    await developerAPI.generateSolution('n1', 't1');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/developer/solution'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ nicheId: 'n1', templateId: 't1' })
      })
    );
  });

  it('monetization.generateStrategy calls correct endpoint', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({ strategy: 'ok' })
    });
    await monetizationAPI.generateStrategy('s1', { foo: 1 });
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/monetization/strategy'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ solutionId: 's1', options: { foo: 1 } })
      })
    );
  });

  it('marketing.generateCampaign calls correct endpoint', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({ campaign: 'ok' })
    });
    await marketingAPI.generateCampaign('s2', [1], [2]);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/marketing/campaign'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ solutionId: 's2', audienceIds: [1], channelIds: [2] })
      })
    );
  });
});