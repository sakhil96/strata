"use client";

import { useState } from "react";

const PERSONAS = [
  { key: "PLANNING_ROLE", label: "Planning" },
  { key: "PROCUREMENT_ROLE", label: "Procurement" },
  { key: "LOGISTICS_ROLE", label: "Logistics" },
  { key: "EXECUTIVE_ROLE", label: "Executive" },
] as const;

interface PersonaDialProps {
  active: string;
  onChange: (persona: string) => void;
}

export function PersonaDial({ active, onChange }: PersonaDialProps) {
  return (
    <nav
      role="tablist"
      aria-label="Persona selector"
      className="flex gap-3 border-b border-hairline pb-1"
    >
      {PERSONAS.map((p) => (
        <button
          key={p.key}
          role="tab"
          aria-selected={active === p.key}
          onClick={() => onChange(p.key)}
          className={`
            text-micro uppercase tracking-widest pb-1 transition-colors duration-160
            border-b-2
            ${
              active === p.key
                ? "text-ore border-ore"
                : "text-ash border-transparent hover:text-bone"
            }
          `}
        >
          {p.label}
        </button>
      ))}
    </nav>
  );
}
