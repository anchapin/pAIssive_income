/**
 * PostCSS Configuration
 * 
 * This file configures PostCSS plugins for the project.
 * It includes Tailwind CSS and other PostCSS plugins.
 */

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
