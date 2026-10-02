"use client";

import { motion, useReducedMotion } from "framer-motion";

import { formatValue } from "@/lib/format";
import type { LegacyNumber } from "@/lib/types";

export function Strata({ legacy, governed, basis, revealed }: { legacy: LegacyNumber[]; governed: number; basis: string; revealed: boolean }) {
  const still = useReducedMotion();
  return (
    <div>
      <ol className="space-y-4">
        {legacy.map((l, i) => (
          <li key={l.key} className="grid grid-cols-12 gap-x-3 border-b border-hairline pb-3">
            <p className="micro col-span-12 md:col-span-3">
              {String(i + 1).padStart(2, "0")} {l.team} · {l.label}
            </p>
            <div className="relative col-span-12 md:col-span-4">
              <p className={`font-display text-3xl font-light tabular transition-colors duration-240 ${revealed ? "text-ash" : "text-bone"}`}>
                {formatValue(l.value, "ratio")}
              </p>
              <motion.span
                aria-hidden
                initial={false}
                animate={{ scaleX: revealed ? 1 : 0 }}
                transition={{ duration: still ? 0 : 0.24, delay: still ? 0 : i * 0.04, ease: [0.16, 1, 0.3, 1] }}
                style={{ originX: 0 }}
                className="absolute left-0 top-1/2 block h-px w-[12ch] bg-bone"
              />
            </div>
            <p className="col-span-12 text-sm text-ash md:col-span-5">{l.basis}</p>
          </li>
        ))}
      </ol>
      <motion.div
        initial={false}
        animate={{ opacity: revealed ? 1 : 0, y: revealed || still ? 0 : 8 }}
        transition={{ duration: 0.24, ease: [0.16, 1, 0.3, 1] }}
        className="mt-6 grid grid-cols-12 gap-x-3"
        aria-hidden={!revealed}
      >
        <p className="micro col-span-12 text-ore md:col-span-3">Governed · on_time_delivery v1</p>
        <p className="col-span-12 font-display text-5xl font-light tabular text-ore md:col-span-5">{formatValue(governed, "ratio")}</p>
        <p className="col-span-12 text-sm text-bone md:col-span-4">{basis}</p>
      </motion.div>
    </div>
  );
}
