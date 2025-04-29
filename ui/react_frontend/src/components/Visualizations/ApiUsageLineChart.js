import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';
import { Typography, Box } from '@mui/material';

/**
 * API Usage Line Chart component for visualizing API request metrics over time.
 * 
 * @param {Object} props Component props
 * @param {Array} props.data Array of data points with date and metrics
 * @param {string} props.dataKey The key in the data object to plot
 * @param {string} props.name Display name for the metric
 * @param {string} props.color Line color
 * @param {number} props.height Chart height in pixels
 * @param {string} props.title Chart title
 * @param {string} props.yAxisLabel Label for Y axis
 * @param {function} props.tooltipFormatter Function to format tooltip values
 * @param {number} props.threshold Optional threshold value to show as reference line
 * @param {string} props.thresholdLabel Optional label for threshold line
 */
const ApiUsageLineChart = ({
  data,
  dataKey,
  name,
  color = '#8884d8',
  height = 300,
  title,
  yAxisLabel,
  tooltipFormatter = (value) => [value, name],
  threshold,
  thresholdLabel
}) => {
  if (!data || data.length === 0) {
    return (
      <Box sx={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No data available
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {title && (
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }} />
          <Tooltip formatter={tooltipFormatter} />
          <Legend />
          <Line
            type="monotone"
            dataKey={dataKey}
            name={name}
            stroke={color}
            activeDot={{ r: 8 }}
          />
          {threshold !== undefined && (
            <ReferenceLine
              y={threshold}
              label={thresholdLabel}
              stroke="red"
              strokeDasharray="3 3"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ApiUsageLineChart;
