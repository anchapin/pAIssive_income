# Enhanced Tailwind CSS Build System

This document describes the enhanced features of the Tailwind CSS build system.

## Table of Contents

- [Configuration File](#configuration-file)
- [Error Handling and Logging](#error-handling-and-logging)
- [Multiple Input/Output Files](#multiple-inputoutput-files)
- [Build Tool Integration](#build-tool-integration)
- [Custom PostCSS Plugins](#custom-postcss-plugins)
- [Command Line Interface](#command-line-interface)

## Configuration File

The build system now supports a JSON configuration file for storing default settings. This allows you to customize the build process without modifying the code.

### Default Configuration Locations

The system looks for configuration files in the following locations:

1. `./tailwind.config.json`
2. `./ui/tailwind.config.json`
3. `./config/tailwind.config.json`

### Configuration Structure

```json
{
  "defaults": {
    "static": {
      "configPath": "./tailwind.config.js",
      "inputPath": "./ui/static/css/tailwind.css",
      "outputPath": "./ui/static/css/tailwind.output.css",
      "minify": true
    },
    "react": {
      "configPath": "./ui/react_frontend/tailwind.config.js",
      "inputPath": "./ui/react_frontend/src/index.css",
      "outputPath": "./ui/react_frontend/src/tailwind.output.css",
      "minify": true
    }
  },
  "logging": {
    "level": "info",
    "format": "detailed",
    "logToFile": false,
    "logFilePath": "./logs/tailwind-build.log",
    "maxLogFileSize": 10485760,
    "maxLogFiles": 5
  },
  "buildTools": {
    "webpack": {
      "enabled": false,
      "configPath": "./webpack.config.js"
    },
    "vite": {
      "enabled": false,
      "configPath": "./vite.config.js"
    }
  },
  "postcss": {
    "useConfigFile": true,
    "configPath": "./postcss.config.js",
    "plugins": [
      {
        "name": "tailwindcss",
        "options": {}
      },
      {
        "name": "autoprefixer",
        "options": {}
      }
    ]
  },
  "errorHandling": {
    "retryCount": 3,
    "retryDelay": 1000,
    "failFast": false,
    "continueOnError": true
  },
  "performance": {
    "concurrentBuilds": 2,
    "cacheEnabled": true,
    "cachePath": "./.cache/tailwind"
  }
}
```

## Error Handling and Logging

The build system now includes enhanced error handling and logging capabilities.

### Log Levels

- `error`: Only critical errors
- `warn`: Warnings and errors
- `info`: General information (default)
- `debug`: Detailed debugging information

### Error Recovery

The system will automatically retry failed builds with configurable retry count and delay. You can configure:

- `retryCount`: Number of retry attempts (default: 3)
- `retryDelay`: Delay between retries in milliseconds (default: 1000)
- `failFast`: Whether to throw errors or return false (default: false)
- `continueOnError`: Whether to continue building other files if one fails (default: true)

### Log File

You can enable logging to a file by setting `logging.logToFile` to `true` and configuring the file path.

## Multiple Input/Output Files

The build system now supports processing multiple input/output file pairs in a single run.

### Command Line Usage

```bash
node tailwind_utils.js --add-file ./config1.js ./input1.css ./output1.css --add-file ./config2.js ./input2.css ./output2.css
```

### Configuration File

```json
{
  "additionalFiles": [
    {
      "configPath": "./config1.js",
      "inputPath": "./input1.css",
      "outputPath": "./output1.css",
      "minify": true
    },
    {
      "configPath": "./config2.js",
      "inputPath": "./input2.css",
      "outputPath": "./output2.css",
      "minify": false
    }
  ]
}
```

### Parallel Processing

You can enable parallel processing of multiple files by setting `--parallel` or configuring `performance.concurrentBuilds` to a value greater than 1.

## Build Tool Integration

The build system now integrates with popular build tools like webpack and Vite.

### Webpack Integration

```bash
node tailwind_utils.js --webpack ./webpack.config.js
```

This will:
1. Load the webpack configuration
2. Add PostCSS loader with Tailwind CSS if not already present
3. Run the webpack build process

### Vite Integration

```bash
node tailwind_utils.js --vite ./vite.config.js
```

This will run the Vite build process with Tailwind CSS integration.

## Custom PostCSS Plugins

The build system now supports custom PostCSS plugins through configuration.

### PostCSS Configuration File

```js
// postcss.config.js
module.exports = {
  plugins: {
    'tailwindcss': {},
    'autoprefixer': {},
    'postcss-preset-env': {
      features: {
        'nesting-rules': true
      }
    },
    'cssnano': process.env.NODE_ENV === 'production' ? {
      preset: ['default', {
        discardComments: {
          removeAll: true,
        },
      }]
    } : false
  }
};
```

### Command Line Usage

```bash
node tailwind_utils.js --postcss-config ./postcss.config.js
```

### Configuration File

```json
{
  "postcss": {
    "useConfigFile": true,
    "configPath": "./postcss.config.js",
    "plugins": [
      {
        "name": "tailwindcss",
        "options": {}
      },
      {
        "name": "autoprefixer",
        "options": {}
      },
      {
        "name": "postcss-preset-env",
        "options": {
          "features": {
            "nesting-rules": true
          }
        }
      }
    ]
  }
}
```

## Command Line Interface

The build system now supports an enhanced command line interface with more options.

```
Tailwind CSS Utility Script

Usage:
  node tailwind_utils.js [options]

Basic Options:
  --config <path>       Path to tailwind config file (default: ./tailwind.config.js)
  --input <path>        Path to input CSS file (default: ./ui/static/css/tailwind.css)
  --output <path>       Path to output CSS file (default: ./ui/static/css/tailwind.output.css)
  --watch               Watch for changes and rebuild
  --no-minify           Don't minify the output
  --help, -h            Display this help message

Advanced Options:
  --config-file <path>  Path to JSON configuration file
  --log-level <level>   Set log level (error, warn, info, debug)
  --parallel            Build multiple files in parallel
  --no-parallel         Disable parallel builds
  
Multiple File Support:
  --add-file <config> <input> <output>  Add a file to build (can be used multiple times)
  
PostCSS Integration:
  --postcss-config <path>  Path to PostCSS config file
  
Build Tool Integration:
  --webpack <path>      Enable webpack integration with config path
  --vite <path>         Enable Vite integration with config path
```
