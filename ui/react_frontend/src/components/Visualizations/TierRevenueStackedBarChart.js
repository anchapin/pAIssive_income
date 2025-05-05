import React, { useState, useRef } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush,
  ReferenceArea,
  ReferenceLine
} from 'recharts';
import {
  Box,
  Button,
  ButtonGroup,
  FormGroup,
  FormControlLabel,
  Checkbox,
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
  Switch,
  Chip,
  Grid,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import AddIcon from '@mui/icons-material/Add';
import SettingsIcon from '@mui/icons-material/Settings';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';

/**
 * TierRevenueStackedBarChart - Component for visualizing revenue breakdown by subscription tiers
 *
 * This component displays a stacked bar chart visualization of revenue breakdown
 * by different subscription tiers over time, based on the RevenueProjector's project_revenue method.
 *
 * Enhanced with interactive features like:
 * - Data filtering options
 * - Chart appearance controls
 * - Data export functionality
 * - Custom reference lines
 * - Comparison view options
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of revenue projection data objects by month
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 400)
 * @param {boolean} props.showQuarterly - Whether to show quarterly aggregates instead of monthly data
 * @returns {React.Component} An enhanced interactive stacked bar chart component for tier revenue visualization
 */
const TierRevenueStackedBarChart = ({
  data,
  title = "Revenue by Subscription Tier",
  height = 400,
  showQuarterly = false
}) => {
  // Interactive feature states
  const [isQuarterly, setIsQuarterly] = useState(showQuarterly);
  const [visibleTiers, setVisibleTiers] = useState({});
  const [chartSettings, setChartSettings] = useState({
    showGridLines: true,
    showLegend: true,
    barOpacity: 1.0,
    barRadius: 0,
    stacked: true
  });

  // Reference lines state
  const [referenceLines, setReferenceLines] = useState([]);
  const [showReferenceLineDialog, setShowReferenceLineDialog] = useState(false);
  const [newReferenceLine, setNewReferenceLine] = useState({
    position: isQuarterly ? "Q2" : "Month 6",
    label: "Break Even",
    value: 5000,
    color: "#f44336"
  });

  // Settings dialog state
  const [showSettingsDialog, setShowSettingsDialog] = useState(false);

  // Menu state
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  // Chart ref for exporting/saving
  const chartRef = useRef(null);

  // Brush state
  const [brushIndices, setBrushIndices] = useState({
    startIndex: 0,
    endIndex: data?.length - 1 || 0
  });

  // View comparison state
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonTarget, setComparisonTarget] = useState('cumulative');

  // If no data, return a message
  if (!Array.isArray(data) || data.length === 0) {
    return <div>No tier revenue data available for visualization</div>;
  }

  // Get all unique tier names from the data
  const getAllTierNames = (projections) => {
    const tierNames = new Set();

    projections.forEach(month => {
      if (month.tier_revenue) {
        Object.keys(month.tier_revenue).forEach(tier => {
          tierNames.add(tier);
        });
      }
    });

    return Array.from(tierNames);
  };

  const tierNames = getAllTierNames(data);

  // Initialize visible tiers if needed
  if (Object.keys(visibleTiers).length === 0 && tierNames.length > 0) {
    const initialVisibleTiers = {};
    tierNames.forEach(tier => {
      initialVisibleTiers[tier] = true;
    });
    setVisibleTiers(initialVisibleTiers);
  }

  // Define colors for each tier
  const tierColors = {
    'Basic': '#8884d8',
    'Pro': '#82ca9d',
    'Premium': '#ffc658',
    'Enterprise': '#ff8042',
    'Professional': '#82ca9d',
    // Fallback colors for other tier names
    'Tier 1': '#8884d8',
    'Tier 2': '#82ca9d',
    'Tier 3': '#ffc658',
    'Tier 4': '#ff8042',
    'Tier 5': '#a4de6c',
  };

  // Format the data for the chart (adding a proper month/quarter label)
  const formatMonthlyData = (projections) => {
    return projections.map((month, index) => {
      const formattedMonth = {
        month: month.month,
        monthLabel: `Month ${month.month}`,
        totalRevenue: 0,
        cumulativeRevenue: month.cumulative_revenue || 0,
        index
      };

      // Add each tier's revenue to the formatted month
      tierNames.forEach(tier => {
        const tierRevenue = month.tier_revenue && month.tier_revenue[tier]
          ? month.tier_revenue[tier]
          : 0;

        formattedMonth[tier] = tierRevenue;
        formattedMonth.totalRevenue += tierRevenue;
      });

      return formattedMonth;
    });
  };

  // Format the data as quarterly aggregates
  const formatQuarterlyData = (projections) => {
    const quarterlyData = [];

    // Group monthly data into quarters
    for (let quarter = 1; quarter <= Math.ceil(projections.length / 3); quarter++) {
      const startMonth = (quarter - 1) * 3 + 1;
      const endMonth = Math.min(quarter * 3, projections.length);

      const quarterData = {
        quarter: quarter,
        quarterLabel: `Q${quarter}`,
        totalRevenue: 0,
        cumulativeRevenue: 0,
        index: quarter - 1
      };

      // Initialize tier revenues for this quarter
      tierNames.forEach(tier => {
        quarterData[tier] = 0;
      });

      // Sum up the monthly revenues for this quarter
      for (let month = startMonth; month <= endMonth; month++) {
        const monthData = projections.find(m => m.month === month);
        if (monthData && monthData.tier_revenue) {
          tierNames.forEach(tier => {
            const tierRevenue = monthData.tier_revenue[tier] || 0;
            quarterData[tier] += tierRevenue;
            quarterData.totalRevenue += tierRevenue;
          });

          // Use the last month in the quarter for the cumulative revenue
          if (month === endMonth && monthData.cumulative_revenue) {
            quarterData.cumulativeRevenue = monthData.cumulative_revenue;
          }
        }
      }

      quarterlyData.push(quarterData);
    }

    return quarterlyData;
  };

  // Format the chart data based on the selected view
  const chartData = isQuarterly
    ? formatQuarterlyData(data)
    : formatMonthlyData(data);

  const visibleData = chartData.slice(
    brushIndices.startIndex,
    brushIndices.endIndex + 1
  );

  // Custom tooltip formatter
  const customTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      // Filter out non-visible tiers and comparison data if not showing comparison
      const filteredPayload = payload.filter(entry => {
        if (entry.dataKey === 'cumulativeRevenue' && !showComparison) return false;
        if (entry.dataKey === 'totalRevenue' && !showComparison) return false;
        if (!visibleTiers[entry.dataKey] && tierNames.includes(entry.dataKey)) return false;
        return true;
      });

      if (filteredPayload.length === 0) return null;

      // Calculate the total visible revenue
      const visibleTotal = filteredPayload.reduce((sum, entry) => {
        if (tierNames.includes(entry.dataKey)) {
          return sum + (entry.value || 0);
        }
        return sum;
      }, 0);

      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #cccccc',
          boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
          borderRadius: '4px',
          maxWidth: '300px'
        }}>
          <p className="label" style={{
            fontWeight: 'bold',
            margin: '0 0 8px',
            borderBottom: '1px solid #eee',
            paddingBottom: '5px'
          }}>{label}</p>

          {/* Tier revenue data */}
          <div style={{ marginBottom: '8px' }}>
            {filteredPayload.map((entry, index) => {
              // Skip comparison data for now, we'll show it separately
              if (entry.dataKey === 'cumulativeRevenue' || entry.dataKey === 'totalRevenue') {
                return null;
              }

              const percentage = visibleTotal > 0
                ? ((entry.value / visibleTotal) * 100).toFixed(1)
                : 0;

              return (
                <div key={index} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '4px'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    width: '60%'
                  }}>
                    <span style={{
                      display: 'inline-block',
                      width: '10px',
                      height: '10px',
                      backgroundColor: entry.color,
                      marginRight: '5px'
                    }}></span>
                    <span style={{ color: '#333' }}>{entry.name}:</span>
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'flex-end',
                    width: '40%'
                  }}>
                    <span style={{ fontWeight: 'bold', marginRight: '5px' }}>
                      ${entry.value.toLocaleString(undefined, {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                      })}
                    </span>
                    <span style={{
                      fontSize: '0.8em',
                      color: '#666',
                      width: '40px',
                      textAlign: 'right'
                    }}>
                      {percentage}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Visible total */}
          <div style={{
            borderTop: '1px solid #eee',
            paddingTop: '5px',
            display: 'flex',
            justifyContent: 'space-between',
            fontWeight: 'bold'
          }}>
            <span>Total:</span>
            <span>
              ${visibleTotal.toLocaleString(undefined, {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
              })}
            </span>
          </div>

          {/* Comparison data if enabled */}
          {showComparison && (
            <div style={{ marginTop: '10px', borderTop: '1px dashed #ccc', paddingTop: '5px' }}>
              <p style={{ margin: '0 0 5px', fontWeight: 'bold', fontSize: '0.9em' }}>
                Comparison Data:
              </p>

              {filteredPayload.map((entry, index) => {
                if (entry.dataKey !== 'cumulativeRevenue' && entry.dataKey !== 'totalRevenue') {
                  return null;
                }

                return (
                  <div key={`comp-${index}`} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    color: entry.color
                  }}>
                    <span>{entry.name}:</span>
                    <span style={{ fontWeight: 'bold' }}>
                      ${entry.value.toLocaleString(undefined, {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                      })}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  // Toggle functions
  const toggleView = () => setIsQuarterly(!isQuarterly);

  const toggleTier = (tier) => {
    setVisibleTiers(prev => ({
      ...prev,
      [tier]: !prev[tier]
    }));
  };

  const toggleAllTiers = (value) => {
    const newVisibleTiers = {};
    tierNames.forEach(tier => {
      newVisibleTiers[tier] = value;
    });
    setVisibleTiers(newVisibleTiers);
  };

  // Settings functions
  const updateChartSetting = (setting, value) => {
    setChartSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  // Menu functions
  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Reference line functions
  const handleAddReferenceLine = () => {
    setShowReferenceLineDialog(true);
    handleMenuClose();
  };

  const handleReferenceLineChange = (field, value) => {
    setNewReferenceLine({ ...newReferenceLine, [field]: value });
  };

  const handleSaveReferenceLine = () => {
    setReferenceLines([...referenceLines, newReferenceLine]);
    setShowReferenceLineDialog(false);
    // Reset the form
    setNewReferenceLine({
      position: isQuarterly ? "Q2" : "Month 6",
      label: "Break Even",
      value: 5000,
      color: "#f44336"
    });
  };

  const handleRemoveReferenceLine = (index) => {
    setReferenceLines(referenceLines.filter((_, i) => i !== index));
  };

  // Export chart data functions
  const exportData = (format) => {
    handleMenuClose();

    if (format === 'csv') {
      // Create CSV content
      let csvContent = "data:text/csv;charset=utf-8,";

      // Add headers
      const headers = [isQuarterly ? "Quarter" : "Month", "Total Revenue"];

      // Add tier names as headers
      tierNames.forEach(tier => {
        headers.push(tier);
      });

      csvContent += headers.join(",") + "\n";

      // Add data rows
      chartData.forEach(item => {
        const row = [
          isQuarterly ? item.quarterLabel : item.monthLabel,
          item.totalRevenue.toFixed(2)
        ];

        // Add each tier's revenue
        tierNames.forEach(tier => {
          row.push(item[tier].toFixed(2));
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
            <MuiTooltip title="Toggle Data Comparison">
              <Button
                onClick={() => setShowComparison(!showComparison)}
                color={showComparison ? "primary" : "inherit"}
                variant={showComparison ? "contained" : "outlined"}
                startIcon={<CompareArrowsIcon />}
              >
                Compare
              </Button>
            </MuiTooltip>

            <MuiTooltip title="Chart Settings">
              <Button
                onClick={() => setShowSettingsDialog(true)}
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
            <MenuItem onClick={handleAddReferenceLine}>
              <AddIcon fontSize="small" sx={{ mr: 1 }} />
              Add Reference Line
            </MenuItem>
          </Menu>
        </Box>
      </Box>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} md={6}>
          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2">Subscription Tiers</Typography>
              <Box>
                <Button
                  size="small"
                  onClick={() => toggleAllTiers(true)}
                  sx={{ minWidth: 'auto', mr: 1 }}
                >
                  All
                </Button>
                <Button
                  size="small"
                  onClick={() => toggleAllTiers(false)}
                  sx={{ minWidth: 'auto' }}
                >
                  None
                </Button>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {tierNames.map(tier => (
                <Chip
                  key={tier}
                  label={tier}
                  color={visibleTiers[tier] ? "primary" : "default"}
                  variant={visibleTiers[tier] ? "filled" : "outlined"}
                  onClick={() => toggleTier(tier)}
                  sx={{
                    opacity: visibleTiers[tier] ? 1 : 0.6,
                    '& .MuiChip-label': {
                      paddingLeft: '5px'
                    },
                    '&:before': {
                      content: '""',
                      display: 'block',
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      backgroundColor: tierColors[tier] || '#888',
                      marginLeft: '8px'
                    }
                  }}
                />
              ))}
            </Box>
          </Box>
        </Grid>

        <Grid item xs={12} md={6}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={isQuarterly}
                  onChange={toggleView}
                  color="primary"
                />
              }
              label="Quarterly View"
            />

            {showComparison && (
              <FormControl size="small" variant="outlined" sx={{ minWidth: 180 }}>
                <InputLabel id="comparison-target-label">Compare With</InputLabel>
                <Select
                  labelId="comparison-target-label"
                  id="comparison-target"
                  value={comparisonTarget}
                  onChange={(e) => setComparisonTarget(e.target.value)}
                  label="Compare With"
                >
                  <MenuItem value="cumulative">Cumulative Revenue</MenuItem>
                  <MenuItem value="total">Total Revenue (Line)</MenuItem>
                </Select>
              </FormControl>
            )}
          </Box>
        </Grid>
      </Grid>

      {/* Reference lines display */}
      {referenceLines.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Reference Lines:</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {referenceLines.map((line, index) => (
              <Chip
                key={index}
                label={`${line.label} (${line.value.toLocaleString()} at ${line.position})`}
                onDelete={() => handleRemoveReferenceLine(index)}
                size="small"
                sx={{
                  backgroundColor: line.color + '20', // Add transparency
                  borderLeft: `3px solid ${line.color}`
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={visibleData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          {chartSettings.showGridLines && <CartesianGrid strokeDasharray="3 3" />}
          <XAxis dataKey={isQuarterly ? "quarterLabel" : "monthLabel"} />
          <YAxis
            tickFormatter={(value) => `$${value >= 1000 ? `${(value / 1000).toFixed(0)}k` : value}`}
            domain={['auto', 'auto']}
          />
          <Tooltip content={customTooltip} />
          {chartSettings.showLegend && <Legend />}

          {/* Create a bar for each visible tier */}
          {tierNames.map((tier) => (
            visibleTiers[tier] && (
              <Bar
                key={tier}
                dataKey={tier}
                name={tier}
                stackId={chartSettings.stacked ? "a" : null}
                fill={tierColors[tier] || `#${Math.floor(Math.random()*16777215).toString(16)}`}
                fillOpacity={chartSettings.barOpacity}
                radius={chartSettings.stacked ? [0, 0, 0, 0] : [chartSettings.barRadius, chartSettings.barRadius, 0, 0]}
              />
            )
          ))}

          {/* Comparison line if enabled */}
          {showComparison && comparisonTarget === 'cumulative' && (
            <Bar
              dataKey="cumulativeRevenue"
              name="Cumulative Revenue"
              fill="none"
              stroke="#ff4081"
              strokeWidth={2}
              stackId="b"
              isAnimationActive={false}
            />
          )}

          {showComparison && comparisonTarget === 'total' && (
            <Line
              type="monotone"
              dataKey="totalRevenue"
              name="Total Revenue"
              stroke="#ff4081"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              isAnimationActive={false}
            />
          )}

          {/* Reference lines */}
          {referenceLines.map((line, index) => (
            <ReferenceLine
              key={index}
              y={line.value}
              stroke={line.color}
              strokeDasharray="3 3"
              label={{
                value: line.label,
                position: 'insideBottomRight',
                fill: line.color,
                fontSize: 12
              }}
            />
          ))}

          <Brush
            dataKey={isQuarterly ? "quarterLabel" : "monthLabel"}
            height={30}
            stroke="#8884d8"
            onChange={({ startIndex, endIndex }) => {
              if (startIndex !== undefined && endIndex !== undefined) {
                setBrushIndices({
                  startIndex,
                  endIndex
                });
              }
            }}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Help text */}
      <Box sx={{ mt: 1, fontSize: '0.8rem', color: 'text.secondary' }}>
        <Typography variant="caption">
          Tip: Use the brush below the chart to focus on specific time periods. Click on tier names in the legend to toggle visibility.
        </Typography>
      </Box>

      {/* Reference Line Dialog */}
      <Dialog open={showReferenceLineDialog} onClose={() => setShowReferenceLineDialog(false)}>
        <DialogTitle>Add Reference Line</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              label="Value (Revenue $)"
              type="number"
              value={newReferenceLine.value}
              onChange={(e) => handleReferenceLineChange('value', parseInt(e.target.value, 10))}
              fullWidth
              margin="normal"
              inputProps={{
                min: 0,
                step: 100
              }}
            />

            <TextField
              label="Label"
              value={newReferenceLine.label}
              onChange={(e) => handleReferenceLineChange('label', e.target.value)}
              fullWidth
              margin="normal"
            />

            <TextField
              label="Position"
              value={newReferenceLine.position}
              onChange={(e) => handleReferenceLineChange('position', e.target.value)}
              helperText={`e.g., "${isQuarterly ? 'Q2' : 'Month 6'}" (Used for display purposes only)`}
              fullWidth
              margin="normal"
            />

            <TextField
              label="Color"
              type="color"
              value={newReferenceLine.color}
              onChange={(e) => handleReferenceLineChange('color', e.target.value)}
              fullWidth
              margin="normal"
              sx={{
                '& input': {
                  height: '50px',
                  padding: '0 10px',
                }
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowReferenceLineDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveReferenceLine} variant="contained" color="primary">
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Chart Settings Dialog */}
      <Dialog open={showSettingsDialog} onClose={() => setShowSettingsDialog(false)}>
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
                    checked={chartSettings.stacked}
                    onChange={(e) => updateChartSetting('stacked', e.target.checked)}
                  />
                }
                label="Stacked Bars"
              />
            </FormGroup>

            <Typography id="bar-opacity-slider" gutterBottom>
              Bar Opacity: {chartSettings.barOpacity}
            </Typography>
            <Slider
              value={chartSettings.barOpacity}
              onChange={(_, newValue) => updateChartSetting('barOpacity', newValue)}
              aria-labelledby="bar-opacity-slider"
              step={0.1}
              marks
              min={0.1}
              max={1}
            />

            <Typography id="bar-radius-slider" gutterBottom>
              Bar Corner Radius: {chartSettings.barRadius}
            </Typography>
            <Slider
              value={chartSettings.barRadius}
              onChange={(_, newValue) => updateChartSetting('barRadius', newValue)}
              aria-labelledby="bar-radius-slider"
              disabled={chartSettings.stacked}
              step={1}
              marks
              min={0}
              max={10}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettingsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default TierRevenueStackedBarChart;
