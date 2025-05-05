import React from 'react';
import { Snackbar, Alert, Stack } from '@mui/material';
import { useAppContext } from '../../context/AppContext';
import { ActionTypes } from '../../context/AppContext';

const Notifications = () => {
  const { notifications, dispatch } = useAppContext();

  const handleClose = (id) => {
    dispatch({
      type: ActionTypes.REMOVE_NOTIFICATION,
      payload: id
    });
  };

  return (
    <Stack spacing={2} sx={{ position: 'fixed', bottom: 24, right: 24, zIndex: 2000 }}>
      {notifications.map((notification) => (
        <Snackbar
          key={notification.id}
          open={true}
          autoHideDuration={notification.timeout || 5000}
          onClose={() => handleClose(notification.id)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            onClose={() => handleClose(notification.id)}
            severity={notification.type || 'info'}
            variant="filled"
            sx={{ width: '100%' }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      ))}
    </Stack>
  );
};

export default Notifications;
