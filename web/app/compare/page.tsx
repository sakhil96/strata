"use client";

import { useEffect, useState } from "react";

import { Convergence } from "@/components/convergence";
import { Ledger } from "@/components/ledger";
import { PageHead } from "@/components/section";
import { Loading, Problem } from "@/components/states";
import { ApiProblem, api } from "@/lib/api";
import { PERSONA_LABEL } from "@/lib/format";
import type { CompareResult, Persona } from "@/lib/types";

const ROLES: Persona[] = ["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE"];
const CASES: { title: string; phrasings: Record<string, string> }[] = [
  {
    title: "On-time delivery, FY2026",
    phrasings: {
      PLANNING_ROLE: "What is our delivery rate for FY2026?",
      PROCUREMENT_ROLE: "What is customer delivery performance for FY2026?",
      LOGISTICS_ROLE: "What is delivery reliability for FY2026?",
    },
  },
  {
    title: "Fill rate in Q3",
    phrasings: {
      PLANNING_ROLE: "What was availability in Q3?",
      PROCUREMENT_ROLE: "What was unit fill in Q3?",
      LOGISTICS_ROLE: "What was shipment completeness in Q3?",
    },
  },
  {
    title: "Days of inventory at year end",
    phrasings: {
      PLANNING_ROLE: "What are our days of supply?",
      PROCUREMENT_ROLE: "How many stock days do we hold?",
      LOGISTICS_ROLE: "What is warehouse days cover?",
    },
  },
];

export default function ComparePage() {
  const [chosen, setChosen] = useState(0);
  const [phrasings, setPhrasings] = useState<Record<string, string>>(CASES[0].phrasings);
  const [result, setResult] = useState<CompareResult | null>(null);
  const [problem, setProblem] = useState<ApiProblem | null>(null);
  const [busy, setBusy] = useState(false);
  const [settled, setSettled] = useState(false);
  const [open, setOpen] = useState<Persona | null>(null);

  async function run(next: Record<string, string>) {
    setBusy(true);
    setSettled(false);
    setProblem(null);
    try {
      const reply = await api.compare(next);
      setResult(reply);
      window.setTimeout(() => setSettled(true), 400);
    } catch (err) {
      setProblem(err instanceof ApiProblem ? err : new ApiProblem({ error: "failed", message: String(err) }, 0));
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void run(CASES[0].phrasings);
  }, []);

  return (
    <>
      <PageHead
        numeral="06"
        kicker="Three roles, three phrasings"
        title="Do the teams agree?"
        lede="Each role asks in its own words and runs under its own Snowflake role. When the three semantic queries hash the same, the numerals settle on one baseline and a single hairline joins them."
      />
      <div className="mb-6 flex flex-wrap gap-3">
        {CASES.map((c, i) => (
          <button
            key={c.title}
            type="button"
            className={i === chosen ? "action" : "quiet-action"}
            onClick={() => {
              setChosen(i);
              setPhrasings(c.phrasings);
              void run(c.phrasings);
            }}
          >
            {c.title}
          </button>
        ))}
      </div>
      <form
        className="mb-8 grid grid-cols-12 gap-x-3 gap-y-2"
        onSubmit={(e) => {
          e.preventDefault();
          void run(phrasings);
        }}
      >
        {ROLES.map((role) => (
          <label key={role} className="col-span-12 md:col-span-4">
            <span className="micro">{PERSONA_LABEL[role]} asks</span>
            <input
              className="control mt-0.5 w-full"
              value={phrasings[role] ?? ""}
              maxLength={500}
              onChange={(e) => setPhrasings({ ...phrasings, [role]: e.target.value })}
            />
          </label>
        ))}
        <div className="col-span-12">
          <button type="submit" className="action" disabled={busy}>
            {busy ? "Asking all three" : "Ask all three"}
          </button>
        </div>
      </form>
      <div aria-live="polite">
        {busy && !result ? <Loading what="Asking as planning, procurement and logistics" /> : null}
        {problem ? <Problem problem={problem} /> : null}
        {result ? (
          <Convergence columns={result.columns} converged={result.converged} hash={result.hash} settled={settled} />
        ) : null}
      </div>
      {result ? (
        <div className="mt-8 grid grid-cols-12 gap-x-3">
          {result.columns.map((c) => (
            <div key={c.role} className="col-span-12 md:col-span-4">
              <button
                type="button"
                className="quiet-action"
                aria-expanded={open === c.role}
                onClick={() => setOpen(open === c.role ? null : c.role)}
              >
                {open === c.role ? "Close" : "Open"} the {PERSONA_LABEL[c.role].toLowerCase()} ledger
              </button>
              {open === c.role && c.ledger ? <Ledger answer={c.ledger} /> : null}
            </div>
          ))}
        </div>
      ) : null}
    </>
  );
}
