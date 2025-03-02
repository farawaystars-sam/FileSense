const { app, BrowserWindow, ipcMain, dialog } = require('electron/main')
const path = require('path');
// For versioning in the footer
// const { ipcMain } = require("electron");
const packageJson = require("./package.json");
const { stringify } = require('querystring');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    //autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),  // link the JS file for interaction
      nodeIntegration: true
    }
  });

  mainWindow.loadFile('index.html');  // Load the HTML UI
}

// // Handle the folder selection request
// ipcMain.handle('select-folder', async () => {
//     const result = await dialog.showOpenDialog({
//         title: "Select a folder",
//         properties: ["openDirectory"]
//     });
//     // Return the selected folder path or null if canceled
//     return result.filePaths.length > 0 ? result.filePaths[0] : null;
// });

console.log(packageJson.version);
// Listen for version request from renderer process
// ipcMain.on("get-app-version", (event) => {
//     console.log(packageJson)
//     event.reply("app-version", packageJson.version);
// }).catch(err => {
//   console.error('Failed to get version:', err);
// });

async function handleFileOpen () {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openDirectory'] // Specify that you want to open a directory
  });

  if (!canceled) {
    return filePaths[0]
  }
  else{
    return null
  }
}
async function do_something(inputPath) {
  return `Processed: ${inputPath.toUpperCase()}`;
}

ipcMain.handle('process-path', async (event, inputPath) => {
  const result = await do_something(inputPath);
  return result;
});

app.whenReady().then(() => {
  ipcMain.handle('dialog:openFile', handleFileOpen)
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// TODO on selecting the folder path call backend to get json to diplay intiatial tree
// TODO on click on process button call backend to process and return for data for b data
// TODO on click accept call backend to implemet the changes
