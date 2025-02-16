import React from 'react';
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Checkbox,
  Paper,
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';

const DirectoryTree = ({ structure, selectedFiles, onFileSelect }) => {
  const renderTree = (node) => {
    const isFile = node.type === 'file';
    const isSelected = selectedFiles.includes(node.path);

    return (
      <List key={node.path} sx={{ pl: 2 }}>
        <ListItem
          dense
          button
          onClick={() => isFile && onFileSelect(node.path)}
        >
          <ListItemIcon>
            {isFile ? (
              <Checkbox
                edge="start"
                checked={isSelected}
                tabIndex={-1}
                disableRipple
              />
            ) : (
              <FolderIcon color="primary" />
            )}
          </ListItemIcon>
          <ListItemText primary={node.name} />
          {isFile && <InsertDriveFileIcon color="action" />}
        </ListItem>
        {node.children &&
          node.children.map((childNode) => renderTree(childNode))}
      </List>
    );
  };

  return (
    <Paper elevation={3} sx={{ maxHeight: '70vh', overflow: 'auto', p: 1 }}>
      {structure && renderTree(structure)}
    </Paper>
  );
};

export default DirectoryTree;
