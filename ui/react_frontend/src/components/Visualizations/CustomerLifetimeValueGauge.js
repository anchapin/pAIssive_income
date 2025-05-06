import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend
} from 'recharts';

/**
 * CustomerLifetimeValueGauge - Component for visualizing customer lifetime value metrics
 *
 * This component displays gauge visualizations for customer lifetime value (LTV)
 * and related metrics based on the RevenueProjector's calculate_lifetime_value method.
 *
 * @param {Object} props - Component props
 * @param {Object} props.data - LTV data object with values for different time periods
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 300)
 * @returns {React.Component} A gauge chart component for LTV visualization
 */
const CustomerLifetimeValueGauge = ({
  data,
  title = "Customer Lifetime Value",
  height = 300
}) => {
  // If no data, return a message
  if (!data) {
    return <div>No lifetime value data available for visualization</div>;
  }

  // Format the data for display
  const formatCurrency = (value) => {
    return `$${value.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };

  // Create dataset for the gauge chart
  const createGaugeData = (currentValue, maxValue) => {
    // If current value exceeds max value, adjust max value
    const adjustedMaxValue = currentValue > maxValue ? currentValue * 1.2 : maxValue;

    return [
      { name: "Value", value: currentValue, color: "#0088FE" },
      { name: "Remaining", value: adjustedMaxValue - currentValue, color: "#EEEEEE" }
    ];
  };

  // Extract values from the data
  const ltvOneYear = data.one_year_value || 0;
  const ltvThreeYear = data.three_year_value || 0;
  const ltvFiveYear = data.five_year_value || 0;
  const ltvFull = data.lifetime_value || 0;

  // Create datasets for each gauge
  const oneYearData = createGaugeData(ltvOneYear, ltvFull);
  const threeYearData = createGaugeData(ltvThreeYear, ltvFull);
  const fiveYearData = createGaugeData(ltvFiveYear, ltvFull);

  // Calculate sizes for responsive layout
  const gaugeSize = height * 0.8;
  const innerRadius = gaugeSize * 0.7;
  const outerRadius = gaugeSize * 0.9;

  // Create a custom label component to display the value in the center of the gauge
  const renderCustomizedLabel = (value) => {
    return ({ cx, cy }) => (
      <text
        x={cx}
        y={cy}
        fill="#333333"
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={16}
        fontWeight="bold"
      >
        {formatCurrency(value)}
      </text>
    );
  };

  // Create a custom legend to display all values
  const CustomLegend = () => (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
      <div style={{ textAlign: 'center' }}>
        <h4 style={{ margin: '0 0 5px 0' }}>1-Year</h4>
        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#0088FE' }}>
          {formatCurrency(ltvOneYear)}
        </div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <h4 style={{ margin: '0 0 5px 0' }}>3-Year</h4>
        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#0088FE' }}>
          {formatCurrency(ltvThreeYear)}
        </div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <h4 style={{ margin: '0 0 5px 0' }}>5-Year</h4>
        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#0088FE' }}>
          {formatCurrency(ltvFiveYear)}
        </div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <h4 style={{ margin: '0 0 5px 0' }}>Lifetime</h4>
        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#0088FE' }}>
          {formatCurrency(ltvFull)}
        </div>
      </div>
    </div>
  );

  // Additional metrics from the data
  const averageRevenuePerUser = data.average_revenue_per_user || 0;
  const churnRate = data.churn_rate || 0;
  const averageLifetimeMonths = data.average_lifetime_months || 0;

  return (
    <div className="chart-container">
      <h3>{title}</h3>

      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ display: 'flex', justifyContent: 'space-around', width: '100%' }}>
          <div style={{ width: '30%', height: gaugeSize, position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <ResponsiveContainer width="100%" height={gaugeSize}>
              <PieChart>
                <Pie
                  data={threeYearData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={renderCustomizedLabel(ltvThreeYear)}
                  outerRadius={outerRadius}
                  innerRadius={innerRadius}
                  startAngle={180}
                  endAngle={0}
                  dataKey="value"
                >
                  {threeYearData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{ textAlign: 'center', marginTop: '10px' }}>
              <h4>3-Year LTV</h4>
            </div>
          </div>
        </div>

        <CustomLegend />

        <div style={{ marginTop: '20px', width: '100%', padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
          <h4 style={{ margin: '0 0 10px 0' }}>Additional Metrics</h4>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: '14px', color: '#666' }}>Monthly ARPU:</div>
              <div style={{ fontSize: '16px', fontWeight: 'bold' }}>{formatCurrency(averageRevenuePerUser)}</div>
            </div>
            <div>
              <div style={{ fontSize: '14px', color: '#666' }}>Churn Rate:</div>
              <div style={{ fontSize: '16px', fontWeight: 'bold' }}>{(churnRate * 100).toFixed(1)}%</div>
            </div>
            <div>
              <div style={{ fontSize: '14px', color: '#666' }}>Avg. Customer Lifetime:</div>
              <div style={{ fontSize: '16px', fontWeight: 'bold' }}>{averageLifetimeMonths.toFixed(1)} months</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerLifetimeValueGauge;
