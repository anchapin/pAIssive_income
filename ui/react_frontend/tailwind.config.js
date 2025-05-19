/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
    "./index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          main: '#4e73df',
        },
        secondary: {
          main: '#858796',
        },
        success: {
          main: '#1cc88a',
        },
        info: {
          main: '#36b9cc',
        },
        warning: {
          main: '#f6c23e',
        },
        error: {
          main: '#e74a3b',
        },
        background: {
          default: '#f8f9fc',
          paper: '#ffffff',
        },
      },
      fontFamily: {
        sans: ['"Nunito"', '"Helvetica"', '"Arial"', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
