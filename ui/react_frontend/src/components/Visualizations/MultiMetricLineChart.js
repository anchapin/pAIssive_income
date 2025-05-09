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
  Brush,
  ReferenceLine,
  ReferenceArea,
  // Label is imported but not used
} from 'recharts';
import {
  Box,
  Button,
  ButtonGroup,
  FormGroup,
  FormControlLabel,
  // Checkbox is imported but not used
  Switch,
  IconButton,
  Tooltip as MuiTooltip,
  Menu,
  MenuItem,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Divider,
  Chip,
  Grid,
  Select,
  FormControl,
  InputLabel,
  Slider
} from '@mui/material';
// ZoomInIcon is imported but not used
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import DownloadIcon from '@mui/icons-material/Download';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import AddIcon from '@mui/icons-material/Add';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import SettingsIcon from '@mui/icons-material/Settings';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';

/**
 * MultiMetricLineChart - Flexible component for visualizing multiple metrics over time
 *
 * This component displays a line chart visualization of multiple metrics over time,
 * with rich interactive features for data exploration and analysis.
 *
 * Features:
 * - Support for multiple data series
 * - Interactive zooming and panning
 * - Custom reference lines and areas
 * - Data export capabilities
 * - Series toggling and appearance customization
 * - Data point annotations
 * - Moving averages and trend lines
 * - Comparison between data series
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of data objects with time points and metrics
 * @param {Array} props.metrics - Array of metric definitions {key, name, color, type} to display
 * @param {string} props.xAxisKey - The key for x-axis values in the data objects
 * @param {string} props.xAxisLabel - Label for the x-axis (default: "Time")
 * @param {string} props.yAxisLabel - Label for the y-axis (default: "Value")
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 400)
 * @param {Object} props.formatter - Optional formatter functions for tooltip and axis values
 * @returns {React.Component} An enhanced interactive line chart component
 */
