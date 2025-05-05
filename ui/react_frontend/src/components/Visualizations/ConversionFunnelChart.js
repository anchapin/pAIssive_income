import React, { useState, useRef } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  LabelList,
  ResponsiveContainer
} from 'recharts';
import {
  Box,
  Typography,
  Button,
  ButtonGroup,
  FormControl,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Card,
  CardContent,
  Divider,
  Menu,
  Grid,
  Tabs,
  Tab,
  Chip,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import EqualizerIcon from '@mui/icons-material/Equalizer';
import CompareIcon from '@mui/icons-material/Compare';
import InfoIcon from '@mui/icons-material/Info';

/**
 * ConversionFunnelChart - Component for visualizing user conversion funnels
 *
 * This component displays a conversion funnel visualization showing the progression
 * of users through different stages of a conversion process, such as from visitors
 * to free users to paid subscribers.
 *
 * Enhanced with interactive features like:
 * - Drill-down analysis for each funnel stage
 * - Time-period comparison
 * - Data export and sharing options
 * - Detailed conversion metrics and insights
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of funnel stage data objects
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 400)
 * @param {Object} props.comparisonData - Optional data for comparing funnels (previous period)
 * @param {Array} props.segmentOptions - Optional list of user segments for filtering
 * @returns {React.Component} An enhanced interactive funnel chart component
 */
const ConversionFunnelChart = ({
  data = [],
  title = "User Conversion Funnel",
  height = 400,
  comparisonData = null,
  segmentOptions = ["All Users", "New Users", "Returning Users", "Mobile Users", "Desktop Users"]
}) => {
  // State for showing comparison funnel
  const [showComparison, setShowComparison] = useState(false);

  // State for display options
  const [sortMethod, setSortMethod] = useState('default');
  const [selectedSegment, setSelectedSegment] = useState("All Users");

  // State for drill-down dialog
  const [drilldownOpen, setDrilldownOpen] = useState(false);
  const [selectedStage, setSelectedStage] = useState(null);
  const [drilldownTabValue, setDrilldownTabValue] = useState(0);

  // Menu state
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  // Chart ref for exporting
  const chartRef = useRef(null);

  // If no data, return a message
  if (!Array.isArray(data) || data.length === 0) {
    return <div>No conversion funnel data available for visualization</div>;
  }

  // Function to sort data based on selected method
  const getSortedData = (inputData) => {
    if (!inputData) return [];

    let sortedData = [...inputData];

    switch (sortMethod) {
      case 'value-desc':
        return sortedData.sort((a, b) => b.value - a.value);
      case 'value-asc':
        return sortedData.sort((a, b) => a.value - b.value);
      case 'name-asc':
        return sortedData.sort((a, b) => a.name.localeCompare(b.name));
      case 'name-desc':
        return sortedData.sort((a, b) => b.name.localeCompare(a.name));
      case 'default':
      default:
        // Keep original order which is typically the funnel flow order
        return sortedData;
    }
  };

  // Calculate conversion rates between stages
  const calculateFunnelData = (inputData) => {
    if (!inputData) return [];

    const processedData = getSortedData(inputData);

    return processedData.map((item, index) => {
      const nextItem = processedData[index + 1];
      const prevItem = index > 0 ? processedData[index - 1] : null;

      // Calculate conversion rates
      const conversionRate = nextItem ? (nextItem.value / item.value) * 100 : null;
      const previousConversionRate = prevItem ? (item.value / prevItem.value) * 100 : null;

      return {
        ...item,
        conversionRate: conversionRate !== null ? conversionRate.toFixed(1) : null,
        dropoff: conversionRate !== null ? 100 - conversionRate : null,
        previousConversionRate: previousConversionRate !== null ? previousConversionRate.toFixed(1) : null,
        percentOfTop: index > 0 ? (item.value / processedData[0].value * 100).toFixed(1) : "100.0"
      };
    });
  };

  const funnelData = calculateFunnelData(data);
  const comparisonFunnelData = calculateFunnelData(comparisonData);

  // Generate mock drill-down data for a selected funnel stage
  const generateDrilldownData = (stage) => {
    if (!stage) return null;

    // For demo purposes, we'll create some plausible mock data
    // In a real app, this would come from API calls or props

    // 1. Time trends data (last 7 days)
    const trendData = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));

      // Create a value with some randomness but showing a general trend
      // based on the stage's position in the funnel
      const stageIndex = funnelData.findIndex(s => s.name === stage.name);
      const baseValue = stage.value * (0.9 + Math.random() * 0.2) / 7;

      // Earlier stages have more variance
      const variance = (funnelData.length - stageIndex) / funnelData.length;
      const randomFactor = 1 - variance * (Math.random() * 0.3);

      return {
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        value: Math.round(baseValue * randomFactor),
        name: stage.name
      };
    });

    // 2. Segment breakdown
    const segmentData = [
      { segment: "Mobile", value: Math.round(stage.value * 0.4) },
      { segment: "Desktop", value: Math.round(stage.value * 0.5) },
      { segment: "Tablet", value: Math.round(stage.value * 0.1) }
    ];

    // 3. User sources
    const sourceData = [
      { source: "Direct", value: Math.round(stage.value * 0.3) },
      { source: "Organic Search", value: Math.round(stage.value * 0.25) },
      { source: "Social Media", value: Math.round(stage.value * 0.2) },
      { source: "Email", value: Math.round(stage.value * 0.15) },
      { source: "Referral", value: Math.round(stage.value * 0.1) }
    ];

    // 4. User journey paths (entry and exit)
    const previousStageIndex = funnelData.findIndex(s => s.name === stage.name) - 1;
    const nextStageIndex = funnelData.findIndex(s => s.name === stage.name) + 1;

    const previousStage = previousStageIndex >= 0 ? funnelData[previousStageIndex] : null;
    const nextStage = nextStageIndex < funnelData.length ? funnelData[nextStageIndex] : null;

    return {
      trendData,
      segmentData,
      sourceData,
      previousStage,
      nextStage
    };
  };

  // Custom tooltip formatter
  const customTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;

      // Determine if we're showing comparison data
      const isComparison = payload.length > 1 && payload[1]?.dataKey === "comparisonValue";
      const comparisonValue = isComparison ? payload[1].value : null;

      const changePercent = isComparison && comparisonValue
        ? ((data.value - comparisonValue) / comparisonValue * 100).toFixed(1)
        : null;

      const changeDirection = changePercent > 0 ? 'increase' : 'decrease';

      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '15px',
          border: '1px solid #cccccc',
          borderRadius: '4px',
          boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
          minWidth: '200px'
        }}>
          <p className="label" style={{
            fontWeight: 'bold',
            borderBottom: '1px solid #eee',
            paddingBottom: '8px',
            marginTop: 0
          }}>{data.name}</p>

          <div style={{ margin: '10px 0' }}>
            <p style={{ margin: '5px 0', display: 'flex', justifyContent: 'space-between' }}>
              <span>Count:</span>
              <span style={{ fontWeight: 'bold' }}>{data.value.toLocaleString()}</span>
            </p>

            {isComparison && (
              <p style={{ margin: '5px 0', display: 'flex', justifyContent: 'space-between' }}>
                <span>Previous:</span>
                <span>{comparisonValue.toLocaleString()}</span>
              </p>
            )}

            {changePercent !== null && (
              <p style={{
                margin: '5px 0',
                display: 'flex',
                justifyContent: 'space-between',
                color: changeDirection === 'increase' ? '#4caf50' : '#f44336'
              }}>
                <span>Change:</span>
                <span style={{ fontWeight: 'bold' }}>
                  {changeDirection === 'increase' ? '+' : ''}{changePercent}%
                </span>
              </p>
            )}
          </div>

          <Divider sx={{ my: 1 }} />

          <div>
            {data.previousConversionRate && (
              <p style={{ margin: '5px 0', fontSize: '0.9em' }}>
                Conversion from previous: {data.previousConversionRate}%
              </p>
            )}

            {data.conversionRate && (
              <p style={{ margin: '5px 0', fontSize: '0.9em' }}>
                Conversion to next: {data.conversionRate}%
              </p>
            )}

            <p style={{ margin: '5px 0', fontSize: '0.9em' }}>
              % of top: {data.percentOfTop}%
            </p>

            {data.dropoff !== null && (
              <p style={{ margin: '5px 0', fontSize: '0.9em', color: '#d32f2f' }}>
                Dropoff: {data.dropoff.toFixed(1)}%
              </p>
            )}
          </div>

          <Divider sx={{ my: 1 }} />

          <Button
            size="small"
            variant="outlined"
            sx={{ fontSize: '0.8em', mt: 1 }}
            onClick={() => handleDrilldown(data)}
          >
            Analyze This Stage
          </Button>
        </div>
      );
    }
    return null;
  };

  // Handle drill-down dialog
  const handleDrilldown = (stage) => {
    setSelectedStage(stage);
    setDrilldownOpen(true);
  };

  const handleCloseDrilldown = () => {
    setDrilldownOpen(false);
  };

  // Handle menu open/close
  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Handle drill-down tab change
  const handleDrilldownTabChange = (event, newValue) => {
    setDrilldownTabValue(newValue);
  };

  // Export chart data
  const exportData = (format) => {
    handleMenuClose();

    if (format === 'csv') {
      // Create CSV content
      let csvContent = "data:text/csv;charset=utf-8,";

      // Add headers
      csvContent += "Stage,Users,Conversion Rate,Dropoff\n";

      // Add data rows
      funnelData.forEach((item, index) => {
        const nextItem = funnelData[index + 1];
        const conversionRate = nextItem ? item.conversionRate + "%" : "N/A";
        const dropoff = nextItem ? item.dropoff + "%" : "N/A";

        csvContent += `${item.name},${item.value},${conversionRate},${dropoff}\n`;
      });

      // Create download link
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `${title.replace(/\s+/g, '_')}_data.csv`);
      document.body.appendChild(link);

      // Trigger download and cleanup
      link.click();
      document.body.removeChild(link);
    } else if (format === 'json') {
      // Create JSON content
      const jsonContent = JSON.stringify(funnelData, null, 2);

      // Create download link
      const blob = new Blob([jsonContent], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `${title.replace(/\s+/g, '_')}_data.json`);
      document.body.appendChild(link);

      // Trigger download and cleanup
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  // Generate the drill-down data when a stage is selected
  const drilldownData = selectedStage ? generateDrilldownData(selectedStage) : null;

  return (
    <Card className="chart-container" ref={chartRef} variant="outlined">
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{title}</Typography>
          <Box>
            <ButtonGroup variant="outlined" size="small" sx={{ mr: 1 }}>
              <Button
                onClick={() => setShowComparison(!showComparison)}
                startIcon={<CompareIcon />}
                color={showComparison ? "primary" : "inherit"}
                disabled={!comparisonData}
              >
                Compare
              </Button>
            </ButtonGroup>

            <IconButton onClick={handleMenuClick}>
              <MoreVertIcon />
            </IconButton>

            <Menu
              anchorEl={anchorEl}
              open={open}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={() => exportData('csv')}>
                <DownloadIcon fontSize="small" sx={{ mr: 1 }} />
                Export as CSV
              </MenuItem>
              <MenuItem onClick={() => exportData('json')}>
                <DownloadIcon fontSize="small" sx={{ mr: 1 }} />
                Export as JSON
              </MenuItem>
            </Menu>
          </Box>
        </Box>

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} sm={6}>
            <FormControl size="small" fullWidth>
              <Select
                value={sortMethod}
                onChange={(e) => setSortMethod(e.target.value)}
                displayEmpty
              >
                <MenuItem value="default">Default Order</MenuItem>
                <MenuItem value="value-desc">Sort by Users (High to Low)</MenuItem>
                <MenuItem value="value-asc">Sort by Users (Low to High)</MenuItem>
                <MenuItem value="name-asc">Sort by Name (A-Z)</MenuItem>
                <MenuItem value="name-desc">Sort by Name (Z-A)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl size="small" fullWidth>
              <Select
                value={selectedSegment}
                onChange={(e) => setSelectedSegment(e.target.value)}
                displayEmpty
              >
                {segmentOptions.map((option) => (
                  <MenuItem key={option} value={option}>{option}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <ResponsiveContainer width="100%" height={height}>
          <BarChart
            data={funnelData}
            layout="vertical"
            margin={{ top: 20, right: 40, left: 100, bottom: 5 }}
            barGap={0}
            barCategoryGap="15%"
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis
              dataKey="name"
              type="category"
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={customTooltip} />

            {/* Comparison bar if comparison data is available and shown */}
            {showComparison && comparisonFunnelData && comparisonFunnelData.length > 0 && (
              <Bar
                dataKey={(entry) => {
                  const comparisonEntry = comparisonFunnelData.find(
                    item => item.name === entry.name
                  );
                  return comparisonEntry ? comparisonEntry.value : 0;
                }}
                name="Previous Period"
                fill="#82ca9d"
                fillOpacity={0.6}
                radius={[0, 0, 0, 0]}
              />
            )}

            <Bar
              dataKey="value"
              name="Current Users"
              fill="#8884d8"
              minPointSize={5}
              radius={[0, 4, 4, 0]}
              onClick={(data) => handleDrilldown(data)}
              cursor="pointer"
            >
              <LabelList
                dataKey="value"
                position="right"
                formatter={(value) => value.toLocaleString()}
                style={{ fill: '#333', fontSize: '12px', fontWeight: 'bold' }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Conversion Rates:</Typography>
          <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 180 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Conversion Step</TableCell>
                  <TableCell align="right">From</TableCell>
                  <TableCell align="right">To</TableCell>
                  <TableCell align="right">Conversion</TableCell>
                  <TableCell align="right">Dropoff</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {funnelData.map((item, index) => {
                  if (index < funnelData.length - 1) {
                    return (
                      <TableRow key={index}
                        sx={{
                          '&:last-child td, &:last-child th': { border: 0 },
                          cursor: 'pointer',
                          '&:hover': { backgroundColor: 'rgba(0,0,0,0.04)' }
                        }}
                        onClick={() => handleDrilldown(item)}
                      >
                        <TableCell component="th" scope="row">
                          Step {index + 1}
                        </TableCell>
                        <TableCell align="right">{item.name}</TableCell>
                        <TableCell align="right">{funnelData[index + 1].name}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={`${item.conversionRate}%`}
                            size="small"
                            color={
                              parseInt(item.conversionRate) > 50 ? 'success' :
                              parseInt(item.conversionRate) > 25 ? 'warning' : 'error'
                            }
                          />
                        </TableCell>
                        <TableCell align="right">{item.dropoff.toFixed(1)}%</TableCell>
                      </TableRow>
                    );
                  }
                  return null;
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>

        {/* Stage Drill-down Dialog */}
        <Dialog
          open={drilldownOpen}
          onClose={handleCloseDrilldown}
          maxWidth="md"
          fullWidth
        >
          {selectedStage && drilldownData && (
            <>
              <DialogTitle>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6">
                    {selectedStage.name} - Analysis
                  </Typography>
                  <Chip
                    label={`${selectedStage.value.toLocaleString()} users`}
                    color="primary"
                  />
                </Box>
              </DialogTitle>
              <DialogContent dividers>
                <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                  <Tabs value={drilldownTabValue} onChange={handleDrilldownTabChange}>
                    <Tab label="Overview" icon={<InfoIcon />} iconPosition="start" />
                    <Tab label="Trends" icon={<EqualizerIcon />} iconPosition="start" />
                    <Tab label="Segments" icon={<CompareIcon />} iconPosition="start" />
                  </Tabs>
                </Box>

                {/* Overview Tab */}
                {drilldownTabValue === 0 && (
                  <Box>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <Typography variant="subtitle1" gutterBottom>
                          Stage Information
                        </Typography>
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableBody>
                              <TableRow>
                                <TableCell component="th" scope="row">
                                  Stage Name
                                </TableCell>
                                <TableCell>{selectedStage.name}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell component="th" scope="row">
                                  User Count
                                </TableCell>
                                <TableCell>{selectedStage.value.toLocaleString()}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell component="th" scope="row">
                                  Percentage of Top
                                </TableCell>
                                <TableCell>{selectedStage.percentOfTop}%</TableCell>
                              </TableRow>

                              {selectedStage.previousConversionRate && (
                                <TableRow>
                                  <TableCell component="th" scope="row">
                                    Conversion from Previous
                                  </TableCell>
                                  <TableCell>{selectedStage.previousConversionRate}%</TableCell>
                                </TableRow>
                              )}

                              {selectedStage.conversionRate && (
                                <TableRow>
                                  <TableCell component="th" scope="row">
                                    Conversion to Next
                                  </TableCell>
                                  <TableCell>{selectedStage.conversionRate}%</TableCell>
                                </TableRow>
                              )}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle1" gutterBottom>
                          Top Sources
                        </Typography>
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Source</TableCell>
                                <TableCell align="right">Users</TableCell>
                                <TableCell align="right">%</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {drilldownData.sourceData.map((source) => (
                                <TableRow key={source.source}>
                                  <TableCell>{source.source}</TableCell>
                                  <TableCell align="right">{source.value.toLocaleString()}</TableCell>
                                  <TableCell align="right">
                                    {((source.value / selectedStage.value) * 100).toFixed(1)}%
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle1" gutterBottom>
                          User Segments
                        </Typography>
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Segment</TableCell>
                                <TableCell align="right">Users</TableCell>
                                <TableCell align="right">%</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {drilldownData.segmentData.map((segment) => (
                                <TableRow key={segment.segment}>
                                  <TableCell>{segment.segment}</TableCell>
                                  <TableCell align="right">{segment.value.toLocaleString()}</TableCell>
                                  <TableCell align="right">
                                    {((segment.value / selectedStage.value) * 100).toFixed(1)}%
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Grid>
                    </Grid>
                  </Box>
                )}

                {/* Trends Tab */}
                {drilldownTabValue === 1 && (
                  <Box>
                    <Typography variant="subtitle1" gutterBottom>
                      Daily Trend (Last 7 Days)
                    </Typography>

                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart
                        data={drilldownData.trendData}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" name={selectedStage.name} fill="#8884d8" />
                      </BarChart>
                    </ResponsiveContainer>

                    <Box sx={{ mt: 3 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        Performance Metrics
                      </Typography>

                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={4}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography color="text.secondary" gutterBottom>
                                Average Daily Users
                              </Typography>
                              <Typography variant="h5" component="div">
                                {Math.round(
                                  drilldownData.trendData.reduce((sum, day) => sum + day.value, 0) /
                                  drilldownData.trendData.length
                                ).toLocaleString()}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography color="text.secondary" gutterBottom>
                                Highest Day
                              </Typography>
                              <Typography variant="h5" component="div">
                                {Math.max(...drilldownData.trendData.map(day => day.value)).toLocaleString()}
                              </Typography>
                              <Typography variant="body2">
                                {drilldownData.trendData.reduce((max, day) =>
                                  day.value > max.value ? day : max, drilldownData.trendData[0]).date}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography color="text.secondary" gutterBottom>
                                Weekly Growth
                              </Typography>
                              <Typography variant="h5" component="div"
                                color={
                                  drilldownData.trendData[6].value > drilldownData.trendData[0].value ?
                                  "success.main" : "error.main"
                                }
                              >
                                {(((drilldownData.trendData[6].value / drilldownData.trendData[0].value) - 1) * 100).toFixed(1)}%
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                      </Grid>
                    </Box>
                  </Box>
                )}

                {/* Segments Tab */}
                {drilldownTabValue === 2 && (
                  <Box>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle1" gutterBottom>
                          Device Type
                        </Typography>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart
                            data={drilldownData.segmentData}
                            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="segment" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" name="Users" fill="#8884d8" />
                          </BarChart>
                        </ResponsiveContainer>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle1" gutterBottom>
                          Traffic Sources
                        </Typography>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart
                            data={drilldownData.sourceData}
                            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="source" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" name="Users" fill="#82ca9d" />
                          </BarChart>
                        </ResponsiveContainer>
                      </Grid>
                    </Grid>
                  </Box>
                )}
              </DialogContent>
              <DialogActions>
                <Button onClick={handleCloseDrilldown}>Close</Button>
                <Button
                  color="primary"
                  variant="contained"
                  onClick={() => {
                    // In a real app, this would create a report or share the data
                    handleCloseDrilldown();
                  }}
                >
                  Generate Report
                </Button>
              </DialogActions>
            </>
          )}
        </Dialog>
      </CardContent>
    </Card>
  );
};

export default ConversionFunnelChart;
