"use client";

import { useRef, type KeyboardEvent } from "react";

import { PERSONA_LABEL } from "@/lib/format";
import { DIAL, usePersona } from "@/lib/persona";

export function PersonaDial() {
  const { persona, signedInAs, pinned, setPersona } = usePersona();
  const buttons = useRef<(HTMLButtonElement | null)[]>([]);

  function onKey(event: KeyboardEvent, index: number) {
    const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    if (!step) return;
    event.preventDefault();
    const next = (index + step + DIAL.length) % DIAL.length;
    setPersona(DIAL[next]);
    buttons.current[next]?.focus();
  }

  return (
    <div role="radiogroup" aria-label="Answer as role" className="flex items-baseline gap-3">
      <span className="micro hidden lg:inline">Role</span>
      {DIAL.map((role, i) => {
        const active = role === persona;
        return (
          <button
            key={role}
            ref={(el) => {
              buttons.current[i] = el;
            }}
            type="button"
            role="radio"
            aria-checked={active}
            aria-disabled={pinned && !active ? true : undefined}
            tabIndex={active ? 0 : -1}
            onClick={() => setPersona(role)}
            onKeyDown={(e) => onKey(e, i)}
            className={`group relative pb-0.5 font-mono text-micro uppercase transition-colors duration-160 ${
              active ? "text-ore" : "text-ash hover:text-bone"
            }`}
          >
            <span className="mr-0.5 tabular text-ash" aria-hidden>
              {String(i + 1).padStart(2, "0")}
            </span>
            {PERSONA_LABEL[role]}
            {signedInAs === role ? <span className="sr-only"> (your role)</span> : null}
            <span
              aria-hidden
              className={`absolute -bottom-px left-0 h-px w-full transition-colors duration-160 ${active ? "bg-ore" : "bg-transparent"}`}
            />
          </button>
        );
      })}
    </div>
  );
}
