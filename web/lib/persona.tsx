"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { api } from "./api";
import type { Persona } from "./types";

export const DIAL: Persona[] = ["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE", "EXECUTIVE_ROLE"];
const STORAGE_KEY = "strata.persona";

interface PersonaState {
  persona: Persona;
  signedInAs: Persona | null;
  setPersona: (p: Persona) => void;
}

const Context = createContext<PersonaState | null>(null);

export function PersonaProvider({ children }: { children: ReactNode }) {
  const [persona, setPersonaState] = useState<Persona>("EXECUTIVE_ROLE");
  const [signedInAs, setSignedInAs] = useState<Persona | null>(null);

  useEffect(() => {
    const kept = window.sessionStorage.getItem(STORAGE_KEY) as Persona | null;
    api
      .personas()
      .then(({ default: role }) => {
        setSignedInAs(role);
        if (!kept) setPersonaState(role);
      })
      .catch(() => setSignedInAs(null));
    if (kept && DIAL.includes(kept)) setPersonaState(kept);
  }, []);

  const setPersona = useCallback((p: Persona) => {
    setPersonaState(p);
    window.sessionStorage.setItem(STORAGE_KEY, p);
  }, []);

  const value = useMemo(() => ({ persona, signedInAs, setPersona }), [persona, signedInAs, setPersona]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function usePersona(): PersonaState {
  const state = useContext(Context);
  if (!state) throw new Error("usePersona must sit inside PersonaProvider");
  return state;
}
