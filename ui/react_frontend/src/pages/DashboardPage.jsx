import React from 'react';
import { Box, Typography, Grid, Paper, Card, CardContent, CardHeader, LinearProgress } from '@mui/material';
import { styled } from '@mui/material/styles';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
}));

const DashboardPage = () => {
  // This would typically be fetched from an API
  const projectsData = [
    { id: 1, name: 'AI Writing Assistant', status: 'Active', revenue: 1250, subscribers: 48, progress: 100 },
    { id: 2, name: 'Local Code Helper', status: 'In Development', revenue: 0, subscribers: 0, progress: 65 },
    { id: 3, name: 'Data Analysis Tool', status: 'In Research', revenue: 0, subscribers: 0, progress: 25 },
  ];

  const totalRevenue = projectsData.reduce((sum, project) => sum + project.revenue, 0);
  const totalSubscribers = projectsData.reduce((sum, project) => sum + project.subscribers, 0);

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Total Revenue"
              sx={{
                backgroundColor: (theme) => theme.palette.background.default,
                borderBottom: (theme) => `1px solid ${theme.palette.divider}`
              }}
            />
            <CardContent>
              <Typography variant="h3" color="primary">
                ${totalRevenue}
              </Typography>
              <Typography variant="subtitle2">
                Monthly Recurring Revenue
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Subscribers"
              sx={{
                backgroundColor: (theme) => theme.palette.background.default,
                borderBottom: (theme) => `1px solid ${theme.palette.divider}`
              }}
            />
            <CardContent>
              <Typography variant="h3" color="primary">
                {totalSubscribers}
              </Typography>
              <Typography variant="subtitle2">
                Total Active Subscribers
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Projects"
              sx={{
                backgroundColor: (theme) => theme.palette.background.default,
                borderBottom: (theme) => `1px solid ${theme.palette.divider}`
              }}
            />
            <CardContent>
              <Typography variant="h3" color="primary">
                {projectsData.length}
              </Typography>
              <Typography variant="subtitle2">
                Total Projects
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Typography variant="h5" gutterBottom>
        Projects
      </Typography>

      <Grid container spacing={3}>
        {projectsData.map((project) => (
          <Grid item xs={12} key={project.id}>
            <Item>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="h6" component="div">
                  {project.name}
                </Typography>
                <Typography variant="subtitle1" component="div">
                  Status: <span style={{ fontWeight: 'bold' }}>{project.status}</span>
                </Typography>
              </Box>

              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2">
                  Monthly Revenue: ${project.revenue}
                </Typography>
                <Typography variant="body2">
                  Subscribers: {project.subscribers}
                </Typography>
              </Box>

              <Box>
                <Typography variant="body2" mb={1}>
                  Progress:
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={project.progress}
                  sx={{
                    height: 10,
                    borderRadius: 5,
                    backgroundColor: '#e3e6f0',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor:
                        project.progress === 100 ? '#1cc88a' :
                        project.progress > 50 ? '#4e73df' :
                        '#f6c23e'
                    }
                  }}
                />
              </Box>
            </Item>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default DashboardPage;
