/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        heading: ["Raleway", "system-ui", "sans-serif"],
        body: ["Lato", "system-ui", "sans-serif"],
      },
      colors: {
        halo: {
          primary: "rgb(26,153,136)",     // #1A9988
          secondary: "rgb(235,86,0)",     // #EB5600
          softGreen: "rgb(176,192,159)",  // #B0C09F
          softYellow: "rgb(241,205,86)",  // #F1CD56
          softBlue: "rgb(205,226,235)",   // #CDE2EB
        },
      },
      borderRadius: {
        halo: "16px",
      },
    },
  },
  plugins: [],
};
