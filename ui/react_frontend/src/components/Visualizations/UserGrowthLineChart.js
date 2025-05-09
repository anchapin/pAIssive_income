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
  ReferenceArea
} from 'recharts';
import {
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
  Box,
  Typography,
  Divider,
  Chip
} from '@mui/material';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import DownloadIcon from '@mui/icons-material/Download';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import AddIcon from '@mui/icons-material/Add';

/**
 * UserGrowthLineChart - Component for visualizing user growth projections over time
 *
 * This component displays a line chart visualization of user growth projections
 * based on the RevenueProjector's project_users method. It can show total, free, and
 * paid users over time, with options to toggle each data series.
 *
 * Enhanced with interactive features like:
 * - Zooming and panning
 * - Custom reference lines
 * - Data export options
 * - Customizable display options
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of user projection data objects by month
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 400)
 * @returns {React.Component} An enhanced interactive line chart component for user growth visualization
 */
const UserGrowthLineChart = ({
  data,
  title = "User Growth Projections",
  height = 400
}) => {
  // State for tracking which lines to show
  const [showTotal, setShowTotal] = useState(true);
  const [showFree, setShowFree] = useState(true);
  const [showPaid, setShowPaid] = useState(true);

  // State for zoom functionality
  const [zoomState, setZoomState] = useState({
    leftIndex: 0,
    rightIndex: data?.length - 1 || 0,
    isZooming: false,
    startIndex: null,
    endIndex: null,
  });

  // State for reference lines
  const [referenceLines, setReferenceLines] = useState([]);
  const [showReferenceLineDialog, setShowReferenceLineDialog] = useState(false);
  const [newReferenceLine, setNewReferenceLine] = useState({
    month: 12,
    label: "1 Year",
    color: "#ff4081"
  });

  // Menu state
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  // Chart ref for exporting/saving
  const chartRef = useRef(null);

  // If no data, return a message
  if (!Array.isArray(data) || data.length === 0) {
    return <div>No user projection data available for visualization</div>;
  }

  // Format the data for the line chart (adding a proper month label)
  const formatData = (projections) => {
    return projections.map((month, index) => ({
      ...month,
      monthLabel: `Month ${month.month}`, // Add a readable month label
      index // Add index for zooming functionality
    }));
  };

  // Format the chart data
  const chartData = formatData(data);

  // Get the data visible in the current zoom window
  const visibleData = chartData.slice(zoomState.leftIndex, zoomState.rightIndex + 1);

  // Custom tooltip formatter
  const customTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #cccccc',
          boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
          borderRadius: '4px'
        }}>
          <p className="label" style={{ fontWeight: 'bold', marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '5px' }}>{label}</p>
          {payload
            .filter(entry =>
              (entry.dataKey === "total_users" && showTotal) ||
              (entry.dataKey === "free_users" && showFree) ||
              (entry.dataKey === "paid_users" && showPaid)
            )
            .map((entry, index) => (
              <p key={index} style={{
                color: entry.color,
                margin: '5px 0',
                display: 'flex',
                justifyContent: 'space-between'
              }}>
                <span>{entry.name}:</span>
                <span style={{ fontWeight: 'bold', marginLeft: '10px' }}>
                  {entry.value.toLocaleString()}
                </span>
              </p>
            ))}

          {/* Add projected growth rate if we have more than one month of data */}
          {payload[0]?.payload?.month > 1 && (
            <div style={{
              borderTop: '1px solid #eee',
              paddingTop: '5px',
              marginTop: '5px',
              fontSize: '0.9em'
            }}>
              <p style={{ margin: '5px 0', color: '#666' }}>
                Monthly Growth: ~{((payload[0]?.payload?.total_users /
                  chartData[payload[0]?.payload?.index - 1]?.total_users - 1) * 100).toFixed(1)}%
              </p>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  // Toggle functions for each line
  const toggleTotal = () => setShowTotal(!showTotal);
  const toggleFree = () => setShowFree(!showFree);
  const togglePaid = () => setShowPaid(!showPaid);

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

  // Handle adding a reference line
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
      month: 12,
      label: "1 Year",
      color: "#ff4081"
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
      csvContent += "Month,Total Users,Free Users,Paid Users\n";

      // Add data rows
      chartData.forEach(item => {
        csvContent += `${item.month},${item.total_users},${item.free_users},${item.paid_users}\n`;
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

      <Box sx={{ mb: 2 }}>
        <FormGroup row>
          <FormControlLabel
            control={<Checkbox checked={showTotal} onChange={toggleTotal} color="primary" />}
            label="Total Users"
          />
          <FormControlLabel
            control={<Checkbox checked={showFree} onChange={toggleFree} color="success" />}
            label="Free Users"
          />
          <FormControlLabel
            control={<Checkbox checked={showPaid} onChange={togglePaid} color="warning" />}
            label="Paid Users"
          />
        </FormGroup>
      </Box>

      {/* Reference lines display */}
      {referenceLines.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Reference Lines:</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {referenceLines.map((line, index) => (
              <Chip
                key={index}
                label={`${line.label} (Month ${line.month})`}
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
        <LineChart
          data={visibleData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          onMouseDown={handleZoomStart}
          onMouseMove={handleZoomMove}
          onMouseUp={handleZoomEnd}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="monthLabel" />
          <YAxis
            tickFormatter={(value) => value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value}
            domain={['auto', 'auto']}
          />
          <Tooltip content={customTooltip} />
          <Legend />

          {showTotal && (
            <Line
              type="monotone"
              dataKey="total_users"
              name="Total Users"
              stroke="#8884d8"
              activeDot={{ r: 8 }}
              strokeWidth={2}
            />
          )}

          {showFree && (
            <Line
              type="monotone"
              dataKey="free_users"
              name="Free Users"
              stroke="#82ca9d"
              strokeWidth={2}
            />
          )}

          {showPaid && (
            <Line
              type="monotone"
              dataKey="paid_users"
              name="Paid Users"
              stroke="#ff8042"
              strokeWidth={2}
            />
          )}

          {/* Display reference lines */}
          {referenceLines.map((line, index) => (
            <ReferenceLine
              key={index}
              x={`Month ${line.month}`}
              stroke={line.color}
              strokeDasharray="3 3"
              label={{ value: line.label, position: 'top', fill: line.color }}
            />
          ))}

          {/* Display zoom area while selecting */}
          {zoomState.isZooming && zoomState.startIndex !== null && zoomState.endIndex !== null && (
            <ReferenceArea
              x1={chartData[Math.min(zoomState.startIndex, zoomState.endIndex)]?.monthLabel}
              x2={chartData[Math.max(zoomState.startIndex, zoomState.endIndex)]?.monthLabel}
              strokeOpacity={0.3}
              fill="#8884d8"
              fillOpacity={0.3}
            />
          )}

          <Brush
            dataKey="monthLabel"
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

      {/* Reference Line Dialog */}
      <Dialog open={showReferenceLineDialog} onClose={() => setShowReferenceLineDialog(false)}>
        <DialogTitle>Add Reference Line</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              label="Month"
              type="number"
              value={newReferenceLine.month}
              onChange={(e) => handleReferenceLineChange('month', parseInt(e.target.value, 10))}
              fullWidth
              margin="normal"
              inputProps={{
                min: 1,
                max: chartData.length,
                step: 1
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
    </div>
  );
};

export default UserGrowthLineChart;
