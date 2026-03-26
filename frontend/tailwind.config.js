/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#F8F9FA",
        primary: "#2D9CDB",
        success: "#27AE60",
      },
      fontFamily: {
        sans: ["Inter", "Poppins", "Roboto", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
