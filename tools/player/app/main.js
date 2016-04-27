'use strict';

const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
let mainWindow;

function createWindow () {
  mainWindow = new BrowserWindow({width: 800, height: 600, frame: false, movable: false, resizable: false, transparent: true});
  
  mainWindow.setSkipTaskbar(true);
  // app.dock.setBadge('') 

  mainWindow.setAlwaysOnTop(true);
  mainWindow.setPosition(100, 100);
  mainWindow.setSize(300, 300);
  
  mainWindow.loadURL('file://' + __dirname + '/../../../../../build/html5/index.html');
  // mainWindow.loadURL('http://localhost:8080');
  mainWindow.on('closed', function() {
    mainWindow = null;
  });
}

app.on('ready', createWindow);
app.on('window-all-closed', function () {
  //if (process.platform !== 'darwin') {
    app.quit();
  //}
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});
