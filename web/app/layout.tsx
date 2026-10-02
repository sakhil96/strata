import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import { Shell } from "@/components/shell";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: { default: "Strata · governed supply chain metrics", template: "%s · Strata" },
  description:
    "One supply chain ontology, compiled into governed Snowflake semantic views, so planning, procurement and logistics get the same number for the same question.",
};

export const viewport: Viewport = { themeColor: "#0B0D10", colorScheme: "dark" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en-GB">
      <body className="min-h-screen bg-ground text-bone">
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
