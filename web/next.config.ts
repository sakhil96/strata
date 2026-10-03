import type { NextConfig } from "next";

// STRATA_PREVIEW_API is the local preview only (scripts/preview.sh): next dev forwards /api to a
// local API, which a static export cannot do. Builds leave it unset and export as before.
const preview = process.env.STRATA_PREVIEW_API;

const config: NextConfig = {
  ...(preview ? {} : { output: "export" as const }),
  reactStrictMode: true,
  poweredByHeader: false,
  images: { unoptimized: true },
  env: {
    NEXT_PUBLIC_STRATA_MODE: process.env.STRATA_MODE ?? "live",
    NEXT_PUBLIC_STRATA_API: process.env.STRATA_API ?? "",
  },
  // Agent answers can take a minute; the dev proxy's own limit is 30 s.
  ...(preview
    ? {
        rewrites: async () => [{ source: "/api/:path*", destination: `${preview}/api/:path*` }],
        experimental: { proxyTimeout: 240_000 },
      }
    : {}),
};

export default config;
