import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Divider,
  Card,
  CardContent,
  Avatar,
  Chip,
  CircularProgress
} from '@mui/material';
import { styled } from '@mui/material/styles';
import SaveIcon from '@mui/icons-material/Save';
import PersonIcon from '@mui/icons-material/Person';
import { useAppContext } from '../context/AppContext';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
}));

/**
 * User profile page component
 * Allows users to view and update their profile information
 */
const ProfilePage = () => {
  const { user, addNotification, fetchUserProfile } = useAppContext();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    username: '',
    bio: ''
  });
  const [isSaving, setIsSaving] = useState(false);

  // Load user data into form when component mounts or user data changes
  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        username: user.username || '',
        bio: user.bio || ''
      });
    }
  }, [user]);

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      // In a real app, this would call an API to update the user profile
      // await apiClient.user.updateProfile(formData);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Refresh user data
      await fetchUserProfile();

      addNotification({
        type: 'success',
        message: 'Profile updated successfully!'
      });
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Failed to update profile. Please try again.'
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (!user) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Your Profile
      </Typography>

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar
                sx={{
                  width: 120,
                  height: 120,
                  margin: '0 auto 16px',
                  bgcolor: 'primary.main'
                }}
              >
                <PersonIcon sx={{ fontSize: 64 }} />
              </Avatar>

              <Typography variant="h6" gutterBottom>
                {user.name || user.username}
              </Typography>

              <Typography color="text.secondary" paragraph>
                Member since: {new Date().toLocaleDateString()}
              </Typography>

              <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 1 }}>
                {user.roles?.map(role => (
                  <Chip
                    key={role}
                    label={role.charAt(0).toUpperCase() + role.slice(1)}
                    color={role === 'admin' ? 'error' : role === 'creator' ? 'primary' : 'default'}
                    size="small"
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Item>
            <Typography variant="h6" gutterBottom>
              Edit Profile Information
            </Typography>

            <Divider sx={{ mb: 3 }} />

            <Box component="form" onSubmit={handleSubmit} noValidate>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    disabled // Username typically shouldn't be changed
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Bio"
                    name="bio"
                    multiline
                    rows={4}
                    value={formData.bio}
                    onChange={handleChange}
                    placeholder="Tell us a bit about yourself"
                  />
                </Grid>

                <Grid item xs={12}>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<SaveIcon />}
                    disabled={isSaving}
                  >
                    {isSaving ? 'Saving...' : 'Save Changes'}
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </Item>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProfilePage;
