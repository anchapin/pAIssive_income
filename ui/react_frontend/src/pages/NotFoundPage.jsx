import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { Link } from 'react-router-dom';
import { styled } from '@mui/material/styles';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(4),
  textAlign: 'center',
  color: theme.palette.text.secondary,
}));

const NotFoundPage = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '60vh'
      }}
    >
      <Item>
        <ErrorOutlineIcon fontSize="large" color="error" sx={{ fontSize: 60, mb: 2 }} />
        <Typography variant="h4" gutterBottom>
          404 - Page Not Found
        </Typography>
        <Typography variant="body1" paragraph>
          The page you're looking for doesn't exist or has been moved.
        </Typography>
        <Button component={Link} to="/" variant="contained" color="primary">
          Return to Home
        </Button>
      </Item>
    </Box>
  );
};

export default NotFoundPage;