import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardHeader,
  Tabs,
  Tab,
  TextField,
  InputAdornment,
  Slider,
  FormControlLabel,
  Switch,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  Stack,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { styled } from '@mui/material/styles';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
// Import our visualization components
import {
  UserGrowthLineChart,
  RevenueAreaChart,
  TierRevenueStackedBarChart,
  CustomerLifetimeValueGauge
} from '../components/Visualizations';

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
      id={`monetization-tabpanel-${index}`}
      aria-labelledby={`monetization-tab-${index}`}
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

const MonetizationPage = () => {
  const [tabValue, setTabValue] = useState(0);
  const [basePrice, setBasePrice] = useState(19.99);
  const [tierCount, setTierCount] = useState(3);
  const [includeFreeTrialTier, setIncludeFreeTrialTier] = useState(true);
  const [includeEnterpriseCustomTier, setIncludeEnterpriseCustomTier] = useState(true);
  const [subscriptionModel, setSubscriptionModel] = useState('monthly');
  const [annualDiscountPercent, setAnnualDiscountPercent] = useState(20);
  const [projectionMonths, setProjectionMonths] = useState(36);
  const [growthRate, setGrowthRate] = useState(5); // 5% monthly growth rate
  const [projectionViewIndex, setProjectionViewIndex] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleBasePriceChange = (event) => {
    setBasePrice(parseFloat(event.target.value));
  };

  const handleTierCountChange = (event, newValue) => {
    setTierCount(newValue);
  };

  const handleGenerate = () => {
    // In a real app, this would call the backend to generate the pricing strategy
    console.log('Generate clicked');
  };

  const handleProjectionViewChange = (event, newValue) => {
    setProjectionViewIndex(newValue);
  };

  const mockSubscriptionTiers = [
    {
      name: 'Free Trial',
      price: 0,
      billingCycle: 'N/A',
      features: [
        'Limited access to basic features',
        '3 projects',
        'Community support',
        '7-day trial period'
      ],
      highlighted: false,
      visible: includeFreeTrialTier
    },
    {
      name: 'Basic',
      price: basePrice,
      billingCycle: subscriptionModel,
      features: [
        'Full access to basic features',
        '10 projects',
        'Email support',
        'Basic analytics'
      ],
      highlighted: false,
      visible: true
    },
    {
      name: 'Professional',
      price: basePrice * 2.5,
      billingCycle: subscriptionModel,
      features: [
        'Access to all features',
        'Unlimited projects',
        'Priority support',
        'Advanced analytics',
        'Team collaboration'
      ],
      highlighted: true,
      visible: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      billingCycle: subscriptionModel,
      features: [
        'Everything in Professional',
        'Custom integrations',
        'Dedicated support',
        'SLA guarantees',
        'Onboarding assistance'
      ],
      highlighted: false,
      visible: includeEnterpriseCustomTier
    }
  ];

  const visibleTiers = mockSubscriptionTiers.filter(tier => tier.visible);

  // Enhanced mock data for visualizations
  const generateMockUserProjections = () => {
    const projections = [];
    let totalUsers = 50; // Initial users
    let freeUsers = 50;
    let paidUsers = 0;
    const monthlyAcquisition = 50; // New users per month
    const monthlyConversion = 0.1; // 10% of free users convert to paid each month
    const monthlyChurn = 0.05; // 5% churn rate
    
    for (let month = 1; month <= projectionMonths; month++) {
      // Add new users
      const newUsers = monthlyAcquisition * Math.pow(1 + growthRate / 100, month - 1);
      
      // Calculate conversions
      const conversions = Math.floor(freeUsers * monthlyConversion);
      
      // Calculate churn
      const paidChurn = Math.floor(paidUsers * monthlyChurn);
      const freeChurn = Math.floor(freeUsers * monthlyChurn);
      
      // Update totals
      paidUsers = paidUsers + conversions - paidChurn;
      freeUsers = freeUsers + newUsers - conversions - freeChurn;
      totalUsers = freeUsers + paidUsers;
      
      projections.push({
        month,
        total_users: Math.floor(totalUsers),
        free_users: Math.floor(freeUsers),
        paid_users: Math.floor(paidUsers),
        new_users: Math.floor(newUsers),
        churned_users: Math.floor(paidChurn + freeChurn)
      });
    }
    
    return projections;
  };
  
  const generateMockRevenueProjections = (userProjections) => {
    return userProjections.map(month => {
      // Distribute paid users across tiers
      const basicUsers = Math.floor(month.paid_users * 0.6);
      const proUsers = Math.floor(month.paid_users * 0.3);
      const enterpriseUsers = month.paid_users - basicUsers - proUsers;
      
      // Calculate monthly revenue by tier
      const basicRevenue = basicUsers * basePrice;
      const proRevenue = proUsers * (basePrice * 2.5);
      const enterpriseRevenue = enterpriseUsers * (basePrice * 5);
      
      const totalRevenue = basicRevenue + proRevenue + enterpriseRevenue;
      const previousCumulative = month.month > 1 ? 
        mockRevenueProjections[month.month - 2].cumulative_revenue : 0;
      
      return {
        ...month,
        tier_users: {
          'Basic': basicUsers,
          'Professional': proUsers,
          'Enterprise': enterpriseUsers
        },
        tier_revenue: {
          'Basic': basicRevenue,
          'Professional': proRevenue,
          'Enterprise': enterpriseRevenue
        },
        total_revenue: totalRevenue,
        cumulative_revenue: previousCumulative + totalRevenue
      };
    });
  };
  
  // Generate mock user projections
  const mockUserProjections = generateMockUserProjections();
  
  // Generate mock revenue projections based on user projections
  const mockRevenueProjections = generateMockRevenueProjections(mockUserProjections);
  
  // Generate mock lifetime value data
  const mockLifetimeValueData = {
    average_revenue_per_user: (basePrice * 0.6) + (basePrice * 2.5 * 0.3) + (basePrice * 5 * 0.1),
    churn_rate: 0.05,
    average_lifetime_months: 1 / 0.05, // 1/churn_rate
    one_year_value: ((basePrice * 0.6) + (basePrice * 2.5 * 0.3) + (basePrice * 5 * 0.1)) * 12,
    three_year_value: ((basePrice * 0.6) + (basePrice * 2.5 * 0.3) + (basePrice * 5 * 0.1)) * 36,
    five_year_value: ((basePrice * 0.6) + (basePrice * 2.5 * 0.3) + (basePrice * 5 * 0.1)) * 60,
    lifetime_value: ((basePrice * 0.6) + (basePrice * 2.5 * 0.3) + (basePrice * 5 * 0.1)) * (1 / 0.05)
  };
  
  // Calculate simplified projections for the table view
  const tableProjections = [50, 120, 250, 450, 800, 1200].map(userCount => {
    const paidUsers = Math.floor(userCount * 0.05);
    const basicUsers = Math.floor(paidUsers * 0.6);
    const proUsers = Math.floor(paidUsers * 0.35);
    const enterpriseUsers = Math.floor(paidUsers * 0.05);
    
    const monthlyRevenue = (basicUsers * basePrice) + 
                        (proUsers * basePrice * 2.5) + 
                        (enterpriseUsers * basePrice * 5);
                        
    const annualRevenue = monthlyRevenue * 12;
    const lifetimeValue = monthlyRevenue * 20; // 20 months average lifetime
    
    return {
      userCount,
      paidUsers,
      monthlyRevenue,
      annualRevenue,
      lifetimeValue
    };
  });

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Monetization Strategy
      </Typography>
      <Typography variant="subtitle1" paragraph>
        Create effective monetization strategies with subscription models and pricing optimization.
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="monetization tabs">
          <Tab label="Subscription Model" />
          <Tab label="Pricing Strategy" />
          <Tab label="Revenue Projections" />
        </Tabs>
      </Box>
      
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Item>
              <Typography variant="h6" gutterBottom>
                Subscription Model Configuration
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    label="Base Price"
                    type="number"
                    value={basePrice}
                    onChange={handleBasePriceChange}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">$</InputAdornment>,
                    }}
                    fullWidth
                    margin="normal"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Typography id="tier-count-slider" gutterBottom>
                    Number of Tiers: {tierCount}
                  </Typography>
                  <Slider
                    value={tierCount}
                    onChange={handleTierCountChange}
                    aria-labelledby="tier-count-slider"
                    valueLabelDisplay="auto"
                    step={1}
                    marks
                    min={1}
                    max={5}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Stack direction="row" spacing={2}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={includeFreeTrialTier}
                          onChange={(e) => setIncludeFreeTrialTier(e.target.checked)}
                        />
                      }
                      label="Include Free Trial Tier"
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={includeEnterpriseCustomTier}
                          onChange={(e) => setIncludeEnterpriseCustomTier(e.target.checked)}
                        />
                      }
                      label="Include Enterprise Tier"
                    />
                  </Stack>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography gutterBottom>
                    Billing Cycle Options
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Chip
                      label="Monthly"
                      color={subscriptionModel === 'monthly' ? 'primary' : 'default'}
                      onClick={() => setSubscriptionModel('monthly')}
                      clickable
                    />
                    <Chip
                      label="Annual"
                      color={subscriptionModel === 'annual' ? 'primary' : 'default'}
                      onClick={() => setSubscriptionModel('annual')}
                      clickable
                    />
                    <Chip
                      label="Both"
                      color={subscriptionModel === 'both' ? 'primary' : 'default'}
                      onClick={() => setSubscriptionModel('both')}
                      clickable
                    />
                  </Stack>
                </Grid>
                
                {(subscriptionModel === 'annual' || subscriptionModel === 'both') && (
                  <Grid item xs={12}>
                    <Typography id="annual-discount-slider" gutterBottom>
                      Annual Discount: {annualDiscountPercent}%
                    </Typography>
                    <Slider
                      value={annualDiscountPercent}
                      onChange={(e, value) => setAnnualDiscountPercent(value)}
                      aria-labelledby="annual-discount-slider"
                      valueLabelDisplay="auto"
                      step={5}
                      marks
                      min={0}
                      max={40}
                    />
                  </Grid>
                )}
                
                <Grid item xs={12}>
                  <Box textAlign="center" mt={2}>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleGenerate}
                      startIcon={<MonetizationOnIcon />}
                    >
                      Generate Subscription Model
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Item>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Subscription Tiers Preview
            </Typography>
            
            <Grid container spacing={2}>
              {visibleTiers.map((tier, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Card 
                    variant={tier.highlighted ? 'elevation' : 'outlined'}
                    elevation={tier.highlighted ? 3 : 1}
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      position: 'relative',
                      borderColor: tier.highlighted ? 'primary.main' : 'inherit'
                    }}
                  >
                    {tier.highlighted && (
                      <Box
                        sx={{
                          position: 'absolute',
                          top: 10,
                          right: 10,
                          backgroundColor: 'primary.main',
                          color: 'white',
                          px: 1,
                          py: 0.5,
                          borderRadius: 1,
                          fontSize: '0.75rem',
                          fontWeight: 'bold'
                        }}
                      >
                        RECOMMENDED
                      </Box>
                    )}
                    
                    <CardHeader
                      title={tier.name}
                      titleTypographyProps={{ align: 'center' }}
                      sx={{ backgroundColor: tier.highlighted ? 'primary.light' : '#f8f9fc' }}
                    />
                    
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'center',
                          alignItems: 'baseline',
                          mb: 2,
                        }}
                      >
                        <Typography component="h2" variant="h3">
                          {typeof tier.price === 'number' ? `$${tier.price}` : tier.price}
                        </Typography>
                        <Typography variant="subtitle1" color="text.secondary">
                          {tier.billingCycle === 'monthly' ? '/mo' : tier.billingCycle === 'annual' ? '/yr' : ''}
                        </Typography>
                      </Box>
                      
                      <Divider sx={{ mb: 2 }} />
                      
                      <List dense>
                        {tier.features.map((feature, featureIndex) => (
                          <ListItem key={featureIndex} disablePadding>
                            <ListItemText primary={feature} />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Grid>
        </Grid>
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Item>
              <Typography variant="h6" gutterBottom>
                Pricing Strategy Analysis
              </Typography>
              
              <Typography variant="body2" paragraph>
                This section will provide insights on optimal pricing strategies based on market research, competitor analysis, and customer willingness to pay.
              </Typography>
              
              <Box sx={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">
                  Pricing analysis charts will appear here after generating a subscription model.
                </Typography>
              </Box>
            </Item>
          </Grid>
        </Grid>
      </TabPanel>
      
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          {/* Revenue projection configuration */}
          <Grid item xs={12}>
            <Item>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={4}>
                  <Typography id="projection-months-slider" gutterBottom>
                    Projection Months: {projectionMonths}
                  </Typography>
                  <Slider
                    value={projectionMonths}
                    onChange={(e, value) => setProjectionMonths(value)}
                    aria-labelledby="projection-months-slider"
                    valueLabelDisplay="auto"
                    step={6}
                    marks={[
                      { value: 12, label: '12m' },
                      { value: 24, label: '24m' },
                      { value: 36, label: '36m' },
                      { value: 48, label: '48m' },
                      { value: 60, label: '60m' }
                    ]}
                    min={12}
                    max={60}
                  />
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Typography id="growth-rate-slider" gutterBottom>
                    Monthly Growth Rate: {growthRate}%
                  </Typography>
                  <Slider
                    value={growthRate}
                    onChange={(e, value) => setGrowthRate(value)}
                    aria-labelledby="growth-rate-slider"
                    valueLabelDisplay="auto"
                    step={1}
                    marks={[
                      { value: 0, label: '0%' },
                      { value: 5, label: '5%' },
                      { value: 10, label: '10%' },
                      { value: 20, label: '20%' }
                    ]}
                    min={0}
                    max={20}
                  />
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleGenerate}
                    startIcon={<MonetizationOnIcon />}
                    fullWidth
                  >
                    Generate Projections
                  </Button>
                </Grid>
              </Grid>
            </Item>
          </Grid>
          
          {/* Visualization selectors */}
          <Grid item xs={12}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
              <Tabs 
                value={projectionViewIndex} 
                onChange={handleProjectionViewChange} 
                aria-label="revenue projection visualizations"
                variant="scrollable"
                scrollButtons="auto"
              >
                <Tab label="User Growth" />
                <Tab label="Revenue Growth" />
                <Tab label="Revenue by Tier" />
                <Tab label="Customer LTV" />
                <Tab label="Tabular Data" />
              </Tabs>
            </Box>
          </Grid>
          
          {/* Visualizations */}
          <Grid item xs={12}>
            <Item sx={{ display: projectionViewIndex === 0 ? 'block' : 'none' }}>
              <UserGrowthLineChart 
                data={mockUserProjections} 
                title="User Growth Over Time" 
                height={500}
              />
            </Item>
            
            <Item sx={{ display: projectionViewIndex === 1 ? 'block' : 'none' }}>
              <RevenueAreaChart 
                data={mockRevenueProjections} 
                title="Revenue Growth Over Time" 
                height={500}
                milestones={[
                  { month: 6, label: "6 Months" },
                  { month: 12, label: "1 Year" },
                  { month: 24, label: "2 Years" }
                ]}
              />
            </Item>
            
            <Item sx={{ display: projectionViewIndex === 2 ? 'block' : 'none' }}>
              <TierRevenueStackedBarChart 
                data={mockRevenueProjections} 
                title="Revenue by Subscription Tier" 
                height={500}
              />
            </Item>
            
            <Item sx={{ display: projectionViewIndex === 3 ? 'block' : 'none' }}>
              <CustomerLifetimeValueGauge 
                data={mockLifetimeValueData} 
                title="Customer Lifetime Value Analysis" 
                height={500}
              />
            </Item>
            
            <Item sx={{ display: projectionViewIndex === 4 ? 'block' : 'none' }}>
              <Typography variant="h6" gutterBottom>
                Revenue Projections - Tabular Data
              </Typography>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Total Users</TableCell>
                      <TableCell>Paid Users</TableCell>
                      <TableCell>Monthly Revenue</TableCell>
                      <TableCell>Annual Revenue</TableCell>
                      <TableCell>Avg. Lifetime Value</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {tableProjections.map((row, index) => (
                      <TableRow key={index}>
                        <TableCell>{row.userCount}</TableCell>
                        <TableCell>{row.paidUsers}</TableCell>
                        <TableCell>${row.monthlyRevenue.toFixed(2)}</TableCell>
                        <TableCell>${row.annualRevenue.toFixed(2)}</TableCell>
                        <TableCell>${row.lifetimeValue.toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              <Box mt={3} textAlign="center">
                <Typography variant="subtitle2" color="text.secondary">
                  Note: These projections are based on an estimated 5% conversion rate 
                  and 20-month average retention.
                </Typography>
              </Box>
            </Item>
          </Grid>
          
          {/* Summary metrics */}
          <Grid item xs={12}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Projected Users (Year 3)
                    </Typography>
                    <Typography variant="h4">
                      {mockUserProjections[mockUserProjections.length - 1]?.total_users.toLocaleString()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Projected Monthly Revenue (Year 3)
                    </Typography>
                    <Typography variant="h4">
                      ${mockRevenueProjections[mockRevenueProjections.length - 1]?.total_revenue.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                      })}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Projected Cumulative Revenue
                    </Typography>
                    <Typography variant="h4">
                      ${mockRevenueProjections[mockRevenueProjections.length - 1]?.cumulative_revenue.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                      })}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Customer Lifetime Value
                    </Typography>
                    <Typography variant="h4">
                      ${mockLifetimeValueData.lifetime_value.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                      })}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
};

export default MonetizationPage;