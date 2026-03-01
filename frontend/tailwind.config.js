/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: "#1a1a2e",
        "navy-light": "#16213e",
        accent: "#0f3460",
        coral: "#e94560",
        success: "#00b894",
        warning: "#fdcb6e",
        danger: "#d63031",
      },
    },
  },
  plugins: [],
};
