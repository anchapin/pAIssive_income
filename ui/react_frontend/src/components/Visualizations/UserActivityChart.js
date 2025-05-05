import React, { useState } from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush
} from 'recharts';
import {
  FormGroup,
  FormControlLabel,
  Checkbox,
  Box,
  Grid
} from '@mui/material';

/**
 * UserActivityChart - Component for visualizing user engagement metrics over time
 *
 * This component displays a chart visualization of various user engagement metrics
 * over time, such as active users, session counts, feature usage, etc.
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of time-series data objects with engagement metrics
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 400)
 * @param {Array} props.metrics - Array of metric objects to display
 * @returns {React.Component} A chart component for user activity visualization
 */
const UserActivityChart = ({
  data = [],
  title = "User Activity Metrics",
  height = 400,
  metrics = [
    { key: 'dau', name: 'Daily Active Users', color: '#8884d8', type: 'bar' },
    { key: 'wau', name: 'Weekly Active Users', color: '#82ca9d', type: 'bar' },
    { key: 'mau', name: 'Monthly Active Users', color: '#ffc658', type: 'bar' },
    { key: 'avg_session_time', name: 'Avg. Session Time (min)', color: '#ff8042', type: 'line' },
    { key: 'avg_actions_per_session', name: 'Avg. Actions Per Session', color: '#0088fe', type: 'line' }
  ]
}) => {
  // State to track which metrics to display
  const [visibleMetrics, setVisibleMetrics] = useState(
    metrics.reduce((acc, metric) => ({ ...acc, [metric.key]: true }), {})
  );

  // If no data, return a message
  if (!Array.isArray(data) || data.length === 0) {
    return <div>No user activity data available for visualization</div>;
  }

  // Toggle visibility of a metric
  const handleToggleMetric = (metricKey) => {
    setVisibleMetrics({
      ...visibleMetrics,
      [metricKey]: !visibleMetrics[metricKey]
    });
  };

  // Custom tooltip formatter
  const customTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #cccccc'
        }}>
          <p className="label" style={{ fontWeight: 'bold', margin: '0 0 8px 0' }}>{label}</p>
          {payload
            .filter(entry => visibleMetrics[entry.dataKey])
            .map((entry, index) => {
              const metric = metrics.find(m => m.key === entry.dataKey);
              return (
                <p key={index} style={{
                  color: entry.stroke || entry.fill,
                  margin: '4px 0'
                }}>
                  {metric ? metric.name : entry.dataKey}: {entry.value.toLocaleString()}
                </p>
              );
            })}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container">
      <h3>{title}</h3>

      <Box mb={2}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <FormGroup row>
              {metrics.map((metric) => (
                <FormControlLabel
                  key={metric.key}
                  control={
                    <Checkbox
                      checked={visibleMetrics[metric.key]}
                      onChange={() => handleToggleMetric(metric.key)}
                      style={{ color: metric.color }}
                    />
                  }
                  label={metric.name}
                />
              ))}
            </FormGroup>
          </Grid>
        </Grid>
      </Box>

      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />

          {/* Primary Y-axis for user counts */}
          <YAxis
            yAxisId="left"
            orientation="left"
            label={{ value: 'User Count', angle: -90, position: 'insideLeft' }}
          />

          {/* Secondary Y-axis for other metrics */}
          <YAxis
            yAxisId="right"
            orientation="right"
            label={{ value: 'Session Metrics', angle: -90, position: 'insideRight' }}
          />

          <Tooltip content={customTooltip} />
          <Legend />

          {/* Render each metric with its appropriate type */}
          {metrics.map((metric) => {
            if (!visibleMetrics[metric.key]) return null;

            if (metric.type === 'line') {
              return (
                <Line
                  key={metric.key}
                  type="monotone"
                  dataKey={metric.key}
                  name={metric.name}
                  stroke={metric.color}
                  yAxisId="right"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              );
            } else {
              return (
                <Bar
                  key={metric.key}
                  dataKey={metric.key}
                  name={metric.name}
                  fill={metric.color}
                  yAxisId="left"
                />
              );
            }
          })}

          <Brush dataKey="date" height={30} stroke="#8884d8" />
        </ComposedChart>
      </ResponsiveContainer>

      <Box mt={2} sx={{ fontSize: '14px', color: 'text.secondary' }}>
        <p><strong>DAU</strong>: Daily Active Users - Users who used the application on the given day</p>
        <p><strong>WAU</strong>: Weekly Active Users - Unique users who used the application in the past 7 days</p>
        <p><strong>MAU</strong>: Monthly Active Users - Unique users who used the application in the past 30 days</p>
      </Box>
    </div>
  );
};

export default UserActivityChart;
