// Monorepo support: resolve ../shared (single-source BLE protocol)
// without copying it into mobile/. Standard Metro watchFolders setup.
const { getDefaultConfig } = require('expo/metro-config');
const path = require('path');

const config = getDefaultConfig(__dirname);
config.watchFolders = [path.resolve(__dirname, '../shared')];
config.resolver.nodeModulesPaths = [path.resolve(__dirname, 'node_modules')];

module.exports = config;
