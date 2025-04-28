import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

/**
 * ScoreDistributionPieChart - Component for visualizing the distribution of opportunity scores
 * 
 * This component displays a pie chart visualization showing the distribution of
 * opportunity scores across different categories (excellent, very good, good, fair, limited).
 * It's especially useful for visualizing the output of the OpportunityScorer's score_distribution.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.data - Score distribution data object with count properties
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 400)
 * @returns {React.Component} A pie chart component for score distribution visualization
 */
const ScoreDistributionPieChart = ({ 
  data, 
  title = "Opportunity Score Distribution", 
  height = 400 
}) => {
  // If no data, return a message
  if (!data) {
    return <div>No data available for visualization</div>;
  }

  // Format the data for the pie chart
  const formatData = (distribution) => {
    return [
      { name: 'Excellent (0.8-1.0)', value: distribution.excellent || 0, color: '#4CAF50' },
      { name: 'Very Good (0.6-0.8)', value: distribution.very_good || 0, color: '#8BC34A' },
      { name: 'Good (0.4-0.6)', value: distribution.good || 0, color: '#FFEB3B' },
      { name: 'Fair (0.2-0.4)', value: distribution.fair || 0, color: '#FF9800' },
      { name: 'Limited (0-0.2)', value: distribution.limited || 0, color: '#F44336' }
    ].filter(item => item.value > 0); // Only include categories that have values
  };

  // Format the chart data
  const chartData = formatData(data);
  
  // If no data after filtering, return a message
  if (chartData.length === 0) {
    return <div>No score distribution data available</div>;
  }
  
  // Custom tooltip formatter
  const customTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{ 
          backgroundColor: 'white', 
          padding: '10px', 
          border: '1px solid #cccccc' 
        }}>
          <p className="label">{`${payload[0].name}: ${payload[0].value}`}</p>
          <p className="intro">{`${(payload[0].value / getTotalCount(data) * 100).toFixed(1)}% of opportunities`}</p>
        </div>
      );
    }
    return null;
  };
  
  // Get the total count of opportunities
  const getTotalCount = (distribution) => {
    return (
      (distribution.excellent || 0) +
      (distribution.very_good || 0) +
      (distribution.good || 0) +
      (distribution.fair || 0) +
      (distribution.limited || 0)
    );
  };

  return (
    <div className="chart-container">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={true}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={customTooltip} />
          <Legend layout="vertical" align="right" verticalAlign="middle" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ScoreDistributionPieChart;