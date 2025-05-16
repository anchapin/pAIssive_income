import React, { useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush
} from 'recharts';

/**
 * RevenueAreaChart - Component for visualizing revenue projections over time
 *
 * This component displays an area chart visualization of revenue projections
 * based on the RevenueProjector's project_revenue method. It can show monthly and
 * cumulative revenue over time, with options to toggle each data series.
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of revenue projection data objects by month
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 400)
 * @param {Array} props.milestones - Optional milestones to display as reference lines
 * @returns {React.Component} An area chart component for revenue visualization
 */
const RevenueAreaChart = ({
  data,
  title = "Revenue Projections",
  height = 400,
  milestones = []
}) => {
  // State for tracking which data to show
  const [showMonthly, setShowMonthly] = useState(true);
  const [showCumulative, setShowCumulative] = useState(true);

  // If no data, return a message
  if (!Array.isArray(data) || data.length === 0) {
    return <div>No revenue projection data available for visualization</div>;
  }

  // Format the data for the chart (adding a proper month label)
  const formatData = (projections) => {
    return projections.map(month => ({
      ...month,
      monthLabel: `Month ${month.month}`, // Add a readable month label
      // Format revenue values for display
      formattedMonthlyRevenue: month.total_revenue ? `$${month.total_revenue.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}` : '$0.00',
      formattedCumulativeRevenue: month.cumulative_revenue ? `$${month.cumulative_revenue.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}` : '$0.00',
    }));
  };

  // Format the chart data
  const chartData = formatData(data);

  // Custom tooltip formatter
  const customTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #cccccc'
        }}>
          <p className="label" style={{ fontWeight: 'bold' }}>{label}</p>
          {payload.map((entry, index) => {
            // Check if this is a monetary value
            const isMonetary = entry.name.toLowerCase().includes('revenue');
            const value = isMonetary
              ? `$${entry.value.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}`
              : entry.value.toLocaleString();

            return (
              <p key={index} style={{ color: entry.color }}>
                {`${entry.name}: ${value}`}
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  };

  // Toggle functions for each data series
  const toggleMonthly = () => setShowMonthly(!showMonthly);
  const toggleCumulative = () => setShowCumulative(!showCumulative);

  return (
    <div className="chart-container">
      <h3>{title}</h3>

      <div style={{ marginBottom: '10px' }}>
        <label style={{ marginRight: '15px' }}>
          <input
            type="checkbox"
            checked={showMonthly}
            onChange={toggleMonthly}
            style={{ marginRight: '5px' }}
          />
          Monthly Revenue
        </label>
        <label>
          <input
            type="checkbox"
            checked={showCumulative}
            onChange={toggleCumulative}
            style={{ marginRight: '5px' }}
          />
          Cumulative Revenue
        </label>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={chartData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="monthLabel" />
          <YAxis
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip content={customTooltip} />
          <Legend />

          {showMonthly && (
            <Area
              type="monotone"
              dataKey="monthlyRevenue"
              name="Monthly Revenue"
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.3}
              activeDot={{ r: 8 }}
            />
          )}

          {showCumulative && (
            <Area
              type="monotone"
              dataKey="cumulativeRevenue"
              name="Cumulative Revenue"
              stroke="#82ca9d"
              fill="#82ca9d"
              fillOpacity={0.3}
            />
          )}

          {/* Add milestone reference lines if provided */}
          {milestones.map((milestone, index) => (
            <ReferenceLine
              key={index}
              x={`Month ${milestone.month}`}
              stroke="red"
              label={milestone.label}
            />
          ))}

          <Brush dataKey="monthLabel" height={30} stroke="#8884d8" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RevenueAreaChart;
