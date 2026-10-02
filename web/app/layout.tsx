import type { Metadata } from "next";
import "@/styles/tokens.css";

export const metadata: Metadata = {
  title: "STRATA — Governed Supply Chain Ontology",
  description:
    "Three teams. Three numbers. One question. STRATA governs supply chain metrics through a single ontology.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-ground text-bone min-h-screen">
        <div className="mx-auto max-w-page px-3">{children}</div>
      </body>
    </html>
  );
}
