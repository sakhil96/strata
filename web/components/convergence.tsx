"use client";

import { motion, useReducedMotion } from "framer-motion";

import { PERSONA_LABEL, formatValue, shortHash } from "@/lib/format";
import type { CompareColumn } from "@/lib/types";

const OFFSETS = [-48, 24, -16];

export function Convergence({
  columns,
  converged,
  hash,
  settled = true,
}: {
  columns: CompareColumn[];
  converged: boolean;
  hash: string | null;
  settled?: boolean;
}) {
  const still = useReducedMotion();
  const aligned = settled && converged;
  return (
    <figure aria-label={converged ? "Three roles, one governed number" : "The roles did not agree"}>
      <div className="grid grid-cols-12 gap-x-3 gap-y-6">
        {columns.map((c, i) => (
          <div key={c.role} className="col-span-12 md:col-span-4">
            <p className="micro">
              {String(i + 1).padStart(2, "0")} {PERSONA_LABEL[c.role]}
            </p>
            <p className="mt-1 min-h-12 font-display text-lg italic font-light text-ash">&ldquo;{c.phrasing}&rdquo;</p>
            <motion.p
              initial={false}
              animate={{ y: aligned || still ? 0 : OFFSETS[i % OFFSETS.length] }}
              transition={{ duration: 0.24, ease: [0.16, 1, 0.3, 1], delay: i * 0.04 }}
              className={`mt-3 font-display text-4xl font-light tabular lg:text-5xl ${aligned ? "text-ore" : "text-bone"}`}
            >
              {c.refusal ? "—" : formatValue(c.value ?? null, c.unit ?? "ratio")}
            </motion.p>
            <p className="mt-1 font-mono text-micro text-ash">
              {c.refusal ? `not answered: ${c.refusal.replaceAll("_", " ")}` : `${c.metric_name} · ${shortHash(c.hash)}`}
            </p>
          </div>
        ))}
      </div>
      <figcaption className="mt-4">
        <motion.div
          initial={false}
          animate={{ scaleX: aligned ? 1 : 0 }}
          transition={{ duration: 0.24, ease: [0.16, 1, 0.3, 1] }}
          style={{ originX: 0 }}
          className="h-px bg-ore"
          aria-hidden
        />
        <p className="mt-1 font-mono text-micro text-ash">
          {aligned
            ? `one semantic query · ${hash}`
            : converged
              ? "resolving to the governed definition"
              : "the three phrasings resolved to different queries; open each ledger to see why"}
        </p>
      </figcaption>
    </figure>
  );
}
