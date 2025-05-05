import React from 'react';
import { Box, Typography, Grid, Paper, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Link } from 'react-router-dom';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(3),
  textAlign: 'center',
  color: theme.palette.text.secondary,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'space-between',
}));

const HomePage = () => {
  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to pAIssive Income Framework
        </Typography>
        <Typography variant="subtitle1" gutterBottom>
          A comprehensive framework for developing and monetizing niche AI agents to generate passive income
          through subscription-based software tools powered by local AI.
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Item elevation={3}>
            <div>
              <Typography variant="h6" component="h2" gutterBottom>
                Niche Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Identify profitable niches with high demand and low competition using our advanced AI-powered
                market analysis tools.
              </Typography>
            </div>
            <Button component={Link} to="/niche-analysis" variant="contained" color="primary">
              Analyze Niches
            </Button>
          </Item>
        </Grid>

        <Grid item xs={12} md={4}>
          <Item elevation={3}>
            <div>
              <Typography variant="h6" component="h2" gutterBottom>
                Solution Development
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Design and develop AI-powered solutions for specific niches with our developer tools and templates.
              </Typography>
            </div>
            <Button component={Link} to="/developer" variant="contained" color="primary">
              Develop Solutions
            </Button>
          </Item>
        </Grid>

        <Grid item xs={12} md={4}>
          <Item elevation={3}>
            <div>
              <Typography variant="h6" component="h2" gutterBottom>
                Monetization
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Create effective monetization strategies with subscription models and pricing optimization.
              </Typography>
            </div>
            <Button component={Link} to="/monetization" variant="contained" color="primary">
              Create Strategy
            </Button>
          </Item>
        </Grid>

        <Grid item xs={12} md={6}>
          <Item elevation={3}>
            <div>
              <Typography variant="h6" component="h2" gutterBottom>
                Marketing
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Develop targeted marketing campaigns to reach ideal customers and grow your subscriber base.
              </Typography>
            </div>
            <Button component={Link} to="/marketing" variant="contained" color="primary">
              Plan Marketing
            </Button>
          </Item>
        </Grid>

        <Grid item xs={12} md={6}>
          <Item elevation={3}>
            <div>
              <Typography variant="h6" component="h2" gutterBottom>
                Dashboard
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Monitor your projects, track performance, and manage your passive income streams.
              </Typography>
            </div>
            <Button component={Link} to="/dashboard" variant="contained" color="primary">
              View Dashboard
            </Button>
          </Item>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HomePage;
