import React, { useState } from 'react';
import './App.css';
import { Box, Grid, Paper, TextField, Button, Typography, CircularProgress } from '@mui/material';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import axios from 'axios';

function App() {
  const [path, setPath] = useState('');
  const [aboutText, setAboutText] = useState('');
  const [directoryStructure, setDirectoryStructure] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [fileAnalysis, setFileAnalysis] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePathSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('http://localhost:5000/api/analyze-path', { path });
      setDirectoryStructure(response.data.structure);
      setSelectedFiles([]);
      setFileAnalysis({});
    } catch (error) {
      setError(error.response?.data?.error || 'Error analyzing path');
    }
    setLoading(false);
  };

  const handleFileSelect = async (filePath) => {
    setSelectedFiles(prev => {
      const newSelection = prev.includes(filePath)
        ? prev.filter(p => p !== filePath)
        : [...prev, filePath];
      
      // Analyze selected files
      if (!prev.includes(filePath)) {
        analyzeFiles([filePath]);
      }
      
      return newSelection;
    });
  };

  const analyzeFiles = async (files) => {
    try {
      const response = await axios.post('http://localhost:5000/api/analyze-files', { files });
      const newAnalysis = { ...fileAnalysis };
      response.data.results.forEach(result => {
        newAnalysis[result.path] = {
          summary: result.summary,
          analysis: result.analysis
        };
      });
      setFileAnalysis(newAnalysis);
    } catch (error) {
      setError(error.response?.data?.error || 'Error analyzing files');
    }
  };

  const renderDirectoryTree = (node, level = 0) => {
    if (!node) return null;

    const isFile = node.type === 'file';
    const isSelected = selectedFiles.includes(node.path);
    const hasProposedChanges = isFile ? node.proposed_changes : node.proposed_structure;

    return (
      <div key={node.path} style={{ marginLeft: level * 20 }}>
        <div className="folder-item">
          <span 
            className="checkbox" 
            onClick={() => isFile && handleFileSelect(node.path)}
            style={{ 
              cursor: isFile ? 'pointer' : 'default',
              borderColor: hasProposedChanges ? '#2196f3' : '#ccc'
            }}
          >
            {!isFile && '■'}
            {isFile && isSelected && '✓'}
          </span>
          <span style={{ 
            color: hasProposedChanges ? '#2196f3' : 'inherit',
            fontWeight: hasProposedChanges ? 500 : 'normal'
          }}>
            {node.name}
          </span>
          {hasProposedChanges && (
            <Typography
              variant="caption"
              sx={{
                ml: 1,
                color: '#2196f3',
                fontSize: '12px',
                fontStyle: 'italic'
              }}
            >
              (Changes proposed)
            </Typography>
          )}
        </div>
        
        {/* Show proposed changes for files */}
        {isFile && isSelected && node.proposed_changes && (
          <div className="proposed-changes">
            <Typography variant="caption" color="primary">
              Proposed Changes:
            </Typography>
            <Typography variant="body2" sx={{ ml: 2, mt: 0.5 }}>
              {node.proposed_changes}
            </Typography>
          </div>
        )}
        
        {/* Show proposed structure for directories */}
        {!isFile && node.proposed_structure && (
          <div className="proposed-structure">
            <Typography variant="caption" color="primary" sx={{ display: 'block', mt: 1, mb: 0.5 }}>
              Proposed Structure:
            </Typography>
            <div style={{ marginLeft: 20 }}>
              {renderProposedStructure(node.proposed_structure)}
            </div>
          </div>
        )}
        
        {node.children?.map(child => renderDirectoryTree(child, level + 1))}
      </div>
    );
  };

  const renderProposedStructure = (structure) => {
    if (!structure) return null;

    return (
      <div className="proposed-item">
        <Typography variant="body2" sx={{ color: '#2196f3' }}>
          • {structure.name}
        </Typography>
        {structure.children?.map(child => (
          <div key={child.name} style={{ marginLeft: 20 }}>
            {renderProposedStructure(child)}
          </div>
        ))}
      </div>
    );
  };

  const handleFolderUpload = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true;
    input.directory = true;
    input.multiple = true;
    
    input.onchange = (e) => {
      if (e.target.files.length > 0) {
        // Get the common parent directory from the first file
        const firstFile = e.target.files[0];
        const pathParts = firstFile.webkitRelativePath.split('/');
        const folderName = pathParts[0];
        setPath(folderName);
        
        // Create a directory structure from the files
        const structure = {
          type: 'directory',
          name: folderName,
          path: folderName,
          children: []
        };
        
        // Process all files
        Array.from(e.target.files).forEach(file => {
          const relativePath = file.webkitRelativePath;
          const parts = relativePath.split('/');
          
          // Skip the first part as it's the root folder
          let current = structure;
          for (let i = 1; i < parts.length; i++) {
            const part = parts[i];
            const isFile = i === parts.length - 1;
            
            if (isFile) {
              current.children.push({
                type: 'file',
                name: part,
                path: relativePath
              });
            } else {
              let folder = current.children.find(
                child => child.type === 'directory' && child.name === part
              );
              if (!folder) {
                folder = {
                  type: 'directory',
                  name: part,
                  path: parts.slice(0, i + 1).join('/'),
                  children: []
                };
                current.children.push(folder);
              }
              current = folder;
            }
          }
        });
        
        setDirectoryStructure(structure);
        setSelectedFiles([]);
        setFileAnalysis({});
      }
    };
    
    input.click();
  };

  return (
    <div className="App">
      <Grid container spacing={2} sx={{ height: '100%', p: 2 }}>
        {/* Left Panel */}
        <Grid item xs={4}>
          <Paper className="panel">
            <div className="logo-box">
              <InsertDriveFileIcon sx={{ fontSize: 40 }} />
            </div>
            
            <Typography 
              variant="h6" 
              sx={{ 
                mb: 3,
                fontWeight: 500,
                textAlign: 'center',
                color: '#2196f3'
              }}
            >
              An AI powered files reorganization tool that just makes sense! 🎉 FYP PROJ
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                <input
                  type="text"
                  className="path-input"
                  style={{ flex: 1 }}
                  placeholder="/path/to/folder"
                  value={path}
                  onChange={(e) => setPath(e.target.value)}
                />
                <Button
                  variant="outlined"
                  onClick={handleFolderUpload}
                  startIcon={<FolderOpenIcon />}
                >
                  Browse
                </Button>
              </div>
              <Button
                className="process-button"
                variant="outlined"
                fullWidth
                onClick={handlePathSubmit}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Process'}
              </Button>
            </Box>
            
            {error && (
              <Typography color="error" sx={{ mt: 2 }}>
                {error}
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Middle Panel */}
        <Grid item xs={4}>
          <Paper className="panel">
            <div className="folder-tree">
              {directoryStructure && renderDirectoryTree(directoryStructure)}
              {!directoryStructure && (
                <Typography color="textSecondary">
                  Enter a path or upload a folder to view its structure
                </Typography>
              )}
            </div>
          </Paper>
        </Grid>

        {/* Right Panel */}
        <Grid item xs={4}>
          <Paper className="panel">
            {selectedFiles.length > 0 ? (
              selectedFiles.map(file => (
                <div key={file} className="file-summary">
                  <Typography variant="h6" className="info-title">
                    {file.split('/').pop()}
                  </Typography>
                  <Typography variant="body1">
                    {fileAnalysis[file]?.summary || 'Analyzing...'}
                  </Typography>
                  {fileAnalysis[file]?.analysis && (
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                      Proposed changes: {fileAnalysis[file].analysis}
                    </Typography>
                  )}
                </div>
              ))
            ) : (
              <Typography color="textSecondary">
                Select a file to view its summary and analysis
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
}

export default App;
