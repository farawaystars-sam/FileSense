const { app, BrowserWindow } = require('electron');
const path = require('path');
// For versioning in the footer
const { ipcMain } = require("electron");
const packageJson = require("./package.json");
const { stringify } = require('querystring');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    autoHideMenuBar: true,
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
console.log(packageJson.version);
// Listen for version request from renderer process
ipcMain.on("get-app-version", (event) => {
    console.log(packageJson)
    event.reply("app-version", packageJson.version);
}).catch(err => {

  console.error('Failed to get version:', err);

});