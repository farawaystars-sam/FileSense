import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

const FileSummary = ({ selectedFile, summary }) => {
  return (
    <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        File Summary
      </Typography>
      {selectedFile ? (
        <Box>
          <Typography variant="subtitle1" color="primary" gutterBottom>
            {selectedFile}
          </Typography>
          <Typography variant="body1">
            {summary || 'Loading summary...'}
          </Typography>
        </Box>
      ) : (
        <Typography variant="body1" color="text.secondary">
          Select a file to view its summary
        </Typography>
      )}
    </Paper>
  );
};

export default FileSummary;
