import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';

/**
 * OpportunityBarChart - Component for comparing opportunity scores using a bar chart
 *
 * This component displays a bar chart visualization for comparing opportunity scores
 * across different niches. It can display either overall scores or specific factor scores.
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of opportunity data objects
 * @param {string} props.dataKey - The data key to use for the comparison (default: "overall_score")
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 400)
 * @returns {React.Component} A bar chart component for opportunity comparison
 */
const OpportunityBarChart = ({
  data,
  dataKey = "overall_score",
  title = "Opportunity Score Comparison",
  height = 400
}) => {
  // If no data, return null
  if (!Array.isArray(data) || data.length === 0) {
    return <div>No data available for visualization</div>;
  }

  // Format the data for the bar chart
  const formatData = (opportunities) => {
    return opportunities.map(opp => ({
      name: opp.niche || "Unknown",
      value: opp[dataKey] || 0,
      // Add a color based on the score value
      color: getScoreColor(opp[dataKey] || 0)
    }));
  };

  // Get a color based on the score value (green for high, yellow for medium, red for low)
  const getScoreColor = (score) => {
    if (score >= 0.8) return '#4CAF50'; // Green
    if (score >= 0.6) return '#8BC34A'; // Light Green
    if (score >= 0.4) return '#FFEB3B'; // Yellow
    if (score >= 0.2) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  // Format the chart data
  const chartData = formatData(data);

  // Sort the data by score (descending)
  chartData.sort((a, b) => b.value - a.value);

  // Format the tooltip value
  const formatTooltip = (value) => {
    return [value.toFixed(2), dataKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())];
  };

  // Get a label for the Y-axis based on the dataKey
  const getAxisLabel = () => {
    const label = dataKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    return label;
  };

  return (
    <div className="chart-container">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey=os.environ.get("KEY") />
          <YAxis domain={[0, 1]} label={{ value: getAxisLabel(), angle: -90, position: 'insideLeft' }} />
          <Tooltip formatter={formatTooltip} />
          <Legend />
          <Bar dataKey=os.environ.get("KEY") name={getAxisLabel()}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default OpportunityBarChart;
