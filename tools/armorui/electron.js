'use strict';
const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
let mainWindow;

function createWindow () {
    mainWindow = new BrowserWindow({width: 1240, height: 640, autoHideMenuBar: true, useContentSize: true});
    mainWindow.loadURL('file://' + __dirname + '/index.html');
    mainWindow.on('closed', function() { mainWindow = null; });
}
app.on('ready', createWindow);
app.on('window-all-closed', function () { app.quit(); });
app.on('activate', function () { if (mainWindow === null) { createWindow(); } });