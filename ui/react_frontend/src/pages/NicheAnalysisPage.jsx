import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  LinearProgress,
  Card,
  CardContent,
  CardHeader,
  Rating
} from '@mui/material';
import { styled } from '@mui/material/styles';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
}));

const NicheAnalysisPage = () => {
  const [selectedSegments, setSelectedSegments] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

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
    }
  };

  // Handle segment removal
  const handleSegmentRemove = (segmentToRemove) => {
    setSelectedSegments(selectedSegments.filter(segment => segment !== segmentToRemove));
  };

  // Handle search term change
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  // Handle analysis submission
  const handleAnalyze = () => {
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
            ]
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
            ]
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
            ]
          },
        ]
      };
      
      setAnalysisResults(mockResults);
      setIsAnalyzing(false);
    }, 2000);
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
            
            <Box mt={3} textAlign="center">
              <Button
                variant="contained"
                color="primary"
                disabled={selectedSegments.length === 0 || isAnalyzing}
                onClick={handleAnalyze}
                sx={{ minWidth: '200px' }}
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
                      sx={{ backgroundColor: '#f8f9fc', borderBottom: '1px solid #e3e6f0' }}
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
      </Grid>
    </Box>
  );
};

export default NicheAnalysisPage;