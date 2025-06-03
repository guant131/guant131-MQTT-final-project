const { defineConfig } = require('@vue/cli-service');
const webpack = require('webpack');

// vue.config.js
module.exports = {
  configureWebpack: {
    resolve: {
      fallback: {
        fs: require.resolve('browserify-fs'),
        path: require.resolve('path-browserify'),
        stream: require.resolve('stream-browserify'),
        buffer: require.resolve('buffer/'),
        process: require.resolve('process/browser'),
        util: require.resolve('util-deprecate'),
        http: require.resolve('stream-http'),
        crypto: require.resolve("crypto-browserify"),
        vm: require.resolve("vm-browserify"),
      }
    },
    plugins: [
      new webpack.ProvidePlugin({
        Buffer: ['buffer', 'Buffer'],
        process: 'process/browser',
      })
    ]
  }
};