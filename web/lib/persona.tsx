"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { api } from "./api";
import type { Persona } from "./types";

export const DIAL: Persona[] = ["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE", "EXECUTIVE_ROLE", "EMEA_PLANNING_ROLE"];
const STORAGE_KEY = "strata.persona";

interface PersonaState {
  persona: Persona;
  signedInAs: Persona | null;
  pinned: boolean;
  setPersona: (p: Persona) => void;
}

const Context = createContext<PersonaState | null>(null);

export function PersonaProvider({ children }: { children: ReactNode }) {
  const [persona, setPersonaState] = useState<Persona>("EXECUTIVE_ROLE");
  const [signedInAs, setSignedInAs] = useState<Persona | null>(null);
  const [pinned, setPinned] = useState(false);

  useEffect(() => {
    const kept = window.sessionStorage.getItem(STORAGE_KEY) as Persona | null;
    api
      .personas()
      .then(({ default: role, pinned: fixed }) => {
        setSignedInAs(role);
        setPinned(Boolean(fixed));
        // A signed-in user mapped to a persona answers as that persona; the dial follows them.
        if (fixed || !kept) setPersonaState(role);
      })
      .catch(() => setSignedInAs(null));
    if (kept && DIAL.includes(kept)) setPersonaState(kept);
  }, []);

  const setPersona = useCallback(
    (p: Persona) => {
      if (pinned) return;
      setPersonaState(p);
      window.sessionStorage.setItem(STORAGE_KEY, p);
    },
    [pinned],
  );

  const value = useMemo(() => ({ persona, signedInAs, pinned, setPersona }), [persona, signedInAs, pinned, setPersona]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function usePersona(): PersonaState {
  const state = useContext(Context);
  if (!state) throw new Error("usePersona must sit inside PersonaProvider");
  return state;
}
