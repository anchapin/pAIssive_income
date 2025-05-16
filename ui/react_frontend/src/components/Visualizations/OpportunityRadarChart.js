import React from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

/**
 * OpportunityRadarChart - Component for visualizing opportunity scores using a radar chart
 *
 * This component displays a radar chart visualization of opportunity scores based on
 * the six factors assessed by the OpportunityScorer (market size, growth rate, competition,
 * problem severity, solution feasibility, and monetization potential).
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of opportunity data objects
 * @param {string} props.title - Chart title
 * @param {number} props.height - Chart height in pixels (default: 400)
 * @returns {React.Component} A radar chart component for opportunity scoring visualization
 */
const OpportunityRadarChart = ({ data, title = "Opportunity Factor Analysis", height = 400 }) => {
  // Format the data for the radar chart if it's a single opportunity
  const formatSingleOpportunity = (opportunity) => {
    if (!opportunity || !opportunity.factors) return [];

    // Extract factor scores from the opportunity data
    return [
      {
        subject: "Market Size",
        value: opportunity.factors.market_size || 0,
        fullMark: 1.0,
      },
      {
        subject: "Growth Rate",
        value: opportunity.factors.growth_rate || 0,
        fullMark: 1.0,
      },
      {
        subject: "Competition",
        value: opportunity.factors.competition || 0,
        fullMark: 1.0,
      },
      {
        subject: "Problem Severity",
        value: opportunity.factors.problem_severity || 0,
        fullMark: 1.0,
      },
      {
        subject: "Solution Feasibility",
        value: opportunity.factors.solution_feasibility || 0,
        fullMark: 1.0,
      },
      {
        subject: "Monetization Potential",
        value: opportunity.factors.monetization_potential || 0,
        fullMark: 1.0,
      }
    ];
  };

  // Format the data for multiple opportunities
  const formatMultipleOpportunities = (opportunities) => {
    if (!Array.isArray(opportunities) || opportunities.length === 0) return [];

    // Create a dataset with all opportunities for comparison
    return opportunities.map(opp => ({
      name: opp.niche,
      marketSize: opp.factors?.market_size || 0,
      growthRate: opp.factors?.growth_rate || 0,
      competition: opp.factors?.competition || 0,
      problemSeverity: opp.factors?.problem_severity || 0,
      solutionFeasibility: opp.factors?.solution_feasibility || 0,
      monetizationPotential: opp.factors?.monetization_potential || 0,
    }));
  };

  // Determine if we're dealing with a single opportunity or multiple for comparison
  const isSingleOpportunity = !Array.isArray(data) || data.length === 1;
  const chartData = isSingleOpportunity
    ? formatSingleOpportunity(Array.isArray(data) ? data[0] : data)
    : formatMultipleOpportunities(data);

  // Define colors for up to 10 opportunities
  const colors = [
    '#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088fe',
    '#00c49f', '#ffbb28', '#ff8042', '#a4de6c', '#d0ed57'
  ];

  return (
    <div className="chart-container">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        {isSingleOpportunity ? (
          <RadarChart outerRadius={90} data={chartData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="subject" />
            <PolarRadiusAxis angle={30} domain={[0, 1.0]} />
            <Radar
              name="Opportunity Score"
              dataKey="value"
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.6}
            />
            <Tooltip formatter={(value) => [value.toFixed(2), "Score"]} />
            <Legend />
          </RadarChart>
        ) : (
          <RadarChart outerRadius={90} data={chartData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="subject" />
            <PolarRadiusAxis angle={30} domain={[0, 1.0]} />
            {["marketSize", "growthRate", "competition", "problemSeverity", "solutionFeasibility", "monetizationPotential"].map(
              (dataKey, index) => (
                <Radar
                  key={dataKey}
                  name={dataKey.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase())}
                  dataKey={dataKey}
                  stroke={colors[index % colors.length]}
                  fill={colors[index % colors.length]}
                  fillOpacity={0.6}
                />
              )
            )}
            <Tooltip formatter={(value) => [value.toFixed(2), "Score"]} />
            <Legend />
          </RadarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};

export default OpportunityRadarChart;
