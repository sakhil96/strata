import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    fontFamily: {
      display: ["Fraunces", "serif"],
      sans: ["Instrument Sans", "sans-serif"],
      mono: ["JetBrains Mono", "monospace"],
    },
    fontSize: {
      micro: ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.14em" }],
      sm: ["0.8125rem", { lineHeight: "1.25rem" }],
      base: ["0.9375rem", { lineHeight: "1.5rem" }],
      lg: ["1.125rem", { lineHeight: "1.75rem" }],
      xl: ["1.5rem", { lineHeight: "2rem" }],
      "2xl": ["2.25rem", { lineHeight: "2.5rem" }],
      "3xl": ["3.5rem", { lineHeight: "3.75rem" }],
      "4xl": ["5.5rem", { lineHeight: "5.5rem" }],
      "5xl": ["8rem", { lineHeight: "8rem" }],
    },
    colors: {
      ground: "#0B0D10",
      stratum: "#121519",
      "stratum-2": "#181C22",
      hairline: "#232830",
      bone: "#E9E4DA",
      ash: "#9AA0A6",
      ore: "#E36F2E",
      good: "#6FCF97",
      warn: "#F2C94C",
      critical: "#EB5757",
      paper: "#F4F1EA",
      ink: "#121212",
      transparent: "transparent",
    },
    spacing: {
      0: "0px",
      1: "8px",
      2: "16px",
      3: "24px",
      4: "32px",
      5: "40px",
      6: "48px",
      8: "64px",
      10: "80px",
      12: "96px",
      16: "128px",
      20: "160px",
    },
    borderRadius: {
      none: "0",
      sm: "2px",
      DEFAULT: "2px",
    },
    maxWidth: {
      page: "1440px",
    },
    extend: {
      gridTemplateColumns: {
        "12": "repeat(12, minmax(0, 1fr))",
      },
    },
  },
};

export default config;
