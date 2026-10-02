// Lighthouse against the static export. Needs Chrome and `npx lighthouse`; fails under the budgets.
import { execFileSync } from "node:child_process";
import { readFileSync, mkdirSync } from "node:fs";

const BASE = process.env.STRATA_URL ?? "http://127.0.0.1:8000";
const PAGES = ["/", "/ask", "/compare", "/before-after", "/glossary"];
const BUDGET = { performance: 0.9, accessibility: 1.0, "best-practices": 0.95 };

mkdirSync("lighthouse", { recursive: true });
let failed = 0;
for (const page of PAGES) {
  const out = `lighthouse/${page === "/" ? "home" : page.slice(1)}.json`;
  execFileSync(
    "npx",
    ["--yes", "lighthouse", BASE + page, "--quiet", "--output=json", `--output-path=${out}`, "--chrome-flags=--headless=new"],
    { stdio: "inherit" },
  );
  const report = JSON.parse(readFileSync(out, "utf8"));
  for (const [category, floor] of Object.entries(BUDGET)) {
    const score = report.categories[category].score;
    const ok = score >= floor;
    if (!ok) failed += 1;
    console.log(`${ok ? "pass" : "FAIL"}  ${page}  ${category} ${score} (floor ${floor})`);
  }
}
process.exit(failed ? 1 : 0);
