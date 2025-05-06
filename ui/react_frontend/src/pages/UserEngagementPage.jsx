import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Slider,
  Stack,
  Chip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import DateRangeIcon from '@mui/icons-material/DateRange';

// Import our user engagement visualization components
import {
  ConversionFunnelChart,
  CohortRetentionChart,
  UserActivityChart
} from '../components/Visualizations';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
}));

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`visualization-tabpanel-${index}`}
      aria-labelledby={`visualization-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const UserEngagementPage = () => {
  // State variables
  const [tabValue, setTabValue] = useState(0);
  const [dateRange, setDateRange] = useState('last30days');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [userSegment, setUserSegment] = useState('all');

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle filter changes
  const handleDateRangeChange = (event) => {
    setDateRange(event.target.value);
  };

  const handlePlatformFilterChange = (event) => {
    setPlatformFilter(event.target.value);
  };

  const handleUserSegmentChange = (event) => {
    setUserSegment(event.target.value);
  };

  const handleRefreshData = () => {
    // In a real app, this would fetch new data based on the filters
    console.log('Refreshing data with filters:', { dateRange, platformFilter, userSegment });
  };

  // Mock data for the Conversion Funnel
  const mockFunnelData = [
    { name: 'Website Visitors', value: 10000 },
    { name: 'Signup Page Views', value: 5000 },
    { name: 'Signup Started', value: 3200 },
    { name: 'Signup Completed', value: 2000 },
    { name: 'Product Usage', value: 1500 },
    { name: 'Paid Conversion', value: 300 }
  ];

  // Mock data for Cohort Retention
  const mockRetentionData = [
    {
      size: 1200,
      retention: [100, 80, 65, 55, 48, 45, 40, 38, 35, 33, 31, 30]
    },
    {
      size: 980,
      retention: [100, 82, 67, 58, 50, 44, 40, 38, 36, 35, 33]
    },
    {
      size: 1050,
      retention: [100, 78, 62, 52, 46, 42, 39, 37, 35, 33]
    },
    {
      size: 1300,
      retention: [100, 75, 60, 50, 43, 39, 35, 33, 31]
    },
    {
      size: 1100,
      retention: [100, 78, 64, 52, 45, 41, 38, 35]
    },
    {
      size: 950,
      retention: [100, 82, 67, 57, 48, 44, 40]
    },
    {
      size: 1250,
      retention: [100, 83, 70, 60, 52, 48]
    },
    {
      size: 1400,
      retention: [100, 84, 72, 62, 54]
    },
    {
      size: 1550,
      retention: [100, 85, 73, 65]
    },
    {
      size: 1700,
      retention: [100, 86, 75]
    },
    {
      size: 1850,
      retention: [100, 87]
    },
    {
      size: 2000,
      retention: [100]
    }
  ];

  const cohortLabels = [
    'Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025', 'May 2025',
    'Jun 2025', 'Jul 2025', 'Aug 2025', 'Sep 2025', 'Oct 2025',
    'Nov 2025', 'Dec 2025'
  ];

  // Mock data for User Activity Chart
  const mockActivityData = Array.from({ length: 90 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (90 - i));
    const dateString = date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });

    // Create some patterns in the data
    const dayOfWeek = date.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;

    // Base values
    let dau = 200 + i * 5 + (isWeekend ? -100 : 0);
    let wau = 800 + i * 12;
    let mau = 3000 + i * 25;

    // Add some randomness
    dau += Math.floor(Math.random() * 50);
    wau += Math.floor(Math.random() * 100);
    mau += Math.floor(Math.random() * 200);

    // Session metrics
    const avg_session_time = 10 + Math.random() * 5;
    const avg_actions_per_session = 8 + Math.random() * 3;

    return {
      date: dateString,
      dau,
      wau,
      mau,
      avg_session_time,
      avg_actions_per_session,
    };
  });

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        User Engagement Analysis
      </Typography>
      <Typography variant="subtitle1" paragraph>
        Monitor and analyze user engagement metrics to improve user retention and product experience.
      </Typography>

      {/* Filters */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12}>
          <Item>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Date Range</InputLabel>
                  <Select
                    value={dateRange}
                    label="Date Range"
                    onChange={handleDateRangeChange}
                  >
                    <MenuItem value="last7days">Last 7 Days</MenuItem>
                    <MenuItem value="last30days">Last 30 Days</MenuItem>
                    <MenuItem value="last90days">Last 90 Days</MenuItem>
                    <MenuItem value="last6months">Last 6 Months</MenuItem>
                    <MenuItem value="lastyear">Last Year</MenuItem>
                    <MenuItem value="custom">Custom Range</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Platform</InputLabel>
                  <Select
                    value={platformFilter}
                    label="Platform"
                    onChange={handlePlatformFilterChange}
                  >
                    <MenuItem value="all">All Platforms</MenuItem>
                    <MenuItem value="web">Web</MenuItem>
                    <MenuItem value="mobile">Mobile</MenuItem>
                    <MenuItem value="desktop">Desktop</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>User Segment</InputLabel>
                  <Select
                    value={userSegment}
                    label="User Segment"
                    onChange={handleUserSegmentChange}
                  >
                    <MenuItem value="all">All Users</MenuItem>
                    <MenuItem value="free">Free Users</MenuItem>
                    <MenuItem value="paid">Paid Users</MenuItem>
                    <MenuItem value="new">New Users</MenuItem>
                    <MenuItem value="returning">Returning Users</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={3}>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<DateRangeIcon />}
                  fullWidth
                  onClick={handleRefreshData}
                >
                  Apply Filters
                </Button>
              </Grid>
            </Grid>
          </Item>
        </Grid>
      </Grid>

      {/* Key Metrics */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Daily Active Users
              </Typography>
              <Typography variant="h4">
                {mockActivityData[mockActivityData.length - 1].dau.toLocaleString()}
              </Typography>
              <Typography color="success.main" variant="body2">
                +5.2% from previous period
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Monthly Active Users
              </Typography>
              <Typography variant="h4">
                {mockActivityData[mockActivityData.length - 1].mau.toLocaleString()}
              </Typography>
              <Typography color="success.main" variant="body2">
                +12.8% from previous period
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Avg. Session Duration
              </Typography>
              <Typography variant="h4">
                {mockActivityData[mockActivityData.length - 1].avg_session_time.toFixed(1)} min
              </Typography>
              <Typography color="success.main" variant="body2">
                +1.5 min from previous period
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Retention Rate (30 days)
              </Typography>
              <Typography variant="h4">
                42.3%
              </Typography>
              <Typography color="error.main" variant="body2">
                -1.8% from previous period
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main content with tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="engagement visualizations">
          <Tab label="User Activity" />
          <Tab label="Conversion Funnel" />
          <Tab label="Cohort Retention" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <UserActivityChart
          data={mockActivityData}
          title="User Activity Over Time"
          height={500}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <ConversionFunnelChart
          data={mockFunnelData}
          title="User Conversion Funnel"
          height={500}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <CohortRetentionChart
          data={mockRetentionData}
          cohortLabels={cohortLabels}
          title="Monthly Cohort Retention Analysis"
          periodLabel="Month"
        />
      </TabPanel>
    </Box>
  );
};

export default UserEngagementPage;
