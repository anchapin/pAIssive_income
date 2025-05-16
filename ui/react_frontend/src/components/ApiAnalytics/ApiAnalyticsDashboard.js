import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  ApiUsageLineChart,
  ApiEndpointBarChart,
  ApiStatusPieChart
} from '../Visualizations';

/**
 * API Analytics Dashboard component.
 * Displays comprehensive analytics for API usage.
 */
const ApiAnalyticsDashboard = () => {
  // State for analytics data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [requestsData, setRequestsData] = useState([]);
  const [endpointStats, setEndpointStats] = useState([]);
  const [statusCodeData, setStatusCodeData] = useState([]);
  const [timeRange, setTimeRange] = useState(30); // Default to 30 days

  // Fetch analytics data
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch summary data
        const summaryResponse = await fetch(`/api/v1/analytics/summary?days=${timeRange}`);
        if (!summaryResponse.ok) {
          throw new Error(`Failed to fetch summary data: ${summaryResponse.statusText}`);
        }
        const summaryData = await summaryResponse.json();
        setSummaryData(summaryData);

        // Fetch daily requests data
        const requestsResponse = await fetch(`/api/v1/analytics/requests?days=${timeRange}&aggregate=daily`);
        if (!requestsResponse.ok) {
          throw new Error(`Failed to fetch requests data: ${requestsResponse.statusText}`);
        }
        const requestsData = await requestsResponse.json();
        setRequestsData(requestsData.items);

        // Fetch endpoint stats
        const endpointResponse = await fetch(`/api/v1/analytics/endpoints?days=${timeRange}`);
        if (!endpointResponse.ok) {
          throw new Error(`Failed to fetch endpoint stats: ${endpointResponse.statusText}`);
        }
        const endpointData = await endpointResponse.json();
        setEndpointStats(endpointData);

        // Process status code data
        const statusCodes = {};
        const items = requestsData.items || [];
        items.forEach(item => {
          const statusCode = item.status_code;
          const statusGroup = Math.floor(statusCode / 100) * 100;
          const statusName = getStatusCodeName(statusGroup);

          if (!statusCodes[statusName]) {
            statusCodes[statusName] = 0;
          }
          statusCodes[statusName]++;
        });

        const processedStatusCodeData = Object.entries(statusCodes).map(([name, value]) => ({
          name,
          value
        }));

        setStatusCodeData(processedStatusCodeData);
      } catch (err) {
        console.error('Error fetching analytics data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, [timeRange]);

  // Helper function to get status code name
  const getStatusCodeName = (statusGroup) => {
    switch (statusGroup) {
      case 200:
        return 'Success (2xx)';
      case 300:
        return 'Redirect (3xx)';
      case 400:
        return 'Client Error (4xx)';
      case 500:
        return 'Server Error (5xx)';
      default:
        return `Status ${statusGroup}`;
    }
  };

  // Handle time range change
  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ m: 2 }}>
        <Alert severity="error">
          Error loading analytics data: {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          API Analytics Dashboard
        </Typography>

        {/* Time range selector */}
        <Box sx={{ mb: 3 }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel id="time-range-label">Time Range</InputLabel>
            <Select
              labelId="time-range-label"
              id="time-range-select"
              value={timeRange}
              label="Time Range"
              onChange={handleTimeRangeChange}
            >
              <MenuItem value={7}>Last 7 days</MenuItem>
              <MenuItem value={30}>Last 30 days</MenuItem>
              <MenuItem value={90}>Last 90 days</MenuItem>
              <MenuItem value={180}>Last 180 days</MenuItem>
              <MenuItem value={365}>Last 365 days</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Summary cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Requests
                </Typography>
                <Typography variant="h4">
                  {summaryData?.total_requests?.toLocaleString() || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Error Rate
                </Typography>
                <Typography variant="h4">
                  {summaryData?.error_rate ? `${(summaryData.error_rate * 100).toFixed(2)}%` : '0%'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Avg Response Time
                </Typography>
                <Typography variant="h4">
                  {summaryData?.avg_response_time ? `${summaryData.avg_response_time.toFixed(2)}ms` : '0ms'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Unique Users
                </Typography>
                <Typography variant="h4">
                  {summaryData?.unique_users?.toLocaleString() || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Charts */}
        <Grid container spacing={3}>
          {/* API Requests Over Time */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <ApiUsageLineChart
                data={requestsData}
                dataKey=os.environ.get("KEY")
                name="API Requests"
                color="#2196f3"
                height={300}
                title="API Requests Over Time"
                yAxisLabel="Requests"
              />
            </Paper>
          </Grid>

          {/* Response Time Over Time */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <ApiUsageLineChart
                data={requestsData}
                dataKey=os.environ.get("KEY")
                name="Response Time"
                color="#ff9800"
                height={300}
                title="Average Response Time"
                yAxisLabel="Time (ms)"
                tooltipFormatter={(value) => [`${value.toFixed(2)}ms`, 'Avg Response Time']}
              />
            </Paper>
          </Grid>

          {/* Error Rate Over Time */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <ApiUsageLineChart
                data={requestsData.map(item => ({
                  ...item,
                  error_rate: item.error_count / item.request_count
                }))}
                dataKey=os.environ.get("KEY")
                name="Error Rate"
                color="#f44336"
                height={300}
                title="Error Rate Over Time"
                yAxisLabel="Error Rate"
                tooltipFormatter={(value) => [`${(value * 100).toFixed(2)}%`, 'Error Rate']}
                threshold={0.05}
                thresholdLabel="5% Threshold"
              />
            </Paper>
          </Grid>

          {/* Top Endpoints by Usage */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <ApiEndpointBarChart
                data={endpointStats}
                dataKey=os.environ.get("KEY")
                name="Requests"
                color="#4caf50"
                height={400}
                title="Top Endpoints by Usage"
                showLabels={true}
              />
            </Paper>
          </Grid>

          {/* Status Code Distribution */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <ApiStatusPieChart
                data={statusCodeData}
                height={400}
                title="Status Code Distribution"
              />
            </Paper>
          </Grid>

          {/* Slowest Endpoints */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <ApiEndpointBarChart
                data={endpointStats}
                dataKey=os.environ.get("KEY")
                name="Avg Response Time (ms)"
                color="#9c27b0"
                height={400}
                title="Endpoints by Average Response Time"
                tooltipFormatter={(value) => [`${value.toFixed(2)}ms`, 'Avg Response Time']}
                showLabels={true}
              />
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default ApiAnalyticsDashboard;
