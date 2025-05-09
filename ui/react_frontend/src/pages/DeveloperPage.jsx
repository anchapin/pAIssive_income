import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardHeader,
  Button,
  Stepper,
  Step,
  StepLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CodeIcon from '@mui/icons-material/Code';
// SettingsIcon is imported but not used
// CloudDownloadIcon is imported but not used
import IntegrationInstructionsIcon from '@mui/icons-material/IntegrationInstructions';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
}));

const DeveloperPage = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedNiche, setSelectedNiche] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [solution, setSolution] = useState(null);
  const [open, setOpen] = useState(false);

  // Mock niches data (would come from API)
  const niches = [
    {
      id: 1,
      name: 'AI-powered content optimization',
      segment: 'Content Creation',
      opportunityScore: 0.87
    },
    {
      id: 2,
      name: 'Local AI code assistant',
      segment: 'Software Development',
      opportunityScore: 0.92
    },
    {
      id: 3,
      name: 'AI-powered financial analysis',
      segment: 'Finance',
      opportunityScore: 0.75
    },
  ];

  // Mock templates data (would come from API)
  const templates = [
    {
      id: 1,
      name: 'Web Application',
      description: 'A web-based tool with responsive design',
      technologies: ['React', 'Node.js', 'MongoDB']
    },
    {
      id: 2,
      name: 'Desktop Application',
      description: 'A native desktop application with local AI integration',
      technologies: ['Electron', 'Python', 'PyTorch']
    },
    {
      id: 3,
      name: 'Mobile Application',
      description: 'A cross-platform mobile app',
      technologies: ['React Native', 'Node.js', 'SQLite']
    },
    {
      id: 4,
      name: 'CLI Tool',
      description: 'A command-line interface tool',
      technologies: ['Python', 'Click', 'SQLite']
    },
  ];

  const steps = ['Select Niche', 'Choose Template', 'Generate Solution'];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleNicheSelect = (event) => {
    setSelectedNiche(event.target.value);
  };

  const handleTemplateSelect = (templateId) => {
    setSelectedTemplate(templateId);
  };

  const handleGenerateSolution = () => {
    setIsGenerating(true);

    // Simulate API call delay
    setTimeout(() => {
      const selectedNicheObj = niches.find(niche => niche.id === selectedNiche);
      const selectedTemplateObj = templates.find(template => template.id === selectedTemplate);

      // Mock solution generation (in a real app, this would come from backend)
      const mockSolution = {
        id: Math.floor(Math.random() * 1000),
        name: `${selectedNicheObj.name} Tool`,
        description: `A powerful tool for ${selectedNicheObj.name.toLowerCase()} built with ${selectedTemplateObj.technologies.join(', ')}.`,
        niche: selectedNicheObj,
        template: selectedTemplateObj,
        features: [
          'User authentication and profiles',
          'AI-powered analysis and recommendations',
          'Data visualization dashboard',
          'Custom reporting and exports',
          'API integration capabilities'
        ],
        technologies: selectedTemplateObj.technologies,
        architecture: {
          frontend: selectedTemplateObj.technologies[0],
          backend: selectedTemplateObj.technologies[1],
          database: selectedTemplateObj.technologies[2],
          aiModels: ['Transformer-based model', 'Fine-tuned for specific domain']
        },
        deploymentOptions: [
          'Self-hosted option',
          'Cloud deployment (AWS, Azure, GCP)',
          'Docker container'
        ],
        developmentTime: '4-6 weeks',
        nextSteps: [
          'Set up development environment',
          'Initialize project structure',
          'Integrate AI models',
          'Develop core features',
          'Create user interface',
          'Add authentication and user management',
          'Implement data storage',
          'Test and refine'
        ]
      };

      setSolution(mockSolution);
      setIsGenerating(false);
      setOpen(true);
    }, 3000);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleReset = () => {
    setActiveStep(0);
    setSelectedNiche('');
    setSelectedTemplate('');
    setSolution(null);
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Select a niche to develop a solution for:
              </Typography>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="niche-select-label">Niche</InputLabel>
                <Select
                  labelId="niche-select-label"
                  id="niche-select"
                  value={selectedNiche}
                  onChange={handleNicheSelect}
                  label="Niche"
                >
                  {niches.map((niche) => (
                    <MenuItem key={niche.id} value={niche.id}>
                      {niche.name} (Opportunity: {niche.opportunityScore.toFixed(2)})
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>Choose a niche from your analysis results</FormHelperText>
              </FormControl>
            </Grid>

            {selectedNiche && (
              <Grid item xs={12}>
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Selected Niche Details:
                  </Typography>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6">
                        {niches.find(niche => niche.id === selectedNiche)?.name}
                      </Typography>
                      <Typography color="textSecondary">
                        Market segment: {niches.find(niche => niche.id === selectedNiche)?.segment}
                      </Typography>
                      <Box display="flex" alignItems="center" mt={1}>
                        <Typography variant="body2">
                          Opportunity Score:
                        </Typography>
                        <Chip
                          size="small"
                          label={niches.find(niche => niche.id === selectedNiche)?.opportunityScore.toFixed(2)}
                          color="primary"
                          sx={{ ml: 1 }}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Box>
              </Grid>
            )}
          </Grid>
        );
      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Choose a template for your solution:
              </Typography>
            </Grid>

            {templates.map((template) => (
              <Grid item xs={12} sm={6} key={template.id}>
                <Card
                  variant="outlined"
                  sx={{
                    cursor: 'pointer',
                    border: selectedTemplate === template.id ? '2px solid #4e73df' : '1px solid rgba(0, 0, 0, 0.12)'
                  }}
                  onClick={() => handleTemplateSelect(template.id)}
                >
                  <CardHeader
                    title={template.name}
                    sx={{ backgroundColor: selectedTemplate === template.id ? 'rgba(78, 115, 223, 0.1)' : '#f8f9fc' }}
                  />
                  <CardContent>
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {template.description}
                    </Typography>
                    <Typography variant="subtitle2">
                      Technologies:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                      {template.technologies.map((tech) => (
                        <Chip key={tech} label={tech} size="small" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        );
      case 2:
        return (
          <Box textAlign="center">
            <Typography variant="subtitle1" gutterBottom>
              Ready to generate your solution!
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              We'll create a detailed solution design based on your selected niche and template.
            </Typography>
            <Box my={3}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleGenerateSolution}
                disabled={isGenerating}
                sx={{ minWidth: 200 }}
                startIcon={<IntegrationInstructionsIcon />}
              >
                {isGenerating ? 'Generating...' : 'Generate Solution'}
              </Button>
            </Box>
            {isGenerating && (
              <Box sx={{ width: '100%', mt: 2 }}>
                <LinearProgress />
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  This may take a minute...
                </Typography>
              </Box>
            )}
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Solution Development
      </Typography>
      <Typography variant="subtitle1" paragraph>
        Design and develop AI-powered solutions for specific niches with our developer tools and templates.
      </Typography>

      <Item sx={{ mb: 4 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Item>

      <Item>
        <Box p={2}>
          {getStepContent(activeStep)}
        </Box>
        <Divider sx={{ my: 2 }} />
        <Box display="flex" justifyContent="space-between" p={2}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>

          <Button
            variant="contained"
            color="primary"
            onClick={handleNext}
            disabled={
              (activeStep === 0 && !selectedNiche) ||
              (activeStep === 1 && !selectedTemplate) ||
              activeStep === steps.length - 1 ||
              isGenerating
            }
          >
            {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
          </Button>
        </Box>
      </Item>

      {/* Solution details dialog */}
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="solution-dialog-title"
        maxWidth="md"
        fullWidth
      >
        <DialogTitle id="solution-dialog-title">
          Solution Generated: {solution?.name}
        </DialogTitle>
        <DialogContent dividers>
          <DialogContentText component="div">
            <Typography paragraph>
              {solution?.description}
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Features
                </Typography>
                <List dense>
                  {solution?.features.map((feature, index) => (
                    <ListItem key={index} disablePadding>
                      <ListItemText primary={feature} />
                    </ListItem>
                  ))}
                </List>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Architecture
                </Typography>
                <List dense>
                  {solution?.architecture && Object.entries(solution.architecture).map(([key, value]) => (
                    <ListItem key={key} disablePadding>
                      <ListItemText
                        primary={`${key.charAt(0).toUpperCase() + key.slice(1)}: ${Array.isArray(value) ? value.join(', ') : value}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Deployment Options
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {solution?.deploymentOptions.map((option, index) => (
                    <Chip key={index} label={option} />
                  ))}
                </Box>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Next Steps
                </Typography>
                <Stepper activeStep={-1} orientation="vertical">
                  {solution?.nextSteps.map((step, index) => (
                    <Step key={index}>
                      <StepLabel>{step}</StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </Grid>
            </Grid>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleReset}
            startIcon={<CodeIcon />}
          >
            Start Development
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DeveloperPage;
