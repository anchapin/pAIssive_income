import {
    Box,
    // FormControl is imported but not used
    // InputLabel is imported but not used
    // Select is imported but not used
    // MenuItem is imported but not used
    Button,
    Card,
    CardContent,
    CardHeader,
    Chip,
    Grid,
    // Divider is imported but not used
    LinearProgress,
    List,
    ListItem,
    ListItemText,
    Paper,
    // Rating is imported but not used
    Tab,
    Tabs,
    TextField,
    Typography
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useState } from 'react';
// Import our new visualization components
import {
    OpportunityBarChart,
    OpportunityRadarChart,
    ScoreDistributionPieChart
} from '../components/Visualizations';

// Constants
const ERROR_MESSAGE_SELECT_SEGMENT = 'Please select at least one segment.';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
}));

// TabPanel component for handling tab content
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`visualization-tabpanel-${index}`}
      aria-labelledby={`visualization-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `visualization-tab-${index}`,
    'aria-controls': `visualization-tabpanel-${index}`,
  };
}

const NicheAnalysisPage = () => {
  const [selectedSegments, setSelectedSegments] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [validationError, setValidationError] = useState('');

  // Market segments available for analysis
  const marketSegments = [
    'E-commerce',
    'Content Creation',
    'Software Development',
    'Education',
    'Healthcare',
    'Finance',
    'Marketing',
    'Legal',
    'Real Estate',
    'Hospitality',
    'Manufacturing',
    'Retail',
    'Transportation',
  ];

  // Filter segments based on search term
  const filteredSegments = marketSegments.filter(segment =>
    segment.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Handle segment selection
  const handleSegmentSelect = (segment) => {
    if (!selectedSegments.includes(segment)) {
      setSelectedSegments([...selectedSegments, segment]);
      setValidationError('');
    }
  };

  // Handle segment removal
  const handleSegmentRemove = (segmentToRemove) => {
    const newSegments = selectedSegments.filter(segment => segment !== segmentToRemove);
    setSelectedSegments(newSegments);
    if (newSegments.length === 0) {
      setValidationError(ERROR_MESSAGE_SELECT_SEGMENT);
    }
  };

  // Handle search term change
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle analysis submission
  const handleAnalyze = () => {
    if (selectedSegments.length === 0) {
      setValidationError(ERROR_MESSAGE_SELECT_SEGMENT);
      return;
    }
    setValidationError('');
    setIsAnalyzing(true);

    // Simulate API call delay
    setTimeout(() => {
      // Mock analysis results (in a real app, this would come from backend)
      const mockResults = {
        niches: [
          {
            id: 1,
            name: 'AI-powered content optimization',
            segment: 'Content Creation',
            opportunityScore: 0.87,
            competitionLevel: 'Medium',
            demandLevel: 'High',
            profitPotential: 0.85,
            problems: [
              'Content creators struggle with SEO optimization',
              'Manual keyword research is time-consuming',
              'Difficulty in maintaining voice consistency'
            ],
            // Add factor scores for visualization
            factors: {
              market_size: 0.85,
              growth_rate: 0.90,
              competition: 0.65,
              problem_severity: 0.75,
              solution_feasibility: 0.95,
              monetization_potential: 0.88
            }
          },
          {
            id: 2,
            name: 'Local AI code assistant',
            segment: 'Software Development',
            opportunityScore: 0.92,
            competitionLevel: 'Low',
            demandLevel: 'Very High',
            profitPotential: 0.90,
            problems: [
              'Privacy concerns with cloud-based coding assistants',
              'Need for offline coding support',
              'Customized code suggestions for specific frameworks'
            ],
            // Add factor scores for visualization
            factors: {
              market_size: 0.90,
              growth_rate: 0.95,
              competition: 0.85,
              problem_severity: 0.90,
              solution_feasibility: 0.85,
              monetization_potential: 0.92
            }
          },
          {
            id: 3,
            name: 'AI-powered financial analysis',
            segment: 'Finance',
            opportunityScore: 0.75,
            competitionLevel: 'High',
            demandLevel: 'High',
            profitPotential: 0.82,
            problems: [
              'Complex data interpretation requires expertise',
              'Real-time financial decision support is limited',
              'Personalized investment strategies are expensive'
            ],
            // Add factor scores for visualization
            factors: {
              market_size: 0.80,
              growth_rate: 0.70,
              competition: 0.45,
              problem_severity: 0.85,
              solution_feasibility: 0.75,
              monetization_potential: 0.82
            }
          },
        ],
        // Add score distribution for visualization
        scoreDistribution: {
          excellent: 2,
          very_good: 1,
          good: 0,
          fair: 0,
          limited: 0
        }
      };

      setAnalysisResults(mockResults);
      setIsAnalyzing(false);
    }, 2000);
  };

  // Prepare data for the radar chart (single opportunity)
  const getSelectedNicheData = () => {
    if (!analysisResults || !analysisResults.niches || analysisResults.niches.length === 0) {
      return null;
    }
    // Return the first niche by default
    return analysisResults.niches[0];
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Niche Analysis
      </Typography>
      <Typography variant="subtitle1" paragraph>
        Identify profitable niches with high demand and low competition using our AI-powered market analysis tools.
      </Typography>

      <Grid container spacing={3}>
        {/* Market segment selection section */}
        <Grid item xs={12} md={6}>
          <Item>
            <Typography variant="h6" gutterBottom>
              Select Market Segments
            </Typography>

            <Box mb={2}>
              <TextField
                fullWidth
                label="Search Market Segments"
                variant="outlined"
                value={searchTerm}
                onChange={handleSearchChange}
                inputProps={{ 'aria-label': 'search market segments' }}
              />
            </Box>

            <Box mb={3} sx={{ maxHeight: '300px', overflowY: 'auto' }}>
              <List dense component="div" role="list">
                {filteredSegments.map((segment) => (
                  <ListItem
                    key={segment}
                    role="listitem"
                    button
                    onClick={() => handleSegmentSelect(segment)}
                    disabled={selectedSegments.includes(segment)}
                  >
                    <ListItemText primary={segment} />
                  </ListItem>
                ))}
              </List>
            </Box>

            <Typography variant="subtitle2" gutterBottom>
              Selected Segments:
            </Typography>

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {selectedSegments.map((segment) => (
                <Chip
                  key={segment}
                  label={segment}
                  onDelete={() => handleSegmentRemove(segment)}
                  color="primary"
                />
              ))}
            </Box>

            {/* Validation feedback */}
            {validationError && (
              <Box sx={{ mt: 2 }}>
                <Typography color="error" variant="body2" role="alert">
                  {validationError}
                </Typography>
              </Box>
            )}

            <Box mt={3} textAlign="center">
              <Button
                variant="contained"
                color="primary"
                disabled={selectedSegments.length === 0 || isAnalyzing}
                onClick={handleAnalyze}
                sx={{ minWidth: '200px' }}
                aria-label="Analyze Niches"
                startIcon={!isAnalyzing && <span role="img" aria-label="analyze">🔍</span>}
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze Niches'}
              </Button>
            </Box>
          </Item>
        </Grid>

        {/* Analysis results section */}
        <Grid item xs={12} md={6}>
          <Item>
            <Typography variant="h6" gutterBottom>
              Analysis Results
            </Typography>

            {isAnalyzing ? (
              <Box sx={{ width: '100%' }}>
                <Typography variant="body2" align="center" gutterBottom>
                  Analyzing market segments...
                </Typography>
                <LinearProgress color="primary" />
              </Box>
            ) : analysisResults ? (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Found {analysisResults.niches.length} promising niches
                </Typography>

                {analysisResults.niches.map((niche) => (
                  <Card key={niche.id} sx={{ mb: 2 }}>
                    <CardHeader
                      title={niche.name}
                      subheader={`Segment: ${niche.segment}`}
                      sx={{
                        backgroundColor: (theme) => theme.palette.background.default,
                        borderBottom: (theme) => `1px solid ${theme.palette.divider}`
                      }}
                    />
                    <CardContent>
                      <Box sx={{ mb: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography component="div" variant="subtitle1">
                          Opportunity Score:
                        </Typography>
                        <Chip
                          label={niche.opportunityScore.toFixed(2)}
                          color={niche.opportunityScore > 0.8 ? 'success' : niche.opportunityScore > 0.7 ? 'primary' : 'warning'}
                        />
                      </Box>

                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography component="div" variant="body2">
                          Competition: {niche.competitionLevel}
                        </Typography>
                        <Typography component="div" variant="body2">
                          Demand: {niche.demandLevel}
                        </Typography>
                      </Box>

                      <Typography variant="subtitle2" sx={{ mt: 1 }}>
                        Key Problems:
                      </Typography>
                      <List dense>
                        {niche.problems.map((problem, index) => (
                          <ListItem key={index} disablePadding sx={{ py: 0.5 }}>
                            <ListItemText primary={problem} />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography color="text.secondary" variant="body1">
                  Select market segments and click "Analyze Niches" to start
                </Typography>
              </Box>
            )}
          </Item>
        </Grid>

        {/* Visualization section - only show when we have analysis results */}
        {analysisResults && (
          <Grid item xs={12}>
            <Item>
              <Typography variant="h6" gutterBottom>
                Market Analysis Visualizations
              </Typography>

              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={tabValue} onChange={handleTabChange} aria-label="market analysis visualizations">
                  <Tab label="Factor Analysis" {...a11yProps(0)} />
                  <Tab label="Opportunity Comparison" {...a11yProps(1)} />
                  <Tab label="Score Distribution" {...a11yProps(2)} />
                </Tabs>
              </Box>

              <TabPanel value={tabValue} index={0}>
                <OpportunityRadarChart
                  data={getSelectedNicheData()}
                  title="Opportunity Factor Analysis"
                  height={400}
                />
              </TabPanel>

              <TabPanel value={tabValue} index={1}>
                <OpportunityBarChart
                  data={analysisResults.niches}
                  dataKey=os.environ.get("KEY")
                  title="Opportunity Score Comparison"
                  height={400}
                />
              </TabPanel>

              <TabPanel value={tabValue} index={2}>
                <ScoreDistributionPieChart
                  data={analysisResults.scoreDistribution}
                  title="Opportunity Score Distribution"
                  height={400}
                />
              </TabPanel>
            </Item>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default NicheAnalysisPage;
