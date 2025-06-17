const { override, addBabelPreset } = require('customize-cra');
const path = require('path');

module.exports = override(
  addBabelPreset('@babel/preset-env', {
    targets: {
      node: 'current',
    },
  }),
  addBabelPreset('@babel/preset-react'),
  (config) => {
    // Apply babel loader configuration
    const babelRule = config.module.rules.find(rule => rule.oneOf).oneOf.find(
      rule => rule.loader && rule.loader.includes('babel-loader')
    );

    if (babelRule) {
      babelRule.include = [
        path.resolve('src'),
        path.resolve('node_modules/@mui/system')
      ];
    }

    // Force webpack to use the fixed version of nth-check for all instances
    // Also, add an alias for path-to-regexp to use our mock
    if (config.resolve && config.resolve.alias) {
      config.resolve.alias['nth-check'] = path.resolve(__dirname, 'node_modules/nth-check');
      config.resolve.alias['path-to-regexp'] = path.resolve(__dirname, 'tests/mock_path_to_regexp_fixed.js');
    } else if (config.resolve) {
      config.resolve.alias = {
        'nth-check': path.resolve(__dirname, 'node_modules/nth-check'),
        'path-to-regexp': path.resolve(__dirname, 'tests/mock_path_to_regexp_fixed.js')
      };
    } else {
      config.resolve = {
        alias: {
          'nth-check': path.resolve(__dirname, 'node_modules/nth-check'),
          'path-to-regexp': path.resolve(__dirname, 'tests/mock_path_to_regexp_fixed.js')
        }
      };
    }

    return config;
  }
);
