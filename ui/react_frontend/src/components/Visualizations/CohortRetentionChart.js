import React from 'react';
import { styled } from '@mui/material/styles';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box
} from '@mui/material';

/**
 * CohortRetentionChart - Component for visualizing user retention over time by cohort
 *
 * This component displays a cohort analysis visualization showing how user retention
 * rates change over time for different user cohorts (e.g., users who joined in a specific month).
 *
 * @param {Object} props - Component props
 * @param {Array} props.data - Array of cohort retention data objects
 * @param {string} props.title - Chart title
 * @param {string} props.periodLabel - Label for the time period (e.g., "Month", "Week")
 * @param {Array} props.cohortLabels - Array of labels for each cohort (e.g., ["Jan 2023", "Feb 2023"])
 * @returns {React.Component} A cohort table component for retention visualization
 */
const CohortRetentionChart = ({
  data = [],
  title = "User Retention Analysis",
  periodLabel = "Month",
  cohortLabels = []
}) => {
  // If no data, return a message
  if (!Array.isArray(data) || data.length === 0) {
    return <div>No retention data available for visualization</div>;
  }

  // Function to determine background color based on retention rate
  const getBackgroundColor = (value) => {
    if (value === 100) return '#1a237e'; // Dark blue for 100% (initial cohort)
    if (value >= 80) return '#2196f3'; // Blue
    if (value >= 60) return '#4caf50'; // Green
    if (value >= 40) return '#8bc34a'; // Light green
    if (value >= 20) return '#ffeb3b'; // Yellow
    if (value >= 10) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  // Function to determine text color based on background color
  const getTextColor = (backgroundColor) => {
    // Dark backgrounds need light text
    if (['#1a237e', '#2196f3', '#4caf50', '#f44336'].includes(backgroundColor)) {
      return '#ffffff';
    }
    // Light backgrounds need dark text
    return '#000000';
  };

  // Custom styled TableCell for retention values
  const RetentionCell = styled(TableCell)(({ theme, retention }) => {
    const backgroundColor = getBackgroundColor(retention);
    const textColor = getTextColor(backgroundColor);

    return {
      backgroundColor: backgroundColor,
      color: textColor,
      fontWeight: 'bold',
      textAlign: 'center',
      minWidth: '60px',
      position: 'relative',
      '&:after': {
        content: `'${retention}%'`,
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        fontSize: '0.825rem',
      },
    };
  });

  return (
    <div className="chart-container">
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>

      <Box mb={2}>
        <Typography variant="body2" color="textSecondary">
          This chart shows the percentage of users from each cohort who remain active in subsequent time periods.
          The darker/more vibrant the color, the higher the retention rate.
        </Typography>
      </Box>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Cohort</TableCell>
              <TableCell>Size</TableCell>
              {Array.from({ length: data[0].retention.length }, (_, i) => (
                <TableCell key={i} align="center">
                  {periodLabel} {i}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                <TableCell component="th" scope="row">
                  {cohortLabels[rowIndex] || `Cohort ${rowIndex + 1}`}
                </TableCell>
                <TableCell>{row.size.toLocaleString()}</TableCell>
                {row.retention.map((value, colIndex) => (
                  <RetentionCell
                    key={colIndex}
                    retention={value}
                  >
                    &nbsp;
                  </RetentionCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Box mt={2} display="flex" alignItems="center" flexWrap="wrap" gap={1}>
        <Typography variant="body2">Legend:</Typography>
        {[100, 80, 60, 40, 20, 10, 0].map((value, index) => (
          <Box
            key={index}
            sx={{
              width: '20px',
              height: '20px',
              backgroundColor: getBackgroundColor(value),
              mr: 0.5,
              border: '1px solid #ccc',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography
              variant="caption"
              sx={{
                color: getTextColor(getBackgroundColor(value)),
                fontSize: '8px',
                fontWeight: 'bold'
              }}
            >
              {value}%
            </Typography>
          </Box>
        ))}
      </Box>
    </div>
  );
};

export default CohortRetentionChart;
