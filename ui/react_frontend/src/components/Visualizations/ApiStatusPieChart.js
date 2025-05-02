import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend
} from 'recharts';
import { Typography, Box } from '@mui/material';

/**
 * API Status Pie Chart component for visualizing API status code distribution.
 * 
 * @param {Object} props Component props
 * @param {Array} props.data Array of data points with name and value
 * @param {Array} props.colors Array of colors for pie slices
 * @param {number} props.height Chart height in pixels
 * @param {string} props.title Chart title
 * @param {function} props.tooltipFormatter Function to format tooltip values
 */
const ApiStatusPieChart = ({
  data,
  colors = ['#4caf50', '#ff9800', '#f44336', '#9c27b0', '#2196f3'],
  height = 300,
  title,
  tooltipFormatter = (value, name) => [`${value} requests`, name]
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

  // Generate colors for each data point
  const getColor = (index) => {
    return colors[index % colors.length];
  };

  return (
    <Box sx={{ width: '100%' }}>
      {title && (
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={true}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(index)} />
            ))}
          </Pie>
          <Tooltip formatter={tooltipFormatter} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ApiStatusPieChart;
