import React, { useState } from 'react';
import { TextField, Button, Box, Paper } from '@mui/material';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';

const FileInput = ({ onPathSubmit }) => {
  const [path, setPath] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onPathSubmit(path);
  };

  return (
    <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="/path/to/folder"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            size="small"
          />
          <Button
            variant="contained"
            startIcon={<FolderOpenIcon />}
            onClick={handleSubmit}
          >
            Process
          </Button>
        </Box>
      </form>
    </Paper>
  );
};

export default FileInput;
