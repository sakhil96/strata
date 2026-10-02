import type { NextConfig } from "next";

const config: NextConfig = {
  output: "export",
  reactStrictMode: true,
  poweredByHeader: false,
  images: { unoptimized: true },
  env: {
    NEXT_PUBLIC_STRATA_MODE: process.env.STRATA_MODE ?? "live",
    NEXT_PUBLIC_STRATA_API: process.env.STRATA_API ?? "",
  },
};

export default config;
