"use client";

import { animate, useInView, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

import { formatValue } from "@/lib/format";

export function Numeral({
  value,
  unit,
  className = "",
  digits,
}: {
  value: number | null | undefined;
  unit: string;
  className?: string;
  digits?: number;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const seen = useInView(ref, { once: true });
  const still = useReducedMotion();
  // The real value until the count-up runs, so a numeral never seen on screen never reads as zero.
  const [shown, setShown] = useState<number | null>(value ?? null);
  const counted = useRef(false);

  useEffect(() => {
    if (value === null || value === undefined) return setShown(null);
    if (still || counted.current) return setShown(value);
    if (!seen) return;
    counted.current = true;
    const controls = animate(0, value, { duration: 0.6, ease: [0.16, 1, 0.3, 1], onUpdate: setShown });
    return () => controls.stop();
  }, [value, seen, still]);

  return (
    <span ref={ref} className={`font-display tabular ${className}`}>
      <span className="sr-only">{formatValue(value, unit, digits)}</span>
      <span aria-hidden data-numeral={formatValue(value, unit, digits)}>
        {formatValue(shown, unit, digits)}
      </span>
    </span>
  );
}
