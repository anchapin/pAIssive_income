import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Link
} from '@mui/material';
import { styled } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import CodeIcon from '@mui/icons-material/Code';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import CampaignIcon from '@mui/icons-material/Campaign';
import PeopleIcon from '@mui/icons-material/People';
import TerminalIcon from '@mui/icons-material/Terminal';
import WebIcon from '@mui/icons-material/Web';
// Import the AgentUI component
import { AgentUI } from '../components/AgentUI';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
}));

// Example theme configuration for AgentUI
const theme = {
  primaryColor: "#007bff",
  secondaryColor: "#f5f5f5",
  fontFamily: "Roboto, Arial, sans-serif",
  borderRadius: "8px",
  darkMode: false,
};

const AboutPage = () => {
  const [agent, setAgent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch agent info from backend
  useEffect(() => {
    async function fetchAgent() {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('/api/agent');
        if (!response.ok) throw new Error('Failed to fetch agent data');
        const data = await response.json();
        setAgent(data);
      } catch (err) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    }
    fetchAgent();
  }, []);

  // Handle actions from ag-ui and send to backend
  const onAction = useCallback(async (action) => {
    try {
      const response = await fetch('/api/agent/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action),
      });
      if (!response.ok) throw new Error('Failed to submit action');
      // Optionally, refetch agent data or update UI here
    } catch (err) {
      alert('Error sending action: ' + (err.message || err));
    }
  }, []);
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        About pAIssive Income Framework
      </Typography>

      <Grid container spacing={4}>
        <Grid item xs={12} md={8}>
          <Item>
            <Typography variant="h5" gutterBottom>
              Overview
            </Typography>
            <Typography paragraph>
              The pAIssive Income Framework is a comprehensive system for developing and monetizing niche AI tools to generate passive income.
              It provides a structured approach to identifying profitable niches, developing targeted solutions, creating effective monetization
              strategies, and marketing your products.
            </Typography>
            <Typography paragraph>
              Built with a focus on local AI models, the framework enables developers to create tools that address specific problems in various
              market segments while ensuring user privacy and reducing operational costs.
            </Typography>

            <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
              Framework Components
            </Typography>

            <Grid container spacing={3} mb={4}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardHeader
                    title="Niche Analysis"
                    avatar={<SearchIcon color="primary" />}
                    sx={{ backgroundColor: '#f8f9fc' }}
                  />
                  <CardContent>
                    <Typography paragraph>
                      Tools for analyzing market segments and identifying profitable niches:
                    </Typography>
                    <List dense>
                      <ListItem disablePadding>
                        <ListItemText primary="Market Analyzer" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Problem Identifier" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Opportunity Scorer" />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardHeader
                    title="AI Models"
                    avatar={<TerminalIcon color="primary" />}
                    sx={{ backgroundColor: '#f8f9fc' }}
                  />
                  <CardContent>
                    <Typography paragraph>
                      A system for managing and using local AI models:
                    </Typography>
                    <List dense>
                      <ListItem disablePadding>
                        <ListItemText primary="Model Manager" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Model Adapters" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Performance Monitoring" />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardHeader
                    title="Solution Development"
                    avatar={<CodeIcon color="primary" />}
                    sx={{ backgroundColor: '#f8f9fc' }}
                  />
                  <CardContent>
                    <Typography paragraph>
                      Tools for designing and developing AI-powered solutions:
                    </Typography>
                    <List dense>
                      <ListItem disablePadding>
                        <ListItemText primary="Developer Agent" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Tool Templates" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Local AI Integration" />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardHeader
                    title="Monetization"
                    avatar={<MonetizationOnIcon color="primary" />}
                    sx={{ backgroundColor: '#f8f9fc' }}
                  />
                  <CardContent>
                    <Typography paragraph>
                      Tools for creating monetization strategies:
                    </Typography>
                    <List dense>
                      <ListItem disablePadding>
                        <ListItemText primary="Subscription Models" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Pricing Calculator" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Revenue Projector" />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardHeader
                    title="Marketing"
                    avatar={<CampaignIcon color="primary" />}
                    sx={{ backgroundColor: '#f8f9fc' }}
                  />
                  <CardContent>
                    <Typography paragraph>
                      Tools for creating marketing strategies and content:
                    </Typography>
                    <List dense>
                      <ListItem disablePadding>
                        <ListItemText primary="Strategy Generator" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Content Templates" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Channel Strategies" />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardHeader
                    title="Agent Team"
                    avatar={<PeopleIcon color="primary" />}
                    sx={{ backgroundColor: '#f8f9fc' }}
                  />
                  <CardContent>
                    <Typography paragraph>
                      A team of specialized AI agents that collaborate:
                    </Typography>
                    <List dense>
                      <ListItem disablePadding>
                        <ListItemText primary="Researcher Agent" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Developer Agent" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Monetization Agent" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Marketing Agent" />
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemText primary="Feedback Agent" />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Typography variant="h5" gutterBottom>
              Workflow
            </Typography>
            <Typography paragraph>
              The typical workflow with the pAIssive Income Framework follows these steps:
            </Typography>

            <Box sx={{ pl: 2 }}>
              <ol>
                <li>
                  <Typography paragraph>
                    <strong>Niche Analysis:</strong> Identify promising niches and problems to solve
                  </Typography>
                </li>
                <li>
                  <Typography paragraph>
                    <strong>Solution Development:</strong> Create AI-powered solutions for the identified problems
                  </Typography>
                </li>
                <li>
                  <Typography paragraph>
                    <strong>Monetization Strategy:</strong> Develop pricing models and subscription plans
                  </Typography>
                </li>
                <li>
                  <Typography paragraph>
                    <strong>Marketing Plan:</strong> Create marketing strategies and content
                  </Typography>
                </li>
                <li>
                  <Typography paragraph>
                    <strong>Implementation:</strong> Build and deploy the solution
                  </Typography>
                </li>
                <li>
                  <Typography paragraph>
                    <strong>Optimization:</strong> Continuously monitor and improve performance
                  </Typography>
                </li>
              </ol>
            </Box>
          </Item>
        </Grid>

        <Grid item xs={12} md={4}>
          <Item>
            <Typography variant="h6" gutterBottom>
              Resources
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <WebIcon />
                </ListItemIcon>
                <ListItemText
                  primary="Documentation"
                  secondary="Comprehensive guides and API reference"
                />
              </ListItem>
              <ListItem button component={Link} href="https://github.com/yourusername/pAIssive_income" target="_blank">
                <ListItemIcon>
                  <CodeIcon />
                </ListItemIcon>
                <ListItemText
                  primary="GitHub Repository"
                  secondary="Source code and examples"
                />
              </ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom>
              Version Information
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText primary="Current Version" secondary="0.1.0" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Released" secondary="April 27, 2025" />
              </ListItem>
              <ListItem>
                <ListItemText primary="License" secondary="MIT" />
              </ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom>
              Requirements
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText primary="Python" secondary="3.8 or higher" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Node.js" secondary="14.0 or higher (for UI)" />
              </ListItem>
              <ListItem>
                <ListItemText primary="GPU" secondary="Optional, recommended for larger models" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Storage" secondary="10+ GB for models" />
              </ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom>
              Agent UI Integration
            </Typography>
            {loading ? (
              <Typography>Loading agent...</Typography>
            ) : error ? (
              <Typography color="error">Error: {error}</Typography>
            ) : agent ? (
              <Box sx={{ mt: 2 }}>
                <AgentUI
                  agent={agent}
                  theme={theme}
                  onAction={onAction}
                />
              </Box>
            ) : (
              <Typography>No agent data available.</Typography>
            )}
          </Item>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AboutPage;
