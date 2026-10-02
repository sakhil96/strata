import type { Config } from "tailwindcss";

const token = (name: string) => `rgb(var(--${name}) / <alpha-value>)`;

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  safelist: ["text-micro", "text-sm", "text-base", "text-lg", "text-xl", "text-2xl", "text-3xl", "text-4xl", "text-5xl"],
  theme: {
    colors: {
      transparent: "transparent",
      current: "currentColor",
      ground: token("ground"),
      stratum: token("stratum"),
      "stratum-2": token("stratum-2"),
      hairline: token("hairline"),
      bone: token("bone"),
      ash: token("ash"),
      ore: token("ore"),
      good: token("good"),
      warn: token("warn"),
      critical: token("critical"),
      paper: token("paper"),
      ink: token("ink"),
    },
    fontFamily: {
      display: ["Fraunces", "Georgia", "serif"],
      sans: ["Instrument Sans", "system-ui", "sans-serif"],
      mono: ["JetBrains Mono", "ui-monospace", "monospace"],
    },
    fontSize: {
      micro: ["11px", { lineHeight: "16px", letterSpacing: "0.14em" }],
      sm: ["13px", { lineHeight: "20px" }],
      base: ["15px", { lineHeight: "24px" }],
      lg: ["18px", { lineHeight: "28px" }],
      xl: ["24px", { lineHeight: "32px" }],
      "2xl": ["36px", { lineHeight: "40px", letterSpacing: "-0.01em" }],
      "3xl": ["56px", { lineHeight: "56px", letterSpacing: "-0.02em" }],
      "4xl": ["88px", { lineHeight: "88px", letterSpacing: "-0.03em" }],
      "5xl": ["128px", { lineHeight: "120px", letterSpacing: "-0.04em" }],
    },
    spacing: {
      0: "0",
      px: "1px",
      0.5: "4px",
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
      rail: "320px",
    },
    borderRadius: { none: "0", sm: "2px" },
    boxShadow: { none: "none" },
    screens: { sm: "390px", md: "768px", lg: "1024px", xl: "1440px" },
    extend: {
      maxWidth: { page: "1440px", measure: "60ch", rail: "320px" },
      transitionDuration: { 120: "120ms", 160: "160ms", 240: "240ms" },
      transitionTimingFunction: { out: "cubic-bezier(0.16, 1, 0.3, 1)" },
    },
  },
};

export default config;
