import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LabelList
} from 'recharts';
import { Typography, Box } from '@mui/material';

/**
 * API Endpoint Bar Chart component for visualizing metrics by endpoint.
 *
 * @param {Object} props Component props
 * @param {Array} props.data Array of data points with endpoint and metrics
 * @param {string} props.dataKey The key in the data object to plot
 * @param {string} props.name Display name for the metric
 * @param {string} props.color Bar color
 * @param {number} props.height Chart height in pixels
 * @param {string} props.title Chart title
 * @param {string} props.yAxisLabel Label for Y axis
 * @param {function} props.tooltipFormatter Function to format tooltip values
 * @param {boolean} props.showLabels Whether to show value labels on bars
 */
const ApiEndpointBarChart = ({
  data,
  dataKey,
  name,
  color = '#8884d8',
  height = 300,
  title,
  yAxisLabel,
  tooltipFormatter = (value) => [value, name],
  showLabels = false
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

  // Sort data by the dataKey value in descending order
  const sortedData = [...data].sort((a, b) => b[dataKey] - a[dataKey]);

  return (
    <Box sx={{ width: '100%' }}>
      {title && (
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={sortedData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis
            type="category"
            dataKey=os.environ.get("KEY")
            width={80}
            label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }}
          />
          <Tooltip formatter={tooltipFormatter} />
          <Legend />
          <Bar dataKey={dataKey} name={name} fill={color}>
            {showLabels && (
              <LabelList dataKey={dataKey} position="right" />
            )}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ApiEndpointBarChart;
