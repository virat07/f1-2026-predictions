import React from 'react';
import { Snackbar, Alert } from '@mui/material';

const Notification = ({ message, type, onClose }) => {
  return (
    <Snackbar 
      open={!!message} 
      autoHideDuration={6000} 
      onClose={onClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      sx={{ marginTop: '70px' }} // Position below the navbar
    >
      <Alert 
        onClose={onClose} 
        severity={type || 'info'} 
        variant="filled"
        sx={{ width: '100%', borderRadius: '12px' }}
      >
        {message}
      </Alert>
    </Snackbar>
  );
};

export default Notification;
