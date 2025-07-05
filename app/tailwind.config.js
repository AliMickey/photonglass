module.exports = {
    content: [
      "./templates/**/*.html"
    ],
    darkMode: 'class',
    theme: {
      extend: {
        colors: {
          primary: {
            DEFAULT: '#4a5568'
          },
          dark: {
            DEFAULT: '#121212',
            100: '#1E1E1E',
            200: '#2D2D2D',
            300: '#3D3D3D',
            400: '#4D4D4D',
            500: '#5C5C5C'
          }
        },
        fontSize: {
          'base': '1.125rem',
          'sm': '1rem',
          'lg': '1.25rem', 
          'xl': '1.375rem',
          '2xl': '1.5rem',
          '3xl': '1.875rem',
          '4xl': '2.25rem',
          '5xl': '3rem',
        }
      },
    },
    plugins: [],
  }