import { test } from "@playwright/test";

// Committed for design review; regenerate with `npm run e2e -- screenshots`.
const PAGES = ["/", "/ask", "/compare", "/before-after", "/glossary", "/governance", "/operations", "/about"];

for (const path of PAGES) {
  test(`capture ${path}`, async ({ page }, info) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto(path);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1500);
    const name = path === "/" ? "landing" : path.slice(1).replaceAll("/", "-");
    await page.screenshot({ path: `tests/screenshots/${info.project.name}-${name}.png`, fullPage: true });
  });
}
