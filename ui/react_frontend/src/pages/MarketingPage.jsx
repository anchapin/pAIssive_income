import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardHeader,
  // CardMedia is imported but not used
  Tabs,
  Tab,
  // TextField is imported but not used
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  LinearProgress,
  IconButton,
  Stack
} from '@mui/material';
import { styled } from '@mui/material/styles';
import RefreshIcon from '@mui/icons-material/Refresh';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import EditIcon from '@mui/icons-material/Edit';
import CampaignIcon from '@mui/icons-material/Campaign';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
}));

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`marketing-tabpanel-${index}`}
      aria-labelledby={`marketing-tab-${index}`}
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

const MarketingPage = () => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedSolution, setSelectedSolution] = useState('');
  const [targetAudience, setTargetAudience] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);

  // Mock solutions data (would come from API)
  const solutions = [
    { id: 1, name: 'AI-powered Content Optimization Tool' },
    { id: 2, name: 'Local AI Code Assistant' },
    { id: 3, name: 'AI-powered Financial Analysis' },
  ];

  // Mock audience personas
  const audiencePersonas = [
    { id: 1, name: 'Content Creators', interests: ['SEO', 'Writing', 'Social Media'] },
    { id: 2, name: 'Small Business Owners', interests: ['Marketing', 'Automation', 'Analytics'] },
    { id: 3, name: 'Software Developers', interests: ['Coding', 'Productivity', 'AI Tools'] },
    { id: 4, name: 'Financial Analysts', interests: ['Data Analysis', 'Market Trends', 'Forecasting'] },
    { id: 5, name: 'Marketing Professionals', interests: ['Campaign Management', 'Analytics', 'Content Creation'] },
  ];

  // Marketing channels
  const marketingChannels = [
    { id: 1, name: 'Social Media', platforms: ['Twitter', 'LinkedIn', 'Facebook', 'Instagram'] },
    { id: 2, name: 'Email Marketing', platforms: ['Newsletters', 'Drip Campaigns', 'Announcements'] },
    { id: 3, name: 'Content Marketing', platforms: ['Blog Posts', 'Tutorials', 'eBooks', 'Webinars'] },
    { id: 4, name: 'Paid Advertising', platforms: ['Google Ads', 'Facebook Ads', 'LinkedIn Ads'] },
    { id: 5, name: 'Community Engagement', platforms: ['Reddit', 'Discord', 'Forums', 'Q&A Sites'] },
  ];

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleSolutionChange = (event) => {
    setSelectedSolution(event.target.value);
  };

  const handleAudienceChange = (event) => {
    setTargetAudience(event.target.value);
  };

  const handleChannelChange = (event) => {
    setSelectedChannel(event.target.value);
  };

  const handleGenerate = () => {
    setIsGenerating(true);

    // Simulate API call delay
    setTimeout(() => {
      // Mock generated marketing content (in a real app, this would come from backend)
      const mockContent = {
        strategy: {
          title: `Marketing Strategy for ${solutions.find(s => s.id === selectedSolution)?.name}`,
          summary: `A comprehensive marketing approach targeting ${targetAudience.map(id => audiencePersonas.find(p => p.id === id)?.name).join(', ')} through ${selectedChannel.map(id => marketingChannels.find(c => c.id === id)?.name).join(', ')}.`,
          keyPoints: [
            'Focus on solving specific pain points for each audience segment',
            'Highlight the AI-powered capabilities and unique features',
            'Emphasize ease of use and quick implementation',
            'Showcase real-world examples and case studies',
            'Leverage free trial to demonstrate value'
          ],
          timeline: '3-month campaign with phased rollout',
        },
        content: {
          socialMedia: [
            {
              platform: 'Twitter',
              posts: [
                "Tired of manual [task]? Our new AI tool automates the entire process. Try it free: [link] #AI #Productivity",
                "Save 5+ hours every week with [Product Name]. Our users are reporting incredible time savings and better results. Learn more: [link]",
                "\"I can't believe how much time this saves me\" - actual customer quote about [Product Name]. See what the buzz is about: [link]"
              ]
            },
            {
              platform: 'LinkedIn',
              posts: [
                "Introducing [Product Name]: The AI-powered solution professionals are using to automate [task] and improve results by up to 40%. Learn more in the comments!",
                "We analyzed 1,000+ user workflows and discovered the biggest time-wasters in [industry]. Here's how our AI tool solves them: [link]",
              ]
            }
          ],
          emailMarketing: [
            {
              type: "Welcome Email",
              subject: "Welcome to [Product Name]! Here's How to Get Started",
              content: `Hi [Name],

Thank you for signing up for [Product Name]! We're excited to have you on board.

Here's how to get started in just 3 simple steps:
1. Complete your profile setup
2. Connect your first [data source/tool]
3. Run your first automated [task]

Need help? Reply to this email or check out our quick-start guide: [link]

Best regards,
The [Product Name] Team`
            },
            {
              type: 'Feature Announcement',
              subject: 'New: [Feature] Just Added to Your Account',
              content: `Hi [Name],

We've just released a powerful new feature that many of you have been requesting...

[Feature description with benefits]

Login now to try it out: [link]

As always, we'd love to hear your feedback!

Best regards,
The [Product Name] Team`
            }
          ],
          blogPosts: [
            {
              title: `How [Industry Professionals] Are Saving 5+ Hours Per Week With AI`,
              outline: [
                'Introduction: The time challenges facing [industry professionals]',
                'The hidden costs of manual [task]',
                'How AI is transforming [industry] workflows',
                'Real-world case study: [Customer example]',
                'Getting started with AI tools for [industry]',
                'Conclusion: The future of AI in [industry]'
              ]
            }
          ],
          landingPage: {
            headline: `Save Time and Improve Results with AI-Powered [Solution]`,
            subheadline: `Automate [task] and focus on what matters most`,
            keyFeatures: [
              'Feature 1: [Benefit statement]',
              'Feature 2: [Benefit statement]',
              'Feature 3: [Benefit statement]'
            ],
            callToAction: 'Start Your Free Trial',
            socialProof: '1,000+ professionals are already saving time with [Product Name]'
          }
        }
      };

      setGeneratedContent(mockContent);
      setIsGenerating(false);
    }, 2500);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // In a real app, you would show a notification that text was copied
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Marketing Campaign
      </Typography>
      <Typography variant="subtitle1" paragraph>
        Develop targeted marketing campaigns to reach ideal customers and grow your subscriber base.
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="marketing tabs">
          <Tab label="Campaign Setup" />
          <Tab label="Content Generation" />
          <Tab label="Channel Strategy" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Item>
              <Typography variant="h6" gutterBottom>
                Campaign Configuration
              </Typography>

              <Box mb={3}>
                <FormControl fullWidth margin="normal">
                  <InputLabel id="solution-select-label">Solution</InputLabel>
                  <Select
                    labelId="solution-select-label"
                    id="solution-select"
                    value={selectedSolution}
                    onChange={handleSolutionChange}
                    label="Solution"
                  >
                    {solutions.map((solution) => (
                      <MenuItem key={solution.id} value={solution.id}>
                        {solution.name}
                      </MenuItem>
                    ))}
                  </Select>
                  <FormHelperText>Select the solution to market</FormHelperText>
                </FormControl>
              </Box>

              <Box mb={3}>
                <FormControl fullWidth margin="normal">
                  <InputLabel id="audience-select-label">Target Audience</InputLabel>
                  <Select
                    labelId="audience-select-label"
                    id="audience-select"
                    multiple
                    value={targetAudience}
                    onChange={handleAudienceChange}
                    label="Target Audience"
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip
                            key={value}
                            label={audiencePersonas.find(persona => persona.id === value)?.name}
                            size="small"
                          />
                        ))}
                      </Box>
                    )}
                  >
                    {audiencePersonas.map((persona) => (
                      <MenuItem key={persona.id} value={persona.id}>
                        {persona.name}
                      </MenuItem>
                    ))}
                  </Select>
                  <FormHelperText>Select target audience personas</FormHelperText>
                </FormControl>
              </Box>

              <Box mb={3}>
                <FormControl fullWidth margin="normal">
                  <InputLabel id="channel-select-label">Marketing Channels</InputLabel>
                  <Select
                    labelId="channel-select-label"
                    id="channel-select"
                    multiple
                    value={selectedChannel}
                    onChange={handleChannelChange}
                    label="Marketing Channels"
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip
                            key={value}
                            label={marketingChannels.find(channel => channel.id === value)?.name}
                            size="small"
                          />
                        ))}
                      </Box>
                    )}
                  >
                    {marketingChannels.map((channel) => (
                      <MenuItem key={channel.id} value={channel.id}>
                        {channel.name}
                      </MenuItem>
                    ))}
                  </Select>
                  <FormHelperText>Select marketing channels</FormHelperText>
                </FormControl>
              </Box>

              <Box textAlign="center" mt={4}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleGenerate}
                  disabled={isGenerating || !selectedSolution || targetAudience.length === 0 || selectedChannel.length === 0}
                  startIcon={<CampaignIcon />}
                >
                  {isGenerating ? 'Generating...' : 'Generate Marketing Campaign'}
                </Button>
              </Box>

              {isGenerating && (
                <Box sx={{ width: '100%', mt: 3 }}>
                  <LinearProgress />
                  <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                    Crafting your marketing campaign...
                  </Typography>
                </Box>
              )}
            </Item>
          </Grid>

          <Grid item xs={12} md={6}>
            <Item>
              <Typography variant="h6" gutterBottom>
                Selected Audience Personas
              </Typography>

              {targetAudience.length > 0 ? (
                <Box>
                  {targetAudience.map(audienceId => {
                    const persona = audiencePersonas.find(p => p.id === audienceId);
                    return persona ? (
                      <Card key={persona.id} variant="outlined" sx={{ mb: 2 }}>
                        <CardHeader title={persona.name} sx={{ backgroundColor: '#f8f9fc' }} />
                        <CardContent>
                          <Typography variant="subtitle2">
                            Key Interests:
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                            {persona.interests.map((interest, idx) => (
                              <Chip key={idx} label={interest} size="small" />
                            ))}
                          </Box>
                        </CardContent>
                      </Card>
                    ) : null;
                  })}
                </Box>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="text.secondary">
                    Select target audience personas to see details
                  </Typography>
                </Box>
              )}

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Selected Marketing Channels
              </Typography>

              {selectedChannel.length > 0 ? (
                <Box>
                  {selectedChannel.map(channelId => {
                    const channel = marketingChannels.find(c => c.id === channelId);
                    return channel ? (
                      <Card key={channel.id} variant="outlined" sx={{ mb: 2 }}>
                        <CardHeader title={channel.name} sx={{ backgroundColor: '#f8f9fc' }} />
                        <CardContent>
                          <Typography variant="subtitle2">
                            Platforms:
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                            {channel.platforms.map((platform, idx) => (
                              <Chip key={idx} label={platform} size="small" />
                            ))}
                          </Box>
                        </CardContent>
                      </Card>
                    ) : null;
                  })}
                </Box>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="text.secondary">
                    Select marketing channels to see details
                  </Typography>
                </Box>
              )}
            </Item>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {generatedContent ? (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Item>
                <Typography variant="h6" gutterBottom>
                  {generatedContent.strategy.title}
                </Typography>
                <Typography paragraph>
                  {generatedContent.strategy.summary}
                </Typography>

                <Typography variant="subtitle1" gutterBottom>
                  Key Strategy Points:
                </Typography>
                <List>
                  {generatedContent.strategy.keyPoints.map((point, idx) => (
                    <ListItem key={idx} disablePadding>
                      <ListItemText primary={point} />
                    </ListItem>
                  ))}
                </List>
              </Item>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Social Media Content
              </Typography>

              {generatedContent.content.socialMedia.map((platform, idx) => (
                <Item key={idx} sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    {platform.platform} Posts
                  </Typography>

                  {platform.posts.map((post, postIdx) => (
                    <Card key={postIdx} variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="body1">{post}</Typography>
                        <Stack direction="row" spacing={1} justifyContent="flex-end" mt={1}>
                          <IconButton size="small" onClick={() => copyToClipboard(post)}>
                            <ContentCopyIcon fontSize="small" />
                          </IconButton>
                          <IconButton size="small">
                            <EditIcon fontSize="small" />
                          </IconButton>
                          <IconButton size="small">
                            <RefreshIcon fontSize="small" />
                          </IconButton>
                        </Stack>
                      </CardContent>
                    </Card>
                  ))}
                </Item>
              ))}
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Email Marketing Templates
              </Typography>

              {generatedContent.content.emailMarketing.map((email, idx) => (
                <Item key={idx} sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    {email.type}
                  </Typography>

                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        Subject: {email.subject}
                      </Typography>
                      <Typography
                        variant="body1"
                        component="pre"
                        sx={{
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'inherit',
                          my: 2,
                          p: 2,
                          backgroundColor: '#f8f9fc',
                          borderRadius: 1
                        }}
                      >
                        {email.content}
                      </Typography>
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        <IconButton size="small" onClick={() => copyToClipboard(email.content)}>
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                        <IconButton size="small">
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton size="small">
                          <RefreshIcon fontSize="small" />
                        </IconButton>
                      </Stack>
                    </CardContent>
                  </Card>
                </Item>
              ))}
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Blog Post Ideas
              </Typography>

              {generatedContent.content.blogPosts.map((post, idx) => (
                <Item key={idx} sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    {post.title}
                  </Typography>

                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        Outline:
                      </Typography>
                      <List dense>
                        {post.outline.map((item, itemIdx) => (
                          <ListItem key={itemIdx} disablePadding sx={{ py: 0.5 }}>
                            <ListItemText primary={item} />
                          </ListItem>
                        ))}
                      </List>
                      <Stack direction="row" spacing={1} justifyContent="flex-end" mt={1}>
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<EditIcon />}
                        >
                          Expand
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Item>
              ))}
            </Grid>
          </Grid>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography color="text.secondary">
              Configure and generate a marketing campaign to see content here
            </Typography>
          </Box>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Item>
              <Typography variant="h6" gutterBottom>
                Channel Strategy
              </Typography>

              <Typography variant="body2" paragraph>
                This section will provide detailed strategies for each selected marketing channel, including posting schedules, budget allocation, and performance metrics.
              </Typography>

              <Box sx={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">
                  Channel strategies will appear here after generating a marketing campaign.
                </Typography>
              </Box>
            </Item>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
};

export default MarketingPage;
