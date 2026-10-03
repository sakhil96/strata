"use client";

import { AnimatePresence, motion } from "framer-motion";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { DEMO } from "@/lib/api";

// The live service endpoint; the mirror links to it and holds nothing that can call it.
const LIVE_URL = process.env.NEXT_PUBLIC_STRATA_LIVE_URL ?? "https://mbloac-dzvlnoz-zv32033.snowflakecomputing.app";
import { PersonaProvider } from "@/lib/persona";

import { PersonaDial } from "./persona-dial";
import { StatusLine } from "./status-line";

const NAV = [
  { href: "/ask", label: "Ask" },
  { href: "/compare", label: "Compare" },
  { href: "/before-after", label: "Before and after" },
  { href: "/glossary", label: "Glossary" },
  { href: "/governance", label: "Governance" },
  { href: "/operations", label: "Operations" },
  { href: "/about", label: "About" },
];

export function Shell({ children }: { children: ReactNode }) {
  const path = usePathname();
  return (
    <PersonaProvider>
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:bg-ground focus:p-1">
        Skip to content
      </a>
      <header className="mx-auto max-w-page px-3">
        <div className="flex flex-wrap items-baseline justify-between gap-y-2 border-b border-hairline py-2">
          <Link href="/" className="font-display text-lg font-semibold tracking-tight text-bone">
            Strata
            <span className="ml-1 font-mono text-micro uppercase text-ash">supply chain ontology</span>
          </Link>
          <PersonaDial />
        </div>
        <nav aria-label="Primary" className="flex flex-wrap gap-x-3 gap-y-1 py-1">
          {NAV.map((n) => {
            const here = path === n.href || path?.startsWith(`${n.href}/`);
            return (
              <Link
                key={n.href}
                href={n.href}
                aria-current={here ? "page" : undefined}
                className={`text-sm underline-offset-4 transition-colors duration-160 ${
                  here
                    ? "text-bone underline decoration-ore"
                    : "text-ash hover:text-bone hover:underline hover:decoration-hairline"
                }`}
              >
                {n.label}
              </Link>
            );
          })}
        </nav>
        {DEMO ? (
          <p className="micro border-t border-hairline py-1 text-warn">
            Recorded demo data · answers replayed from the recorded local build; nothing here reaches Snowflake.{" "}
            <a className="underline" href={LIVE_URL}>
              Open the live app
            </a>
          </p>
        ) : null}
      </header>
      <AnimatePresence mode="wait">
        <motion.main
          id="main"
          key={path}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.12 }}
          className="mx-auto max-w-page px-3 pb-12"
        >
          {children}
        </motion.main>
      </AnimatePresence>
      <footer className="mx-auto max-w-page px-3">
        <div className="border-t border-hairline py-2">
          <StatusLine />
        </div>
      </footer>
    </PersonaProvider>
  );
}
