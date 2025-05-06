import React, { useState, useRef } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
  Label
} from 'recharts';
import {
  Box,
  Typography,
  Button,
  ButtonGroup,
  Paper,
  Tabs,
  Tab,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Switch,
  FormControlLabel,
  Collapse,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  useTheme,
  Menu
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import SettingsIcon from '@mui/icons-material/Settings';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import TuneIcon from '@mui/icons-material/Tune';
import TableChartIcon from '@mui/icons-material/TableChart';
import InfoIcon from '@mui/icons-material/Info';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SaveIcon from '@mui/icons-material/Save';
import InsightsIcon from '@mui/icons-material/Insights';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import MoreVertIcon from '@mui/icons-material/MoreVert';

/**
 * RevenueProjectionChart - Component for visualizing revenue projections
 *
 * This component displays revenue projections over time, allowing users to:
 * - Compare multiple revenue scenarios (optimistic, realistic, pessimistic)
 * - Adjust key parameters to see different projections
 * - Perform sensitivity analysis on critical factors
 * - View breakeven points and other key metrics
 * - Export and save projections for reporting
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of projection data points
 * @param {string} props.title - Chart title
 * @param {Object} props.additionalScenarios - Optional additional revenue scenarios
 * @param {number} props.height - Chart height in pixels (default: 400)
 * @returns {React.Component} An enhanced interactive revenue projection chart
 */
const RevenueProjectionChart = ({
  data = [],
  title = "Revenue Projection",
  additionalScenarios = null,
  height = 400
}) => {
  const theme = useTheme();
  const chartRef = useRef(null);

  // State for active tab (view mode)
  const [activeTab, setActiveTab] = useState(0);

  // State for showing table view
  const [showTable, setShowTable] = useState(false);

  // State for controlling the forecast parameters panel
  const [showForecastPanel, setShowForecastPanel] = useState(false);

  // State for sensitivity analysis dialog
  const [sensitivityDialogOpen, setSensitivityDialogOpen] = useState(false);

  // State for forecast parameters
  const [forecastParams, setForecastParams] = useState({
    growthRate: 10,
    churnRate: 5,
    conversionRate: 2.5,
    pricingTier: 'standard'
  });

  // State for displayed scenarios
  const [activeScenarios, setActiveScenarios] = useState(['baseline']);

  // Menu anchor for the more options menu
  const [anchorEl, setAnchorEl] = useState(null);

  // State for the comparison mode
  const [comparisonMode, setComparisonMode] = useState('absolute'); // 'absolute' or 'percentage'

  // Generate additional scenarios based on the baseline data
  const generateScenarios = () => {
    if (!data || data.length === 0) return {};

    // Create optimistic scenario: 20% higher revenue growth
    const optimisticData = data.map(item => ({
      ...item,
      revenue: Math.round(item.revenue * (1 + (item.month / 12) * 0.2))
    }));

    // Create pessimistic scenario: 20% lower revenue growth
    const pessimisticData = data.map(item => ({
      ...item,
      revenue: Math.round(item.revenue * (1 - (item.month / 12) * 0.2))
    }));

    // Create custom scenario based on user parameters
    const customData = generateCustomForecast();

    return {
      optimistic: optimisticData,
      pessimistic: pessimisticData,
      custom: customData
    };
  };

  // Generate a custom forecast based on user parameters
  const generateCustomForecast = () => {
    if (!data || data.length === 0) return [];

    const pricingMultiplier = {
      basic: 0.8,
      standard: 1.0,
      premium: 1.5
    };

    return data.map(item => {
      // Apply growth rate compounded monthly
      const growthFactor = Math.pow(1 + forecastParams.growthRate / 100 / 12, item.month);

      // Apply churn as reduction factor
      const churnFactor = 1 - (forecastParams.churnRate / 100) * (item.month / 12);

      // Apply conversion rate effect (simplified)
      const conversionEffect = 1 + (forecastParams.conversionRate - 2.5) / 100;

      // Apply pricing tier
      const pricingEffect = pricingMultiplier[forecastParams.pricingTier];

      // Calculate adjusted revenue
      const adjustedRevenue = Math.round(
        item.revenue * growthFactor * churnFactor * conversionEffect * pricingEffect
      );

      return {
        ...item,
        revenue: adjustedRevenue
      };
    });
  };

  // Get all scenarios data
  const scenarios = {
    baseline: data,
    ...generateScenarios(),
    ...(additionalScenarios || {})
  };

  // Update custom forecast parameters
  const handleForecastParamChange = (param, value) => {
    setForecastParams(prev => ({
      ...prev,
      [param]: value
    }));
  };

  // Toggle scenario visibility
  const toggleScenario = (scenario) => {
    setActiveScenarios(prev => {
      if (prev.includes(scenario)) {
        return prev.filter(s => s !== scenario);
      } else {
        return [...prev, scenario];
      }
    });
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Handle menu open/close
  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  // Calculate key metrics for analysis
  const calculateMetrics = () => {
    if (!data || data.length === 0) return {};

    // Find breakeven point (assuming costs start at 20% of first month revenue and grow at 5% per month)
    const initialCost = data[0].revenue * 0.8;
    let breakevenMonth = null;
    let cumulativeRevenue = 0;
    let cumulativeCost = initialCost;

    for (let i = 0; i < data.length; i++) {
      cumulativeRevenue += data[i].revenue;
      cumulativeCost += initialCost * Math.pow(1.05, i);

      if (cumulativeRevenue >= cumulativeCost && breakevenMonth === null) {
        breakevenMonth = data[i].month;
      }
    }

    // Calculate total projected revenue
    const totalProjectedRevenue = data.reduce((sum, item) => sum + item.revenue, 0);

    // Calculate average monthly growth rate
    const monthlyGrowth = data.length > 1 ?
      Math.pow(data[data.length - 1].revenue / data[0].revenue, 1 / (data.length - 1)) - 1 :
      0;

    return {
      breakevenMonth,
      totalProjectedRevenue,
      monthlyGrowthRate: monthlyGrowth * 100,
      peakRevenueMonth: data.reduce((max, item) => item.revenue > max.revenue ? item : max, data[0]),
    };
  };

  // Calculate metrics for the current data
  const metrics = calculateMetrics();

  // Export data to CSV or JSON
  const exportData = (format) => {
    handleMenuClose();

    if (format === 'csv') {
      // Create CSV content with active scenarios
      let csvContent = "data:text/csv;charset=utf-8,Month,Date";

      // Add column headers for each active scenario
      activeScenarios.forEach(scenario => {
        csvContent += `,${scenario.charAt(0).toUpperCase() + scenario.slice(1)}`;
      });
      csvContent += "\n";

      // Add data rows
      data.forEach((item, index) => {
        const row = [`${item.month}`, `${item.date}`];

        activeScenarios.forEach(scenario => {
          const scenarioData = scenarios[scenario][index];
          row.push(scenarioData ? scenarioData.revenue : '');
        });

        csvContent += row.join(',') + "\n";
      });

      // Create download link
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `${title.replace(/\s+/g, '_')}_projections.csv`);
      document.body.appendChild(link);

      // Trigger download and cleanup
      link.click();
      document.body.removeChild(link);
    } else if (format === 'json') {
      // Create JSON content with active scenarios
      const exportData = {
        title,
        date: new Date().toISOString(),
        scenarios: {}
      };

      activeScenarios.forEach(scenario => {
        exportData.scenarios[scenario] = scenarios[scenario];
      });

      // Create download link
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `${title.replace(/\s+/g, '_')}_projections.json`);
      document.body.appendChild(link);

      // Trigger download and cleanup
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  // Color mapping for scenarios
  const scenarioColors = {
    baseline: theme.palette.primary.main,
    optimistic: theme.palette.success.main,
    pessimistic: theme.palette.error.main,
    custom: theme.palette.warning.main
  };

  // Custom tooltip formatter
  const customTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Paper
          elevation={3}
          sx={{
            padding: 2,
            backgroundColor: 'white',
            minWidth: '200px'
          }}
        >
          <Typography variant="subtitle2">
            {payload[0].payload.date}
          </Typography>
          <Divider sx={{ my: 1 }} />

          {payload.map((entry, index) => {
            // Skip entries that don't belong to active scenarios
            const scenarioName = entry.dataKey.split('_')[1] || 'baseline';
            if (!activeScenarios.includes(scenarioName)) return null;

            return (
              <Box
                key={`item-${index}`}
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mb: 0.5
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      backgroundColor: entry.color,
                      marginRight: 1,
                      borderRadius: '50%'
                    }}
                  />
                  <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                    {scenarioName}:
                  </Typography>
                </Box>
                <Typography variant="body2" fontWeight="bold">
                  {formatCurrency(entry.value)}
                </Typography>
              </Box>
            );
          })}

          {payload.length > 1 && comparisonMode === 'percentage' && (
            <>
              <Divider sx={{ my: 1 }} />
              <Box sx={{ mt: 1 }}>
                {payload.slice(1).map((entry, index) => {
                  const baselineValue = payload[0].value;
                  const percentDiff = ((entry.value - baselineValue) / baselineValue * 100).toFixed(1);
                  const isPositive = entry.value > baselineValue;

                  const scenarioName = entry.dataKey.split('_')[1] || '';
                  if (!activeScenarios.includes(scenarioName)) return null;

                  return (
                    <Box
                      key={`diff-${index}`}
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        mb: 0.5
                      }}
                    >
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {scenarioName} vs. Baseline:
                      </Typography>
                      <Typography
                        variant="body2"
                        fontWeight="bold"
                        color={isPositive ? 'success.main' : 'error.main'}
                        sx={{ display: 'flex', alignItems: 'center' }}
                      >
                        {isPositive ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />}
                        {percentDiff}%
                      </Typography>
                    </Box>
                  );
                })}
              </Box>
            </>
          )}
        </Paper>
      );
    }
    return null;
  };

  return (
    <Card className="chart-container" ref={chartRef} variant="outlined">
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{title}</Typography>
          <Box>
            <ButtonGroup variant="outlined" size="small" sx={{ mr: 1 }}>
              <Button
                startIcon={<TuneIcon />}
                onClick={() => setShowForecastPanel(!showForecastPanel)}
                color={showForecastPanel ? "primary" : "inherit"}
              >
                Parameters
              </Button>
              <Button
                startIcon={<TableChartIcon />}
                onClick={() => setShowTable(!showTable)}
                color={showTable ? "primary" : "inherit"}
              >
                Table
              </Button>
              <Button
                startIcon={<InsightsIcon />}
                onClick={() => setSensitivityDialogOpen(true)}
              >
                Sensitivity
              </Button>
            </ButtonGroup>

            <IconButton onClick={handleMenuClick}>
              <MoreVertIcon />
            </IconButton>

            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={() => exportData('csv')}>
                <FileDownloadIcon fontSize="small" sx={{ mr: 1 }} />
                Export as CSV
              </MenuItem>
              <MenuItem onClick={() => exportData('json')}>
                <FileDownloadIcon fontSize="small" sx={{ mr: 1 }} />
                Export as JSON
              </MenuItem>
              <MenuItem onClick={() => setComparisonMode(comparisonMode === 'absolute' ? 'percentage' : 'absolute')}>
                <CompareArrowsIcon fontSize="small" sx={{ mr: 1 }} />
                {comparisonMode === 'absolute' ? 'Show % Differences' : 'Show Absolute Values'}
              </MenuItem>
            </Menu>
          </Box>
        </Box>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Revenue" />
            <Tab label="Analysis" />
            <Tab label="Scenarios" />
          </Tabs>
        </Box>

        <Box sx={{ mb: 2 }}>
          {/* Scenario toggles */}
          <ButtonGroup variant="outlined" size="small">
            <Button
              onClick={() => toggleScenario('baseline')}
              sx={{
                borderColor: activeScenarios.includes('baseline') ? scenarioColors.baseline : undefined,
                color: activeScenarios.includes('baseline') ? scenarioColors.baseline : undefined,
                fontWeight: activeScenarios.includes('baseline') ? 'bold' : 'normal'
              }}
            >
              Baseline
            </Button>
            <Button
              onClick={() => toggleScenario('optimistic')}
              sx={{
                borderColor: activeScenarios.includes('optimistic') ? scenarioColors.optimistic : undefined,
                color: activeScenarios.includes('optimistic') ? scenarioColors.optimistic : undefined,
                fontWeight: activeScenarios.includes('optimistic') ? 'bold' : 'normal'
              }}
            >
              Optimistic
            </Button>
            <Button
              onClick={() => toggleScenario('pessimistic')}
              sx={{
                borderColor: activeScenarios.includes('pessimistic') ? scenarioColors.pessimistic : undefined,
                color: activeScenarios.includes('pessimistic') ? scenarioColors.pessimistic : undefined,
                fontWeight: activeScenarios.includes('pessimistic') ? 'bold' : 'normal'
              }}
            >
              Pessimistic
            </Button>
            <Button
              onClick={() => toggleScenario('custom')}
              sx={{
                borderColor: activeScenarios.includes('custom') ? scenarioColors.custom : undefined,
                color: activeScenarios.includes('custom') ? scenarioColors.custom : undefined,
                fontWeight: activeScenarios.includes('custom') ? 'bold' : 'normal'
              }}
            >
              Custom
            </Button>
          </ButtonGroup>
        </Box>

        <Collapse in={showForecastPanel}>
          <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Forecast Parameters
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" gutterBottom>
                  Growth Rate: {forecastParams.growthRate}%
                </Typography>
                <Slider
                  value={forecastParams.growthRate}
                  onChange={(e, val) => handleForecastParamChange('growthRate', val)}
                  min={0}
                  max={30}
                  step={0.5}
                  marks={[
                    { value: 0, label: '0%' },
                    { value: 15, label: '15%' },
                    { value: 30, label: '30%' }
                  ]}
                />
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" gutterBottom>
                  Churn Rate: {forecastParams.churnRate}%
                </Typography>
                <Slider
                  value={forecastParams.churnRate}
                  onChange={(e, val) => handleForecastParamChange('churnRate', val)}
                  min={0}
                  max={20}
                  step={0.5}
                  marks={[
                    { value: 0, label: '0%' },
                    { value: 10, label: '10%' },
                    { value: 20, label: '20%' }
                  ]}
                />
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" gutterBottom>
                  Conversion Rate: {forecastParams.conversionRate}%
                </Typography>
                <Slider
                  value={forecastParams.conversionRate}
                  onChange={(e, val) => handleForecastParamChange('conversionRate', val)}
                  min={0.5}
                  max={5}
                  step={0.1}
                  marks={[
                    { value: 0.5, label: '0.5%' },
                    { value: 2.5, label: '2.5%' },
                    { value: 5, label: '5%' }
                  ]}
                />
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel id="pricing-tier-label">Pricing Tier</InputLabel>
                  <Select
                    labelId="pricing-tier-label"
                    value={forecastParams.pricingTier}
                    onChange={(e) => handleForecastParamChange('pricingTier', e.target.value)}
                    size="small"
                  >
                    <MenuItem value="basic">Basic (-20%)</MenuItem>
                    <MenuItem value="standard">Standard</MenuItem>
                    <MenuItem value="premium">Premium (+50%)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>
        </Collapse>

        {/* Revenue Projection Chart */}
        {activeTab === 0 && (
          <ResponsiveContainer width="100%" height={height}>
            <LineChart
              data={data}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                padding={{ left: 20, right: 20 }}
                tick={{ fontSize: 12 }}
              />
              <YAxis
                tickFormatter={(value) => formatCurrency(value)}
                width={80}
              />
              <Tooltip content={customTooltip} />
              <Legend />

              {/* Breakeven reference line */}
              {metrics.breakevenMonth && (
                <ReferenceLine
                  x={data.find(d => d.month === metrics.breakevenMonth)?.date}
                  stroke="#2e7d32"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                >
                  <Label
                    value="Break Even"
                    position="top"
                    fill="#2e7d32"
                    fontSize={12}
                  />
                </ReferenceLine>
              )}

              {/* Render each active scenario line */}
              {activeScenarios.includes('baseline') && (
                <Line
                  type="monotone"
                  dataKey="revenue"
                  name="Baseline"
                  stroke={scenarioColors.baseline}
                  strokeWidth={2}
                  activeDot={{ r: 8 }}
                />
              )}

              {activeScenarios.includes('optimistic') && scenarios.optimistic && (
                <Line
                  type="monotone"
                  dataKey={(entry, index) => scenarios.optimistic[index]?.revenue}
                  name="Optimistic"
                  stroke={scenarioColors.optimistic}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              )}

              {activeScenarios.includes('pessimistic') && scenarios.pessimistic && (
                <Line
                  type="monotone"
                  dataKey={(entry, index) => scenarios.pessimistic[index]?.revenue}
                  name="Pessimistic"
                  stroke={scenarioColors.pessimistic}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              )}

              {activeScenarios.includes('custom') && scenarios.custom && (
                <Line
                  type="monotone"
                  dataKey={(entry, index) => scenarios.custom[index]?.revenue}
                  name="Custom"
                  stroke={scenarioColors.custom}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              )}

              <Brush
                dataKey="date"
                height={30}
                stroke="#8884d8"
                startIndex={0}
                endIndex={Math.min(11, data.length - 1)}
              />
            </LineChart>
          </ResponsiveContainer>
        )}

        {/* Analysis View */}
        {activeTab === 1 && (
          <Grid container spacing={3}>
            {/* Key metrics cards */}
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Projected Revenue
                  </Typography>
                  <Typography variant="h5" component="div">
                    {formatCurrency(metrics.totalProjectedRevenue)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Break Even Point
                  </Typography>
                  <Typography variant="h5" component="div">
                    {metrics.breakevenMonth !== null ? `Month ${metrics.breakevenMonth}` : 'N/A'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Monthly Growth Rate
                  </Typography>
                  <Typography variant="h5" component="div">
                    {metrics.monthlyGrowthRate.toFixed(1)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Peak Revenue Month
                  </Typography>
                  <Typography variant="h5" component="div">
                    {metrics.peakRevenueMonth.date}
                  </Typography>
                  <Typography color="text.secondary">
                    {formatCurrency(metrics.peakRevenueMonth.revenue)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Analysis charts */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Cumulative Revenue
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart
                  data={data.map((item, index) => {
                    // Calculate cumulative revenue up to this point
                    let cumRevenue = 0;
                    for (let i = 0; i <= index; i++) {
                      cumRevenue += data[i].revenue;
                    }

                    return {
                      ...item,
                      cumulative: cumRevenue
                    };
                  })}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis tickFormatter={(value) => formatCurrency(value)} />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Line
                    type="monotone"
                    dataKey="cumulative"
                    name="Cumulative Revenue"
                    stroke="#8884d8"
                    fill="#8884d8"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Monthly Growth
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart
                  data={data.map((item, index) => {
                    // Calculate month-over-month growth
                    let growthPercent = 0;
                    if (index > 0 && data[index - 1].revenue > 0) {
                      growthPercent = ((item.revenue / data[index - 1].revenue) - 1) * 100;
                    }

                    return {
                      ...item,
                      growth: growthPercent
                    };
                  }).slice(1)} // Skip first month as it has no growth data
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis
                    tickFormatter={(value) => `${value.toFixed(1)}%`}
                  />
                  <ReferenceLine y={0} stroke="#000" />
                  <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
                  <Line
                    type="monotone"
                    dataKey="growth"
                    name="Monthly Growth"
                    stroke="#82ca9d"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Grid>
          </Grid>
        )}

        {/* Scenario Comparison View */}
        {activeTab === 2 && (
          <Grid container spacing={3}>
            {/* Scenario comparison table */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Scenario Comparison
              </Typography>

              <Paper variant="outlined">
                <Box sx={{ p: 2, overflowX: 'auto' }}>
                  <table style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    textAlign: 'left'
                  }}>
                    <thead>
                      <tr>
                        <th style={{ padding: '8px', borderBottom: '1px solid #eee' }}>Metric</th>
                        {activeScenarios.map(scenario => (
                          <th
                            key={scenario}
                            style={{
                              padding: '8px',
                              borderBottom: '1px solid #eee',
                              color: scenarioColors[scenario]
                            }}
                          >
                            {scenario.charAt(0).toUpperCase() + scenario.slice(1)}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>
                          Total Revenue
                        </td>
                        {activeScenarios.map(scenario => {
                          const scenarioData = scenarios[scenario];
                          const total = scenarioData.reduce((sum, item) => sum + item.revenue, 0);

                          return (
                            <td
                              key={scenario}
                              style={{ padding: '8px', borderBottom: '1px solid #eee' }}
                            >
                              {formatCurrency(total)}
                            </td>
                          );
                        })}
                      </tr>
                      <tr>
                        <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>
                          Average Monthly
                        </td>
                        {activeScenarios.map(scenario => {
                          const scenarioData = scenarios[scenario];
                          const avg = scenarioData.reduce((sum, item) => sum + item.revenue, 0) / scenarioData.length;

                          return (
                            <td
                              key={scenario}
                              style={{ padding: '8px', borderBottom: '1px solid #eee' }}
                            >
                              {formatCurrency(avg)}
                            </td>
                          );
                        })}
                      </tr>
                      <tr>
                        <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>
                          Final Month
                        </td>
                        {activeScenarios.map(scenario => {
                          const scenarioData = scenarios[scenario];
                          const finalRevenue = scenarioData[scenarioData.length - 1].revenue;

                          return (
                            <td
                              key={scenario}
                              style={{ padding: '8px', borderBottom: '1px solid #eee' }}
                            >
                              {formatCurrency(finalRevenue)}
                            </td>
                          );
                        })}
                      </tr>
                      <tr>
                        <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>
                          Peak Revenue
                        </td>
                        {activeScenarios.map(scenario => {
                          const scenarioData = scenarios[scenario];
                          const peak = scenarioData.reduce(
                            (max, item) => item.revenue > max ? item.revenue : max,
                            0
                          );

                          return (
                            <td
                              key={scenario}
                              style={{ padding: '8px', borderBottom: '1px solid #eee' }}
                            >
                              {formatCurrency(peak)}
                            </td>
                          );
                        })}
                      </tr>
                      <tr>
                        <td style={{ padding: '8px' }}>
                          Growth Rate
                        </td>
                        {activeScenarios.map(scenario => {
                          const scenarioData = scenarios[scenario];
                          const monthlyGrowth = scenarioData.length > 1 ?
                            Math.pow(scenarioData[scenarioData.length - 1].revenue / scenarioData[0].revenue, 1 / (scenarioData.length - 1)) - 1 :
                            0;

                          return (
                            <td
                              key={scenario}
                              style={{ padding: '8px' }}
                            >
                              {(monthlyGrowth * 100).toFixed(1)}%
                            </td>
                          );
                        })}
                      </tr>
                    </tbody>
                  </table>
                </Box>
              </Paper>
            </Grid>

            {/* Full Data Table */}
            {showTable && (
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Monthly Projections
                </Typography>

                <Paper variant="outlined">
                  <Box sx={{ p: 2, overflowX: 'auto' }}>
                    <table style={{
                      width: '100%',
                      borderCollapse: 'collapse',
                      textAlign: 'left',
                      fontSize: '0.9rem'
                    }}>
                      <thead>
                        <tr>
                          <th style={{ padding: '8px', borderBottom: '1px solid #eee' }}>Month</th>
                          <th style={{ padding: '8px', borderBottom: '1px solid #eee' }}>Date</th>
                          {activeScenarios.map(scenario => (
                            <th
                              key={scenario}
                              style={{
                                padding: '8px',
                                borderBottom: '1px solid #eee',
                                color: scenarioColors[scenario]
                              }}
                            >
                              {scenario.charAt(0).toUpperCase() + scenario.slice(1)}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {data.map((item, index) => (
                          <tr key={index}>
                            <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>
                              {item.month}
                            </td>
                            <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>
                              {item.date}
                            </td>

                            {activeScenarios.map(scenario => {
                              const scenarioData = scenarios[scenario][index];

                              return (
                                <td
                                  key={scenario}
                                  style={{ padding: '8px', borderBottom: '1px solid #eee' }}
                                >
                                  {formatCurrency(scenarioData ? scenarioData.revenue : 0)}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                </Paper>
              </Grid>
            )}
          </Grid>
        )}

        {/* Sensitivity Analysis Dialog */}
        <Dialog
          open={sensitivityDialogOpen}
          onClose={() => setSensitivityDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6">
                Revenue Sensitivity Analysis
              </Typography>
            </Box>
          </DialogTitle>
          <DialogContent dividers>
            <Typography variant="subtitle1" gutterBottom>
              Impact of Key Parameters on Total Revenue
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="body2" gutterBottom>
                  The chart below shows how changing different parameters affects the projected total revenue.
                  Each bar shows the revenue impact when increasing the parameter by 10%.
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={[
                      {
                        name: 'Growth Rate',
                        impact: 15, // These are simulated values for illustration
                        value: formatCurrency(metrics.totalProjectedRevenue * 1.15)
                      },
                      {
                        name: 'Conversion Rate',
                        impact: 8,
                        value: formatCurrency(metrics.totalProjectedRevenue * 1.08)
                      },
                      {
                        name: 'Pricing',
                        impact: 10,
                        value: formatCurrency(metrics.totalProjectedRevenue * 1.10)
                      },
                      {
                        name: 'Churn Rate',
                        impact: -12,
                        value: formatCurrency(metrics.totalProjectedRevenue * 0.88)
                      },
                      {
                        name: 'Marketing Spend',
                        impact: 7,
                        value: formatCurrency(metrics.totalProjectedRevenue * 1.07)
                      }
                    ]}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    layout="vertical"
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" tickFormatter={(value) => `${value}%`} />
                    <YAxis dataKey="name" type="category" />
                    <Tooltip
                      formatter={(value, name, props) => [
                        `${value}%`, 'Revenue Impact'
                      ]}
                      labelFormatter={() => '10% Increase In Parameter'}
                    />
                    <Bar
                      dataKey="impact"
                      fill={(entry) => entry.impact > 0 ? '#4caf50' : '#f44336'}
                      label={{
                        position: 'right',
                        formatter: (item) => `${item.impact > 0 ? '+' : ''}${item.impact}%`
                      }}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Scenario Analysis
                </Typography>

                <TableContainer component={Paper} variant="outlined">
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr>
                        <th style={{ padding: '12px', border: '1px solid #eee', textAlign: 'left' }}>Scenario</th>
                        <th style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right' }}>Total Revenue</th>
                        <th style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right' }}>Change</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid #eee' }}>Baseline</td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right' }}>
                          {formatCurrency(metrics.totalProjectedRevenue)}
                        </td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right' }}>-</td>
                      </tr>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid #eee' }}>Growth Rate +10%</td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right' }}>
                          {formatCurrency(metrics.totalProjectedRevenue * 1.15)}
                        </td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right', color: '#4caf50' }}>
                          +15.0%
                        </td>
                      </tr>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid #eee' }}>Growth Rate -10%</td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right' }}>
                          {formatCurrency(metrics.totalProjectedRevenue * 0.85)}
                        </td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right', color: '#f44336' }}>
                          -15.0%
                        </td>
                      </tr>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid #eee' }}>Pricing +20%</td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right' }}>
                          {formatCurrency(metrics.totalProjectedRevenue * 1.2)}
                        </td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right', color: '#4caf50' }}>
                          +20.0%
                        </td>
                      </tr>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid #eee' }}>Churn Rate +5%</td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right' }}>
                          {formatCurrency(metrics.totalProjectedRevenue * 0.94)}
                        </td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right', color: '#f44336' }}>
                          -6.0%
                        </td>
                      </tr>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid #eee' }}>Best Case Combined</td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right' }}>
                          {formatCurrency(metrics.totalProjectedRevenue * 1.45)}
                        </td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right', color: '#4caf50' }}>
                          +45.0%
                        </td>
                      </tr>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid #eee' }}>Worst Case Combined</td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right' }}>
                          {formatCurrency(metrics.totalProjectedRevenue * 0.65)}
                        </td>
                        <td style={{ padding: '12px', border: '1px solid #eee', textAlign: 'right', color: '#f44336' }}>
                          -35.0%
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </TableContainer>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSensitivityDialogOpen(false)}>Close</Button>
            <Button
              color="primary"
              variant="contained"
              startIcon={<FileDownloadIcon />}
              onClick={() => {
                // Would export the analysis in a real app
                setSensitivityDialogOpen(false);
              }}
            >
              Export Analysis
            </Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

export default RevenueProjectionChart;
