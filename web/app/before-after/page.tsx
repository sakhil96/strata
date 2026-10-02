"use client";

import { useState } from "react";
import { Strata } from "@/components/strata";
import { SectionNumber } from "@/components/section-number";
import { StatusBar } from "@/components/status-bar";

export default function BeforeAfterPage() {
  return (
    <main className="pt-6">
      <SectionNumber number="06" />
      <h1 className="font-display text-2xl font-light mt-1 mb-4">
        Before and after
      </h1>

      <p className="text-ash text-base max-w-[600px] mb-6">
        Compare legacy definitions with the governed answer. Each legacy
        definition used a different date basis, exclusion rule, or averaging
        method. The governed answer uses the ontology&rsquo;s single definition.
      </p>

      <div className="grid grid-cols-12 gap-3">
        <div className="col-span-7">
          <Strata
            legacy={[
              {
                label: "Planning team (requested date basis)",
                basis: "actual_delivery_date <= requested_date",
                value: "88.7%",
              },
              {
                label: "Logistics team (carrier ETA basis)",
                basis: "actual_delivery <= carrier_eta",
                value: "93.1%",
              },
              {
                label: "Executive dashboard (included cancelled)",
                basis: "committed_date basis, cancelled lines included",
                value: "86.2%",
              },
            ]}
            governed={{
              value: "91.3%",
              basis:
                "actual_delivery_date <= committed_date, cancelled excluded (on_time_delivery v1)",
            }}
          />
        </div>
        <div className="col-span-5">
          <div className="border-l border-hairline pl-3 py-2">
            <p className="text-micro uppercase text-ash tracking-widest">
              Why the numbers differ
            </p>
            <ul className="text-sm text-ash space-y-2 mt-2">
              <li>
                Planning used the customer-requested date, which is typically
                earlier than the committed date, producing a lower number.
              </li>
              <li>
                Logistics compared against carrier ETA, which is set by the
                carrier after shipment, producing a higher number.
              </li>
              <li>
                The executive dashboard included cancelled lines in the
                denominator, diluting the rate.
              </li>
              <li>
                The governed definition uses committed date, excludes cancelled
                lines, and measures delivery — the SCOR-aligned standard.
              </li>
            </ul>
          </div>
        </div>
      </div>

      <StatusBar />
    </main>
  );
}