const MultiMetricLineChart = ({
  data = [],
  metrics = [],
  xAxisKey = "time",
  xAxisLabel = "Time",
  yAxisLabel = "Value",
  title = "Metrics Over Time",
  height = 400,
  formatter = {
    yAxis: (value) => value,
    tooltip: (value) => value
  }
}) => {
  // State for tracking which metrics to show
  const [visibleMetrics, setVisibleMetrics] = useState(() => {
    const initialState = {};
    metrics.forEach(metric => {
      initialState[metric.key] = true;
    });
    return initialState;
  });

  // State for chart display settings
  const [chartSettings, setChartSettings] = useState({
    showGridLines: true,
    showLegend: true,
    curveType: 'linear', // linear, monotone, natural, step
    dotSize: 5,
    lineThickness: 2,
    areaUnderLine: false,
    yAxisMin: 'auto',
    yAxisMax: 'auto',
    connectNulls: true,
    showSettingsDialog: false
  });

  // State for zoom functionality
  const [zoomState, setZoomState] = useState({
    leftIndex: 0,
    rightIndex: data?.length - 1 || 0,
    isZooming: false,
    startIndex: null,
    endIndex: null,
  });

  // State for reference elements
  const [referenceLines, setReferenceLines] = useState([]);
  const [referenceAreas, setReferenceAreas] = useState([]);
  const [showReferenceDialog, setShowReferenceDialog] = useState(false);
  const [referenceDialogType, setReferenceDialogType] = useState('line');
  const [newReferenceLine, setNewReferenceLine] = useState({
    value: 0,
    label: "Threshold",
    color: "#ff4081",
    orientation: "horizontal" // horizontal or vertical
  });
  const [newReferenceArea, setNewReferenceArea] = useState({
    start: 0,
    end: 100,
    label: "Target Range",
    color: "#2196f3",
    orientation: "horizontal" // horizontal or vertical
  });

  // State for data analysis
  const [showMovingAverage, setShowMovingAverage] = useState(false);
  const [movingAveragePeriod, setMovingAveragePeriod] = useState(3);
  const [showYearOverYear, setShowYearOverYear] = useState(false);

  // Menu state
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  // Chart ref for exporting/saving
  const chartRef = useRef(null);

  // If no data, return a message
  if (!Array.isArray(data) || data.length === 0) {
    return <div>No data available for visualization</div>;
  }

  if (!Array.isArray(metrics) || metrics.length === 0) {
    return <div>No metrics defined for visualization</div>;
  }

  // Format the data for the line chart
  const formatData = (inputData) => {
    return inputData.map((point, index) => ({
      ...point,
      index // Add index for zooming functionality
    }));
  };

  // Format the chart data
  const chartData = formatData(data);

  // Get the data visible in the current zoom window
  const visibleData = chartData.slice(zoomState.leftIndex, zoomState.rightIndex + 1);

  // Calculate moving averages for each visible metric
  const calculateMovingAverages = () => {
    if (!showMovingAverage) return {};

    const movingAverages = {};
    const period = Math.min(movingAveragePeriod, visibleData.length);

    metrics.forEach(metric => {
      if (!visibleMetrics[metric.key]) return;

      movingAverages[`${metric.key}_ma`] = visibleData.map((point, index) => {
        if (index < period - 1) return null;

        let sum = 0;
        for (let i = 0; i < period; i++) {
          sum += visibleData[index - i][metric.key] || 0;
        }
        return sum / period;
      });
    });

    return movingAverages;
  };

  const movingAverages = calculateMovingAverages();

  // Custom tooltip formatter
  const customTooltip = ({ active, payload, label }) => {
    if (!active || !payload || payload.length === 0) return null;

    // Group metrics and moving averages
    const metricValues = {};
    const movingAverageValues = {};

    payload.forEach(entry => {
      const metricKey = entry.dataKey;

      // Check if this is a moving average series
      if (metricKey.endsWith('_ma')) {
        const originalMetricKey = metricKey.replace('_ma', '');
        const metric = metrics.find(m => m.key === originalMetricKey);
        if (metric && entry.value !== null) {
          movingAverageValues[originalMetricKey] = {
            name: `${metric.name} (${movingAveragePeriod}-pt MA)`,
            value: entry.value,
            color: entry.stroke
          };
        }
      }
      // Regular metric
      else {
        const metric = metrics.find(m => m.key === metricKey);
        if (metric && entry.value !== null && visibleMetrics[metricKey]) {
          metricValues[metricKey] = {
            name: metric.name,
            value: entry.value,
            color: entry.stroke
          };
        }
      }
    });

    // Get the raw data point for additional info
    const dataPoint = payload[0].payload;

    return (
      <div className="custom-tooltip" style={{
        backgroundColor: 'white',
        padding: '10px',
        border: '1px solid #cccccc',
        boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
        borderRadius: '4px',
        maxWidth: '280px'
      }}>
        <p className="label" style={{
          fontWeight: 'bold',
          marginTop: 0,
          borderBottom: '1px solid #eee',
          paddingBottom: '5px'
        }}>
          {label || dataPoint[xAxisKey]}
        </p>

        <div style={{ margin: '8px 0' }}>
          {/* Display regular metric values */}
          {Object.values(metricValues).map((metric, index) => (
            <p key={`metric-${index}`} style={{
              color: metric.color,
              margin: '3px 0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>{metric.name}:</span>
              <span style={{ fontWeight: 'bold', marginLeft: '10px' }}>
                {formatter.tooltip ? formatter.tooltip(metric.value) : metric.value.toLocaleString()}
              </span>
            </p>
          ))}
        </div>

        {/* Display moving averages if enabled */}
        {showMovingAverage && Object.values(movingAverageValues).length > 0 && (
          <>
            <Divider sx={{ my: 1 }} />
            <div style={{ margin: '8px 0' }}>
              {Object.values(movingAverageValues).map((metric, index) => (
                <p key={`ma-${index}`} style={{
                  color: metric.color,
                  margin: '3px 0',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: '0.9em'
                }}>
                  <span>{metric.name}:</span>
                  <span style={{ fontWeight: 'bold', marginLeft: '10px' }}>
                    {formatter.tooltip ? formatter.tooltip(metric.value) : metric.value.toLocaleString()}
                  </span>
                </p>
              ))}
            </div>
          </>
        )}

        {/* Display additional data point fields if present */}
        {Object.keys(dataPoint).some(key =>
          key !== xAxisKey &&
          key !== 'index' &&
          !metrics.some(m => m.key === key) &&
          typeof dataPoint[key] !== 'object'
        ) && (
          <>
            <Divider sx={{ my: 1 }} />
            <div style={{ fontSize: '0.9em', color: '#666' }}>
              {Object.entries(dataPoint).map(([key, value]) => {
                // Skip already displayed metrics, index, and complex objects
                if (key === xAxisKey || key === 'index' || metrics.some(m => m.key === key) || typeof value === 'object') {
                  return null;
                }
                return (
                  <p key={key} style={{ margin: '3px 0' }}>
                    {key}: {value}
                  </p>
                );
              })}
            </div>
          </>
        )}
      </div>
    );
  };

  // Toggle functions for metrics visibility
  const toggleMetric = (metricKey) => {
    setVisibleMetrics(prev => ({
      ...prev,
      [metricKey]: !prev[metricKey]
    }));
  };

  const toggleAllMetrics = (value) => {
    const newVisibleMetrics = {};
    metrics.forEach(metric => {
      newVisibleMetrics[metric.key] = value;
    });
    setVisibleMetrics(newVisibleMetrics);
  };

  // Update chart settings
  const updateChartSetting = (setting, value) => {
    setChartSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  // Zoom functions
  const handleZoomStart = (e) => {
    if (!e) return;
    const { activeTooltipIndex } = e;
    if (activeTooltipIndex !== undefined) {
      setZoomState({
        ...zoomState,
        isZooming: true,
        startIndex: activeTooltipIndex
      });
    }
  };

  const handleZoomMove = (e) => {
    if (!zoomState.isZooming || !e) return;
    const { activeTooltipIndex } = e;
    if (activeTooltipIndex !== undefined) {
      setZoomState({
        ...zoomState,
        endIndex: activeTooltipIndex
      });
    }
  };

  const handleZoomEnd = () => {
    if (zoomState.isZooming && zoomState.startIndex !== null && zoomState.endIndex !== null) {
      const leftIndex = Math.min(zoomState.startIndex, zoomState.endIndex);
      const rightIndex = Math.max(zoomState.startIndex, zoomState.endIndex);

      // Only update if the zoom area is at least 2 data points
      if (rightIndex - leftIndex > 1) {
        setZoomState({
          leftIndex,
          rightIndex,
          isZooming: false,
          startIndex: null,
          endIndex: null
        });
      } else {
        // Reset zoom state if area is too small
        setZoomState({
          ...zoomState,
          isZooming: false,
          startIndex: null,
          endIndex: null
        });
      }
    }
  };

  const handleZoomOut = () => {
    setZoomState({
      leftIndex: 0,
      rightIndex: chartData.length - 1,
      isZooming: false,
      startIndex: null,
      endIndex: null
    });
  };

  // Handle menu open/close
  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Handle adding a reference element
  const handleAddReferenceElement = (type) => {
    setReferenceDialogType(type);
    setShowReferenceDialog(true);
    handleMenuClose();
  };

  const handleReferenceLineChange = (field, value) => {
    setNewReferenceLine({ ...newReferenceLine, [field]: value });
  };

  const handleReferenceAreaChange = (field, value) => {
    setNewReferenceArea({ ...newReferenceArea, [field]: value });
  };

  const handleSaveReferenceElement = () => {
    if (referenceDialogType === 'line') {
      setReferenceLines([...referenceLines, newReferenceLine]);
      setNewReferenceLine({
        value: 0,
        label: "Threshold",
        color: "#ff4081",
        orientation: "horizontal"
      });
    } else {
      setReferenceAreas([...referenceAreas, newReferenceArea]);
      setNewReferenceArea({
        start: 0,
        end: 100,
        label: "Target Range",
        color: "#2196f3",
        orientation: "horizontal"
      });
    }
    setShowReferenceDialog(false);
  };

  const handleRemoveReferenceLine = (index) => {
    setReferenceLines(referenceLines.filter((_, i) => i !== index));
  };

  const handleRemoveReferenceArea = (index) => {
    setReferenceAreas(referenceAreas.filter((_, i) => i !== index));
  };

  // Toggle moving average display
  const handleToggleMovingAverage = () => {
    setShowMovingAverage(!showMovingAverage);
  };

  // Toggle year-over-year comparison
  const handleToggleYearOverYear = () => {
    setShowYearOverYear(!showYearOverYear);
  };

  // Export chart data functions
  const exportData = (format) => {
    handleMenuClose();

    if (format === 'csv') {
      // Create CSV content
      let csvContent = "data:text/csv;charset=utf-8,";

      // Add headers
      const headers = [xAxisKey];
      metrics.forEach(metric => {
        headers.push(metric.key);
      });

      csvContent += headers.join(",") + "\n";

      // Add data rows
      chartData.forEach(item => {
        const row = [item[xAxisKey]];
        metrics.forEach(metric => {
          row.push(item[metric.key] !== undefined ? item[metric.key] : '');
        });
        csvContent += row.join(",") + "\n";
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
      const jsonContent = JSON.stringify(chartData, null, 2);

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

  return (
    <div className="chart-container" ref={chartRef}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">{title}</Typography>
        <Box>
          <ButtonGroup variant="outlined" size="small" sx={{ mr: 1 }}>
            <MuiTooltip title="Zoom Out (Reset View)">
              <Button
                onClick={handleZoomOut}
                disabled={zoomState.leftIndex === 0 && zoomState.rightIndex === data.length - 1}
                startIcon={<ZoomOutIcon />}
              >
                Reset Zoom
              </Button>
            </MuiTooltip>

            <MuiTooltip title="Chart Settings">
              <Button
                onClick={() => setChartSettings(prev => ({ ...prev, showSettingsDialog: true }))}
                startIcon={<SettingsIcon />}
              >
                Settings
              </Button>
            </MuiTooltip>
          </ButtonGroup>

          <MuiTooltip title="More Options">
            <IconButton onClick={handleMenuClick}>
              <MoreVertIcon />
            </IconButton>
          </MuiTooltip>

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
            <Divider />
            <MenuItem onClick={() => handleAddReferenceElement('line')}>
              <AddIcon fontSize="small" sx={{ mr: 1 }} />
              Add Reference Line
            </MenuItem>
            <MenuItem onClick={() => handleAddReferenceElement('area')}>
              <AddIcon fontSize="small" sx={{ mr: 1 }} />
              Add Reference Area
            </MenuItem>
            <Divider />
            <MenuItem
              onClick={handleToggleMovingAverage}
              sx={{
                backgroundColor: showMovingAverage ? 'rgba(0,0,0,0.04)' : 'transparent'
              }}
            >
              <ShowChartIcon fontSize="small" sx={{ mr: 1 }} />
              {showMovingAverage ? 'Hide' : 'Show'} Moving Average
            </MenuItem>
            <MenuItem
              onClick={handleToggleYearOverYear}
              sx={{
                backgroundColor: showYearOverYear ? 'rgba(0,0,0,0.04)' : 'transparent'
              }}
            >
              <CompareArrowsIcon fontSize="small" sx={{ mr: 1 }} />
              {showYearOverYear ? 'Hide' : 'Show'} Year-over-Year
            </MenuItem>
          </Menu>
        </Box>
      </Box>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} md={6}>
          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2">Metrics</Typography>
              <Box>
                <Button
                  size="small"
                  onClick={() => toggleAllMetrics(true)}
                  sx={{ minWidth: 'auto', mr: 1 }}
                >
                  All
                </Button>
                <Button
                  size="small"
                  onClick={() => toggleAllMetrics(false)}
                  sx={{ minWidth: 'auto' }}
                >
                  None
                </Button>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {metrics.map(metric => (
                <Chip
                  key={metric.key}
                  label={metric.name}
                  color={visibleMetrics[metric.key] ? "primary" : "default"}
                  variant={visibleMetrics[metric.key] ? "filled" : "outlined"}
                  onClick={() => toggleMetric(metric.key)}
                  sx={{
                    opacity: visibleMetrics[metric.key] ? 1 : 0.6,
                    '& .MuiChip-label': {
                      paddingLeft: '5px'
                    },
                    '&:before': {
                      content: '""',
                      display: 'block',
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      backgroundColor: metric.color || '#888',
                      marginLeft: '8px'
                    }
                  }}
                />
              ))}
            </Box>
          </Box>
        </Grid>

        <Grid item xs={12} md={6}>
          {showMovingAverage && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ mr: 2 }}>
                Moving Average Period:
              </Typography>
              <Slider
                value={movingAveragePeriod}
                min={2}
                max={Math.max(7, Math.floor(visibleData.length / 2))}
                step={1}
                marks={true}
                onChange={(_, newValue) => setMovingAveragePeriod(newValue)}
                valueLabelDisplay="auto"
                sx={{ width: '60%' }}
              />
            </Box>
          )}
        </Grid>
      </Grid>

      {/* Reference elements display */}
      {(referenceLines.length > 0 || referenceAreas.length > 0) && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Reference Elements:</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {referenceLines.map((line, index) => (
              <Chip
                key={`line-${index}`}
                label={`${line.label} (${line.value})`}
                onDelete={() => handleRemoveReferenceLine(index)}
                size="small"
                sx={{
                  backgroundColor: line.color + '20', // Add transparency
                  borderLeft: `3px solid ${line.color}`
                }}
              />
            ))}

            {referenceAreas.map((area, index) => (
              <Chip
                key={`area-${index}`}
                label={`${area.label} (${area.start} - ${area.end})`}
                onDelete={() => handleRemoveReferenceArea(index)}
                size="small"
                sx={{
                  backgroundColor: area.color + '20', // Add transparency
                  borderLeft: `3px solid ${area.color}`
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={visibleData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          onMouseDown={handleZoomStart}
          onMouseMove={handleZoomMove}
          onMouseUp={handleZoomEnd}
        >
          {chartSettings.showGridLines && <CartesianGrid strokeDasharray="3 3" />}

          <XAxis
            dataKey={xAxisKey}
            label={{
              value: xAxisLabel,
              position: 'insideBottomRight',
              offset: -10
            }}
          />

          <YAxis
            domain={[
              chartSettings.yAxisMin === 'auto' ? 'auto' : Number(chartSettings.yAxisMin),
              chartSettings.yAxisMax === 'auto' ? 'auto' : Number(chartSettings.yAxisMax)
            ]}
            tickFormatter={formatter.yAxis || (value => value)}
            label={{
              value: yAxisLabel,
              angle: -90,
              position: 'insideLeft'
            }}
          />

          <Tooltip content={customTooltip} />
          {chartSettings.showLegend && <Legend />}

          {/* Map each metric to a Line component */}
          {metrics.map((metric) => (
            visibleMetrics[metric.key] && (
              <Line
                key={metric.key}
                type={chartSettings.curveType || 'linear'}
                dataKey={metric.key}
                name={metric.name}
                stroke={metric.color}
                fill={metric.color}
                activeDot={{ r: chartSettings.dotSize + 3 || 8 }}
                dot={{ r: chartSettings.dotSize || 5 }}
                strokeWidth={chartSettings.lineThickness || 2}
                connectNulls={chartSettings.connectNulls}
                isAnimationActive={false}
              />
            )
          ))}

          {/* Moving averages */}
          {showMovingAverage && metrics.map((metric) => (
            visibleMetrics[metric.key] && (
              <Line
                key={`${metric.key}_ma`}
                type="monotone"
                dataKey={(entry) => {
                  const index = chartData.findIndex(d =>
                    d[xAxisKey] === entry[xAxisKey]);
                  return movingAverages[`${metric.key}_ma`]?.[index];
                }}
                name={`${metric.name} (${movingAveragePeriod}-pt MA)`}
                stroke={metric.color}
                strokeDasharray="5 5"
                dot={false}
                activeDot={false}
                strokeWidth={2}
                isAnimationActive={false}
              />
            )
          ))}

          {/* Horizontal reference lines */}
          {referenceLines
            .filter(line => line.orientation === 'horizontal')
            .map((line, index) => (
              <ReferenceLine
                key={`h-line-${index}`}
                y={line.value}
                stroke={line.color}
                strokeDasharray="3 3"
                label={{
                  value: line.label,
                  position: 'right',
                  fill: line.color
                }}
              />
            ))
          }

          {/* Vertical reference lines */}
          {referenceLines
            .filter(line => line.orientation === 'vertical')
            .map((line, index) => (
              <ReferenceLine
                key={`v-line-${index}`}
                x={line.value}
                stroke={line.color}
                strokeDasharray="3 3"
                label={{
                  value: line.label,
                  position: 'top',
                  fill: line.color
                }}
              />
            ))
          }

          {/* Horizontal reference areas */}
          {referenceAreas
            .filter(area => area.orientation === 'horizontal')
            .map((area, index) => (
              <ReferenceArea
                key={`h-area-${index}`}
                y1={area.start}
                y2={area.end}
                fill={area.color}
                fillOpacity={0.2}
                label={{
                  value: area.label,
                  position: 'insideRight'
                }}
              />
            ))
          }

          {/* Vertical reference areas */}
          {referenceAreas
            .filter(area => area.orientation === 'vertical')
            .map((area, index) => (
              <ReferenceArea
                key={`v-area-${index}`}
                x1={area.start}
                x2={area.end}
                fill={area.color}
                fillOpacity={0.2}
                label={{
                  value: area.label,
                  position: 'insideTop'
                }}
              />
            ))
          }

          {/* Display zoom area while selecting */}
          {zoomState.isZooming && zoomState.startIndex !== null && zoomState.endIndex !== null && (
            <ReferenceArea
              x1={chartData[Math.min(zoomState.startIndex, zoomState.endIndex)]?.[xAxisKey]}
              x2={chartData[Math.max(zoomState.startIndex, zoomState.endIndex)]?.[xAxisKey]}
              strokeOpacity={0.3}
              fill="#8884d8"
              fillOpacity={0.3}
            />
          )}

          <Brush
            dataKey={xAxisKey}
            height={30}
            stroke="#8884d8"
            onChange={({ startIndex, endIndex }) => {
              if (startIndex !== undefined && endIndex !== undefined) {
                setZoomState({
                  ...zoomState,
                  leftIndex: startIndex,
                  rightIndex: endIndex,
                  isZooming: false,
                  startIndex: null,
                  endIndex: null
                });
              }
            }}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Help text */}
      <Box sx={{ mt: 1, fontSize: '0.8rem', color: 'text.secondary' }}>
        <Typography variant="caption">
          Tip: Click and drag directly on the chart to zoom into a specific area. Use the brush below the chart to adjust the visible range.
        </Typography>
      </Box>

      {/* Reference Element Dialog */}
      <Dialog open={showReferenceDialog} onClose={() => setShowReferenceDialog(false)}>
        <DialogTitle>
          Add Reference {referenceDialogType === 'line' ? 'Line' : 'Area'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {referenceDialogType === 'line' ? (
              <>
                <TextField
                  label="Value"
                  type="number"
                  value={newReferenceLine.value}
                  onChange={(e) => handleReferenceLineChange('value', parseFloat(e.target.value))}
                  fullWidth
                  margin="normal"
                />

                <TextField
                  label="Label"
                  value={newReferenceLine.label}
                  onChange={(e) => handleReferenceLineChange('label', e.target.value)}
                  fullWidth
                  margin="normal"
                />

                <FormControl fullWidth margin="normal">
                  <InputLabel id="orientation-label">Orientation</InputLabel>
                  <Select
                    labelId="orientation-label"
                    value={newReferenceLine.orientation}
                    onChange={(e) => handleReferenceLineChange('orientation', e.target.value)}
                    label="Orientation"
                  >
                    <MenuItem value="horizontal">Horizontal</MenuItem>
                    <MenuItem value="vertical">Vertical</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  label="Color"
                  type="color"
                  value={newReferenceLine.color}
                  onChange={(e) => handleReferenceLineChange('color', e.target.value)}
                  fullWidth
                  margin="normal"
                  sx={{ '& input': { height: '50px', padding: '0 10px' } }}
                />
              </>
            ) : (
              <>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <TextField
                    label="Start Value"
                    type="number"
                    value={newReferenceArea.start}
                    onChange={(e) => handleReferenceAreaChange('start', parseFloat(e.target.value))}
                    fullWidth
                    margin="normal"
                  />

                  <TextField
                    label="End Value"
                    type="number"
                    value={newReferenceArea.end}
                    onChange={(e) => handleReferenceAreaChange('end', parseFloat(e.target.value))}
                    fullWidth
                    margin="normal"
                  />
                </Box>

                <TextField
                  label="Label"
                  value={newReferenceArea.label}
                  onChange={(e) => handleReferenceAreaChange('label', e.target.value)}
                  fullWidth
                  margin="normal"
                />

                <FormControl fullWidth margin="normal">
                  <InputLabel id="area-orientation-label">Orientation</InputLabel>
                  <Select
                    labelId="area-orientation-label"
                    value={newReferenceArea.orientation}
                    onChange={(e) => handleReferenceAreaChange('orientation', e.target.value)}
                    label="Orientation"
                  >
                    <MenuItem value="horizontal">Horizontal</MenuItem>
                    <MenuItem value="vertical">Vertical</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  label="Color"
                  type="color"
                  value={newReferenceArea.color}
                  onChange={(e) => handleReferenceAreaChange('color', e.target.value)}
                  fullWidth
                  margin="normal"
                  sx={{ '& input': { height: '50px', padding: '0 10px' } }}
                />
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowReferenceDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveReferenceElement} variant="contained" color="primary">
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog
        open={chartSettings.showSettingsDialog || false}
        onClose={() => setChartSettings(prev => ({ ...prev, showSettingsDialog: false }))}
      >
        <DialogTitle>Chart Settings</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <FormGroup>
              <FormControlLabel
                control={
                  <Switch
                    checked={chartSettings.showGridLines}
                    onChange={(e) => updateChartSetting('showGridLines', e.target.checked)}
                  />
                }
                label="Show Grid Lines"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={chartSettings.showLegend}
                    onChange={(e) => updateChartSetting('showLegend', e.target.checked)}
                  />
                }
                label="Show Legend"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={chartSettings.connectNulls}
                    onChange={(e) => updateChartSetting('connectNulls', e.target.checked)}
                  />
                }
                label="Connect Null Values"
              />
            </FormGroup>

            <FormControl fullWidth margin="normal">
              <InputLabel id="curve-type-label">Line Curve Type</InputLabel>
              <Select
                labelId="curve-type-label"
                value={chartSettings.curveType}
                onChange={(e) => updateChartSetting('curveType', e.target.value)}
                label="Line Curve Type"
              >
                <MenuItem value="linear">Linear</MenuItem>
                <MenuItem value="monotone">Monotone</MenuItem>
                <MenuItem value="natural">Natural</MenuItem>
                <MenuItem value="step">Step</MenuItem>
              </Select>
            </FormControl>

            <Typography id="dot-size-slider" gutterBottom>
              Dot Size: {chartSettings.dotSize}
            </Typography>
            <Slider
              value={chartSettings.dotSize}
              onChange={(_, newValue) => updateChartSetting('dotSize', newValue)}
              aria-labelledby="dot-size-slider"
              step={1}
              marks
              min={0}
              max={10}
            />

            <Typography id="line-thickness-slider" gutterBottom>
              Line Thickness: {chartSettings.lineThickness}
            </Typography>
            <Slider
              value={chartSettings.lineThickness}
              onChange={(_, newValue) => updateChartSetting('lineThickness', newValue)}
              aria-labelledby="line-thickness-slider"
              step={1}
              marks
              min={1}
              max={5}
            />

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" gutterBottom>
              Y-Axis Range
            </Typography>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Min Value"
                value={chartSettings.yAxisMin}
                onChange={(e) => updateChartSetting('yAxisMin', e.target.value)}
                helperText="Enter a number or 'auto'"
                fullWidth
              />

              <TextField
                label="Max Value"
                value={chartSettings.yAxisMax}
                onChange={(e) => updateChartSetting('yAxisMax', e.target.value)}
                helperText="Enter a number or 'auto'"
                fullWidth
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setChartSettings(prev => ({ ...prev, showSettingsDialog: false }))}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default MultiMetricLineChart;
