const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'renderer.js'),  // link the JS file for interaction
      nodeIntegration: true
    }
  });

  mainWindow.loadFile('index.html');  // Load the HTML UI
}

app.whenReady().then(() => {
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


// For versioning in the footer
const { app, ipcMain } = require("electron");
const packageJson = require("./package.json");

// Listen for version request from renderer process
ipcMain.on("get-app-version", (event) => {
    event.sender.send("app-version", packageJson.version);
});
