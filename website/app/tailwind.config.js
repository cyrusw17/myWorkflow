/** @type {import('tailwindcss').Config} */
export default {
  content: ['./resources/views/**/*.blade.php'],
  theme: {
    extend: {
      colors: {
        accent: { DEFAULT: '#B87333', hover: '#9A6129', subtle: '#F5EDE6' },
      },
    },
  },
  plugins: [],
};
